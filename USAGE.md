# How to Read the Logs
The Temporal Gradient outputs **Internal State Telemetry** rather than conventional debug lines. The goal is to show how internal time (τ) and memory retention respond to salience.

## 1. The clock-rate table
This table shows how the internal clock-rate is reparameterized by salience load (surprise × value).

```text
WALL_T   | TAU | INPUT                               | SALIENCE | CLOCK_RATE (dτ/dt)
============================================================================================
1.0      | 0.15       | "CRITICAL: SECURITY BREACH..."      | 1.5      | 0.15x
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
