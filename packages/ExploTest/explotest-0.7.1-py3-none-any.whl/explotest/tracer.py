import ast
import inspect
import types
from pathlib import Path
from typing import Callable, Any

import dill

from explotest.ast_truncator import ASTTruncator
from explotest.helpers import is_lib_file, random_id


def make_tracer() -> Callable:
    def _tracer(frame: types.FrameType, event: str, _arg: Any):
        """
        Hooks onto default tracer to add instrumentation for ExploTest.
        :param frame: the current python frame
        :param event: the current event (one-of "line", "call", "return")
        :param _arg: currently not used
        :return: must return this object for tracing to work
        """
        filename = frame.f_code.co_filename

        # ignore files we don't have access to
        # NOTE: scratchpad is for dev purposes
        if (
            is_lib_file(filename)
            or (
                "explotest" in filename
                and "scratchpad" not in filename
                and "sc2" not in filename
            )
            or "<string>" in filename
        ):
            return _tracer

        path = Path(filename)
        path.resolve()

        if event == "call":

            # if frame.f_lineno == 0:
            #     return _tracer

            func_name = frame.f_code.co_name
            func = frame.f_globals.get(func_name) or frame.f_locals.get(func_name)

            if hasattr(func, "__data__"):
                globals_id = random_id()
                locals_id = random_id()

                counter = func.__data__
                func.__data__ += 1
                
                # frame^0 is the tracer
                # frame^1 is the function-under-test
                # frame^2 is the function wrapper
                # frame^3 is the caller of the function
                prev_caller = inspect.currentframe().f_back.f_back.f_back
                prev_locals = prev_caller.f_locals
                prev_globals = prev_caller.f_globals
                
                dill.settings["recurse"] = True

                globals_path = f"{path.parent}/pickled/globals_{func_name}_{counter}_{globals_id}.pkl"
                locals_path = f"{path.parent}/pickled/locals_{func_name}_{counter}_{locals_id}.pkl"

                builtins = [
                    "__doc__",
                    "__package__",
                    "__file__",
                    "__loader__",
                    "__spec__",
                    "__annotations__",
                    "__builtins__",
                    "__cached__",
                ]
                for builtin_name in builtins:
                    prev_globals.pop(builtin_name, None)
                with (
                    open(globals_path, "wb") as globals_file,
                    open(locals_path, "wb") as locals_file,
                ):
                    globals_file.write(dill.dumps(dict(prev_globals)))
                    locals_file.write(dill.dumps(dict(prev_locals)))

                # beginning of call block
                begin_line = inspect.getsourcelines(prev_caller)[1]

                # lineno of calling line
                lineno = prev_caller.f_lineno
                adjusted_lineno = lineno - max(1, begin_line) + 1

                if prev_caller.f_code.co_name == "<module>":
                    caller_ast = ast.parse(inspect.getsource(prev_caller).strip())

                    class FunctionRemover(ast.NodeTransformer):
                        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                            return None

                        def visit_ClassDef(self, node: ast.ClassDef) -> None:
                            return None

                    ASTTruncator(adjusted_lineno).visit(caller_ast)
                    fr = FunctionRemover()
                    fr.visit(caller_ast)

                    body = caller_ast.body

                else:
                    # a function or method is the caller
                    caller_ast = ast.parse(inspect.getsource(prev_caller).strip())
                    # print(ast.dump(caller_ast, indent=4, include_attributes=True))

                    trunc = ASTTruncator(adjusted_lineno)

                    # TODO: unsafe
                    body = trunc.visit(caller_ast).body[0].body

                fd = ast.FunctionDef(
                    f"test_{func_name}_{counter}",
                    args=ast.arguments(),
                    body=[
                        ast.Import(names=[ast.alias(name="dill")]),
                        ast.Import(names=[ast.alias(name="inspect")]),
                        ast.With(
                            items=[
                                ast.withitem(
                                    context_expr=ast.Call(
                                        func=ast.Name(id="open", ctx=ast.Load()),
                                        args=[
                                            ast.Constant(value=globals_path),
                                            ast.Constant(value="rb"),
                                        ],
                                    ),
                                    optional_vars=ast.Name(
                                        id="globals_file", ctx=ast.Store()
                                    ),
                                ),
                                ast.withitem(
                                    context_expr=ast.Call(
                                        func=ast.Name(id="open", ctx=ast.Load()),
                                        args=[
                                            ast.Constant(value=locals_path),
                                            ast.Constant(value="rb"),
                                        ],
                                    ),
                                    optional_vars=ast.Name(
                                        id="locals_file", ctx=ast.Store()
                                    ),
                                ),
                            ],
                            body=[
                                ast.Expr(
                                    value=ast.Call(
                                        func=ast.Attribute(
                                            value=ast.Attribute(
                                                value=ast.Call(
                                                    func=ast.Attribute(
                                                        value=ast.Name(
                                                            id="inspect", ctx=ast.Load()
                                                        ),
                                                        attr="currentframe",
                                                        ctx=ast.Load(),
                                                    )
                                                ),
                                                attr="f_globals",
                                                ctx=ast.Load(),
                                            ),
                                            attr="update",
                                            ctx=ast.Load(),
                                        ),
                                        args=[
                                            ast.Call(
                                                func=ast.Attribute(
                                                    value=ast.Name(
                                                        id="dill", ctx=ast.Load()
                                                    ),
                                                    attr="loads",
                                                    ctx=ast.Load(),
                                                ),
                                                args=[
                                                    ast.Call(
                                                        func=ast.Attribute(
                                                            value=ast.Name(
                                                                id="globals_file",
                                                                ctx=ast.Load(),
                                                            ),
                                                            attr="read",
                                                            ctx=ast.Load(),
                                                        )
                                                    )
                                                ],
                                            )
                                        ],
                                    )
                                ),
                                ast.Expr(
                                    value=ast.Call(
                                        func=ast.Attribute(
                                            value=ast.Attribute(
                                                value=ast.Call(
                                                    func=ast.Attribute(
                                                        value=ast.Name(
                                                            id="inspect", ctx=ast.Load()
                                                        ),
                                                        attr="currentframe",
                                                        ctx=ast.Load(),
                                                    )
                                                ),
                                                attr="f_globals",
                                                ctx=ast.Load(),
                                            ),
                                            attr="update",
                                            ctx=ast.Load(),
                                        ),
                                        args=[
                                            ast.Call(
                                                func=ast.Attribute(
                                                    value=ast.Name(
                                                        id="dill", ctx=ast.Load()
                                                    ),
                                                    attr="loads",
                                                    ctx=ast.Load(),
                                                ),
                                                args=[
                                                    ast.Call(
                                                        func=ast.Attribute(
                                                            value=ast.Name(
                                                                id="locals_file",
                                                                ctx=ast.Load(),
                                                            ),
                                                            attr="read",
                                                            ctx=ast.Load(),
                                                        )
                                                    )
                                                ],
                                            )
                                        ],
                                    )
                                ),
                            ],
                        ),
                    ]
                    + body,
                )
                ast.fix_missing_locations(fd)
                # TODO: issue with early returns

                with open(path.parent / f"test_{func_name}_{counter}.py", "w") as f:
                    f.write(ast.unparse(fd))
        return _tracer

    return _tracer
