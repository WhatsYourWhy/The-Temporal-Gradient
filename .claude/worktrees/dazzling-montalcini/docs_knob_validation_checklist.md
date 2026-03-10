# Knob Wiring Validation Checklist (Evidence-Only)

Use the PoC (`anomaly_poc.py`) with two configs per test and compare the produced JSON outputs.

## A) `policies.cooldown_tau` wiring

1. Run with `cooldown_tau: 0.0`.
2. Run with `cooldown_tau: 10.0`.
3. Compare `compute_allowed_count` and `write_log` length.

Expected wiring signal: larger cooldown should reduce compute-allowed writes.

## B) `memory.s_max` cap wiring

1. Set `memory.s_max: 0.6`.
2. Force encode with `memory.encode_threshold: 0.0`.
3. Inspect `write_log[*].strength`.

Expected wiring signal: no strength should exceed 0.6.

## C) `memory.decay_lambda` effect wiring

1. Keep `half_life` fixed.
2. Run once with `decay_lambda: 0.05`, then with `decay_lambda: 0.5`.
3. Compare `total_swept_survivors` / `total_swept_forgotten` at same `tau_final`.

Expected wiring signal: higher lambda should forget more memories by the final sweep.


## PoC summary schema

```json
{
  "total_swept_survivors": 12,
  "total_swept_forgotten": 38
}
```

Legacy aliases (`memories_alive`, `memories_forgotten`) may be present during deprecation but are not canonical.
