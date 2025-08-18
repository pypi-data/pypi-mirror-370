"""Extract a package's public surface by statically parsing source code.

The module relies solely on the standard library :mod:`ast` package to map
exported functions and methods and capture their signatures.  Only a narrow
subset of ``__all__`` expressions is evaluated and no user code is executed,
so dynamically constructed symbols or runtime side effects may be missed.
"""

from __future__ import annotations

import ast
import hashlib
import logging
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .analysers.utils import iter_py_files_at_ref, parse_python_source  # noqa: F401

logger = logging.getLogger(__name__)

# --------- Data model ---------


@dataclass(frozen=True)
class Param:
    """Function parameter description.

    Attributes:
        name: Parameter name.
        kind: Parameter kind (``"posonly"``, ``"pos"``, ``"vararg"``,
            ``"kwonly"``, or ``"varkw"``).
        default: Default value expression if present.
        annotation: Type annotation if present.
    """

    name: str
    kind: str  # "posonly" | "pos" | "vararg" | "kwonly" | "varkw"
    default: str | None
    annotation: str | None


@dataclass(frozen=True)
class FuncSig:
    """Public symbol description.

    Captures functions, methods, classes and selected module level
    assignments. ``params`` and ``returns`` are populated only for callables.

    Attributes:
        fullname: Fully qualified name (e.g. ``module:func``,
            ``module:Class.method`` or ``module:CONST``).
        params: Ordered parameter definitions.
        returns: Return annotation if specified.
        body_hash: Hash of the symbol's body or value used to detect
            implementation changes without signature updates.
    """

    fullname: str  # e.g. pkg.mod:func or pkg.mod:CONST
    params: tuple[Param, ...]
    returns: str | None
    body_hash: str


# symbol -> metadata for functions, methods, classes, and variables
PublicAPI = dict[str, FuncSig]


# --------- Helpers ---------


def render_node(node: ast.AST | None) -> str | None:
    """Render AST nodes such as expressions or annotations.

    Args:
        node: AST node to render.

    Returns:
        String representation of the node or ``None`` if ``node`` is ``None``.
    """

    return ast.unparse(node) if node is not None else None


def _hash_node(node: ast.AST) -> str:
    """Return a stable hash for ``node``.

    Args:
        node: AST node to hash.

    Returns:
        SHA256 digest of the node's structure with attributes ignored.
    """

    dumped = ast.dump(node, include_attributes=False)
    return hashlib.sha256(dumped.encode("utf-8")).hexdigest()


def _parse_exports(mod: ast.Module) -> set[str] | None:
    """Parse ``__all__`` definitions from a module if present.

    The parser understands simple list/tuple literals, ``+`` concatenation,
    and variable references whose values are string literals. This limited
    evaluation avoids executing user code while still supporting common ways of
    constructing ``__all__``.

    Args:
        mod: Parsed module.

    Returns:
        Set of exported symbol names or ``None`` if ``__all__`` is undefined.
    """

    def _eval(node: ast.AST, env: dict[str, list[str]]) -> list[str]:
        """Evaluate simple expressions to a list of strings.

        This supports:

        * List or tuple literals containing string constants or previously
          defined names.
        * ``+`` concatenation of supported expressions.
        * References to previously assigned names stored in ``env``.
        Non-string entries are ignored.
        """

        if isinstance(node, (ast.List, ast.Tuple)):
            out: list[str] = []
            for el in node.elts:
                if isinstance(el, ast.Constant) and isinstance(el.value, str):
                    out.append(el.value)
                elif isinstance(el, ast.Name):
                    out.extend(env.get(el.id, []))
            return out
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return _eval(node.left, env) + _eval(node.right, env)
        if isinstance(node, ast.Name):
            return env.get(node.id, [])
        return []

    env: dict[str, list[str]] = {}
    for stmt in mod.body:
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
            tgt = stmt.targets[0]
            if not isinstance(tgt, ast.Name):
                continue
            evaluated = _eval(stmt.value, env)
            if tgt.id == "__all__":
                # Return explicit export set even if empty
                return set(evaluated)
            env[tgt.id] = evaluated
    return None


