# Temporal Gradient

A simulation framework for **salience-modulated internal time** and
**entropic memory decay**.

Given a stream of text events, Temporal Gradient computes:

- **Ψ (salience)** — novelty × value, scored per event.
- **τ (internal time)** — wall time reparameterized by Ψ. High-salience
  events slow the internal clock; low-salience events speed it up.
- **S (memory strength)** — per-item exponential decay over τ, with
  bounded reconsolidation on access.

Each event produces a validated telemetry packet suitable for offline
analysis, replay, or downstream policy gating.

> This is a dynamics framework. It does not model cognition,
> consciousness, or subjective experience. All claims are limited to
> the state variables, dynamics, and invariants defined in code.

## Install

```bash
git clone https://github.com/WhatsYourWhy/The-Temporal-Gradient
cd The-Temporal-Gradient
pip install -e ".[dev]"
```

Python 3.10+ is required. `PyYAML` is optional — a minimal fallback
parser is used when it's absent.

## Quickstart

```python
import temporal_gradient as tg
from temporal_gradient.policies.compute_cooldown import ComputeCooldownPolicy
from temporal_gradient.telemetry.schema import validate_packet_schema

config = tg.load_config("tg.yaml")

salience = tg.salience.SaliencePipeline(
    tg.salience.RollingJaccardNovelty(window_size=config.salience.window_size),
    tg.salience.KeywordImperativeValue(keywords=config.salience.keywords),
)
clock = tg.clock.ClockRateModulator(
    base_dilation_factor=config.clock.base_dilation_factor,
    min_clock_rate=config.clock.min_clock_rate,
    salience_mode=config.clock.salience_mode,
)
cooldown = ComputeCooldownPolicy(cooldown_tau=config.policies.cooldown_tau)

s = salience.evaluate("CRITICAL: security breach detected.")
clock.tick(psi=s.psi, wall_delta=config.policies.event_wall_delta)

packet = tg.telemetry.ChronometricVector(
    wall_clock_time=config.policies.event_wall_delta,
    tau=clock.tau,
    psi=s.psi,
    recursion_depth=0,
    clock_rate=clock.clock_rate_from_psi(s.psi),
    H=s.novelty,
    V=s.value,
    memory_strength=0.0,
).to_packet()

validate_packet_schema(packet, salience_mode=config.clock.salience_mode)

if cooldown.allows_compute(elapsed_tau=clock.tau):
    ...  # downstream work
```

## Core equations

```
dτ/dt = clamp( 1 / (1 + α·Ψ),  min_rate,  max_rate )
dS/dτ = −λ·S
S(τ⁺) = min(S_max, S(τ⁻) + Δ)      # reconsolidation on access
```

See [`docs/architecture.md`](docs/architecture.md) for the data-flow
diagram, layer responsibilities, and telemetry schema.

## Examples

```bash
python anomaly_poc.py                           # deterministic anomaly-stream PoC
python simulation_run.py                        # end-to-end simulation
python examples/embedding_novelty_replay_demo.py
python scripts/chronos_demo.py                  # minimal clock demo
```

## Tests

```bash
pytest
```

## Docs

- [`docs/architecture.md`](docs/architecture.md) — layers, data flow, packet schema
- [`docs/usage.md`](docs/usage.md) — extended usage and tuning
- [`docs/glossary.md`](docs/glossary.md) — terminology
- [`docs/safety.md`](docs/safety.md) — scope and safety constraints
- [`CHANGELOG.md`](CHANGELOG.md) — release history

## License

Source-available for review — see [LICENSE](LICENSE). Copyright (c)
2026 Justin Shank.
