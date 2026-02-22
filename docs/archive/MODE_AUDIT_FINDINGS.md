# Mode Audit Findings

## Bug / correctness risk

1. **`ChronometricVector.to_packet()` ignores `schema_version` instance state.**
   - The dataclass stores `schema_version` and normalizes it in `__post_init__`, but `to_packet()` always emits `SCHEMA_VERSION` as `CANONICAL_SCHEMA_VERSION` instead of using `self.schema_version`.
   - This can make round-trips lossy/confusing in compatibility flows (`from_packet(..., salience_mode="legacy_density")` preserves a parsed schema version in the object, but serializing back discards that state).
   - File path: `temporal_gradient/telemetry/chronometric_vector.py`.

2. **Constructor-level parameter validation is weaker than config validation.**
   - `load_config()` strictly bounds clock parameters (`min_clock_rate`, `base_dilation_factor`, etc.), but direct `ClockRateModulator(...)` construction does not enforce those bounds.
   - Invalid direct arguments (for example a negative `min_clock_rate`) can produce non-physical or surprising clock-rate behavior while still passing type checks.
   - File paths: `temporal_gradient/config.py`, `temporal_gradient/clock/chronos.py`.

## Design debt

1. **Duplicate psi validation in the `tick()` hot path.**
   - `tick()` validates psi via `_validate_psi()` and then calls `clock_rate_from_psi()`, which re-validates with `_validate_psi()` again.
   - This duplicates logic in a central runtime path and increases maintenance burden if psi policy changes.
   - File path: `temporal_gradient/clock/chronos.py`.

2. **Clock module blends reusable runtime code with demo/CLI behavior in one file.**
   - `temporal_gradient/clock/chronos.py` contains both the core `ClockRateModulator` and a sizable `if __name__ == "__main__":` demo block with output formatting and simulation examples.
   - This coupling makes the module do two jobs (library + executable demo), increasing cognitive load and making library diffs noisier.
   - File path: `temporal_gradient/clock/chronos.py`.

3. **Legacy compatibility behavior is spread across multiple modules.**
   - Legacy-mode handling appears in both clock logic (`salience_mode == "legacy_density"`) and telemetry parsing (`from_packet(..., salience_mode="legacy_density")`) with separate fallback key maps and normalization rules.
   - The behavior is test-covered, but the policy is not centralized, which raises long-term drift risk.
   - File paths: `temporal_gradient/clock/chronos.py`, `temporal_gradient/telemetry/chronometric_vector.py`.

## Ambiguous intent

1. **Docs present a simplified core equation that omits a configured dilation factor used in code.**
   - README describes `dτ/dt = 1/(1+Ψ(t))`, while implementation computes `1/(1 + base_dilation_factor * psi)`.
   - It is unclear whether `base_dilation_factor` is meant as an implementation detail, an extension of the documented equation, or a doc gap.
   - File paths: `README.md`, `temporal_gradient/clock/chronos.py`.

2. **Canonical strictness messaging vs schema-version normalization may be read inconsistently.**
   - Canonical docs emphasize strict canonical schema, but schema validation accepts legacy `SCHEMA_VERSION` value `"1"` and normalizes it.
   - This is likely intentional for migration, but the strictness boundary is subtle and easy for contributors to misread.
   - File paths: `docs/CANONICAL_VS_LEGACY.md`, `temporal_gradient/telemetry/schema.py`.
