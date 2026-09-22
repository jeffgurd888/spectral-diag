"""Engine contract: one narrow protocol, zero API edits to add an engine.

An engine is any class with a ``name`` attribute and a ``diagnose(A, params)``
method returning a dict with any subset of the ``DiagnosticResult`` fields.
Missing fields are backfilled by the reference fallback and reported in
``meta.missing_fields`` so you can see exactly what your engine covers.

Register an engine in your own package's ``pyproject.toml``::

    [project.entry-points."spectral_diag.engines"]
    lean32 = "my_pkg.engine:Lean32Engine"
"""

from importlib.metadata import entry_points
from typing import Any, Dict, Protocol

import numpy as np


class EngineProtocol(Protocol):
    name: str

    def diagnose(self, A: np.ndarray, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return any subset of DiagnosticResult fields. Missing keys are
        filled by the service and reported in meta.missing_fields."""
        ...


def _entry_points(group: str):
    eps = entry_points()
    if hasattr(eps, "select"):  # Python 3.10+
        return eps.select(group=group)
    return eps.get(group, ())


def list_engine_names() -> list:
    return ["fallback"] + [ep.name for ep in _entry_points("spectral_diag.engines")]


def resolve_engine(name: str | None) -> EngineProtocol | None:
    """Resolve an engine name to an instance, or None for the fallback."""
    if name in (None, "", "fallback", "builtin"):
        return None
    for ep in _entry_points("spectral_diag.engines"):
        if ep.name == name:
            return ep.load()()
    raise KeyError(f"engine '{name}' not registered")
