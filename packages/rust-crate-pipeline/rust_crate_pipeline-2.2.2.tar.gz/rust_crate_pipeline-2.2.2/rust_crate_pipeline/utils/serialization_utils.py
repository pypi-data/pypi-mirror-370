from __future__ import annotations

"""
Utility helpers for safely converting complex/third-party objects into
JSON-serialisable data.

This is mainly needed because some libraries (e.g. LiteLLM) return custom
objects like `MarkdownGenerationResult` that don't implement a standard
`__iter__`/`__dict__`/`to_dict` interface.  Downstream code (our CLI and
report generator) can import `to_serializable` when they need to dump
arbitrary nested structures with `json`.
"""

from typing import Any

_PRIMITIVES = (str, int, float, bool, type(None))

try:
    from litellm.utils import MarkdownGenerationResult  # type: ignore
except ImportError:  # pragma: no cover
    MarkdownGenerationResult = None  # type: ignore


def to_serializable(obj: Any) -> Any:  # noqa: ANN401 – generic helper
    """Recursively convert *obj* into something that ``json`` can dump.

    Rules (in order):
    1. Primitive types are returned unchanged.
    2. ``dict`` values and ``list`` / ``tuple`` items are processed recursively.
    3. An object with a ``dict()`` or ``to_dict()`` method is replaced by that
       representation.
    4. Fallback: use ``str(obj)``.
    """
    if isinstance(obj, _PRIMITIVES):
        return obj

    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return [to_serializable(i) for i in obj]

    if hasattr(obj, "to_dict"):
        try:
            return to_serializable(obj.to_dict())
        except Exception:  # pragma: no cover – be permissive
            pass
    elif hasattr(obj, "__dict__"):
        return to_serializable(obj.__dict__)

    # Specific library objects
    if MarkdownGenerationResult is not None and isinstance(obj, MarkdownGenerationResult):
        # Prefer the plain markdown string; fall back to str(obj)
        try:
            return obj.raw_markdown  # type: ignore[attr-defined]
        except Exception:
            return str(obj)

    # Last resort: stringify
    return str(obj)
