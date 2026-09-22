import numpy as np
import pytest

from spectral_diag.service import SpectralService


def test_diagonal_known():
    r = SpectralService().diagnose(np.diag([1.0, 2.0, 3.0, 4.0]), {})
    assert r.n == 4 and abs(r.trace - 10) < 1e-9
    assert abs(r.spectral_gap - 1) < 1e-9
    assert r.meta["missing_fields"] == []  # fallback supplies everything


def test_rejects_nonsquare():
    with pytest.raises(ValueError, match="square"):
        SpectralService().diagnose(np.ones((2, 3)), {})


def test_rejects_nan():
    with pytest.raises(ValueError, match="NaN"):
        SpectralService().diagnose(np.array([[1.0, np.nan], [0.0, 1.0]]), {})


def test_rejects_inf():
    with pytest.raises(ValueError, match="NaN"):
        SpectralService().diagnose(np.array([[1.0, np.inf], [0.0, 1.0]]), {})


def test_deterministic():
    s = SpectralService()
    A = np.random.default_rng(0).standard_normal((8, 8))
    A = A + A.T
    assert s.diagnose(A, {}).eigenvalues == s.diagnose(A, {}).eigenvalues


def test_cache_hit_returns_same_object():
    s = SpectralService()
    A = np.eye(4)
    assert s.diagnose(A, {}) is s.diagnose(A, {})


def test_missing_fields_reported():
    class Partial:
        name = "partial"

        def diagnose(self, A, params):
            return {"trace": 42.0}

    s = SpectralService()
    s.engine = Partial()
    s.engine_name = "partial"
    r = s.diagnose(np.eye(3), {})
    assert "spectral_gap" in r.meta["missing_fields"]
    assert r.trace == 42.0  # engine value wins where supplied
    assert abs(r.determinant - 1.0) < 1e-9  # fallback backfills the rest


def test_unknown_engine_raises():
    with pytest.raises(KeyError, match="not registered"):
        SpectralService(engine_name="no_such_engine")


def test_heat_kernel_keys():
    r = SpectralService().diagnose(np.diag([1.0, 2.0]), {})
    assert "spectral_dim@t=1" in r.heat_kernel
    assert any(k.startswith("Z(t=") for k in r.heat_kernel)
