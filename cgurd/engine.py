# cgurd/engine.py
"""Lean32Engine: 32x32 finite spectral triple (A_F, H_F, D_F, J_F, gamma_F)
diagnostic engine for spectral-diag.

Numerical reference implementation: given a 32x32 internal Dirac operator
(or any square matrix), it computes the eigenvalue spectrum, the physical
mass gap Delta = min |lambda| > 1e-12, the heat-kernel expansion
Z(t) = Tr(exp(-t D_F^2)), and the chirality-odd check against the canonical
32x32 Standard-Model grading.

Status of the meta claims (read before citing):
- ``order_zero_holds`` / ``order_one_holds`` are asserted True by
  construction of the finite geometry, NOT computed from the input matrix.
  They are labels, not verification results.
- ``chirality_odd`` IS computed: it checks {A, gamma_32} = 0 numerically.
Everything else (spectrum, gap, trace, det, cond, heat kernel, symmetry)
is derived from the input matrix.
"""
from typing import Dict, Any
import numpy as np


class Lean32Engine:
    """32x32 Finite Spectral Triple (A_F, H_F, D_F, J_F, gamma_F) diagnostic engine."""
    name: str = "lean32"

    def diagnose(self, A: np.ndarray, params: Dict[str, Any]) -> Dict[str, Any]:
        A = np.asarray(A, dtype=float)
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

        # Order-zero check against 32x32 standard model grading
        gamma_32 = np.diag([1.0] * 8 + [-1.0] * 8 + [-1.0] * 8 + [1.0] * 8)
        chirality_odd = bool(np.allclose(A @ gamma_32 + gamma_32 @ A, 0.0))

        return {
            "n": n,
            "eigenvalues": [float(x) for x in evals],
            "spectral_gap": spectral_gap,
            "trace": float(np.trace(A)),
            "determinant": float(np.linalg.det(A)),
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
                "order_zero_holds": True,
                "order_one_holds": True,
                "chirality_odd": chirality_odd,
            }
        }
