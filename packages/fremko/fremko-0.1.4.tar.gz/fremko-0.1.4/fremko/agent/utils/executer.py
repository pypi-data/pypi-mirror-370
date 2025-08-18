import io
import contextlib
import ast
import traceback
import logging
import inspect
import types
import functools
from typing import Any, Dict, Set, Optional
from llama_index.core.workflow import Context
from asyncio import AbstractEventLoop

logger = logging.getLogger("droidrun")


def is_async_callable(obj) -> bool:
    """
    Return True if `obj` was implemented with `async def` (coroutine or async-generator).
    Handles:
      - plain functions (async or sync)
      - bound/unbound methods
      - functools.partial
      - classmethod/staticmethod descriptors (accesses .__func__)
      - callable objects whose __call__ is async
    Returns False for builtin/C functions or if it can't detect an async function.
    """

    # unwrap functools.partial
    if isinstance(obj, functools.partial):
        obj = obj.func

    # bound method -> underlying function
    if isinstance(obj, types.MethodType):
        obj = obj.__func__

    # direct async check for functions
    if inspect.iscoroutinefunction(obj) or inspect.isasyncgenfunction(obj):
        return True

    # if it's a plain python function (and not coroutine), it's sync
    if inspect.isfunction(obj):
        return False

    # descriptors like classmethod/staticmethod on the class have __func__
    if hasattr(obj, "__func__") and inspect.isfunction(obj.__func__):
        return inspect.iscoroutinefunction(obj.__func__) or inspect.isasyncgenfunction(obj.__func__)

    # callable object: check its __call__
    if hasattr(obj, "__call__"):
        call_attr = obj.__call__
        # if __call__ is a bound method, get the underlying function
        if isinstance(call_attr, types.MethodType):
            call_attr = call_attr.__func__
        if inspect.iscoroutinefunction(call_attr) or inspect.isasyncgenfunction(call_attr):
            return True
        if inspect.isfunction(call_attr):
            return False

    # fallback: builtins or unknown types -> assume sync (False)
    return False