def _positional_params(args: ast.arguments) -> list[Param]:
    """Build positional-only and positional-or-keyword parameters.

    Args:
        args: Function arguments node from the AST.

    Returns:
        Positional parameter descriptors in declaration order.
    """

    posonly = list(args.posonlyargs)
    pos = list(args.args)
    defaults = list(args.defaults)
    # Defaults apply to the tail of the combined positional parameters.
    total = len(posonly) + len(pos)
    d_start = total - len(defaults)
    out: list[Param] = []

    for idx, param in enumerate(posonly + pos):
        default = render_node(defaults[idx - d_start]) if idx >= d_start else None
        kind = "posonly" if idx < len(posonly) else "pos"
        out.append(Param(param.arg, kind, default, render_node(param.annotation)))
    return out


def _vararg_param(args: ast.arguments) -> list[Param]:
    """Return variable positional parameter if present."""

    if args.vararg:
        return [
            Param(args.vararg.arg, "vararg", None, render_node(args.vararg.annotation))
        ]
    return []


def _kwonly_params(args: ast.arguments) -> list[Param]:
    """Build keyword-only parameters in declaration order."""

    out: list[Param] = []
    for param, default in zip(args.kwonlyargs, args.kw_defaults):
        out.append(
            Param(
                param.arg,
                "kwonly",
                render_node(default),
                render_node(param.annotation),
            )
        )
    return out


def _varkw_param(args: ast.arguments) -> list[Param]:
    """Return variable keyword parameter if present."""

    if args.kwarg:
        return [
            Param(args.kwarg.arg, "varkw", None, render_node(args.kwarg.annotation))
        ]
    return []


def _param_list(args: ast.arguments) -> list[Param]:
    """Convert AST parameters to :class:`Param` instances.

    Args:
        args: Function arguments node from the AST.

    Returns:
        Ordered list of parameter descriptors.
    """

    params: list[Param] = []

    # Capture positional-only and positional-or-keyword parameters.
    params.extend(_positional_params(args))

    # Include *args if provided.
    params.extend(_vararg_param(args))

    # Append keyword-only parameters following * or *args.
    params.extend(_kwonly_params(args))

    # Include **kwargs if provided.
    params.extend(_varkw_param(args))

    return params


def _decorator_names(node: ast.ClassDef) -> set[str]:
    """Return decorator names applied to ``node``.

    Args:
        node: Class definition to inspect.

    Returns:
        Set of decorator names as they appear in source.
    """

    return {ast.unparse(dec) for dec in node.decorator_list}


_DATACLASS_DECOS = {
    "dataclass",
    "dataclasses.dataclass",
    "attr.s",
    "attr.define",
    "attr.frozen",
    "attr.mutable",
    "attrs.define",
    "attrs.frozen",
    "attrs.mutable",
}


def _is_dataclass_like(node: ast.ClassDef) -> bool:
    """Return ``True`` if ``node`` appears to be a dataclass/attrs class."""

    return any(name in _DATACLASS_DECOS for name in _decorator_names(node))


def _init_disabled(value: ast.AST | None) -> bool:
    """Return ``True`` if ``value`` disables ``__init__`` generation.

    Args:
        value: Field value expression which may configure ``init=False``.

    Returns:
        ``True`` when ``value`` represents a ``field``/``attr.ib`` call with
        ``init=False``; ``False`` otherwise.
    """

    if not isinstance(value, ast.Call):
        return False
    func_name = ast.unparse(value.func)
    if func_name not in {
        "field",
        "dataclasses.field",
        "attr.ib",
        "attr.field",
        "attrs.field",
    }:
        return False
    for kw in value.keywords:
        if (
            kw.arg == "init"
            and isinstance(kw.value, ast.Constant)
            and kw.value.value is False
        ):
            return True
    return False


