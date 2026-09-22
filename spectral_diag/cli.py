"""spectral — CLI for spectral diagnostics.

Commands:
  diagnose  single matrix file -> JSON/text
  batch     glob of files -> JSONL, exits non-zero on any failure
  gate      CI gate: non-zero exit if the matrix is unhealthy (the wedge)
  engines   list registered engines
  verify    self-check: determinism + golden-spectrum test
  serve     run the FastAPI server
"""

import glob
import json

import numpy as np
import typer

from .engines import _entry_points
from .service import SpectralService

cli = typer.Typer(help="Spectral diagnostics for matrices and operators.")


def _svc(engine: str | None) -> SpectralService:
    return SpectralService(engine_name=engine)


def load_path(p: str) -> np.ndarray:
    if p.endswith(".npy"):
        return np.load(p)
    if p.endswith(".json"):
        return np.array(json.load(open(p)), dtype=float)
    text = open(p).read()
    try:
        return np.loadtxt(__import__("io").StringIO(text), delimiter=",")
    except ValueError:
        return np.loadtxt(__import__("io").StringIO(text))


@cli.command()
def diagnose(
    path: str,
    engine: str = typer.Option(None, help="Engine name (default: fallback)"),
    t: float = 1.0,
    json_out: bool = False,
):
    """Diagnose a single matrix file (.npy, .csv, .json)."""
    A = load_path(path)
    res = _svc(engine).diagnose(A, {"t": t})
    typer.echo(json.dumps(res.to_dict(), indent=2) if json_out else _pretty(res))


@cli.command()
def batch(
    pattern: str,
    engine: str = typer.Option(None, help="Engine name (default: fallback)"),
    out: str = "results.jsonl",
):
    """Diagnose many files; write JSONL. Exits non-zero if any fail."""
    files = sorted(glob.glob(pattern))
    if not files:
        typer.echo(f"no files matched {pattern}", err=True)
        raise typer.Exit(2)
    s, fails = _svc(engine), 0
    with open(out, "w") as fh:
        for f in files:
            try:
                r = s.diagnose(load_path(f), {})
                fh.write(json.dumps({"file": f, "result": r.to_dict()}) + "\n")
            except Exception as e:
                fails += 1
                fh.write(json.dumps({"file": f, "error": str(e)}) + "\n")
    typer.echo(f"{len(files)-fails}/{len(files)} ok -> {out}")
    raise typer.Exit(1 if fails else 0)


@cli.command()
def gate(
    path: str,
    min_gap: float = 1e-6,
    max_cond: float = 1e12,
    engine: str = typer.Option(None, help="Engine name (default: fallback)"),
):
    """CI gate: non-zero exit if the matrix is unhealthy."""
    r = _svc(engine).diagnose(load_path(path), {})
    bad = []
    if r.spectral_gap < min_gap:
        bad.append(f"gap {r.spectral_gap:.3e} < {min_gap:.3e}")
    if r.condition_number > max_cond:
        bad.append(f"cond {r.condition_number:.3e} > {max_cond:.3e}")
    if not r.symmetry["hermitian"]:
        bad.append("not hermitian")
    typer.echo("FAIL: " + "; ".join(bad) if bad else "PASS")
    raise typer.Exit(1 if bad else 0)


@cli.command()
def engines():
    """List registered spectral engines."""
    names = ["fallback"] + [
        ep.name for ep in _entry_points("spectral_diag.engines")
    ]
    typer.echo("\n".join(names))


@cli.command()
def verify():
    """Self-check: determinism + known-spectrum golden test."""
    s = _svc(None)
    A = np.diag([1.0, 2.0, 3.0, 4.0])
    r1, r2 = s.diagnose(A, {}), s.diagnose(A, {})
    assert r1.eigenvalues == r2.eigenvalues, "non-deterministic output"
    assert abs(r1.spectral_gap - 1.0) < 1e-9, "spectral gap wrong"
    assert abs(r1.trace - 10.0) < 1e-9, "trace wrong"
    assert r1.meta["engine"] == "fallback", "engine label wrong"
    typer.echo("verify: OK")


@cli.command()
def serve(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI server."""
    import uvicorn

    uvicorn.run("spectral_diag.api:app", host=host, port=port)


def _pretty(res) -> str:
    lines = [
        f"n={res.n}  trace={res.trace:.6g}  det={res.determinant:.6g}",
        f"spectral_gap={res.spectral_gap:.6g}  cond={res.condition_number:.6g}",
        f"symmetry={res.symmetry}",
        f"engine={res.meta.get('engine')}  missing_fields={res.meta.get('missing_fields')}",
        f"spectral_dim@t=1 = {res.heat_kernel.get('spectral_dim@t=1', float('nan')):.4f}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    cli()
