# Task Proposals Board

## Task board

| Task ID | Title | Priority | Status | Owner | Target Version | Linked PR/Issue |
| --- | --- | --- | --- | --- | --- | --- |
| TG-001 | Rename `chronolog` to `chronology` in `ClockRateModulator` | Medium | Proposed | Unassigned | Next minor release | TBD |
| TG-002 | Align anomaly PoC summary keys with tests to remove `KeyError` drift | High | Proposed | Unassigned | Next patch release | TBD |
| TG-003 | Reconcile checklist guidance with executable test expectations for memory-decay sweep outputs | High | Proposed | Unassigned | Next patch release | TBD |
| TG-004 | Add regression coverage for YAML scientific-notation numerics in fallback parser mode | Medium | Proposed | Unassigned | Next minor release | TBD |

## Execution cadence

This board is reviewed and updated **weekly during engineering triage** and **before each release cut** to confirm priority, status, ownership, target version, and linked implementation artifacts.

## Task details

### TG-001

**Implementation scope**
- `temporal_gradient/clock/chronos.py`
- Docs/tests that reference `chronolog` (identified during implementation)

**Definition of done:** `clock.chronology` is the canonical telemetry-history attribute, `clock.chronolog` remains as a one-release compatibility alias with a deprecation note, and related tests/docs are updated and passing.

### TG-002

**Implementation scope**
- `anomaly_poc.py`
- `tests/test_anomaly_poc.py`

**Definition of done:** implementation and tests use one canonical summary-key schema, anomaly PoC tests pass via `pytest -q tests/test_anomaly_poc.py`, and any temporary compatibility keys are explicitly documented.

### TG-003

**Implementation scope**
- `docs_knob_validation_checklist.md`
- `tests/test_anomaly_poc.py`
- `anomaly_poc.py` (if output schema examples are co-located with implementation)

**Definition of done:** checklist documentation, tests, and implementation reference the same summary field names, a schema snippet is present/updated, and doc-test cross-references are verified in review.

### TG-004

**Implementation scope**
- `temporal_gradient/config.py`
- `tests/test_config_loader_strictness.py` (or a dedicated fallback parser regression test file)

**Definition of done:** regression tests cover scientific-notation numerics (for example `1e-3`) in fallback parser mode, include at least one YAML-unavailable fallback-path test, and pass after parser behavior supports float-valued scientific notation.

## Archival guidance

At release time, move completed entries from this file into `docs/archive/TASK_PROPOSALS_<release>.md` (for example, `docs/archive/TASK_PROPOSALS_v0.4.0.md`) and keep only active or deferred tasks in this tracker.
