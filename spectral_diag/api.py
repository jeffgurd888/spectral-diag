"""Spectral Diagnostics API v0.2.0.

Auth: set SPECTRAL_API_KEYS="key1,key2" to require X-API-Key headers.
Dev mode (no keys configured) accepts everything — do not ship that.

Batch and async jobs: JOBS is an in-process dict. Swap it for Redis and
BackgroundTasks for Celery/RQ/Arq before any real batch workload;
the endpoints stay identical.
"""

import hmac
import io
import json
import os
import time
import uuid

import numpy as np
from fastapi import BackgroundTasks, FastAPI, File, Header, HTTPException, UploadFile
from pydantic import BaseModel, Field

from .engines import list_engine_names, resolve_engine  # noqa: F401 (re-exported for /v1/engines clarity)
from .service import SpectralService

app = FastAPI(title="Spectral Diagnostics API", version="0.2.0")

API_KEYS = set(filter(None, os.getenv("SPECTRAL_API_KEYS", "").split(",")))


def auth(x_api_key: str | None = Header(default=None)):
    if not API_KEYS:
        return  # dev mode: no keys configured
    if not x_api_key or not any(hmac.compare_digest(x_api_key, k) for k in API_KEYS):
        raise HTTPException(401, "invalid API key")


_services: dict = {}


def svc(engine: str | None = None) -> SpectralService:
    key = engine or "fallback"
    if key not in _services:
        _services[key] = SpectralService(engine_name=engine)
    return _services[key]


class DiagnoseRequest(BaseModel):
    matrix: list
    params: dict = Field(default_factory=dict)
    engine: str | None = None


class BatchItem(BaseModel):
    id: str
    matrix: list
    params: dict = Field(default_factory=dict)


class BatchRequest(BaseModel):
    items: list[BatchItem]
    engine: str | None = None


class S3Request(BaseModel):
    bucket: str
    key: str
    fmt: str = "npy"  # npy | csv | json
    params: dict = Field(default_factory=dict)
    engine: str | None = None
    out_bucket: str | None = None
    out_key: str | None = None


@app.get("/health")
def health():
    return {"status": "ok", "engines": list_engine_names()}


@app.get("/v1/engines")
def engines_endpoint():
    return {"engines": list_engine_names()}


@app.post("/v1/diagnose")
def diagnose(req: DiagnoseRequest, x_api_key: str | None = Header(default=None)):
    auth(x_api_key)
    try:
        A = np.array(req.matrix, dtype=float)
        return svc(req.engine).diagnose(A, req.params).to_dict()
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/v1/diagnose/file")
async def diagnose_file(
    file: UploadFile = File(...),
    t: float = 1.0,
    engine: str | None = None,
    x_api_key: str | None = Header(default=None),
):
    auth(x_api_key)
    try:
        A = load_bytes(await file.read(), file.filename or "")
        return svc(engine).diagnose(A, {"t": t}).to_dict()
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/v1/batch")
def batch(req: BatchRequest, x_api_key: str | None = Header(default=None)):
    auth(x_api_key)
    out, errors = [], []
    s = svc(req.engine)
    for item in req.items:
        try:
            out.append(
                {
                    "id": item.id,
                    "result": s.diagnose(
                        np.array(item.matrix, dtype=float), item.params
                    ).to_dict(),
                }
            )
        except Exception as e:
            errors.append({"id": item.id, "error": str(e)})
    return {"ok": out, "errors": errors, "count": len(out)}


JOBS: dict = {}


@app.post("/v1/jobs")
def submit_job(
    req: S3Request,
    bg: BackgroundTasks,
    x_api_key: str | None = Header(default=None),
):
    auth(x_api_key)
    job_id = uuid.uuid4().hex
    JOBS[job_id] = {"status": "queued", "submitted": time.time()}
    bg.add_task(_run_s3_job, job_id, req)
    return {"job_id": job_id, "status": "queued"}


@app.get("/v1/jobs/{job_id}")
def job_status(job_id: str, x_api_key: str | None = Header(default=None)):
    auth(x_api_key)
    if job_id not in JOBS:
        raise HTTPException(404, "unknown job")
    return JOBS[job_id]


@app.post("/v1/diagnose/s3")
def diagnose_s3(req: S3Request, x_api_key: str | None = Header(default=None)):
    auth(x_api_key)
    try:
        return _run_s3_job("sync", req)
    except Exception as e:
        raise HTTPException(400, str(e))


def _run_s3_job(job_id: str, req: S3Request):
    try:
        import boto3  # optional dependency: pip install spectral-diag[s3]

        s3 = boto3.client("s3")
        body = s3.get_object(Bucket=req.bucket, Key=req.key)["Body"].read()
        A = load_bytes(body, req.key)
        res = svc(req.engine).diagnose(A, req.params).to_dict()
        if req.out_bucket and req.out_key:
            s3.put_object(
                Bucket=req.out_bucket,
                Key=req.out_key,
                Body=json.dumps(res).encode(),
                ContentType="application/json",
            )
        out = {"status": "done", "result": res}
    except Exception as e:
        out = {"status": "error", "error": str(e)}
    if job_id != "sync":
        JOBS[job_id] = out
    return out


def load_bytes(data: bytes, name: str) -> np.ndarray:
    if name.endswith(".npy"):
        return np.load(io.BytesIO(data))
    if name.endswith(".json"):
        return np.array(json.loads(data.decode()), dtype=float)
    text = data.decode()
    try:
        return np.loadtxt(io.StringIO(text), delimiter=",")
    except ValueError:
        return np.loadtxt(io.StringIO(text))  # whitespace-separated