class SimpleCodeExecutor:
    """
    A simple code executor that runs Python code with state persistence.

    This executor maintains a global and local state between executions,
    allowing for variables to persist across multiple code runs.

    NOTE: not safe for production use! Use with caution.
    """

    def __init__(
        self,
        loop: AbstractEventLoop,
        locals: Dict[str, Any] = {},
        globals: Dict[str, Any] = {},
        tools={},
        use_same_scope: bool = True,
    ):
        """
        Initialize the code executor.

        Args:
            locals: Local variables to use in the execution context
            globals: Global variables to use in the execution context
            tools: List of tools available for execution
        """

        self._tool_names: Set[str] = set()
        if isinstance(tools, dict):
            logger.debug(
                f"🔧 Initializing SimpleCodeExecutor with tools: {tools.items()}"
            )
            for tool_name, tool_function in tools.items():
                globals[tool_name] = tool_function
                self._tool_names.add(tool_name)
        elif isinstance(tools, list):
            logger.debug(f"🔧 Initializing SimpleCodeExecutor with tools: {tools}")
            # If tools is a list, convert it to a dictionary with tool name as key and function as value
            for tool in tools:
                # Add the tool to globals
                globals[tool.__name__] = tool
                self._tool_names.add(tool.__name__)
        else:
            raise ValueError("Tools must be a dictionary or a list of functions.")

        import time

        globals["time"] = time

        self.globals = globals
        self.locals = locals
        self.loop = loop
        self.use_same_scope = use_same_scope
        if self.use_same_scope:
            # If using the same scope, set the globals and locals to the same dictionary
            self.globals = self.locals = {
                **self.locals,
                **{k: v for k, v in self.globals.items() if k not in self.locals},
            }

        # Pre-compute set of async tool names for fast checks during AST transform
        self._async_tool_names: Set[str] = self._infer_async_tool_names()

    def _infer_async_tool_names(self) -> Set[str]:
        async_names: Set[str] = set()
        for name in self._tool_names:
            obj = self.globals.get(name)
            if obj is None:
                continue
            if is_async_callable(obj):
                async_names.add(name)
        return async_names

    def _refresh_async_tool_names(self) -> None:
        """Recompute async tool names from current globals in case tools changed."""
        self._async_tool_names = self._infer_async_tool_names()

    def _transform_code_insert_awaits(self, code: str) -> ast.Module:
        """
        Transform user code by inserting `await` for async tool calls and
        wrap it into an async function to allow `await` at top-level.

        Also ensures state persistence by declaring all assigned names as global.
        """

        try:
            original_tree = ast.parse(code, mode="exec")
        except SyntaxError:
            # If code is syntactically invalid, fall back to raw exec path
            # by returning a trivial wrapper that just executes the original code.
            # We'll let the existing execution raise a SyntaxError as before.
            original_tree = ast.parse("\n".join(["# fallback", code]), mode="exec")

        # Collect assigned names (to persist across runs)
        assigned_names = self._collect_assigned_names(original_tree)

        # First pass: collect calls that are already directly awaited
        awaited_call_ids: Set[int] = set()

        class AwaitedCallCollector(ast.NodeVisitor):
            def visit_Await(self, node: ast.Await):  # type: ignore[override]
                value = node.value
                if isinstance(value, ast.Call):
                    awaited_call_ids.add(id(value))
                self.generic_visit(node)

        AwaitedCallCollector().visit(original_tree)

        # Second pass: insert Await(...) for calls to async tools not already awaited
        async_tool_names = self._async_tool_names

        def extract_func_name(func_node: ast.AST) -> Optional[str]:
            if isinstance(func_node, ast.Name):
                return func_node.id
            # Support simple attribute access like module.tool, but only if base is Name and attr matches
            if isinstance(func_node, ast.Attribute) and isinstance(func_node.value, ast.Name):
                return func_node.attr
            return None

        class AwaitInserter(ast.NodeTransformer):
            def visit_Call(self, node: ast.Call):  # type: ignore[override]
                self.generic_visit(node)
                func_name = extract_func_name(node.func)
                if func_name and func_name in async_tool_names and id(node) not in awaited_call_ids:
                    return ast.Await(value=node)
                return node

        transformed_tree = AwaitInserter().visit(original_tree)
        ast.fix_missing_locations(transformed_tree)

        # Wrap the transformed statements into an async function to make awaits valid
        wrapper_func_name = "__droidrun_user_code__"
        func_body = list(transformed_tree.body)

        if assigned_names:
            func_body.insert(0, ast.Global(names=sorted(assigned_names)))

        async_func_def = ast.AsyncFunctionDef(
            name=wrapper_func_name,
            args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
            body=func_body,
            decorator_list=[],
            returns=None,
            type_comment=None,
        )

        module = ast.Module(body=[async_func_def], type_ignores=[])
        ast.fix_missing_locations(module)
        return module

    def _collect_assigned_names(self, tree: ast.AST) -> Set[str]:
        """Collect all simple names that are assigned anywhere in the code.

        This helps us declare them as globals inside the async wrapper so that
        state persists across executions.
        """
        names: Set[str] = set()

        def add_target(target: ast.AST):
            if isinstance(target, ast.Name):
                names.add(target.id)
            elif isinstance(target, (ast.Tuple, ast.List)):
                for elt in target.elts:
                    add_target(elt)
            # Skip attributes/subscripts; they don't bind names

        class AssignedNameVisitor(ast.NodeVisitor):
            def visit_Assign(self, node: ast.Assign):  # type: ignore[override]
                for t in node.targets:
                    add_target(t)
                self.generic_visit(node)

            def visit_AnnAssign(self, node: ast.AnnAssign):  # type: ignore[override]
                add_target(node.target)
                self.generic_visit(node)

            def visit_AugAssign(self, node: ast.AugAssign):  # type: ignore[override]
                add_target(node.target)
                self.generic_visit(node)

            def visit_For(self, node: ast.For):  # type: ignore[override]
                add_target(node.target)
                self.generic_visit(node)

            def visit_AsyncFor(self, node: ast.AsyncFor):  # type: ignore[override]
                add_target(node.target)
                self.generic_visit(node)

            def visit_With(self, node: ast.With):  # type: ignore[override]
                for item in node.items:
                    if item.optional_vars is not None:
                        add_target(item.optional_vars)
                self.generic_visit(node)

            def visit_AsyncWith(self, node: ast.AsyncWith):  # type: ignore[override]
                for item in node.items:
                    if item.optional_vars is not None:
                        add_target(item.optional_vars)
                self.generic_visit(node)

            def visit_ExceptHandler(self, node: ast.ExceptHandler):  # type: ignore[override]
                if node.name and isinstance(node.name, str):
                    names.add(node.name)
                self.generic_visit(node)

            def visit_FunctionDef(self, node: ast.FunctionDef):  # type: ignore[override]
                names.add(node.name)
                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):  # type: ignore[override]
                names.add(node.name)
                self.generic_visit(node)

            def visit_ClassDef(self, node: ast.ClassDef):  # type: ignore[override]
                names.add(node.name)
                self.generic_visit(node)

            def visit_Import(self, node: ast.Import):  # type: ignore[override]
                for alias in node.names:
                    names.add(alias.asname or alias.name.split(".")[0])
                self.generic_visit(node)

            def visit_ImportFrom(self, node: ast.ImportFrom):  # type: ignore[override]
                for alias in node.names:
                    names.add(alias.asname or alias.name)
                self.generic_visit(node)

        AssignedNameVisitor().visit(tree)
        # Filter out dunder names and builtins to be safe
        names = {n for n in names if not (n.startswith("__") and n.endswith("__"))}
        return names

    async def execute(self, ctx: Context, code: str) -> str:
        """
        Execute Python code and capture output and return values.

        Args:
            code: Python code to execute

        Returns:
            str: Output from the execution, including print statements.
        """
        # Update UI elements before execution
        self.globals['ui_state'] = await ctx.get("ui_state", None)
        
        # Capture stdout and stderr
        stdout = io.StringIO()
        stderr = io.StringIO()

        output = ""
        try:
            # Transform user code: refresh async tool detection, insert awaits, wrap into async def
            self._refresh_async_tool_names()
            module_ast = self._transform_code_insert_awaits(code)
            compiled = compile(module_ast, filename="<droidrun_user_code>", mode="exec")

            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                # Define the async wrapper function in the shared scope
                exec(compiled, self.globals, self.locals)
                # Retrieve and run it
                func = self.globals.get("__droidrun_user_code__") or self.locals.get(
                    "__droidrun_user_code__"
                )
                if func is None:
                    raise RuntimeError("Failed to prepare user code for execution.")
                await func()

            # Get output
            output = stdout.getvalue()
            if stderr.getvalue():
                output += "\n" + stderr.getvalue()

        except Exception as e:
            # Capture exception information
            output = f"Error: {type(e).__name__}: {str(e)}\n"
            output += traceback.format_exc()

        return output
