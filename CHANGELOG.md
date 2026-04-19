# Changelog

## v0.3.0 — Cleanup & simplification

**Release focus:** remove accumulated compatibility cruft, consolidate
the repo layout, and restate the public API as a single code path.

### Removed

- Root-level compatibility shims (`chronos_engine.py`,
  `chronometric_vector.py`, `entropic_decay.py`, `salience_pipeline.py`).
- `codex_valuation.py` and its `CodexNoveltyAdapter` /
  `CodexValueAdapter` bridges in `temporal_gradient.salience.pipeline`.
- `temporal_gradient/compat/` — legacy schema-version coercion, packet
  fallback keys, density-to-psi normalization.
- `legacy_density` salience mode:
  `ClockRateModulator(salience_mode=..., legacy_density_scale=...)`,
  the `input_context` tick argument, and
  `calculate_information_density()` / `_psi_from_legacy_density()`.
- `validate_packet_schema(salience_mode=...)` kwarg and the
  `validate_packet()` compatibility alias — use `validate_packet_schema()`.
- `ChronometricVector.from_packet(salience_mode=...)` and its legacy
  branch that read `t_obj` / `r` / `legacy_density` keys.
- Legacy `"1"` schema-version migration — only `"1.0"` is accepted.
- `anomaly_detection.py` `memories_alive` / `memories_forgotten` result
  aliases — use `total_swept_survivors` / `total_swept_forgotten`.
- Process / planning docs that had leaked into the public tree
  (`V0.2.0_PR_CHECKLIST.md`, `V0.3.0_PR_CHECKLIST.md`,
  `TASK_PROPOSALS.md`, `docs_knob_validation_checklist.md`,
  `docs/CODE_REVIEW_AUDIT.md`, `docs/DOC_CHANGE_CHECKLIST.md`,
  `docs/DAY1_CONTRIBUTOR_MAP.md`, `docs/MIGRATION_SHIMS.md`,
  `docs/NEWCOMER_GUIDE.md`, `docs/CANONICAL_VS_LEGACY.md`,
  `docs/CANONICAL_SURFACES.md`, `docs/archive/`).
- Meta-tests that guarded shim / doc surface rather than behavior.

### Changed

- Runnable entrypoints moved out of the repo root into `examples/`:
  `anomaly_poc.py` → `examples/anomaly_detection.py`,
  `simulation_run.py` → `examples/simulation.py`, and
  `twin_paradox.py`, `sanity_harness.py`, `calibration_harness.py`.
- Each example prepends the repo root to `sys.path` so it runs from a
  clean checkout without `pip install`.
- `GLOSSARY.md`, `SAFETY.md`, `USAGE.md` moved into `docs/` (lowercase).
- README rewritten: leads with what the framework does, install, and a
  minimal usage example; architecture and schema details moved to
  `docs/architecture.md`.
- License changed from a bespoke source-available "no execute" clause
  to the standard **MIT License**.

### Added

- `pyproject.toml` (Python ≥3.10, optional `PyYAML`, `[dev]` extra
  installs `pytest`).
- `docs/architecture.md` — layer map, data-flow diagram, telemetry
  schema reference.

### Migration

- Replace `from temporal_gradient.telemetry.schema import validate_packet`
  with `validate_packet_schema`.
- Drop `salience_mode=` / `legacy_density_scale=` kwargs from
  `ClockRateModulator(...)` — there is one code path now.
- Drop `salience_mode=` from `validate_packet_schema(...)` and
  `ChronometricVector.from_packet(...)`.
- Drop `input_context=` from `clock.tick(...)`; pass `psi=` directly.
- Replace root-level script paths (`python anomaly_poc.py`, etc.) with
  the new `examples/` locations.
- Consumers of `run_poc(...)`'s result dict should read
  `total_swept_survivors` / `total_swept_forgotten` instead of
  `memories_alive` / `memories_forgotten`.

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
