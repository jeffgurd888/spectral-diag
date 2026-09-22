# Design-Partner Prospects — spectral-diag pilot ($5k fixed, CI gate as wedge)

Researched 2026-09-22 via public sources only. Nobody contacted.
Ranked by likelihood to answer cold outreach.

## Tier 1 — email first

### 1. QuantStack (Paris)
- What: OSS scientific-software consultancy; stewards xtensor, xeus, mamba.
- Why: they maintain `xtensor-blas` (eigvals, matrix_rank, inv) — silent
  singular/ill-conditioned matrices are their users' everyday bug class.
- Angle: "A matrix-health CI gate you can drop into xtensor-blas's own CI —
  open-core, ships as CLI + API your downstream users reuse."
- Signal: https://github.com/quantstack

### 2. Braintrust (SF, $36M Series A)
- What: eval infra with native CI/CD gating of evals.
- Why: they already gate builds on eval metrics; attention rank collapse and
  embedding drift are silent regression modes eval scores miss.
- Angle: "Add a spectral health check to your eval CI gate — catch rank
  collapse the way you already catch score regressions."
- Signal: https://www.braintrust.dev/blog/braintrust-not-eval-framework

### 3. Coreform (Orem, UT)
- What: makers of Coreform Cubit mesh-generation toolkit (ex-Sandia Cubit).
- Why: mesh quality (skewed/degenerate elements) shows up directly in
  stiffness-matrix conditioning — they own the stage where the damage is done.
- Angle: "Fail the build when a meshing change degrades the stiffness-matrix
  condition number, before your customer's solver burns hours."
- Signal: https://github.com/coreformllc

## Tier 2

### 4. PyMC Labs
- Bayesian consultancy (creators of PyMC). Ill-conditioned mass matrices and
  degenerate posteriors are daily debugging pain (HMC divergences).
- Angle: "A spectral-health gate for Bayesian model pipelines — catches
  degenerate mass matrices before sampling burns hours."

### 5. Probabl (Paris, €13M seed)
- Inria spin-off operating the scikit-learn brand. Users constantly hit
  ill-conditioned covariances and collinear features.
- Angle: "Catch ill-conditioned and rank-collapsed design matrices before
  your users do."

### 6. QuantConnect (Seattle)
- Open-source algo-trading platform (LEAN engine). Portfolio optimizers fed
  by estimated covariances; ill-conditioned inputs silently degrade them.
- Angle: "Embed spectral health checks into LEAN's portfolio-construction
  layer — warn users before a bad covariance reaches the optimizer."
- Note: likely an embed/white-label partnership rather than a classic pilot.

### 7. Predictive Engineering (Portland, OR)
- Independent FEA/CFD consultancy, 800+ projects incl. SpaceX, Intel.
  1M+ DOF nonlinear contact models; ill-conditioned stiffness matrices from
  rigid links/contact pairs are the daily enemy.
- Angle: "Fail CI when a mesh or contact change makes your stiffness matrix
  ill-conditioned — before a 3-hour nonlinear run that's numerically doomed."

### 8. WhyLabs (Seattle, Series B)
- AI observability for drift/model health. Embedding-covariance spectra and
  condition-number monitoring of production feature matrices are the natural
  next layer on their drift detectors.
- Angle: "Spectral monitoring on top of your drift platform."

## Tier 3 — longer shots

### 9. Numerai (SF)
- Crowdsourced hedge fund; feature-neutralization projects onto nullspaces of
  factor-exposure matrices — ill-conditioned exposure matrices explode
  neutralization coefficients.
- Angle: "CI-gate your feature-neutralization pipeline."

### 10. Tecton (SF, Series C)
- Enterprise feature platform. Pipelines can silently produce ill-conditioned
  feature matrices; embedding drift is their bread and butter.
- Angle: "Catch rank-collapse before it silently degrades downstream models."

### 11. Convergent Science (Madison, WI)
- CONVERGE CFD with autonomous run-time meshing; sliver cells kill solver
  convergence. Founder-led — cold technical email can reach a decision-maker.
- Angle: "A spectral gate on your meshing pipeline that flags snapshots with
  collapsing rank before the solver diverges at timestep 4,000."

### 12. SimScale (Munich, ~150 people)
- Cloud CFD/FEA platform, 900k+ users. A pre-solve spectral gate cuts wasted
  compute; could become a platform "simulation health score."
- Angle: "A 10-second spectral gate before each FEA run."

## Caveats
- All verified via public sources only; nobody contacted.
- GitHub org handles for the ML-infra entries came from search text, not
  verbatim verification — re-check before using in outreach copy.
- Cut from the list: Headlands (active trade-secret litigation, guarded),
  Anyscale (Series C, too big to reply cold).
- Numerai and SimScale are the least likely to reply; Convergent and SimScale
  are the largest targets.
