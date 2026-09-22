# Spectral Health Pilot — 2-Week Fixed-Scope Offer

**One production pipeline. 3–5 matrices. One pre-empted failure, or you learn
exactly where your numerical risk lives.**

## The problem

Ill-conditioned covariance, rank-collapsed embeddings, drifting Laplacians,
and unstable stiffness matrices don't announce themselves. They ship — and
then they cost you a bad deploy, a wrong price, or a silent model regression.

## What you get (2 weeks, $5,000 fixed)

1. **Diagnostic report (JSONL)** — eigenvalues, spectral gap, condition
   number, heat-kernel / spectral-dimension curve, and symmetry checks for
   3–5 of your production matrices.
2. **One CI gate rule** wired into your build: `spectral gate` fails the
   build when a matrix goes unhealthy (gap collapse, conditioning blowup,
   lost Hermiticity). You choose the thresholds; we tune them on your data.
3. **Findings call** — what we found, what it means, what to watch.

The $5k is **credited in full against an annual license** if you continue.

## Success metric

At least one pre-empted failure — an ill-conditioning, rank collapse, or
drift event you would otherwise have shipped. If we find nothing, you get a
clean bill of spectral health and the gate stays as a guardrail.

## What we need from you

- 3–5 matrices (`.npy`, `.csv`, or via our API/S3) from one pipeline.
- One 30-minute kickoff call, one 30-minute findings call.
- A place to run the gate (GitHub Actions, Jenkins, or your runner).

## Stack

Open-core CLI + FastAPI service. Your data never trains anything; on-prem
Docker available for the pilot on request. No lock-in: the gate is a
one-line shell command.

---

Contact: Jeffrey Michael Gurd, Nexus Research — jeffrey@nexus-research.org
