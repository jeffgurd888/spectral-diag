# Cold Outreach Drafts — spectral-diag pilot

Sender: Jeffrey Michael Gurd, Nexus Research <jeffrey@nexus-research.org>
Repo: https://github.com/jeffgurd888/spectral-diag
Offer: 2-week pilot, $5k fixed, credited in full against an annual license.
See PILOT.md for the full one-pager.

Contacts are NOT verified — find the right person via each org's team page /
GitHub org before sending. Do not blast; one personal email each.

---

## 1. QuantStack

**Send to:** a maintainer of xtensor / xtensor-blas (see github.com/quantstack —
start with whoever is most active on xtensor-blas).

**Subject:** a CI gate for silent singular matrices in xtensor-blas

Hi — I'm Jeff, an independent researcher building spectral-diag, an
open-core tool that computes spectral health (eigenvalues, gap, condition
number, heat kernel, symmetry checks) for matrices and fails a CI build
when a matrix goes unhealthy.

You maintain xtensor-blas, where eigvals/matrix_rank/inv are exactly the
functions that silently misbehave on singular or ill-conditioned inputs.
I'm offering a two-week, $5k-fixed pilot: we wire `spectral gate` into
xtensor-blas's own CI as a reference integration, plus a diagnostic report
on matrices of your choice. The $5k credits in full against an annual
license if you continue.

Repo (public, MIT): https://github.com/jeffgurd888/spectral-diag

Worth a 15-minute call? Happy to start from a single matrix of yours —
`.npy`, `.csv`, or via the API.

— Jeff
Nexus Research

---

## 2. Braintrust

**Send to:** a founding engineer / product lead (see braintrust.dev team page).

**Subject:** a new CI signal: catch embedding rank collapse before evals do

Hi — I'm Jeff, building spectral-diag: spectral health checks for matrices
(eigenvalues, spectral gap, condition number, rank-drift detection) that
gate a CI build the way your eval gates already do.

You gate builds on eval scores. There's a failure mode eval scores miss:
attention rank collapse and embedding drift that degrade a model while
metrics look flat. A spectral check is a cheap, complementary signal —
`n=32` to `n=1M+`, one shell command, JSONL report.

I'm offering a two-week, $5k-fixed pilot: a spectral gate on one of your
eval pipelines plus a diagnostic report on your production embedding
matrices. The $5k credits in full against an annual license.

Repo (public, MIT): https://github.com/jeffgurd888/spectral-diag

Open to a 15-minute call?

— Jeff
Nexus Research

---

## 3. Coreform

**Send to:** technical leadership via coreform.com / forum.coreform.com
(founder-led org — a direct technical email can reach a decision-maker).

**Subject:** fail the build when a mesh change wrecks matrix conditioning

Hi — I'm Jeff, an independent researcher building spectral-diag, an
open-core spectral diagnostics tool: eigenvalues, spectral gap, condition
number, and symmetry checks for matrices, wired as a CI gate.

You own the stage where the damage is done — mesh quality (skewed or
degenerate elements) shows up directly in stiffness-matrix conditioning,
and a bad mesh currently costs your customers a doomed solver run before
anyone notices. A pre-solve spectral gate fails fast instead: one command,
seconds of compute, before the hours-long run.

Two-week, $5k-fixed pilot: we gate one meshing pipeline on stiffness-matrix
health and deliver a diagnostic report on matrices of your choice. The $5k
credits in full against an annual license.

Repo (public, MIT): https://github.com/jeffgurd888/spectral-diag

Worth 15 minutes?

— Jeff
Nexus Research

---

## Sending checklist

- [ ] Verify each recipient (no guessed addresses).
- [ ] Personalize one line per email (a recent blog post, release, or issue).
- [ ] Attach nothing; link the repo and offer the PILOT.md one-pager on reply.
- [ ] Follow up once, 4–5 business days later, then move on.
