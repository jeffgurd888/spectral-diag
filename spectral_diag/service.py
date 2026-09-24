"""Hardened spectral-diagnostics service.

- Schema coercion: square, finite matrices only; clear ValueErrors otherwise.
- Hash-keyed result cache (matrix bytes + params + engine name).
- Engine merging: engine output wins where present; the reference fallback
  backfills the rest and ``meta.missing_fields`` names the gap.
"""

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any, Dict

import numpy as np

from .engines import resolve_engine


@dataclass
class DiagnosticResult:
    n: int
    eigenvalues: list
    spectral_gap: float
    trace: float
    determinant: float
    condition_number: float
    heat_kernel: Dict[str, float]
    symmetry: Dict[str, bool]
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_REQUIRED = {
    "n",
    "eigenvalues",
    "spectral_gap",
    "trace",
    "determinant",
    "condition_number",
    "heat_kernel",
    "symmetry",
}


class SpectralService:
    def __init__(self, engine_name: str | None = None, cache_size: int = 512):
        self.engine_name = engine_name
        self.engine = resolve_engine(engine_name)
        self._cache_size = cache_size
        self._cache: dict = {}

    # ---- public ----
    def diagnose(
        self, A: np.ndarray, params: Dict[str, Any] | None = None
    ) -> DiagnosticResult:
        params = params or {}
        A = np.asarray(A)  # keep complex dtype: D_F is complex Hermitian
        if A.ndim != 2 or A.shape[0] != A.shape[1]:
            raise ValueError(f"matrix must be square, got shape {A.shape}")
        if not np.all(np.isfinite(A)):
            raise ValueError("matrix contains NaN or Inf")

        key = self._key(A, params)
        if key in self._cache:
            return self._cache[key]

        raw = self._run_engine(A, params)
        res = self._coerce(raw, A, params)

        if len(self._cache) >= self._cache_size:
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = res
        return res

    # ---- internals ----
    def _key(self, A: np.ndarray, params: Dict[str, Any]) -> str:
        h = hashlib.sha256(A.tobytes()).hexdigest()
        p = repr(sorted(params.items()))
        return f"{self.engine_name}:{h}:{p}"

    def _run_engine(self, A: np.ndarray, params: Dict[str, Any]) -> Dict[str, Any]:
        if self.engine is not None:
            return dict(self.engine.diagnose(A, params))
        return self._fallback(A, params)

    def _coerce(
        self, raw: Dict[str, Any], A: np.ndarray, params: Dict[str, Any]
    ) -> DiagnosticResult:
        missing = sorted(_REQUIRED - set(raw))
        base = self._fallback(A, params)
        merged = {**base, **{k: v for k, v in raw.items() if k in _REQUIRED}}
        meta = dict(raw.get("meta") or {})
        meta.update(
            {
                "engine": self.engine_name or "fallback",
                "params": params,
                "missing_fields": missing,
                # Provenance: hash of the actual input bytes, emitted by the run
                # itself on every call. Never hand-filled, never invented.
                "input_hash": self._key(A, params),
            }
        )
        return DiagnosticResult(**merged, meta=meta)

    def _fallback(self, A: np.ndarray, params: Dict[str, Any]) -> Dict[str, Any]:
        is_sym = bool(np.allclose(A, A.T))
        evals = np.linalg.eigvalsh(A) if is_sym else np.linalg.eigvals(A)
        evals = np.sort(np.real(evals))

        t_grid = np.logspace(-2, 2, 17)
        Z = np.array([np.sum(np.exp(-t * evals)) for t in t_grid])
        Z = np.maximum(Z, np.finfo(float).tiny)  # avoid log(0) on underflow
        dlogZ = np.gradient(np.log(Z), np.log(t_grid))
        ds_curve = -2.0 * dlogZ

        heat = {f"Z(t={t:.3g})": float(z) for t, z in zip(t_grid, Z)}
        heat["spectral_dim@t=1"] = float(
            np.interp(np.log(1.0), np.log(t_grid), ds_curve)
        )

        return {
            "n": int(A.shape[0]),
            "eigenvalues": [float(x) for x in evals],
            "spectral_gap": float(evals[1] - evals[0]) if len(evals) > 1 else 0.0,
            "trace": float(np.real(np.trace(A))),
            "determinant": float(np.real(np.linalg.det(A))),
            "condition_number": float(np.linalg.cond(A)),
            "heat_kernel": heat,
            "symmetry": {
                "symmetric": is_sym,
                "hermitian": bool(np.allclose(A, A.conj().T)),
                "normal": bool(np.allclose(A @ A.conj().T, A.conj().T @ A)),
            },
        }
