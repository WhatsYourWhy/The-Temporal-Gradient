# Temporal Gradient Glossary (Neutral Terms)

This glossary defines the **only canonical terminology** for public documentation,
telemetry, and specifications in this repository.

| Canonical term | Notes |
| --- | --- |
| **Internal State Telemetry** | Logged outputs of internal \(\tau\), salience load, and memory strength. No claims about experience. |
| **Internal Time Accumulator (\(\tau\))** | Integrated internal coordinate driven by clock-rate reparameterization. Internal time unit; **not age**. |
| **Clock-rate Reparameterization** | Maps salience load \(\Psi\) to \(d\tau/dt\); implemented in the clock-rate modulator with explicit floor/clamp. |
| **Salience Load (Surprise×Value)** | Product of normalized novelty and imperative weight; drives clock-rate changes. |
| **High-salience event** | Input with outsized salience load; described operationally without moral framing. |
| **High-salience regime / Low-salience regime** | Processing contexts with high vs. low salience load. |
| **Pruned / Decayed below threshold** | Memory removed after falling below the retention threshold. |

## Deprecated terms (internal only; exclude from public demos/outputs)
Deprecated terms are preserved here strictly for legacy reference and migration. Do not surface these in public outputs.

| Deprecated term (do not use) | Canonical replacement |
| --- | --- |
| Subjective Experience Metrics | **Internal State Telemetry** |
| Subjective Time | **Internal Time Accumulator (\(\tau\))** |
| Wiltshire Transformation / Time Dilation | **Clock-rate Reparameterization** |
| Semantic Density | **Salience Load (Surprise×Value)** |
| Singularity / Trauma | **High-salience event** |
| Monk / Clerk | **High-salience regime / Low-salience regime** |
| Death of memory | **Pruned / Decayed below threshold** |

## Terminology Enforcement Rules
- Deprecated terms **must not** appear in:
  - public documentation
  - telemetry column names
  - filenames
  - CLI output
- Metaphorical labels may appear **only** in private comments or appendices.
- Core specifications, telemetry, and public docs must use **canonical replacements only**.
