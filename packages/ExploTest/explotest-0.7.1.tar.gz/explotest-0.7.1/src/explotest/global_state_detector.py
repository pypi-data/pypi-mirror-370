"""
The global state detector detects all potential global state in a program. For now, the strategy is static in nature.
It's a part of the test generation pass cycle. All global state will probably be mocked.
"""

import ast
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, override, Literal

from .reconstructor import Reconstructor


@dataclass
class External(ABC):
    value: Any
    name: str

    @abstractmethod
    def get_mock(self, reconstructor: Reconstructor) -> list[ast.AST]: ...

    @override
    def __str__(self):
        return self.name


@dataclass
class ExternalVariable(External):
    @override
    def get_mock(self, reconstructor: Reconstructor) -> list[ast.AST]:
        return []  # stub


@dataclass
class ExternalProcedure(External):
    @override
    def get_mock(self, reconstructor: Reconstructor) -> list[ast.AST]:
        return []  # stub


@dataclass
class CallToOpen(External):
    @override
    def get_mock(self, reconstructor: Reconstructor) -> list[ast.AST]:
        return []  # stub


def find_global_vars(source: ast.Module, proc_name: str) -> list[External]:
    """
    Returns the fully qualified names of all the global variables used in a specified function.
    Raises `ValueError` if function was not found in the source.
    """

    result: list[External] = []

    target_def = find_function_def(source, proc_name)

    if target_def is None:
        raise ValueError(
            f"Function definition not found! source:\n{ast.dump(source, indent=4)}\n\nproc_name: {proc_name}"
        )

    args = target_def.args

    for idx, line in enumerate(target_def.body):
        # print("proc: find_global_vars")
        # print(ast.unparse(line))
        # print("end proc")
        named_attrs = find_names_attributes(line)
        for attr in named_attrs:
            # print(attr)

            attribute_parent = unwrap_attribute(attr)
            if attribute_parent == "CONSTANT":
                continue  # ignore this one, as it's an operation on a constant. string functions are immutable
            defn = find_var_defn(attribute_parent, idx, target_def)
            if defn is None and ast.unparse(
                ast.fix_missing_locations(attribute_parent)
            ) not in [a.arg for a in args.args]:
                # we found an attribute that's external
                # classify the attribute

                result.append(ExternalVariable(None, attribute_parent.id))

    return result


#
# def classify_name(
#     name: ast.Name | Literal["CONSTANT"], name_idx: int, proc: ast.FunctionDef
# ) -> External | Literal["LOCAL"]:
#     """
#     Given a name in the AST, its line position (for more detail), classify whether it's a:
#     - Reference to external variable
#     - External procedure call
#     - Call to `open`.
#     - The string "LOCAL" if the name is defined within the function.
#     """
#     if name == "CONSTANT":
#         return


def unwrap_attribute(
    attribute: ast.Attribute | ast.Name | ast.Call,
) -> ast.Name | Literal["CONSTANT"]:
    if isinstance(
        attribute, ast.Constant
    ):  # case where parent is an instance literal, e.g., a string "abc"
        return "CONSTANT"

    if isinstance(attribute, ast.Name):
        return attribute

    if isinstance(attribute, ast.Call):
        return unwrap_attribute(attribute.func)

    parent = attribute.value

    return unwrap_attribute(parent)


def ast_traverse_find_names_attrs(line: ast.AST) -> list[ast.Name]:
    result = []

    class AttributeAndNameVisitor(ast.NodeVisitor):
        def visit_Attribute(self, node: ast.Attribute):
            result.append(node)

        def visit_Name(self, node: ast.Name):
            result.append(node)

    AttributeAndNameVisitor().visit(line)

    return result


def find_names_attributes(line: ast.AST) -> list[ast.Attribute | ast.Name]:
    """
    Returns all the names and attribute access on a line
    """

    result: list[ast.Attribute | ast.Name] = []

    if isinstance(line, ast.Expr):
        # unwrap expr
        return find_names_attributes(line.value)

    if isinstance(line, ast.Assign):
        # if we have an assign, only look at RHS
        return find_names_attributes(line.value)

    if isinstance(line, ast.Attribute) or isinstance(line, ast.Name):
        return [line]

    # handle "single variable comprehensions"
    if (
        isinstance(line, ast.ListComp)
        or isinstance(line, ast.SetComp)
        or isinstance(line, ast.GeneratorExp)
    ):
        for attr in find_line_attrs_in_sv_comp(line):
            result.append(attr)
    else:
        result += ast_traverse_find_names_attrs(line)

    return result


def find_line_attrs_in_sv_comp(
    line: ast.ListComp | ast.SetComp | ast.GeneratorExp,
) -> list[ast.Attribute]:
    """
    Finds lines and attributes in a single-variable comprehension (i.e., list, set and generator comprehensions)
    """
    result: list[ast.Attribute] = []
    ignorelist: list[ast.Name] = []
    for g in line.generators:
        ignorelist.append(g.target)

    asts_of_interest: list[ast.AST] = []
    asts_of_interest.append(line.elt)

    for g in line.generators:
        asts_of_interest += g.ifs

    for interesting in asts_of_interest:
        names_found = ast_traverse_find_names_attrs(interesting)
        result += list(
            filter(
                lambda attr: ast.unparse(attr)
                not in map(lambda attr: ast.unparse(attr), ignorelist),
                names_found,
            )
        )

    return result


def find_var_defn(
    var: ast.Name, var_idx_in_body: int, func: ast.FunctionDef
) -> ast.Assign | None:
    """
    Find the variable definition of the variable passed in w/ a functiondef.
    Returns none if no in-function definition was found.
    """
    lines_to_look_at = func.body[0:var_idx_in_body]
    for line in reversed(lines_to_look_at):  # look bottom up
        # find any assigns to var
        if isinstance(line, ast.Assign):
            if any(
                [
                    ast.unparse(ast.fix_missing_locations(target))
                    == ast.unparse(ast.fix_missing_locations(var))
                    for target in line.targets
                    if isinstance(target, ast.Name)
                ]
            ):
                return line
    return None


def find_function_def(source: ast.Module, proc_name: str) -> ast.FunctionDef | None:
    """
    Finds the function definition with `proc_name`. Returns None if not found.
    TODO: support function overloading.
    """
    for line in source.body:
        if isinstance(line, ast.FunctionDef):
            if proc_name == line.name:
                return line
    return None
