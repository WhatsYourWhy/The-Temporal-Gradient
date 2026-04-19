# Architecture

## Data flow — single evaluation cycle

```
                         text input
                              │
           ┌──────────────────▼──────────────────┐
           │           SaliencePipeline          │
           │                                     │
           │  ┌────────────────┐  ┌────────────┐ │
           │  │  NoveltyScorer │  │ValueScorer │ │
           │  │   H ∈ [0, 1]   │  │ V ∈ [0, 1] │ │
           │  └───────┬────────┘  └──────┬─────┘ │
           │          └─────────┬────────┘       │
           │               Ψ = H × V             │
           └──────────────────┬──────────────────┘
                              │  Ψ ∈ [0, 1]
           ┌──────────────────▼───────────────────┐
           │          ClockRateModulator          │
           │                                      │
           │  rate = clamp(1 / (1 + α·Ψ),         │
           │               min_rate, max_rate)    │
           │  τ  += wall_delta × rate             │
           └──────────────────┬───────────────────┘
                              │  τ (internal time)
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌──────────────────┐   ┌────────────────────┐
│ DecayEngine   │   │ ComputeCooldown  │   │ChronometricVector  │
│ S·e^(−λΔτ)    │   │ allow if τ ≥ T_cd│   │ to_packet() → dict │
│ reconsolidate │   │                  │   │ validate_packet_   │
│ S=min(S_max,  │   │                  │   │   schema(packet)   │
│    S+ΔS)      │   │                  │   │                    │
└───────────────┘   └──────────────────┘   └────────────────────┘
```

## Layers

| Layer | Module | Responsibility |
|---|---|---|
| salience | `temporal_gradient.salience` | Score novelty H and value V from text; compute Ψ = H·V |
| clock | `temporal_gradient.clock` | Map Ψ to a clock rate; accumulate internal time τ |
| memory | `temporal_gradient.memory` | Encode, decay, and reconsolidate memory strength S over τ |
| policies | `temporal_gradient.policies` | Gate compute eligibility based on elapsed τ |
| telemetry | `temporal_gradient.telemetry` | Package state into a validated canonical packet |

## Public API

```python
import temporal_gradient as tg

tg.load_config(path)                      # -> TemporalGradientConfig
tg.clock.ClockRateModulator(...)          # τ accumulator
tg.salience.SaliencePipeline(novelty, value)
tg.salience.RollingJaccardNovelty(window_size=5)
tg.salience.KeywordImperativeValue(keywords=...)
tg.memory.DecayEngine(...)                # exponential decay + sweep
tg.memory.EntropicMemory(content, ...)
tg.policies.ComputeCooldownPolicy(cooldown_tau=...)
tg.telemetry.ChronometricVector(...).to_packet()
tg.telemetry.validate_packet_schema(packet, ...)
```

## Telemetry packet schema

Required keys: `SCHEMA_VERSION`, `WALL_T`, `TAU`, `SALIENCE`, `CLOCK_RATE`,
`MEMORY_S`, `DEPTH`.

Optional keys (emitted when present): `H`, `V`, `entropy_cost`,
`PROVENANCE_HASH`.

`to_packet()` returns a `dict`. `to_packet_json()` returns a JSON string.

## Stability constraints

- Clock rate has an explicit minimum floor (`min_clock_rate`).
- Reconsolidation is bounded by `s_max`.
- Cooldown window prevents rapid repeated reinforcement.
