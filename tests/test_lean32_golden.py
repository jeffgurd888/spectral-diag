# tests/test_lean32_golden.py
"""Golden-matrix regression suite pinned to the Lean32Engine output."""
import numpy as np
import pytest
from spectral_diag.service import SpectralService


@pytest.fixture
def canonical_dirac_32():
    """Generates canonical 32x32 internal Dirac operator with mass gap 0.5."""
    D = np.zeros((32, 32), dtype=float)
    # Block-diagonal particle/antiparticle sector couplings
    for i in range(8):
        D[i, i + 8] = 0.5
        D[i + 8, i] = 0.5
        D[i + 16, i + 24] = 0.5
        D[i + 24, i + 16] = 0.5
    return D


def test_lean32_golden_spectrum(canonical_dirac_32):
    svc = SpectralService(engine_name="lean32")
    res = svc.diagnose(canonical_dirac_32)

    assert res.n == 32
    assert abs(res.spectral_gap - 0.5) < 1e-9
    assert abs(res.trace - 0.0) < 1e-9
    assert res.meta["engine"] == "lean32"
    assert res.meta["missing_fields"] == []
    assert res.meta["chirality_odd"] is True


def test_lean32_heat_kernel_shape(canonical_dirac_32):
    svc = SpectralService(engine_name="lean32")
    res = svc.diagnose(canonical_dirac_32)
    assert "spectral_dim@t=1" in res.heat_kernel
    # Z(0.01) ~ 32 for the canonical operator: exp(-0.01 * 0.25) ~ 0.9975 per mode
    assert abs(res.heat_kernel["Z(t=0.01)"] - 32 * np.exp(-0.01 * 0.25)) < 1e-6


def test_lean32_non_chiral_matrix_reports_false():
    svc = SpectralService(engine_name="lean32")
    res = svc.diagnose(np.eye(32), {})
    assert res.meta["chirality_odd"] is False
    assert abs(res.spectral_gap - 1.0) < 1e-9
