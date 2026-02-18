# Task Proposals Board

## Task board

| Task ID | Title | Priority | Status | Owner | Target Version | Linked PR/Issue |
| --- | --- | --- | --- | --- | --- | --- |
| TG-001 | Rename `chronolog` to `chronology` in `ClockRateModulator` | Medium | Completed | Codex | v0.2.x | Covered by in-repo tests/docs |
| TG-002 | Align anomaly PoC summary keys with tests to remove `KeyError` drift | High | Completed | Codex | v0.2.x | Covered by in-repo tests/docs |
| TG-003 | Reconcile checklist guidance with executable test expectations for memory-decay sweep outputs | High | Completed | Codex | v0.2.x | Covered by in-repo tests/docs |
| TG-004 | Add regression coverage for YAML scientific-notation numerics in fallback parser mode | Medium | Completed | Codex | v0.2.x | Covered by in-repo tests/docs |
| TG-005 | Plan final removal of misspelled `chronolog` compatibility alias | Medium | Proposed | Unassigned | v0.3.x | Follow-up cleanup task |
| TG-006 | Harden fallback YAML parser to reject mismatched quote delimiters | High | Completed | Codex | v0.3.x | Covered by in-repo tests/docs |
| TG-007 | Sync README test-count claim with current CI reality | Medium | Proposed | Unassigned | v0.2.x | Docs consistency fix |
| TG-008 | Add negative tests for malformed fallback YAML quoting/arrays | Medium | Completed | Codex | v0.3.x | Covered by in-repo tests/docs |
| TG-009 | Remove deprecated typo alias `chronolog` from clock modulator surface | Medium | Proposed | Unassigned | v0.3.x | Typo cleanup + migration-doc follow-up |
| TG-010 | Handle `run_poc(..., n_events=0)` without index/division errors | High | Proposed | Unassigned | v0.2.x | Bug fix in anomaly PoC summary generation |
| TG-011 | Replace stale README fixed test count (`74 passed`) with command-driven wording | Medium | Proposed | Unassigned | v0.2.x | Docs/comment discrepancy fix |
| TG-012 | Add anomaly PoC regression test for empty-event streams (`n_events=0`) | Medium | Proposed | Unassigned | v0.2.x | Test-hardening task tied to TG-010 |

## Execution cadence

Canonical/compatibility source-of-truth references live in [`docs/CANONICAL_SURFACES.md`](docs/CANONICAL_SURFACES.md) and [`docs/MIGRATION_SHIMS.md`](docs/MIGRATION_SHIMS.md).

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

### TG-005

**Implementation scope**
- `temporal_gradient/clock/chronos.py`
- migration docs that still reference alias lifecycle (`docs/CANONICAL_VS_LEGACY.md`, `docs/MIGRATION_SHIMS.md`)

**Definition of done:** remove the deprecated `chronolog` alias at the next planned compatibility-window boundary, update migration docs/changelog, and keep tests green on canonical `chronology` usage only.

### TG-006

**Implementation scope**
- `temporal_gradient/config.py` fallback parser (`_parse_simple_yaml`)

**Definition of done:** fallback parser raises `ConfigValidationError` for malformed quoted scalars (for example mixed `'..."` delimiters) instead of silently normalizing them, with clear error text.

### TG-007

**Implementation scope**
- `README.md` testing-status snippet

**Definition of done:** README no longer reports stale "`74 passed`" output and instead reflects current test-suite status (or references a command without fixed count).

### TG-008

**Implementation scope**
- `tests/test_config_loader_strictness.py`

**Definition of done:** add fallback-parser regression tests that assert invalid quoted YAML content and malformed inline-array inputs are rejected with `ConfigValidationError`.

### TG-009

**Implementation scope**
- `temporal_gradient/clock/chronos.py`
- compatibility lifecycle docs (`docs/MIGRATION_SHIMS.md`, `docs/CANONICAL_VS_LEGACY.md`)

**Definition of done:** remove `ClockRateModulator.chronolog` (misspelled compatibility alias) at the planned shim-removal boundary, ensure canonical `chronology` is the only public attribute, and update migration messaging/tests accordingly.

### TG-010

**Implementation scope**
- `anomaly_poc.py` (`run_poc` summary construction)

**Definition of done:** `run_poc(..., n_events=0)` returns a valid summary without `IndexError`/`ZeroDivisionError` by providing explicit empty-stream defaults for aggregates and terminal telemetry fields.

### TG-011

**Implementation scope**
- `README.md` testing snippet in the quick-check section

**Definition of done:** README no longer hardcodes a stale pass count; it references executable commands and/or dynamic wording that remains accurate as the suite grows.

### TG-012

**Implementation scope**
- `tests/test_anomaly_poc.py`

**Definition of done:** add regression coverage that exercises `run_poc(n_events=0)` and asserts summary-shape invariants (counts, aggregates, and list fields) to prevent empty-input regressions.

## Archival guidance

At release time, move completed entries from this file into `docs/archive/TASK_PROPOSALS_<release>.md` (for example, `docs/archive/TASK_PROPOSALS_v0.4.0.md`) and keep only active or deferred tasks in this tracker.

## Completion updates (current pass)

- **TG-001** complete: `ClockRateModulator.chronology` is canonical and `chronolog` is retained as a deprecated compatibility alias, with dedicated regression coverage.
- **TG-002** complete: anomaly PoC summary uses canonical sweep keys with explicit one-release aliases to prevent key drift.
- **TG-003** complete: checklist guidance reflects the canonical PoC summary schema (`total_swept_survivors` / `total_swept_forgotten`) and explicitly calls out alias deprecation.
- **TG-004** complete: fallback parser path is regression-tested for YAML scientific-notation numerics (for example `1e-1`, `5e-2`) when PyYAML is unavailable.
- **TG-006** complete: fallback parser now rejects mismatched/unterminated quote delimiters with `ConfigValidationError` instead of silently accepting malformed scalars.
- **TG-008** complete: strict fallback-parser regression tests cover malformed quoted scalars and malformed inline-array delimiters/items.
