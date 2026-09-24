# spectral-diag / provenance record
# Status: DECLARED METADATA — not a verified physical experiment
record_id:         sd-run-20260924-1259-schoolcraft
record_type:       computation_run_metadata
declared_by:       operator (self-reported)

# Computation identity
engine:            lean32  (cgurd.engine:Lean32Engine)
engine_version:    v0.2.1
service_version:   spectral-diag v0.2.0
entry_point:       spectral_diag.engines → lean32
input_hash:        PENDING (filled by the run itself — never by hand)
input_shape:       (32, 32)
input_class:       self-adjoint real
computation:       spectral_dimension + temporal_messages
output_artifact:   d_s(σ) table, M(τ), ||[T,D]||_F

# Declared reference coordinates
declared_location:
  address:         11607 S Shaver Rd, Schoolcraft, MI 49087, USA
  role:            operator location (declared)
declared_time:
  date:            2026-09-24
  time_local:      ~12:59 EDT
  timezone:        America/Detroit (UTC−4)
  utc_equivalent:  2026-09-24T16:59Z
declared_by_whom: operator

# Scope note — read before citing
claims:
  physical_experiment_occurred: false
  computation_was_run:          true
  location_verified:            false
  time_verified:                false
  hardware_location_matches_operator_location: unverified
notes: |
  This record declares when and where the operator states the computation
  was performed. It does not attest that a physical experiment took place
  at this address, nor that the computation ran on hardware located there.
  Numerical results are reproducible from the engine, version, and input
  hash above regardless of where they executed.
