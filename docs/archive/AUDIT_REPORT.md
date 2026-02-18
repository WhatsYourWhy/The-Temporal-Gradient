# Structural Validation Report — Temporal Gradient

## A) Executive Summary
The repository is largely modular and internally readable, with clean package boundaries for `clock`, `salience`, `memory`, `policies`, `telemetry`, and config loading. Public compatibility shims are mostly thin aliases with no extra logic, which limits API drift risk. The test suite is broad and currently passing.

However, there are notable intent/implementation gaps:
- `policies.cooldown_tau` is configured and documented, but not integrated into harness execution paths.
- `memory.decay_lambda` and `memory.s_max` are config-validated but not wired into memory dynamics.
- telemetry docs claim `CLOCK_RATE` / `MEMORY_S` may be `null`, but implementation serializes missing values as `0.0`.
- canonical clock invariants can be bypassed by directly passing negative `wall_delta` into `tick`, allowing `tau` regression.

Conclusion: the codebase is **partially coherent** but not fully semantically aligned with its own documentation and config surface. The primary issue pattern is “declared knobs not actually connected to runtime behavior,” which increases drift risk.

## B) Architecture Map

```text
[Config Layer]
  Canonical module: temporal_gradient.config_loader -> temporal_gradient.config
  Public API:
    - load_config(path)
    - Config dataclasses (SalienceConfig/ClockConfig/MemoryConfig/PoliciesConfig/TemporalGradientConfig)
  Inbound deps:
    - temporal_gradient.__init__
    - sanity_harness.py
    - calibration_harness.py
  Outbound deps:
    - pathlib, typing, dataclasses
    - optional PyYAML

[Salience Layer]
  Canonical module: temporal_gradient.salience.pipeline
  Public API:
    - SaliencePipeline.evaluate(text)
    - RollingJaccardNovelty.score(text)
    - KeywordImperativeValue.score(text)
    - SalienceComponents
    - Codex adapters
  Inbound deps:
    - clock layer (demo block import usage)
    - harnesses/simulations/tests
  Outbound deps:
    - re, typing/dataclasses

[Clock Layer]
  Canonical module: temporal_gradient.clock.chronos
  Public API:
    - ClockRateModulator
      - clock_rate_from_psi(psi)
      - tick(psi, input_context, wall_delta)
      - calculate_information_density(input_data)
  Inbound deps:
    - harnesses/simulations/tests
    - package export temporal_gradient.clock
  Outbound deps:
    - salience pipeline + telemetry vector (for __main__ demo)
    - time, math

[Memory Layer]
  Canonical modules: temporal_gradient.memory.decay + temporal_gradient.memory.store
  Public API:
    - should_encode(psi, threshold)
    - initial_strength_from_psi(psi, S_max)
    - decay_strength(strength, elapsed_tau, half_life)
    - EntropicMemory.reconsolidate(...)
    - DecayEngine (add_memory/get_memory/touch_memory/entropy_sweep)
    - DecayMemoryStore / MemoryStore
  Inbound deps:
    - harnesses/simulations/tests
  Outbound deps:
    - uuid/math + store

[Policy Layer]
  Canonical module: temporal_gradient.policies.compute_cooldown
  Compatibility module: temporal_gradient.policies.compute_budget
  Public API:
    - ComputeCooldownPolicy
    - allows_compute(...)
    - ComputeBudgetPolicy alias (shim)
  Inbound deps:
    - tests; README sample only
  Outbound deps:
    - dataclasses

[Telemetry Layer]
  Canonical modules: temporal_gradient.telemetry.chronometric_vector + schema
  Public API:
    - ChronometricVector.to_packet()/from_packet()
    - validate_packet_schema(packet)
    - validate_packet(packet) alias
  Inbound deps:
    - harnesses/simulations/tests
    - clock __main__ demo
  Outbound deps:
    - json + schema validator

[Harness/Simulation Layer]
  Modules:
    - sanity_harness.py
    - calibration_harness.py
    - simulation_run.py
    - twin_paradox.py
  Public API:
    - run_harness(...)
    - run_calibration(...)
    - run_simulation()/run_twin_experiment()
  Inbound deps:
    - tests (harness regression + smoke)
  Outbound deps:
    - clock/salience/memory/telemetry/config
```

## C) Violations List

### 1) Architectural consistency
1. **Policy layer is not integrated into harness execution**: `cooldown_tau` exists in config and policy module, but harnesses do not instantiate/use `ComputeCooldownPolicy` to gate memory writes or compute actions.
2. **Config fields with no runtime effect**: `memory.decay_lambda` and `memory.s_max` are validated and present in config, but memory runtime uses module constant `S_MAX=1.5` and `half_life`; `decay_lambda` is unused.

