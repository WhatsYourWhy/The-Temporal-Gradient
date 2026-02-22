# Task Proposals Board

## Active v0.3 cleanup tasks

| Task ID | Title | Priority | Status | Owner | Target Patch Version | Completion criteria |
| --- | --- | --- | --- | --- | --- | --- |
| TG-013 | Remove root compatibility shim imports from docs/tests and enforce canonical package paths | High | In Progress | @core-maintainers | v0.3.1 | All docs/examples/tests use `temporal_gradient.*` canonical imports only; `tests/test_api_canonical_paths.py` and `tests/test_docs_canonical_imports.py` pass with no shim-path allowances; migration docs clearly mark shim phase-out status. |
| TG-014 | Remove deprecated `ClockRateModulator.chronolog` alias and keep `chronology` as the only public attribute | High | Planned | @clock-owners | v0.3.2 | `temporal_gradient/clock/chronos.py` exposes only `chronology`; alias-dependent tests are removed/updated; `tests/test_clock_rate_modulator.py` and API/docs guard tests pass using canonical names only. |
| TG-015 | Trim migration docs after removals to keep only canonical guidance (archive historical compatibility notes) | Medium | Planned | @docs-maintainers | v0.3.2 | `docs/MIGRATION_SHIMS.md` and `docs/CANONICAL_VS_LEGACY.md` no longer describe active shims/aliases that were removed; stale compatibility examples are deleted or archived; docs consistency check passes. |

## Execution cadence

Canonical/compatibility source-of-truth references live in [`docs/CANONICAL_SURFACES.md`](docs/CANONICAL_SURFACES.md) and [`docs/MIGRATION_SHIMS.md`](docs/MIGRATION_SHIMS.md).

This board is reviewed and updated **weekly during engineering triage** and **before each release cut** to confirm priority, status, ownership, target patch version, and linked implementation artifacts.

## Archive / history (completed hardening items)

| Task ID | Title | Outcome | Completed In |
| --- | --- | --- | --- |
| TG-001 | Rename `chronolog` to `chronology` in `ClockRateModulator` | Completed (canonical attribute landed with temporary alias and coverage) | v0.2.x |
| TG-002 | Align anomaly PoC summary keys with tests to remove `KeyError` drift | Completed | v0.2.x |
| TG-003 | Reconcile checklist guidance with executable test expectations for memory-decay sweep outputs | Completed | v0.2.x |
| TG-004 | Add regression coverage for YAML scientific-notation numerics in fallback parser mode | Completed | v0.2.x |
| TG-006 | Harden fallback YAML parser to reject mismatched quote delimiters | Completed | v0.3.x |
| TG-007 | Sync README test-count claim with current CI reality | Completed | v0.2.x |
| TG-008 | Add negative tests for malformed fallback YAML quoting/arrays | Completed | v0.3.x |
| TG-010 | Handle `run_poc(..., n_events=0)` without index/division errors | Completed | v0.2.x |
| TG-011 | Replace stale README fixed test count (`74 passed`) with command-driven wording | Completed | v0.2.x |
| TG-012 | Add anomaly PoC regression test for empty-event streams (`n_events=0`) | Completed | v0.2.x |

## Archival guidance

At each release cut, move newly completed entries from the active board into this history section (or `docs/archive/TASK_PROPOSALS_<release>.md` for longer snapshots) and keep only active/deferred cleanup work in the top table.
