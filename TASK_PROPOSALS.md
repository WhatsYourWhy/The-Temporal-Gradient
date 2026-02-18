# Codebase Issue Triage: Proposed Follow-up Tasks

## 1) Typo Fix Task
**Title:** Rename `chronolog` to `chronology` in `ClockRateModulator`.

- **Why:** `chronolog` appears to be a typo/abbreviation that harms readability and discoverability for users inspecting telemetry history.
- **Evidence:** `ClockRateModulator.__init__` initializes `self.chronolog = []` and `tick()` appends telemetry entries to it.
- **Scope:**
  - Rename attribute to `chronology` in `temporal_gradient/clock/chronos.py`.
  - Keep a temporary compatibility alias (`chronolog`) for one release window, with deprecation note.
  - Update any tests/docs referencing the old name.
- **Acceptance criteria:**
  - `clock.chronology` is the canonical attribute.
  - Existing callers of `clock.chronolog` still function (with a clear deprecation path).

## 2) Bug Fix Task
**Title:** Align anomaly PoC summary keys with tests (or vice versa) to remove the current failure.

- **Why:** The current test suite fails with `KeyError: 'total_swept_forgotten'`.
- **Evidence:**
  - `run_poc()` returns `memories_forgotten` / `memories_alive` in the summary.
  - `tests/test_anomaly_poc.py` expects `total_swept_forgotten`.
- **Scope:**
  - Choose a single canonical key naming scheme for forget/sweep statistics.
  - Update `anomaly_poc.py` and tests to use the same schema.
  - If backward compatibility is needed, emit both keys temporarily.
- **Acceptance criteria:**
  - `pytest -q` passes.
  - PoC JSON schema is internally consistent and documented.

## 3) Comment/Documentation Discrepancy Task
**Title:** Reconcile checklist guidance with executable test expectations for memory-decay sweep outputs.

- **Why:** The checklist and test describe different output fields for the same validation objective.
- **Evidence:**
  - `docs_knob_validation_checklist.md` instructs checking `memories_alive` / `memories_forgotten`.
  - `tests/test_anomaly_poc.py` currently asserts on `total_swept_forgotten`.
- **Scope:**
  - Update documentation and tests to reference the same canonical field names.
  - Add a short JSON schema snippet for PoC summary fields to avoid drift.
- **Acceptance criteria:**
  - A single set of summary field names is used in docs + tests + implementation.

## 4) Test Improvement Task
**Title:** Add regression coverage for YAML scientific-notation numerics in fallback parser mode.

- **Why:** The fallback parser in `temporal_gradient/config.py` only treats tokens containing `.` as float candidates; values like `1e-3` are parsed as strings and later fail numeric validation unexpectedly.
- **Evidence:**
  - `parse_scalar()` checks for `"." in token` before `float(token)`.
  - Scientific notation is numeric but does not require a dot.
- **Scope:**
  - Add tests in `tests/test_config_loader_strictness.py` (or a new focused file) that validate numeric scientific notation for float-valued fields.
  - Preferably force fallback-parser path (mock `yaml is None`) to capture this code path.
- **Acceptance criteria:**
  - A test fails on current behavior and passes after parser improvement.
  - Scientific notation is accepted consistently for numeric config fields.