### 2) Canonical import surface audit
1. **Canonical public surface exists and is stable** (`temporal_gradient` package exports modules + `load_config`; policy canonical path documented).
2. **Mixed internal imports**: internal scripts mostly import deep module paths directly (`temporal_gradient.clock.chronos`, etc.) rather than canonical package-level namespace.
3. **Compatibility shims are clean**: root shims and `compute_budget` are pure aliases/re-exports with no divergent logic.

### 3) Documentation vs implementation
**Overstated / mismatched claims**
1. `USAGE.md` says `CLOCK_RATE` and `MEMORY_S` may be `null`; implementation emits `0.0` when absent.
2. README “Cooldown window prevents rapid repeated reinforcement” is true in memory API, but harnesses do not pass a cooldown in touch/reconsolidation flow and generally never exercise `touch_memory`.

**Under-documented implementation behavior**
1. Telemetry supports optional `entropy_cost` key in schema, but docs only list optional `H` and `V`.
2. Legacy-density mode behavior in schema validator (`validate_packet_schema` no-op when non-canonical) is not clearly documented as reduced enforcement.

### 4) Invariant enforcement
**Clock**
- Canonical `psi` bounds are enforced in `tick`; strict-mode additionally enforces in `clock_rate_from_psi`.
- **Gap**: no guard against negative `wall_delta` in `tick`, so `tau` can regress.

**Memory**
- Strength cap enforced at store upsert (`0 <= strength <= s_max`), reconsolidation bounded by `S_MAX`.
- Decay over internal time is implemented.
- Diminishing reconsolidation is implemented via `0.1 / access_count` floor at 0.02.
- Cooldown logic exists in `reconsolidate`, but not wired through harness workflows in a policy-governed way.

**Telemetry**
- Required keys and types enforced in canonical mode.
- Schema validation is called in `ChronometricVector.to_packet()` and `sanity_harness`, but not used by `calibration_harness` (which emits summaries only).

**Policy**
- `ComputeCooldownPolicy` semantics match name (boolean gate only, no allocation logic).
- No hidden compute-budget allocator logic found.

### 5) Test suite integrity
- Dedicated tests exist for all major subsystems (clock/salience/memory/telemetry/config/policies/harness/API/shims).
- Canonical and compatibility import surfaces are tested.
- Invariant tests cover many constraints (bounds, schema strictness, store invariants).
- **Coverage gap**: no test for negative `wall_delta` tau regression; no test that config `cooldown_tau`/`decay_lambda` materially affect runtime behavior.

### 6) Duplication & semantic drift
- Root-level shims (`chronos_engine.py`, `salience_pipeline.py`, etc.) are re-export only; acceptable temporary duplication.
- `compute_budget` is a pure alias shim; no semantic drift.
- Real drift source is config-vs-runtime disconnect (`decay_lambda`, `s_max`, `cooldown_tau` not functionally integrated).

## D) Patch Plan (file-level only; normalization, no redesign)
1. **`temporal_gradient/clock/chronos.py`**
   - Add explicit validation for `wall_delta >= 0` in `tick` to enforce tau monotonicity.
2. **`USAGE.md`**
   - Correct telemetry nullability statement (`CLOCK_RATE`/`MEMORY_S` currently serialize as numeric 0.0 fallback).
   - Document optional `entropy_cost` key if retained in schema.
3. **`README.md`**
   - Clarify that policy module is canonical but not currently wired in harness default flow (or wire it if intended).
4. **`temporal_gradient/config.py` + memory/policy integration files**
   - Either wire `decay_lambda`, `s_max`, and `cooldown_tau` into runtime behavior, or remove/deprecate unused config keys to avoid semantic drift.
5. **`tests/test_clock_edge_cases.py` (or new dedicated test file)**
   - Add explicit regression test asserting negative `wall_delta` is rejected.

## E) Risk Assessment
- **Structural Risk Score: 5/10**
  - Layering is clear, but some declared controls are disconnected from behavior.
- **API Drift Risk Score: 6/10**
  - Canonical surfaces are good; drift risk comes from tolerated legacy paths and partially wired config knobs.
- **Documentation Drift Risk Score: 7/10**
  - Several behavior claims/implications diverge from actual serialization and runtime usage.
- **Refactor Fragility Risk: 6/10**
  - Strong tests reduce fragility, but hidden inert config fields make refactors easy to get semantically wrong.

## Internal Coherence Verdict
**Partially coherent, not fully coherent.**
Core dynamics are implemented consistently, but policy/config/documentation alignment is incomplete.
