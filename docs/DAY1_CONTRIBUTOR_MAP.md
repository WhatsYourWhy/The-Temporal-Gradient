# Day 1 Contributor Map

This guide is for first-time contributors who want a fast path from “I want to change X” to the right file(s), tests, and safety checks.

## If you want to change X, edit Y

| If you want to change… | Edit these files first | Then validate with… |
| --- | --- | --- |
| **Salience scoring** (novelty/value/`psi` behavior) | `temporal_gradient/salience/pipeline.py`, `temporal_gradient/salience/embedding_novelty.py`, `temporal_gradient/salience/provenance.py` | `tests/test_salience_pipeline.py`, `tests/test_salience_pipeline_determinism.py`, `tests/test_salience_contracts.py`, `tests/test_salience_provenance_hash.py`, `tests/test_salience_provenance_determinism.py` |
| **Clock/timebase dynamics** (`tau`, clock-rate clamps, strict mode) | `temporal_gradient/clock/chronos.py` | `tests/test_clock_contracts.py`, `tests/test_clock_edge_cases.py`, `tests/test_clock_rate_modulator.py`, `tests/test_clock_strict_mode.py` |
| **Memory decay/store invariants** (`S`, decay floors, store guards) | `temporal_gradient/memory/decay.py`, `temporal_gradient/memory/store.py` | `tests/test_memory_store.py`, `tests/test_memory_store_invariants.py`, `tests/test_entropic_decay.py`, `tests/test_entropic_decay_precision.py` |
| **Telemetry packet shape/schema** | `temporal_gradient/telemetry/chronometric_vector.py`, `temporal_gradient/telemetry/schema.py` | `tests/test_telemetry_schema.py`, `tests/test_telemetry_schema_strictness.py`, `tests/test_chronometric_vector_schema.py` |
| **Policies and compute gating** | `temporal_gradient/policies/compute_cooldown.py` | `tests/test_policies_compute_cooldown.py` |

## Required test runs by subsystem

When your PR changes one subsystem, run its targeted tests. If your change crosses subsystem boundaries, run all relevant groups.

### Salience
- `python -m pytest -q tests/test_salience_pipeline.py tests/test_salience_pipeline_determinism.py tests/test_salience_contracts.py tests/test_salience_provenance_hash.py tests/test_salience_provenance_determinism.py tests/test_embedding_novelty.py`

### Clock
- `python -m pytest -q tests/test_clock_contracts.py tests/test_clock_edge_cases.py tests/test_clock_rate_modulator.py tests/test_clock_strict_mode.py`

### Memory
- `python -m pytest -q tests/test_memory_store.py tests/test_memory_store_invariants.py tests/test_entropic_decay.py tests/test_entropic_decay_precision.py`

### Telemetry
- `python -m pytest -q tests/test_telemetry_schema.py tests/test_telemetry_schema_strictness.py tests/test_chronometric_vector_schema.py`

### Policies
- `python -m pytest -q tests/test_policies_compute_cooldown.py`

### Cross-cutting/API/docs safety net
- `python -m pytest -q tests/test_package_api.py tests/test_api_canonical_paths.py tests/test_docs_canonical_imports.py tests/test_root_shims.py`

## Expected local pre-push command order

Before pushing, run the same required gate order as CI:

1. `python -m pytest -q tests/test_packet_contract_check.py` *(pre-test packet-contract gate)*
2. `pytest -q` *(full regression suite)*
3. `python scripts/check_docs_consistency.py` *(docs consistency gate)*

If any command fails, fix the issue and re-run all commands in order so each gate is re-validated.

## Terminology and safety reminders

Before changing docs, comments, names, or examples:
- Use canonical terms from [`GLOSSARY.md`](../GLOSSARY.md).
- Preserve the non-anthropomorphic guardrails and claim boundaries in [`SAFETY.md`](../SAFETY.md).
- If you introduce a term that could be ambiguous, define it in `GLOSSARY.md` in the same PR.

## Canonical vs legacy gotchas (read before editing compatibility paths)

Read [`docs/CANONICAL_VS_LEGACY.md`](./CANONICAL_VS_LEGACY.md) before touching mode-dependent behavior.

Common gotchas:
- Canonical mode enforces strict packet-schema expectations; legacy-density compatibility can accept/derive values differently.
- Canonical keys/imports should be preferred in docs and examples; compatibility shims are migration-only.
- Tests should assert canonical behavior first, then explicitly note any temporary compatibility alias behavior.

## “First PR” templates (from current backlog)

Use these starter templates for small, high-signal first contributions.

### Template A — TG-TASK-001 (`chronolog` → `chronology`)
- **Goal:** Make `clock.chronology` the preferred attribute while preserving `chronolog` as a temporary alias.
- **Likely files:** `temporal_gradient/clock/chronos.py`, relevant docs/tests discovered during search.
- **Checklist:**
  - [x] Add/confirm canonical attribute and compatibility alias.
  - [x] Add a deprecation note for alias usage.
  - [x] Update docs/tests to prefer `chronology`.
  - [x] Run clock + API/docs tests listed above.

### Template B — TG-TASK-002 (anomaly PoC key alignment)
- **Goal:** Align anomaly PoC output summary keys and test assertions to one canonical naming scheme.
- **Likely files:** `anomaly_poc.py`, `tests/test_anomaly_poc.py`.
- **Checklist:**
  - [x] Pick canonical key names and apply consistently.
  - [x] Keep temporary compatibility keys only if necessary (document if retained).
  - [x] Ensure `tests/test_anomaly_poc.py` passes with no key drift.

### Template C — TG-TASK-004 (scientific-notation fallback parser coverage)
- **Goal:** Add regression tests for scientific-notation numerics (for example `1e-3`) in fallback config parser mode.
- **Likely files:** `temporal_gradient/config.py`, `tests/test_config_loader_strictness.py` (or dedicated fallback test file).
- **Checklist:**
  - [x] Add failing regression coverage for pre-fix behavior.
  - [x] Validate fallback parser path where YAML support is unavailable.
  - [x] Confirm scientific-notation values are accepted for float fields.

## Practical Day 1 workflow

1. Pick one bounded task (prefer one TG-TASK item).
2. Edit canonical package files first; touch root shims only when needed for compatibility.
3. Run subsystem-targeted tests from this map.
4. Update docs/checklists when public behavior or naming changes.
5. Include before/after notes in your PR so maintainers can review quickly.
