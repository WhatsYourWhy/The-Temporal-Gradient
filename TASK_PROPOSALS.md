# Codebase Issue Triage: Task Tracker

## Active task index

| ID | Title | Type | Status | Owner | Linked Issue/PR | Target Release |
| --- | --- | --- | --- | --- | --- | --- |
| TG-TASK-001 | Rename `chronolog` to `chronology` in `ClockRateModulator` | Refactor / Typo fix | Proposed | Unassigned | TBD | Next minor release |
| TG-TASK-002 | Align anomaly PoC summary keys with tests to remove `KeyError` drift | Bug fix | Proposed | Unassigned | TBD | Next patch release |
| TG-TASK-003 | Reconcile checklist guidance with executable test expectations for memory-decay sweep outputs | Documentation / Test consistency | Proposed | Unassigned | TBD | Next patch release |
| TG-TASK-004 | Add regression coverage for YAML scientific-notation numerics in fallback parser mode | Test improvement | Proposed | Unassigned | TBD | Next minor release |

## Task details

### TG-TASK-001 — Rename `chronolog` to `chronology` in `ClockRateModulator`

**Affected paths**
- `temporal_gradient/clock/chronos.py`
- Any docs/tests that reference `chronolog` (as discovered during implementation)

**Definition of Done**
- `clock.chronology` is the canonical telemetry-history attribute.
- Existing callers of `clock.chronolog` continue to work for one release window via a compatibility alias.
- A deprecation note is added for `chronolog` usage.
- Tests and docs are updated to reference `chronology` as the preferred name.

### TG-TASK-002 — Align anomaly PoC summary keys with tests to remove `KeyError` drift

**Affected paths**
- `anomaly_poc.py`
- `tests/test_anomaly_poc.py`

**Definition of Done**
- Implementation and tests agree on one canonical naming scheme for sweep/forget summary keys.
- `pytest -q` passes for the anomaly PoC test coverage.
- If temporary backward compatibility keys are retained, they are documented and marked for removal.
- PoC summary output is internally consistent across code and assertions.

### TG-TASK-003 — Reconcile checklist guidance with executable test expectations for memory-decay sweep outputs

**Affected paths**
- `docs_knob_validation_checklist.md`
- `tests/test_anomaly_poc.py`
- `anomaly_poc.py` (if schema/example snippets are co-located with output logic)

**Definition of Done**
- Documentation, tests, and implementation use one shared set of summary field names.
- Checklist language mirrors the canonical output schema used in tests.
- A short summary-schema snippet is added (or updated) to prevent future drift.
- Cross-references between docs and tests are validated during review.

### TG-TASK-004 — Add regression coverage for YAML scientific-notation numerics in fallback parser mode

**Affected paths**
- `temporal_gradient/config.py`
- `tests/test_config_loader_strictness.py` (or a dedicated fallback parser test file)

**Definition of Done**
- Regression tests cover scientific-notation values (for example, `1e-3`) in fallback parser mode.
- At least one test exercises the fallback path where YAML parsing support is unavailable.
- Scientific-notation numerics are accepted for float-valued config fields.
- Tests fail on pre-fix behavior and pass after parser improvements.

## Triage cadence

This tracker is reviewed **weekly during engineering triage** and again **before each release cut** to confirm status, ownership, and release targeting.

## Archival guidance

At release time, move completed entries from this file into `docs/archive/TASK_PROPOSALS_<release>.md` (for example, `docs/archive/TASK_PROPOSALS_v0.4.0.md`) and keep only active or deferred tasks in this tracker.
