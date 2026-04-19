# Changelog

## Unreleased

### Removed

- Root-level compatibility shims (`chronos_engine.py`, `chronometric_vector.py`,
  `entropic_decay.py`, `salience_pipeline.py`).
- `codex_valuation.py` and its `CodexNoveltyAdapter` / `CodexValueAdapter`
  bridges in `temporal_gradient.salience.pipeline`.
- `temporal_gradient/compat/` — legacy schema-version coercion, packet
  fallback keys, density-to-psi normalization.
- `legacy_density` salience mode: `ClockRateModulator(salience_mode=...)`,
  `legacy_density_scale`, `input_context`, and `calculate_information_density()`.
- `validate_packet_schema(salience_mode=...)` kwarg and the
  `validate_packet()` compatibility alias — use `validate_packet_schema()`.
- `ChronometricVector.from_packet(salience_mode=...)` and its legacy
  branch that read `t_obj` / `r` / `legacy_density` keys.
- Legacy `"1"` schema-version migration — only `"1.0"` is accepted now.
- Stale process docs (V0.2.0 / V0.3.0 PR checklists, `TASK_PROPOSALS.md`,
  `docs_knob_validation_checklist.md`, `docs/CODE_REVIEW_AUDIT.md`,
  `docs/DOC_CHANGE_CHECKLIST.md`, `docs/DAY1_CONTRIBUTOR_MAP.md`,
  `docs/MIGRATION_SHIMS.md`, `docs/NEWCOMER_GUIDE.md`,
  `docs/CANONICAL_VS_LEGACY.md`, `docs/CANONICAL_SURFACES.md`,
  `docs/archive/`).

### Changed

- Runnable entrypoints moved from the repo root into `examples/`:
  `anomaly_poc.py` → `examples/anomaly_detection.py`,
  `simulation_run.py` → `examples/simulation.py`,
  and `twin_paradox.py`, `sanity_harness.py`, `calibration_harness.py`
  relocated under `examples/`.
- `GLOSSARY.md`, `SAFETY.md`, `USAGE.md` moved into `docs/` (lowercase).
- README rewritten: leads with what the framework does, install, and a
  minimal usage example; architecture / schema details moved to
  `docs/architecture.md`.
- `anomaly_detection.py` drops the `memories_alive` / `memories_forgotten`
  back-compat aliases on its result dict — use `total_swept_survivors` /
  `total_swept_forgotten`.

### Added

- `pyproject.toml` with Python ≥3.10, optional `PyYAML`, and a `[dev]`
  extra that installs `pytest`.
- `docs/architecture.md` — layer map, data-flow diagram, telemetry
  schema reference.

## v0.2.0 — Canonicalization & Policy Layer Formalization

**Release focus:**
Stabilize the public API surface, normalize naming, formalize the policy
layer, and enforce telemetry/schema discipline.

### Added

- Canonical config surface: `temporal_gradient.config_loader`,
  `load_config(...)` exposed at package root.
- Telemetry schema validator: `validate_packet_schema(...)` (canonical),
  `validate_packet(...)` retained as compatibility alias.
- Policy layer: `ComputeCooldownPolicy` and `allows_compute(...)` cooldown
  gate.
- Structured subsystem test files for the config loader, clock invariants,
  telemetry schema, and policies.
- Compatibility shim modules retained for one release window.

### Renamed / Normalized

- `ComputeBudgetPolicy` → `ComputeCooldownPolicy` (clarifies semantics —
  cooldown gate, not step allocator). `compute_budget` module retained
  as a compatibility shim.
- Telemetry validator naming standardized: `validate_packet_schema` is
  canonical; `validate_packet` calls the canonical implementation.

### Stability & Invariants

- Canonical mode enforces normalized salience bounds.
- Clock rate remains floor-clamped.
- Reconsolidation remains bounded with diminishing returns.
- Cooldown gate prevents rapid repeated compute eligibility.

### No behavior changes intended

v0.2.0 does not modify the core clock-rate equation, salience
computation, entropic decay dynamics, or reconsolidation math. All
changes are structural, naming, and API-surface normalization.
