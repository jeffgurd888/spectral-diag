# tests/test_order_census.py
"""Order-zero / order-one are computed, not asserted.

- Canonical SM one-generation Dirac (C = E = 0): both censuses hold.
- Dirac with nonzero cross-sector blocks C, E: order-one FAILS
  (proves the check is real, not a hardcoded True).
- Non-32x32 input without a supplied algebra: check reported as not run.
- Caller-supplied algebra via params: census runs on the given matrices.
"""
import numpy as np
import pytest

from cgurd.sm_algebra import buildDirac
from spectral_diag.service import SpectralService


@pytest.fixture
def sm_dirac_good():
    rng = np.random.default_rng(2026)
    A = np.diag([0.5, 0.7, 1.1, 0.9, 1.1, 0.9, 1.1, 0.9]).astype(complex)
    Z = np.zeros((8, 8), complex)
    return buildDirac(A, A.conj(), Z, Z)


@pytest.fixture
def sm_dirac_bad():
    rng = np.random.default_rng(2026)
    A = rng.standard_normal((8, 8)) + 1j * rng.standard_normal((8, 8))
    C = rng.standard_normal((8, 8)) + 1j * rng.standard_normal((8, 8))
    E = rng.standard_normal((8, 8)) + 1j * rng.standard_normal((8, 8))
    return buildDirac(A, A.conj(), C, E)


def _svc():
    return SpectralService(engine_name="lean32")


def test_order_census_holds_for_sm_dirac(sm_dirac_good):
    res = _svc().diagnose(sm_dirac_good)
    oz, oo = res.meta["order_zero"], res.meta["order_one"]
    assert oz["checked"] is True and oz["holds"] is True
    assert oo["checked"] is True and oo["holds"] is True
    assert oz["pairs"] == 576 and oo["pairs"] == 576
    assert oz["max_norm"] < 1e-8 and oo["max_norm"] < 1e-8
    assert res.meta["order_zero_holds"] is True
    assert res.meta["order_one_holds"] is True


def test_order_one_detects_nonzero_cross_sector(sm_dirac_bad):
    res = _svc().diagnose(sm_dirac_bad)
    oo = res.meta["order_one"]
    assert oo["checked"] is True
    assert oo["holds"] is False, "nonzero C/E must fail the order-one census"
    assert oo["max_norm"] > 1e-6
    assert res.meta["order_one_holds"] is False
    # order-zero does not involve D: still holds
    assert res.meta["order_zero"]["holds"] is True


def test_noncanonical_dim_reports_not_run():
    res = _svc().diagnose(np.eye(8))
    oz, oo = res.meta["order_zero"], res.meta["order_one"]
    assert oz["checked"] is False and oz["holds"] is None
    assert oo["checked"] is False and oo["holds"] is None
    assert "reason" in oz and "reason" in oo
    assert res.meta["order_zero_holds"] is None


def test_caller_supplied_algebra_is_used():
    # commuting pair -> holds; non-commuting Pauli pair -> fails
    I = np.eye(4)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    P = np.kron(X, np.eye(2))
    Q = np.kron(Z, np.eye(2))
    D = np.diag([1.0, 2.0, 3.0, 4.0])

    ok = _svc().diagnose(D, {"pi_mats": [I], "pi_op_mats": [I]})
    assert ok.meta["order_zero"]["holds"] is True
    assert ok.meta["order_zero"]["basis"] == "caller-supplied algebra representation"

    bad = _svc().diagnose(D, {"pi_mats": [P], "pi_op_mats": [Q]})
    assert bad.meta["order_zero"]["holds"] is False
    assert bad.meta["order_zero"]["max_norm"] > 1e-6
