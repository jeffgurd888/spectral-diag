"""Spectral diagnostics for matrices and operators.

Open-core package: the engine-agnostic wrapper. Your verified engine
registers via the ``spectral_diag.engines`` entry-point group; until then
the built-in NumPy fallback computes every field honestly and reports
what the engine did *not* supply in ``meta.missing_fields``.
"""

__version__ = "0.2.0"
__all__ = ["__version__"]
