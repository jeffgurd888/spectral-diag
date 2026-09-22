import numpy as np
from fastapi.testclient import TestClient

from spectral_diag.api import app

client = TestClient(app)


def _mat(n=4):
    return np.diag([1.0, 2.0, 3.0, 4.0]).tolist()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert "fallback" in r.json()["engines"]


def test_engines():
    r = client.get("/v1/engines")
    assert r.status_code == 200
    assert "fallback" in r.json()["engines"]


def test_diagnose():
    r = client.post("/v1/diagnose", json={"matrix": _mat(), "params": {}})
    assert r.status_code == 200
    body = r.json()
    assert body["n"] == 4
    assert abs(body["spectral_gap"] - 1.0) < 1e-9


def test_diagnose_rejects_bad_matrix():
    r = client.post("/v1/diagnose", json={"matrix": [[1, 2, 3], [4, 5, 6]], "params": {}})
    assert r.status_code == 400


def test_batch():
    r = client.post(
        "/v1/batch",
        json={
            "items": [
                {"id": "good", "matrix": _mat(), "params": {}},
                {"id": "bad", "matrix": [[1, 2], [3]], "params": {}},
            ]
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 1
    assert body["ok"][0]["id"] == "good"
    assert body["errors"][0]["id"] == "bad"


def test_job_unknown():
    r = client.get("/v1/jobs/does-not-exist")
    assert r.status_code == 404


def test_api_key_enforced(monkeypatch):
    import spectral_diag.api as api

    monkeypatch.setattr(api, "API_KEYS", {"secret123"})
    r = client.post("/v1/diagnose", json={"matrix": _mat()})
    assert r.status_code == 401
    r = client.post(
        "/v1/diagnose", json={"matrix": _mat()}, headers={"X-API-Key": "secret123"}
    )
    assert r.status_code == 200
