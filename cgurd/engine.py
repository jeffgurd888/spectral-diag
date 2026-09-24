# cgurd/engine.py
"""Lean32Engine: 32x32 finite spectral triple (A_F, H_F, D_F, J_F, gamma_F)
diagnostic engine for spectral-diag.

Numerical reference implementation: given a 32x32 internal Dirac operator
(or any square matrix), it computes the eigenvalue spectrum, the physical
mass gap Delta = min |lambda| > 1e-12, the heat-kernel expansion
Z(t) = Tr(exp(-t D_F^2)), and the chirality-odd check against the canonical
32x32 Standard-Model grading.

Status of the meta claims (read before citing):
- ``order_zero`` / ``order_one`` are COMPUTED by an explicit generator-pair
  census (max-abs-entry norm over 24x24 = 576 pairs), never asserted.
  Each report carries ``checked``, ``holds``, ``max_norm``, ``pairs``,
  ``tol``, and ``basis``. ``order_zero_holds`` / ``order_one_holds``
  are the plain boolean verdicts (None when the check could not run).
- For 32x32 input the census uses the canonical SM finite geometry
  (A_F = C (+) H (+) M3(C), Option-A rep; see cgurd/sm_algebra.py).
- For other dimensions the census runs only if the caller supplies an
  algebra representation via params: ``pi_mats`` and ``pi_op_mats``
  (lists of n x n array-likes). Otherwise the check is reported as
  not run (``checked: False``) -- never as True.
- ``chirality_odd`` IS computed: it checks {A, gamma_32} = 0 numerically.
Everything else (spectrum, gap, trace, det, cond, heat kernel, symmetry)
is derived from the input matrix.
"""
from typing import Dict, Any, List, Optional, Tuple

import numpy as np

from .sm_algebra import (
    CANONICAL_BASIS,
    canonical_mats,
    gamma_F,
    order_one_census,
    order_zero_census,
)


def _as_mats(objs, n: int, name: str) -> List[np.ndarray]:
    mats = [np.asarray(m, dtype=complex) for m in objs]
    for m in mats:
        if m.shape != (n, n):
            raise ValueError(f"params['{name}'] entries must be {n}x{n}, "
                             f"got {m.shape}")
    return mats


def _resolve_algebra(
    n: int, params: Dict[str, Any]
) -> Optional[Tuple[List[np.ndarray], List[np.ndarray], str]]:
    """Return (pi_mats, pi_op_mats, basis) or None when no representation
    is available for this dimension."""
    if "pi_mats" in params or "pi_op_mats" in params:
        if "pi_mats" not in params or "pi_op_mats" not in params:
            raise ValueError("supply both params['pi_mats'] and "
                             "params['pi_op_mats'] or neither")
        pi_mats = _as_mats(params["pi_mats"], n, "pi_mats")
        pi_op_mats = _as_mats(params["pi_op_mats"], n, "pi_op_mats")
        return pi_mats, pi_op_mats, "caller-supplied algebra representation"
    if n == 32:
        pi_mats, pi_op_mats = canonical_mats()
        return pi_mats, pi_op_mats, CANONICAL_BASIS
    return None


def _not_run(reason: str) -> Dict[str, Any]:
    return {"checked": False, "holds": None, "reason": reason}


class Lean32Engine:
    """32x32 Finite Spectral Triple (A_F, H_F, D_F, J_F, gamma_F) diagnostic engine."""
    name: str = "lean32"

    def diagnose(self, A: np.ndarray, params: Dict[str, Any]) -> Dict[str, Any]:
        A = np.asarray(A)  # keep complex dtype: D_F is complex Hermitian
        n = int(A.shape[0])
        is_sym = bool(np.allclose(A, A.T))
        is_herm = bool(np.allclose(A, A.conj().T))

        # Eigenvalue spectrum computation
        evals = np.linalg.eigvalsh(A) if is_herm else np.real(np.linalg.eigvals(A))
        evals = np.sort(evals)

        # Physical spectral mass gap Delta = min(|lambda| > 1e-12)
        abs_evals = np.sort(np.abs(evals))
        non_zero = abs_evals[abs_evals > 1e-12]
        spectral_gap = float(non_zero[0]) if len(non_zero) > 0 else 0.0

        # Heat Kernel Expansion Z(t) = Tr(exp(-t * D_F^2))
        A_sq = A @ A if is_herm else A.conj().T @ A
        evals_sq = np.sort(np.real(np.linalg.eigvalsh(A_sq)))

        t_grid = np.logspace(-2, 2, 17)
        Z = np.array([np.sum(np.exp(-t * evals_sq)) for t in t_grid])
        Z = np.maximum(Z, np.finfo(float).tiny)  # avoid log(0) on underflow
        dlogZ = np.gradient(np.log(Z), np.log(t_grid))
        ds_curve = -2.0 * dlogZ

        heat = {f"Z(t={t:.3g})": float(z) for t, z in zip(t_grid, Z)}
        heat["spectral_dim@t=1"] = float(np.interp(np.log(1.0), np.log(t_grid), ds_curve))

        # Chirality-odd check against 32x32 standard model grading (computed)
        g32 = gamma_F().real if n == 32 else None
        if g32 is None:
            g32 = np.diag([1.0] * (n // 4) + [-1.0] * (n // 4)
                          + [-1.0] * (n // 4) + [1.0] * (n - 3 * (n // 4)))
        chirality_odd = bool(np.allclose(A @ g32 + g32 @ A, 0.0))

        # Order-zero / order-one: computed census, or honestly not run.
        alg = _resolve_algebra(n, params or {})
        if alg is None:
            reason = ("no algebra representation for dimension "
                      f"{n}: pass params['pi_mats'] and params['pi_op_mats'] "
                      "to run the census")
            order_zero = _not_run(reason)
            order_one = _not_run(reason)
        else:
            pi_mats, pi_op_mats, basis = alg
            order_zero = order_zero_census(pi_mats, pi_op_mats, basis)
            order_one = order_one_census(A.astype(complex), pi_mats,
                                         pi_op_mats, basis)

        return {
            "n": n,
            "eigenvalues": [float(x) for x in evals],
            "spectral_gap": spectral_gap,
            "trace": float(np.real(np.trace(A))),
            "determinant": float(np.real(np.linalg.det(A))),
            "condition_number": float(np.linalg.cond(A)),
            "heat_kernel": heat,
            "symmetry": {
                "symmetric": is_sym,
                "hermitian": is_herm,
                "normal": bool(np.allclose(A @ A.conj().T, A.conj().T @ A)),
            },
            "meta": {
                "hilbert_dim": 32,
                "chiral_sectors": 4,
                "order_zero": order_zero,
                "order_one": order_one,
                "order_zero_holds": order_zero["holds"],
                "order_one_holds": order_one["holds"],
                "chirality_odd": chirality_odd,
            }
        }
