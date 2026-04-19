# Usage

Temporal Gradient outputs **internal state telemetry** — packets that show
how internal time (τ) and memory retention respond to salience. This guide
covers the packet contract, configuration knobs, and the salience
components shipped by default.

See [`architecture.md`](architecture.md) for the data-flow diagram and
public API surface.

## Telemetry packet contract

- `to_packet()` returns a `dict` for schema checks and in-memory processing.
- `to_packet_json()` returns a JSON string for transport or logging.

**Required keys:** `SCHEMA_VERSION`, `WALL_T`, `TAU`, `SALIENCE`,
`CLOCK_RATE`, `MEMORY_S`, `DEPTH`.

**Optional keys:** `H`, `V`, `entropy_cost`, `PROVENANCE_HASH`.

`SCHEMA_VERSION` must be exactly `"1.0"`. `CLOCK_RATE` and `MEMORY_S` fall
back to `0.0` when unset at construction time.

### Example packet

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

### Round-trip

```python
import temporal_gradient as tg
from temporal_gradient.telemetry.schema import validate_packet_schema

packet = tg.telemetry.ChronometricVector(
    wall_clock_time=1.0,
    tau=0.5,
    psi=0.4,
    recursion_depth=0,
    clock_rate=0.71,
    memory_strength=0.2,
).to_packet()

validate_packet_schema(packet)
```

## Reading clock-rate output

```text
WALL_T | TAU  | INPUT                          | SALIENCE | CLOCK_RATE
==============================================================================
1.0    | 0.15 | "CRITICAL: SECURITY BREACH..." | 0.9      | 0.15
2.0    | 1.15 | "Checking local weather..."    | 0.4      | 1.00
```

- **WALL_T** — external time elapsed (seconds).
- **TAU** — internal time accumulator after clock-rate reparameterization.
- **SALIENCE** — Ψ = H × V from the salience pipeline.
- **CLOCK_RATE** — dτ/dt. Below 1.0 means the internal clock slowed to
  process a high-load event. 1.0 is the baseline.

## Memory audit (post-simulation)

```
[ALIVE]  Strength: 1.42 | Content: "My name is Sentinel."
[PRUNED] Content: "Rain. Water. Liquid."
```

- **ALIVE** — above the pruning threshold.
- **PRUNED** — decayed below the threshold and removed by the entropy sweep.

## Configuration knobs

- `clock.base_dilation_factor`, `clock.min_clock_rate` — clock-rate floor
  and sensitivity to salience load.
- `memory.half_life`, `memory.decay_lambda` — decay speed.
- `memory.s_max`, `memory.initial_strength_max` — reconsolidation bounds.
- `policies.cooldown_tau` — compute eligibility window on internal time.

## Salience components

### RollingJaccardNovelty (H)

Tokenize the incoming text, compare against a rolling history window of
recent token sets, return `1 - max_jaccard_similarity`. Default
`window_size=5`. Tokenization: lowercase, split on `[a-z0-9']+`.

Output is in `[0, 1]`. Swap-friendly: any novelty scorer that takes the
current text plus internal history and returns a normalized score works.

### KeywordImperativeValue (V)

Count keyword hits in the current text, return
`min(max_value, base_value + hit_value * hits)`.

- Default keywords: `["must", "never", "critical", "always", "don't",
  "stop", "urgent"]`.
- Default weights: `base_value=0.1`, `hit_value=0.2`, `max_value=1.0`.

Output is clamped to `[0, 1]`. The combined salience `Ψ = H × V`
inherits the same range.
