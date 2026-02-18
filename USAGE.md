# How to Read the Logs
The Temporal Gradient outputs **Internal State Telemetry** rather than conventional debug lines. The goal is to show how internal time (τ) and memory retention respond to salience.
Canonical module references and compatibility shims are listed in [`docs/CANONICAL_SURFACES.md`](docs/CANONICAL_SURFACES.md).


## 0. Telemetry contract (canonical vs extended)
The telemetry packet is versioned and split into **required** vs **optional** keys.
For canonical symbol/module ownership (including telemetry validators and compatibility aliases), see [`docs/CANONICAL_SURFACES.md`](docs/CANONICAL_SURFACES.md).

**Required keys (canonical schema):**
- `SCHEMA_VERSION`
- `WALL_T`
- `TAU`
- `SALIENCE`
- `CLOCK_RATE`
- `MEMORY_S`
- `DEPTH`

**Optional keys (extended telemetry):**
- `H`
- `V`

`CLOCK_RATE` and `MEMORY_S` are always present in canonical packets. If unset at construction time, serialization currently emits numeric fallbacks (`0.0`), not `null`.

`SCHEMA_VERSION` policy is strict: canonical serialization must emit exactly `"1.0"`. For migration input only, validators accept legacy `"1"` and normalize it to `"1.0"` on canonical re-serialization.

CLI tables should print **only canonical columns** by default (`WALL_T`, `TAU`, `SALIENCE`, `CLOCK_RATE`, `MEMORY_S`, `DEPTH`). Extended fields like `H` and `V` are intended for verbose/debug output, not the base schema. Demo scripts may also include an `INPUT` column for readability; it is not part of the canonical packet schema.

### Legacy mode compatibility (`legacy_density`)
`legacy_density` is a migration-only mode. It is not the canonical telemetry contract.

Behavior summary:
- Salience is derived from entropy density and clamped into `[0,1]`.
- Canonical telemetry schema strictness is intentionally bypassed.

Compatibility entry points referenced in this section are cataloged in [`docs/CANONICAL_SURFACES.md`](docs/CANONICAL_SURFACES.md).

Packet-shape examples:

Canonical packet (preferred):
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

Legacy compatibility packet (allowed only in `legacy_density` mode):
```json
{
  "WALL_T": 1.0,
  "TAU": 0.15,
  "SALIENCE": 0.9,
  "DEPTH": 0
}
```

See `docs/CANONICAL_VS_LEGACY.md` for the full migration guidance and deprecation horizon.


## 1. The clock-rate table
This table shows how the internal clock-rate is reparameterized by salience load (surprise × value).

```text
WALL_T   | TAU | INPUT                               | SALIENCE | CLOCK_RATE (dτ/dt)
============================================================================================
1.0      | 0.15       | "CRITICAL: SECURITY BREACH..."      | 0.9      | 0.15x
2.0      | 1.15       | "Checking local weather..."         | 0.4      | 1.00x
```

Key metrics:
- **WALL_T:** External time elapsed (seconds).
- **TAU:** Internal time accumulator after clock-rate reparameterization.
- **SALIENCE:** Surprise×value score from the valuator.
- **CLOCK_RATE (dτ/dt):** Internal clock multiplier after salience modulation.

Interpretation:
- A CLOCK RATE below 1.0x means the internal clock slowed to process a high-load event (reduced internal clock rate), not “bullet time.”
- 1.0x indicates the baseline clock rate.

## 2. The entropy sweep (memory audit)
At the end of the simulation, the decay engine reports which memories stayed above the retention threshold.

```
>>> MEMORY AUDIT (Post-Simulation)
[ALIVE] Strength: 1.42 | Content: "My name is Sentinel."
[PRUNED ] Content: "Rain. Water. Liquid."
```

- **ALIVE:** The memory stayed above the pruning threshold because it started with high salience or was reconsolidated.
- **PRUNED:** The memory decayed below the threshold and was pruned.

## 3. Configuration hints
Adjust these parameters in `simulation_run.py` and the supporting modules to shape the simulation (canonical policy surface: `temporal_gradient.policies.compute_cooldown`; compatibility shim: `temporal_gradient.policies.compute_budget`):
- `base_dilation_factor` and `min_clock_rate` in `ClockRateModulator` to control the clock-rate floor and sensitivity to salience load.
- `half_life` in `DecayEngine` to control decay speed.
- Reconsolidation cooldowns and diminishing returns in `EntropicMemory.reconsolidate` to avoid runaway reinforcement.

## 4. Salience components (H/V)
The salience pipeline currently decomposes **H (novelty)** and **V (value)** into two concrete components with constrained inputs and normalized outputs.

### RollingJaccardNovelty (H)
- **Operational definition:** Compute tokens from the incoming text, compare against a rolling history window, and take `1 - max_jaccard_similarity` across the window. The history stores the most recent **5** token sets (default `window_size=5`).
- **Tokenization:** Lowercase and split on the regex pattern `[a-z0-9']+` to form a unique token set.
- **Allowed inputs:** Current message text **plus** the internal rolling history (no external context).
- **Normalization:** Jaccard similarity is in `[0,1]`, so novelty output is normalized to `[0,1]`.
- **Swap-friendly note:** This component can be replaced with an embedding-based novelty scorer, provided the output stays normalized to `[0,1]` and only uses the current text plus an internal memory of prior text.

### KeywordImperativeValue (V)
- **Operational definition:** Count keyword hits in the current text, then compute `min(max_value, base_value + hit_value * hits)`.
- **Default keyword list:** `["must", "never", "critical", "always", "don't", "stop", "urgent"]`.
- **Default weights:** `base_value=0.1`, `hit_value=0.2`, `max_value=1.0`.
- **Allowed inputs:** Current message text **only** (no access to memory or external context).
- **Normalization:** Value output is clamped to `[0,1]` via `max_value`.

Both components are expected to output normalized scores in `[0,1]`. The combined salience `psi = H × V` inherits the same normalization range.
