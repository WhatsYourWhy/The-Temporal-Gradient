# Newcomer Guide

## What this repo is
Temporal Gradient is a simulation framework for two coupled dynamics:
- an internal time accumulator (`tau`) modulated by salience load (`psi`), and
- an entropic memory strength (`S`) that decays over internal time and can be reinforced.

It is explicitly framed as an engineering dynamics framework (not a cognitive or consciousness model).

## Repository structure at a glance
- `temporal_gradient/` — canonical package code for clock, salience, memory, telemetry, policies, and config.
- `tests/` — comprehensive subsystem and integration tests.
- `docs/` — contributor and canonical-surface documentation.
- Root-level modules like `chronos_engine.py`, `salience_pipeline.py`, `entropic_decay.py`, `chronometric_vector.py` — compatibility shims retained for legacy imports.
- `scripts/` and `examples/` — consistency checks, demos, and deterministic replay examples.

## How the core pieces fit together
1. **Config loading**: `load_config` validates and normalizes settings from `tg.yaml` into typed dataclasses.
2. **Salience pipeline**: computes novelty/value and combines them into salience load (`psi`).
3. **Clock modulator**: advances `tau` from wall time using a clamped rate derived from `psi`.
4. **Memory layer**: stores and decays memory strength over internal time (`tau`).
5. **Telemetry packet**: emits canonical packets (`ChronometricVector`) and validates schema.
6. **Policies**: optional compute gating using internal-time cooldown.

## First files to read
1. `README.md` for canonical usage flow and guardrails.
2. `docs/DAY1_CONTRIBUTOR_MAP.md` for "change X -> edit Y -> run Z tests" mapping.
3. `docs/CANONICAL_SURFACES.md` for canonical imports and shim boundaries.
4. `temporal_gradient/__init__.py` for stable public package surface.

## Practical newcomer workflow
- Prefer canonical imports via `import temporal_gradient as tg`.
- Avoid adding new root-level shims; change canonical package modules first.
- When changing a subsystem, run the targeted tests in `docs/DAY1_CONTRIBUTOR_MAP.md`.
- Before opening PRs, run packet-contract check, full test suite, then docs consistency check.

## Good next learning targets
- Salience determinism and provenance hashing (`temporal_gradient/salience/provenance.py` + related tests).
- Clock strict-mode and salience-mode behavior (`temporal_gradient/clock/chronos.py` + strict-mode tests).
- Telemetry schema evolution constraints (`temporal_gradient/telemetry/schema.py` and schema strictness tests).
- Canonical-vs-legacy lifecycle policy (`docs/CANONICAL_VS_LEGACY.md`, `docs/MIGRATION_SHIMS.md`).
