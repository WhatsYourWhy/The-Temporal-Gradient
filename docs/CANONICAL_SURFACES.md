# Canonical Surfaces and Documentation Owners

This document is the source-of-truth map for **canonical** module surfaces and explicit documentation ownership.

## Canonical module surfaces

| Subsystem | Canonical surface |
| --- | --- |
| clock | `temporal_gradient.clock.chronos` |
| salience | `temporal_gradient.salience.pipeline` |
| memory | `temporal_gradient.memory.*` |
| telemetry | `temporal_gradient.telemetry.*` |
| policies | `temporal_gradient.policies.compute_cooldown` |

## Compatibility notes

The following are compatibility shims and are **not canonical**:
- top-level script/module shim (compatibility-only): `chronos_engine.py`
- policy shim module (compatibility-only): `temporal_gradient.policies.compute_budget`

## Documentation maintainers / owners

Use this ownership map for review routing when public behavior or naming changes.

| Document | Maintainer / owner |
| --- | --- |
| `README.md` | Temporal Gradient maintainers |
| `USAGE.md` | Temporal Gradient maintainers |
| `GLOSSARY.md` | Temporal Gradient maintainers |
| `docs/CANONICAL_SURFACES.md` | Temporal Gradient maintainers |
| `docs/DOC_CHANGE_CHECKLIST.md` | Temporal Gradient maintainers |

If a change affects canonical/compatibility labels, update this file in the same PR.
