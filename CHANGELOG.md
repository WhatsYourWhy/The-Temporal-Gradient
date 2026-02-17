# Changelog

## v0.2.0 — Canonicalization & Policy Layer Formalization

**Release focus:**
Stabilize the public API surface, normalize naming, formalize the policy layer, and enforce telemetry/schema discipline.

### Added

- Canonical config surface:
  - `temporal_gradient.config_loader`
  - `load_config(...)` exposed at package root
- Telemetry schema validator:
  - `validate_packet_schema(...)` (canonical)
  - `validate_packet(...)` retained as compatibility alias
- Policy layer:
  - `ComputeCooldownPolicy` (canonical)
  - `allows_compute(...)` cooldown gate
- Structured subsystem test files for:
  - config loader
  - clock invariants
  - telemetry schema
  - policies
- Compatibility shim modules retained for one release window

### Renamed / Normalized

- `ComputeBudgetPolicy` → `ComputeCooldownPolicy`
  - Clarifies semantics (cooldown gate, not step allocator)
  - `compute_budget` module retained as compatibility shim
- Telemetry validator naming standardized:
  - `validate_packet_schema` is canonical
  - `validate_packet` calls canonical implementation

### Internal Consistency Improvements

- Enforced canonical import paths under `temporal_gradient.*`
- Removed duplicate config loader imports
- Eliminated semantic drift between policy naming and behavior
- Ensured harnesses validate telemetry packets
- Standardized error messaging and docstrings across subsystems

### Stability & Invariants

- Canonical mode enforces normalized salience bounds
- Clock rate remains floor-clamped
- Reconsolidation remains bounded with diminishing returns
- Cooldown gate prevents rapid repeated compute eligibility

### Compatibility

Root-level modules remain as compatibility shims for one release window:

- `chronometric_vector.py`
- `salience_pipeline.py`
- `chronos_engine.py`
- `entropic_decay.py`
- `compute_budget` (policy alias)

Future releases may remove shims.

### No Behavior Changes Intended

This release does not modify:

- Core clock-rate equation
- Salience computation logic
- Entropic decay dynamics
- Reconsolidation math

All changes are structural, naming, and API-surface normalization.

### Why v0.2.0 Exists

> v0.2.0 formalizes the public API surface and eliminates naming/duplication drift introduced during earlier refactors. The emphasis is canonical imports, schema validation, and policy clarity—not new dynamics.
