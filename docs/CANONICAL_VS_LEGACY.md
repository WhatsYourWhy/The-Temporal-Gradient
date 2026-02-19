# Canonical vs Legacy Mode Guide

This document defines runtime mode behavior for contributors, provides import migration guidance, and sets the deprecation horizon for compatibility shims.

## Mode Definitions

### `canonical`

Use `canonical` mode for all new code and integrations.

- Enforces canonical telemetry schema validation with required canonical packet keys.
- Treats normalized salience values as authoritative (`psi` from canonical salience pipeline outputs).
- Rejects packet payloads that do not conform to canonical schema expectations.

### `legacy_density`

`legacy_density` is a compatibility mode for older integrations.

- Preserves support for legacy packet shapes during migration windows.
- Derives and clamps salience from entropy density when canonical salience inputs are absent.
- Applies compatibility-oriented validation behavior rather than strict canonical enforcement.

## Behavior Deltas (`canonical` vs `legacy_density`)

| Behavior area | `canonical` | `legacy_density` |
| --- | --- | --- |
| Schema enforcement | Strict canonical schema validation; non-canonical packet shapes are rejected. | Compatibility-focused validation for legacy packet shapes; strict canonical schema requirements are relaxed. |
| Packet keys | Canonical telemetry key set is required (for example: `WALL_T`, `TAU`, `SALIENCE`, `CLOCK_RATE`, `MEMORY_S`, `DEPTH`). | Legacy or mixed key sets may be accepted for backward compatibility. |
| Salience derivation | Salience is expected from canonical salience pipeline outputs (`H`, `V`, and derived `psi`). | Salience may be derived from entropy density and clamped for compatibility with older emitters. |

## Migration Matrix: Legacy/Shim Imports → Canonical Imports

Use canonical imports in all new/modified files. Keep shim usage only as temporary migration scaffolding.

| Legacy / shim import | Canonical import | Example replacement |
| --- | --- | --- |
| `from chronos_engine import ClockRateModulator` | `from temporal_gradient.clock.chronos import ClockRateModulator` | Replace direct root-level shim import with canonical package path. |
| `from compute_budget import ComputeBudgetPolicy` | `from temporal_gradient.policies.compute_cooldown import ComputeCooldownPolicy` | Rename policy class and module to cooldown naming. |
| `from temporal_gradient.policies.compute_budget import ComputeBudgetPolicy` | `from temporal_gradient.policies.compute_cooldown import ComputeCooldownPolicy` | Update in-package compatibility alias imports to canonical policy module. |
| `from chronometric_vector import ChronometricVector` | `from temporal_gradient.telemetry.chronometric_vector import ChronometricVector` | Migrate telemetry vector imports to canonical telemetry package. |
| `from salience_pipeline import SaliencePipeline, RollingJaccardNovelty, KeywordImperativeValue` | `from temporal_gradient.salience.pipeline import SaliencePipeline, RollingJaccardNovelty, KeywordImperativeValue` | Move salience pipeline and primitives to canonical salience package imports. |
| `from entropic_decay import DecayEngine` | `from temporal_gradient.memory.decay import DecayEngine` | Use canonical memory package path for decay engine access. |
| `ClockRateModulator.chronolog` | `ClockRateModulator.chronology` | Typo alias removed; migrate all telemetry history access to `chronology`. |

### Copy/Paste Migration Examples

#### Policy rename and import migration

```python
# Before (legacy/shim)
from temporal_gradient.policies.compute_budget import ComputeBudgetPolicy

policy = ComputeBudgetPolicy(cooldown_tau=0.5)
```

```python
# After (canonical)
from temporal_gradient.policies.compute_cooldown import ComputeCooldownPolicy

policy = ComputeCooldownPolicy(cooldown_tau=0.5)
```

#### Root-level shim to canonical telemetry import

```python
# Before (legacy/shim)
from chronometric_vector import ChronometricVector
```

```python
# After (canonical)
from temporal_gradient.telemetry.chronometric_vector import ChronometricVector
```

## Operational Recommendations for New Contributors

1. Default to `canonical` mode in local runs, tests, and examples.
2. Use only canonical imports for new files and refactors.
3. Treat `legacy_density` and root-level shims as migration-only compatibility paths.
4. Validate telemetry packets using canonical schema checks in development workflows.
5. When touching compatibility code, leave explicit migration notes in PR descriptions and changelog entries.

Compatibility note: root-level shim modules are intentionally narrow in v0.2.x and expose only documented compatibility symbols (see `docs/CANONICAL_SURFACES.md`). Treat any non-documented shim attributes as unsupported internals.

Alias removal note: `ClockRateModulator.chronolog` has been removed; `ClockRateModulator.chronology` is the only supported attribute for clock telemetry history.

## Deprecation Timeline (release-labeled)

- **v0.2.x**: Canonical mode is the default contributor target; legacy mode and compatibility shims remain available for migration.
- **v0.3.x**: **Staged removal by subsystem** (not a single full-shim drop): each compatibility shim/alias is removed only when its owning subsystem migration criteria are complete and explicitly release-noted.
- **v0.4.0+**: Legacy/shim paths should be considered removed unless explicitly reintroduced with release notes.

For release-by-release migration messaging, update `CHANGELOG.md` Unreleased using the compatibility template and keep this document aligned.
