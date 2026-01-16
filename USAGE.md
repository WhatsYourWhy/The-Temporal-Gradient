# How to Read the Logs
The Temporal Gradient outputs **Internal State Telemetry** rather than conventional debug lines. The goal is to show how internal time (τ) and memory retention respond to salience.

## 0. Telemetry contract (canonical vs extended)
The telemetry packet is versioned and split into **required** vs **optional** keys.

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

CLI tables should print **only canonical columns** by default (`WALL_T`, `TAU`, `SALIENCE`, `CLOCK_RATE`, `MEMORY_S`, `DEPTH`). Extended fields like `H` and `V` are intended for verbose/debug output, not the base schema.

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
[DEAD ] Content: "Rain. Water. Liquid."
```

- **ALIVE:** The memory stayed above the pruning threshold because it started with high salience or was reconsolidated.
- **DEAD:** The memory decayed below the threshold and was pruned.

## 3. Configuration hints
Adjust these parameters in `simulation_run.py` and the supporting modules to shape the simulation:
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
