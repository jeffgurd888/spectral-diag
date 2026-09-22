# spectral-diag

Engine-agnostic spectral diagnostics for matrices and operators: eigenvalues,
spectral gap, heat-kernel / spectral-dimension curve, symmetry checks — as a
CLI, batch runner, CI gate, and FastAPI service.

## What it is (honest version)

This repo is the **wrapper**, not the math breakthrough. The built-in
`fallback` engine is a reference NumPy implementation (eigendecomposition,
heat trace, spectral dimension). It is correct, tested, and honest about
being a reference.

The money is in the **engine contract**: any engine implementing
`EngineProtocol.diagnose` registers via the `spectral_diag.engines`
entry-point group and drops in with zero changes to `api.py` / `cli.py`.
Fields your engine doesn't supply are backfilled by the fallback and named
in `meta.missing_fields` — during the pilot that list is your roadmap, and
you shrink it to zero as the engine matures.

```
Theorem ≠ Simulation ≠ Experiment ≠ Device
```
Numerical diagnostics here are **simulation-tier evidence**, never proofs.
The service never claims otherwise.

## Quickstart

```bash
pip install -e ".[test,s3]"
spectral verify                      # self-check: determinism + golden spectrum
spectral engines                     # list registered engines (fallback + yours)
spectral diagnose examples/covariance.npy --json-out
spectral batch "examples/*.npy" --out results.jsonl
spectral gate examples/laplacian.npy --min-gap 1e-6 --max-cond 1e12
spectral serve                        # FastAPI on :8000
```

## API

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | status + engine list |
| `/v1/engines` | GET | registered engines |
| `/v1/diagnose` | POST | single matrix (JSON body) |
| `/v1/diagnose/file` | POST | upload .npy/.csv/.json |
| `/v1/batch` | POST | many matrices, per-item errors |
| `/v1/diagnose/s3` | POST | sync S3 in/out (needs `boto3`) |
| `/v1/jobs` | POST | async S3 job (queued → done/error) |
| `/v1/jobs/{id}` | GET | job status |

Auth: set `SPECTRAL_API_KEYS="k1,k2"` and send `X-API-Key`. Unset = dev mode
(open). **Do not ship dev mode.**

## Register your engine

In your engine package's `pyproject.toml`:

```toml
[project.entry-points."spectral_diag.engines"]
lean32 = "my_pkg.engine:Lean32Engine"
```

```python
class Lean32Engine:
    name = "lean32"
    def diagnose(self, A, params):
        return {"eigenvalues": [...], "spectral_gap": ..., ...}
        # any subset — the service backfills + reports the rest
```

Then `SpectralService(engine_name="lean32")`, `spectral diagnose m.npy
--engine lean32`, or `POST /v1/diagnose {"engine": "lean32", ...}`.

## The CI gate (the wedge)

```yaml
# .github/workflows/spectral-gate.yml
- run: pip install spectral-diag
- run: spectral gate artifacts/stiffness.npy --min-gap 1e-6 --max-cond 1e12
```

A failing build is the cheapest possible sale: the diagnostic pre-empts a
bad deploy. One pre-empted failure per pilot partner is the success metric.

## Ship checklist

**Engineering (this week)**
1. Point entry-points at the verified engine class; run `spectral verify` + `pytest`.
2. `spectral engines` — confirm your engine appears.
3. Diagnose three real matrices (covariance, graph Laplacian, stiffness —
   samples in `examples/`) and inspect `meta.missing_fields`. Every field the
   fallback still backfills is engine surface you haven't exposed yet.
4. Deploy the Docker image behind TLS; set `SPECTRAL_API_KEYS`.
5. Swap the in-process `JOBS` dict for Redis before any batch workload.

**Pilot (2 weeks, one design partner)**
- Scope: one production pipeline, 3–5 matrices, weekly.
- Deliverable: a JSONL diagnostic report + one CI gate rule in their build.
- Success metric: ≥1 pre-empted failure they'd otherwise have shipped.

**Pricing sketch**
- Free CLI, open-core.
- Team API: $500/mo base + $0.01/diagnostic over 50k.
- Enterprise: on-prem Docker, SSO, custom engine module, SLA — annual.
- Pilot: $5k fixed, credited against annual.

## Status

v0.2.0 — wrapper complete, tested, Dockerized. **Lean32Engine is registered**
(`cgurd.engine:Lean32Engine`, entry-point `lean32`): the canonical 32x32
Dirac operator diagnoses with `missing_fields == []`, mass gap 0.5, and the
golden regression suite passes. Two meta fields — `order_zero_holds` and
`order_one_holds` — are asserted by construction, not computed; they are
labels, not verification results. See the docstring in `cgurd/engine.py`.
