# Documentation Change Checklist

Use this checklist for any PR that changes public behavior, naming, canonical surfaces, or compatibility guidance.

## Docs affected
- [ ] `README.md` updated for public behavior/canonical-vs-compatibility changes
- [ ] `docs/DAY1_CONTRIBUTOR_MAP.md` updated when subsystem entry points, required tests, or onboarding guidance change
- [ ] `USAGE.md` updated for runtime behavior and canonical-vs-compatibility guidance
- [ ] `GLOSSARY.md` updated when canonical terminology or deprecated terminology policy changes
- [ ] `docs/CANONICAL_SURFACES.md` updated when module source-of-truth or doc ownership changes

## Contributor-doc freshness expectations
- [ ] If APIs, canonical names, or compatibility paths evolve, contributor-facing docs are refreshed in the same PR (`README.md`, `docs/DAY1_CONTRIBUTOR_MAP.md`, and linked canonical/legacy guidance as needed)

- [ ] Merge is blocked if shim-status messaging disagrees across `docs/CANONICAL_VS_LEGACY.md`, `CHANGELOG.md` (Unreleased compatibility block), and `docs/CANONICAL_SURFACES.md`

## Review routing
- [ ] Requested review from documented maintainers/owners listed in `docs/CANONICAL_SURFACES.md`
