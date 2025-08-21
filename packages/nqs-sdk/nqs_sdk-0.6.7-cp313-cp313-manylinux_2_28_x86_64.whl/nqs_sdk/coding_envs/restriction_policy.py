# mypy: disable-error-code="no-untyped-def,no-untyped-call"

import importlib
from typing import Any, Dict, Optional, Sequence

from RestrictedPython import RestrictingNodeTransformer
from RestrictedPython.Guards import guarded_iter_unpack_sequence, guarded_unpack_sequence, safer_getattr
from RestrictedPython.PrintCollector import PrintCollector


class CodingNodeTransformer(RestrictingNodeTransformer):
    def visit_AnnAssign(self, node) -> Any:  # noqa: N802
        return self.node_contents_visit(node)

    def visit_TypeAlias(self, node) -> Any:  # noqa: N802
        return self.node_contents_visit(node)

    def visit_TypeVar(self, node) -> Any:  # noqa: N802
        return self.node_contents_visit(node)

    def visit_TypeVarTuple(self, node) -> Any:  # noqa: N802
        return self.node_contents_visit(node)

    def visit_ParamSpec(self, node) -> Any:  # noqa: N802
        return self.node_contents_visit(node)


def custom_imports(libraries: list[str]) -> Any:
    def restricted_imports(
        name: str,
        globals: Optional[Dict[str, Any]] = None,
        locals: Optional[Dict[str, Any]] = None,
        fromlist: Sequence[str] = (),
        level: int = 0,
    ) -> Any:
        if name in libraries:
            return importlib.__import__(name, globals, locals, fromlist, level)
        else:
            raise ImportError(f"Restricted import: {name}")

    return restricted_imports


def guarded_getitem(ob: Dict[str, Any], index: str) -> Any:
    # No restrictions.
    return ob[index]


def guarded_write(allowed_classes: list[str]):
    def guarded_write(ob):
        if ob.__class__.__name__ in allowed_classes:
            return ob
        else:
            raise AttributeError(f"Restricted write: {ob.__class__.__name__}")

    return guarded_write


def guarded_getiter(ob):
    return ob


def implement_policy(
    safe_globals: dict, import_globals: dict = {}, libraries: list[str] = [], allowed_write_classes: list[str] = []
) -> None:
    safe_globals.update(import_globals)
    safe_globals["__metaclass__"] = type
    safe_globals["__name__"] = globals()["__name__"]
    safe_globals["_getitem_"] = guarded_getitem
    safe_globals["__builtins__"]["__import__"] = custom_imports(libraries)
    safe_globals["dict"] = dict
    safe_globals["_write_"] = guarded_write(allowed_write_classes)
    safe_globals["_getiter_"] = guarded_getiter
    safe_globals["_getattr_"] = safer_getattr
    safe_globals["_unpack_sequence_"] = guarded_unpack_sequence
    safe_globals["_iter_unpack_sequence_"] = guarded_iter_unpack_sequence
    safe_globals["__builtins__"]["enumerate"] = globals()["__builtins__"]["enumerate"]
    safe_globals["__builtins__"]["hasattr"] = globals()["__builtins__"]["hasattr"]
    safe_globals["__builtins__"]["max"] = globals()["__builtins__"]["max"]
    safe_globals["__builtins__"]["min"] = globals()["__builtins__"]["min"]
    safe_globals["__builtins__"]["abs"] = globals()["__builtins__"]["abs"]
    safe_globals["__builtins__"]["round"] = globals()["__builtins__"]["round"]
    safe_globals["__builtins__"]["pow"] = globals()["__builtins__"]["pow"]
    safe_globals["__builtins__"]["sorted"] = globals()["__builtins__"]["sorted"]
    safe_globals["__builtins__"]["reversed"] = globals()["__builtins__"]["reversed"]
    safe_globals["__builtins__"]["divmod"] = globals()["__builtins__"]["divmod"]
    safe_globals["__builtins__"]["len"] = globals()["__builtins__"]["len"]
    safe_globals["_print_"] = PrintCollector