def _dataclass_params(node: ast.ClassDef) -> list[Param]:
    """Derive ``__init__`` parameters from dataclass field definitions."""

    params: list[Param] = [Param("self", "pos", None, None)]
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            if _init_disabled(stmt.value):
                continue
            params.append(
                Param(
                    stmt.target.id,
                    "pos",
                    render_node(stmt.value),
                    render_node(stmt.annotation),
                )
            )
    return params


def _is_public(name: str, private_prefixes: tuple[str, ...]) -> bool:
    """Return whether ``name`` represents a public symbol.

    Args:
        name: Symbol name to evaluate.
        private_prefixes: Symbol prefixes considered non-public.

    Returns:
        ``True`` if ``name`` does not begin with any prefix in
        ``private_prefixes``.
    """

    return not name.startswith(private_prefixes)


def _has_overload_decorator(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return ``True`` if ``node`` is decorated with ``typing.overload``."""

    for dec in node.decorator_list:
        # Handle both ``@overload`` and fully qualified forms like ``@typing.overload``.
        if isinstance(dec, ast.Name) and dec.id == "overload":
            return True
        if isinstance(dec, ast.Attribute) and dec.attr == "overload":
            return True
    return False


# --------- Visitor that collects public API ---------


class _APIVisitor(ast.NodeVisitor):
    """Collect public symbols from a module."""

    def __init__(
        self,
        module_name: str,
        exports: set[str] | None,
        private_prefixes: tuple[str, ...],
    ) -> None:
        """Initialize the visitor.

        Args:
            module_name: Name of the module being inspected.
            exports: Explicitly exported symbols if ``__all__`` is defined.
                ``None`` indicates that all public symbols are considered.
            private_prefixes: Symbol prefixes treated as private.
        """

        self.module_name = module_name
        self.exports = exports
        self.private_prefixes = private_prefixes
        self.sigs: list[FuncSig] = []

    def _module_symbol_is_public(self, name: str) -> bool:
        """Return whether a module-level ``name`` should be recorded."""

        if self.exports is None:
            return _is_public(name, self.private_prefixes)
        return name in self.exports

    def _record_symbol(self, name: str, node: ast.AST) -> None:
        """Add ``name`` with a hash of ``node`` to collected signatures."""

        self.sigs.append(
            FuncSig(f"{self.module_name}:{name}", (), None, _hash_node(node))
        )

    def visit_Module(self, node: ast.Module) -> None:  # noqa: D401
        """Collect top-level assignments, functions and classes."""

        for stmt in node.body:
            if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
                tgt = stmt.targets[0]
                if isinstance(tgt, ast.Name) and self._module_symbol_is_public(tgt.id):
                    self._record_symbol(tgt.id, stmt)
                continue
            if (
                isinstance(stmt, ast.AnnAssign)
                and stmt.simple
                and isinstance(stmt.target, ast.Name)
                and self._module_symbol_is_public(stmt.target.id)
            ):
                self._record_symbol(stmt.target.id, stmt)
                continue
            self.visit(stmt)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: D401
        """Collect function definitions."""
        if _has_overload_decorator(node):
            return

        fn = node.name
        if not self._module_symbol_is_public(fn):
            return
        params = tuple(_param_list(node.args))
        ret = render_node(node.returns)
        body_hash = _hash_node(node)
        self.sigs.append(FuncSig(f"{self.module_name}:{fn}", params, ret, body_hash))

    # Async functions have the same signature representation
    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: D401
        """Collect class body hashes and method signatures."""

        cname = node.name
        if not self._module_symbol_is_public(cname):
            return

        is_dcls = _is_dataclass_like(node)

        non_methods = [
            elt
            for elt in node.body
            if not isinstance(elt, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        body_node = ast.Module(body=non_methods, type_ignores=[])
        self._record_symbol(cname, body_node)

        for elt in node.body:
            if isinstance(elt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if _has_overload_decorator(elt):
                    continue
                mname = elt.name
                if not _is_public(mname, self.private_prefixes):
                    continue
                params = tuple(_param_list(elt.args))
                ret = render_node(elt.returns)
                body_hash = _hash_node(elt)
                self.sigs.append(
                    FuncSig(
                        f"{self.module_name}:{cname}.{mname}",
                        params,
                        ret,
                        body_hash,
                    )
                )

        if is_dcls:
            params = tuple(_dataclass_params(node))
            self.sigs.append(
                FuncSig(
                    f"{self.module_name}:{cname}.__init__",
                    params,
                    None,
                    _hash_node(node),
                )
            )


def module_name_from_path(root: str, path: str) -> str:
    """Convert a file path to a module name relative to ``root``.

    Args:
        root: Root directory of the package.
        path: File path under ``root``.

    Returns:
        Dotted module path corresponding to ``path``.

    Raises:
        ValueError: If ``path`` is not located within ``root``.

    Example:
        >>> module_name_from_path('pkg', 'pkg/sub/mod.py')
        'sub.mod'
    """

    try:
        rel = Path(path).with_suffix("").relative_to(Path(root))
    except ValueError as exc:
        raise ValueError(f"{path!r} is not relative to {root!r}") from exc
    return ".".join(rel.parts)


def extract_public_api_from_source(
    module_name: str,
    code: str | ast.AST,
    private_prefixes: Iterable[str] = ("_",),
) -> PublicAPI:
    """Extract the public API from Python source code.

    Args:
        module_name: Name of the module represented by ``code``.
        code: Source text or a pre-parsed module AST.
        private_prefixes: Symbol prefixes treated as private.

    Returns:
        Mapping of symbol names to :class:`FuncSig` objects.

    Notes:
        Returns an empty mapping and logs a warning if ``code`` cannot be parsed.
        Modules defining ``__all__ = []`` export no symbols.

    Example:
        >>> src = 'def greet(name):\n    return f"Hi {name}"\n'
        >>> api = extract_public_api_from_source('mod', src)
        >>> sorted(api)
        ['mod:greet']
    """

    if isinstance(code, str):
        try:
            mod = ast.parse(code)
        except (SyntaxError, UnicodeDecodeError) as exc:
            logger.warning("Failed to parse %s: %s", module_name, exc)
            return {}
    else:
        mod = code

    exports = _parse_exports(mod)
    visitor = _APIVisitor(module_name, exports, tuple(private_prefixes))
    visitor.visit(mod)
    return {s.fullname: s for s in visitor.sigs}


def build_api_at_ref(
    ref: str,
    roots: Iterable[str],
    ignores: Iterable[str],
    private_prefixes: Iterable[str],
) -> PublicAPI:
    """Collect the public API for ``roots`` at a git reference.

    Args:
        ref: Git reference to inspect.
        roots: Root directories containing public modules.
        ignores: Glob patterns for paths to exclude.
        private_prefixes: Symbol prefixes treated as private.

    Returns:
        Mapping of public symbol names to their signatures.

    Example:
        >>> api = build_api_at_ref('HEAD', ['bumpwright'], [], ('_',))
        >>> 'bumpwright:build_api_at_ref' in api
        True
    """

    api: PublicAPI = {}
    for root in roots:
        for path, code in iter_py_files_at_ref(ref, [root], ignore_globs=ignores):
            modname = module_name_from_path(root, path)
            try:
                api.update(
                    extract_public_api_from_source(modname, code, private_prefixes)
                )
            except (SyntaxError, UnicodeDecodeError):
                continue
    return api


__all__ = [
    "Param",
    "FuncSig",
    "PublicAPI",
    "build_api_at_ref",
    "module_name_from_path",
    "extract_public_api_from_source",
]
