# Temporal Gradient

**An engine that gives software a sense of its own time.**

Salience-modulated internal time and entropic memory decay for adaptive Python systems.

[![pytest](https://github.com/WhatsYourWhy/The-Temporal-Gradient/actions/workflows/pytest.yml/badge.svg)](https://github.com/WhatsYourWhy/The-Temporal-Gradient/actions/workflows/pytest.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![Status: Beta](https://img.shields.io/badge/status-beta-orange.svg)](CHANGELOG.md)

---

## Why this exists

Every running program has a clock, but almost none of them have a *tempo*.
They tick at whatever rate the CPU allows, and every tick weighs the same.
A flood of low-stakes events and a single critical signal pass through the
same pipe at the same speed, occupying the same slice of attention. This
is fine for most software. It is conspicuously wrong for any software that
is supposed to *think*.

Temporal Gradient unifies two questions that production agent systems
usually answer with two unrelated layers — *when should the system do
expensive work?* and *what should it remember?* — under a single signal:
**salience**. High-salience events slow the internal clock and reinforce
memory. Quiet stretches accelerate the clock and let stale items decay.
One model. One knob. Adaptive tempo.

## See it in 30 seconds

```bash
pip install -e ".[dev]"
python examples/showcase.py
```

A noisy 20-event stream with one critical signal buried at index 6:

```
NAIVE LRU (capacity=5) — retained:
    request handled ok
    cache hit ratio nominal
    request handled ok
    disk usage at 44 percent
    request handled ok

  critical signal retained: False

TEMPORAL GRADIENT (salience-decayed) — retained:
  * [S=0.20] CRITICAL auth service unreachable must page oncall

  critical signal retained: True
```

A flat LRU evicts the signal with routine traffic. Temporal Gradient
retains it because salience drove the encoding strength and the routine
repeats decayed along internal time.

## Install

```bash
git clone https://github.com/WhatsYourWhy/The-Temporal-Gradient
cd The-Temporal-Gradient
pip install -e ".[dev]"
```

Python 3.10+. `PyYAML` is optional — a minimal fallback parser is used
when it's absent.

## How it works

```
                         text input
                              │
           ┌──────────────────▼──────────────────┐
           │           SaliencePipeline          │
           │   H = novelty       V = value       │
           │            Ψ = H × V                │
           └──────────────────┬──────────────────┘
                              │  Ψ ∈ [0, 1]
           ┌──────────────────▼───────────────────┐
           │          ClockRateModulator          │
           │  dτ/dt = clamp(1/(1+α·Ψ), min, max)  │
           │  τ  += wall_delta × dτ/dt            │
           └──────────────────┬───────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   DecayEngine         ComputeCooldown       ChronometricVector
   S(τ⁺)=S·e^(−λΔτ)    allow if τ ≥ T_cd     → validated packet
   reconsolidate       (gated compute)       (telemetry out)
```

Three state variables, governed by one input signal:

- **Ψ (salience)** — `H × V`. Novelty × value, scored per event.
- **τ (internal time)** — `dτ/dt = clamp(1 / (1 + α·Ψ), min, max)`. High Ψ slows the clock.
- **S (memory strength)** — `dS/dτ = −λ·S`. Decay along internal time, bounded reconsolidation on access.

See [`docs/architecture.md`](docs/architecture.md) for the full data flow,
layer responsibilities, and packet schema.

## Quickstart

```python
import temporal_gradient as tg
from temporal_gradient.policies.compute_cooldown import ComputeCooldownPolicy

config = tg.load_config("tg.yaml")

salience = tg.salience.SaliencePipeline(
    tg.salience.RollingJaccardNovelty(window_size=config.salience.window_size),
    tg.salience.KeywordImperativeValue(keywords=config.salience.keywords),
)
clock = tg.clock.ClockRateModulator(
    base_dilation_factor=config.clock.base_dilation_factor,
    min_clock_rate=config.clock.min_clock_rate,
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

if cooldown.allows_compute(elapsed_tau=clock.tau):
    ...  # downstream work
```

### Example telemetry packet

Every evaluation cycle emits a validated packet for offline analysis,
replay, or downstream policy gating:

```json
{
  "SCHEMA_VERSION": "1.0",
  "WALL_T": 1.0,
  "TAU": 0.15,
  "SALIENCE": 0.9,
  "CLOCK_RATE": 0.15,
  "MEMORY_S": 0.8,
  "DEPTH": 0,
  "H": 0.9,
  "V": 1.0
}
```

## What this is not

- **Not a cognitive model.** The dynamics make no claim about how minds
  work, consciousness, or subjective experience. All claims are limited
  to the state variables and equations defined in the code.
- **Not a product.** No integration with any real event source, no
  persistence layer for the memory store, no deployed callers. The
  default salience scorers (rolling Jaccard for novelty, keyword counts
  for value) are deliberate placeholders. Real use requires a domain-
  appropriate scorer — typically embedding-based novelty.
- **Not a replacement for vector databases.** Temporal Gradient
  complements semantic recall; it doesn't replace it. Pair the two.

## How it compares

| Approach | Importance signal | Memory model | Tempo |
|---|---|---|---|
| Rate limiter | none | none | flat |
| LRU / bounded queue | recency | recency-only eviction | flat |
| Vector DB (mem0, Letta, Zep) | semantic similarity | similarity-ranked recall | flat |
| **Temporal Gradient** | **salience (novelty × value)** | **strength decays along τ; salience reinforces** | **adaptive — τ dilates under load** |

Temporal Gradient is positioned *upstream* of recall — it shapes what
gets encoded and how long it survives, before any similarity search runs.

## Examples

```bash
python examples/showcase.py                     # the 30-second case (start here)
python examples/anomaly_detection.py            # deterministic anomaly-stream PoC
python examples/simulation.py                   # end-to-end simulation
python examples/embedding_novelty_replay_demo.py
python scripts/chronos_demo.py                  # minimal clock-only demo
```

## Tests

```bash
pytest
```

CI runs the full suite on Python 3.10, 3.11, and 3.12.

## Docs

- [`docs/architecture.md`](docs/architecture.md) — layers, data flow, packet schema
- [`docs/usage.md`](docs/usage.md) — extended usage and tuning
- [`docs/glossary.md`](docs/glossary.md) — terminology
- [`docs/safety.md`](docs/safety.md) — scope and safety constraints
- [`CHANGELOG.md`](CHANGELOG.md) — release history
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to contribute

## License

[MIT](LICENSE). Copyright (c) 2026 Justin Shank.
