# Canonical vs Legacy Density Modes

This guide defines the two supported salience/telemetry compatibility modes and when to use each.

## Supported modes

- `canonical`
- `legacy_density`

`canonical` is the default and authoritative behavior for all new integrations.

`legacy_density` exists only to preserve behavior for older harnesses that have not yet migrated to canonical packet production.

## Behavior differences

| Area | `canonical` | `legacy_density` |
|---|---|---|
| Salience source | Uses canonical salience pipeline output (`psi = H × V`) | Derives salience from entropy density, then clamps to `[0,1]` |
| Salience bounds | Enforced normalized bounds | Derived/clamped compatibility path |
| Telemetry schema enforcement | `validate_packet_schema(...)` is enforced | Canonical strictness is intentionally bypassed for compatibility |
| Accepted packet keys | Requires canonical schema keys; optional extended keys are additive | Accepts legacy-shaped packets used by historical integrations |

### Accepted packet keys

Canonical packet schema keys:

- `SCHEMA_VERSION`
- `WALL_T`
- `TAU`
- `SALIENCE`
- `CLOCK_RATE`
- `MEMORY_S`
- `DEPTH`

Extended telemetry keys allowed in canonical packet payloads:

- `H`
- `V`

Legacy integrations may continue emitting historical packet forms while `legacy_density` compatibility remains available.

## Intended usage

Use `canonical` when:

- building new features,
- validating or analyzing telemetry,
- publishing examples or integration docs.

Use `legacy_density` only when:

- you must keep older packet producers running during migration,
- you need a temporary bridge while updating external consumers.

## Deprecation horizon

`legacy_density` is a migration compatibility mode and should be treated as temporary.

- Compatibility shims and legacy behavior are maintained for a release-window transition period.
- Plan to migrate packet production and validation to `canonical` as soon as possible.
- Future releases may remove compatibility-only behavior with normal release-note notice.
