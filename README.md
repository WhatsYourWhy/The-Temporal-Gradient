# Temporal Gradient: Internal Timebase + Entropic Memory

## Status
- Version: 0.2.0
- License: Proprietary source-available (review only; execution requires permission — see LICENSE)

## Canonical Summary
Temporal Gradient is a simulation framework modeling:
1. an internal time accumulator \(\tau\) whose rate is modulated by salience load \(\Psi\), and
2. a memory strength variable \(S\) that decays over internal time and may reconsolidate on access.

The system exposes engineered control signals and structured telemetry for simulation inspection.

This is a dynamics framework, not a cognitive model.

## Guardrails
This project does not model:
- consciousness
- subjective experience
- suffering
- moral status
- life

All claims are limited to defined state variables, dynamics, and testable invariants.

## Core Equations

### Internal timebase
\[
\frac{d\tau}{dt}=\frac{1}{1+\Psi(t)}, \quad \Psi(t)=H(x_t)\cdot V(x_t)
\]

### Entropic memory decay
\[
\frac{dS}{d\tau}=-\lambda S
\]

### Reconsolidation on access
\[
S(\tau_k^+)=\min(S_{\max}, S(\tau_k^-)+\Delta_k)
\]

## Architecture (v0.2.x)

### Clock Layer
- `temporal_gradient.clock.chronos`
- Maps salience load \(\Psi\) to internal clock rate \(d\tau/dt\)
- Canonical mode enforces normalized salience bounds
- Explicit minimum clock floor prevents stalling

### Salience Layer
- `temporal_gradient.salience.pipeline`
- Rolling novelty scoring
- Keyword-based imperative/value scoring
- Canonical salience product \(\Psi = H\cdot V\)

### Memory Layer
- `temporal_gradient.memory.decay`
- Exponential decay over internal time
- Strength cap
- Diminishing reconsolidation
- Optional cooldown window

### Policy Layer
- `temporal_gradient.policies.compute_cooldown`
- `ComputeCooldownPolicy`
- `allows_compute(...)` gate
- This is a cooldown gate, not a compute-step allocator (`compute_budget` is a compatibility shim)
- Canonical policy surface is provided by the library, but enforcement is not globally auto-wired; each harness/runtime must instantiate and apply the policy gate explicitly

### Telemetry Layer
- `temporal_gradient.telemetry`
- `ChronometricVector`
- `validate_packet_schema` (canonical)
- `validate_packet` (compatibility alias)

## Minimal Canonical Usage (v0.2.x)
```python
import temporal_gradient as tg
from temporal_gradient.telemetry.schema import validate_packet_schema
from temporal_gradient.policies.compute_cooldown import ComputeCooldownPolicy

config = tg.load_config("tg.yaml")

clock = tg.clock.ClockRateModulator(
    base_dilation_factor=config.clock.base_dilation_factor,
    min_clock_rate=config.clock.min_clock_rate,
    salience_mode=config.clock.salience_mode,
)

salience = tg.salience.SaliencePipeline(
    tg.salience.RollingJaccardNovelty(),
    tg.salience.KeywordImperativeValue(),
)

cooldown = ComputeCooldownPolicy(cooldown_tau=config.policies.cooldown_tau)

text = "CRITICAL: SECURITY BREACH DETECTED."
sal = salience.evaluate(text)
clock.tick(psi=sal.psi, wall_delta=config.policies.event_wall_delta)

packet = tg.telemetry.ChronometricVector(
    wall_clock_time=config.policies.event_wall_delta,
    tau=clock.tau,
    psi=sal.psi,
    recursion_depth=0,
    clock_rate=clock.clock_rate_from_psi(sal.psi),
    H=sal.novelty,
    V=sal.value,
    memory_strength=0.0,
).to_packet()

validate_packet_schema(packet, salience_mode=config.clock.salience_mode)

if cooldown.allows_compute(elapsed_tau=clock.tau):
    print("Compute permitted.")
```

## Stable Import Surface (v0.2.x)
Canonical imports:
- `import temporal_gradient as tg`
- `tg.load_config(...)`
- `tg.clock`
- `tg.salience`
- `tg.memory`
- `tg.telemetry`

Policy:
- `from temporal_gradient.policies.compute_cooldown import ComputeCooldownPolicy`

Compatibility shims are retained for one release window but are not canonical.

## Telemetry Schema (canonical keys)
- `WALL_T`
- `TAU`
- `SALIENCE`
- `CLOCK_RATE`
- `MEMORY_S`
- `DEPTH`

Validation:
- `validate_packet_schema(...)` is canonical
- `validate_packet(...)` is compatibility alias
- In `legacy_density` mode, canonical packet validation is intentionally bypassed for backward compatibility

## Stability Constraints
- Clock rate has an explicit minimum floor.
- Reconsolidation boost is bounded and diminishes.
- Cooldown window prevents rapid repeated reinforcement.
- Canonical mode enforces salience normalization.
- Legacy density mode derives/clamps salience from entropy density and does not enforce canonical packet-schema strictness.

## Changelog
See `CHANGELOG.md` for the full release history, including `v0.2.0` canonicalization and policy formalization details.

## Testing
Run:
- `pytest -q`

CI uses the same command.

## License Notice
This repository is provided for educational and academic review.

Code examples illustrate structure only.

Execution of the code requires explicit written permission per LICENSE.

## Glossary
Canonical terms and deprecated terms are defined in `GLOSSARY.md`.

## Copyright
Copyright (c) 2026 Justin Shank.
