# Temporal Gradient Glossary (Neutral Terms)

This glossary defines the **only canonical terminology** for public documentation,
telemetry, and specifications in this repository.

| Deprecated term (do not use) | Canonical replacement | Notes |
| --- | --- | --- |
| Subjective Experience Metrics | **Internal State Telemetry** | Logged outputs of internal \(\tau\), salience load, and memory strength. No claims about experience. |
| Subjective Time | **Internal Time Accumulator (\(\tau\))** | Integrated internal coordinate driven by clock-rate reparameterization. Internal time unit; **not age**. |
| Wiltshire Transformation / Time Dilation | **Clock-rate Reparameterization** | Maps salience load \(\Psi\) to \(d\tau/dt\); implemented in the clock-rate modulator with explicit floor/clamp. |
| Semantic Density | **Salience Load (Surprise×Value)** | Product of normalized novelty and imperative weight; drives clock-rate changes. |
| Singularity / Trauma | **High-salience event** | Input with outsized salience load; described operationally without moral framing. |
| Monk / Clerk | **High-salience regime / Low-salience regime** | Processing contexts with high vs. low salience load. |
| Death of memory | **Pruned / Decayed below threshold** | Memory removed after falling below the retention threshold. |

## Terminology Enforcement Rules
- Deprecated terms **must not** appear in:
  - public documentation
  - telemetry column names
  - filenames
  - CLI output
- Metaphorical labels may appear **only** in private comments or appendices.
- Core specifications, telemetry, and public docs must use **canonical replacements only**.
