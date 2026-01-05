# Temporal Gradient Glossary (Neutral Terms)

| Previous term | Replacement | Notes |
| --- | --- | --- |
| Subjective Experience Metrics | **Internal State Telemetry** | Logged outputs of internal τ, salience load, and memory status. |
| Subjective Time / Agent's Age | **Internal Time Accumulator (τ)** | Integrated internal time coordinate driven by the clock-rate modulator. |
| Wiltshire Transformation / Time Dilation | **Clock-rate Reparameterization** | Maps salience load to dτ/dt; implemented in `ClockRateModulator`. |
| Semantic Density | **Salience Load / Surprise×Value Score** | Product of novelty and imperative weight; drives clock-rate changes. |
| Singularity / Trauma | **High-load event** | Input with outsized salience load; documented without moral framing. |
| Monk / Clerk | **High-load regime / Low-load regime** | Processing contexts with high vs. low salience. |
| Death of memory | **Pruned / Decayed below threshold** | Memory removed after falling under the retention threshold. |

Metaphorical labels may be used in comments or appendices only. The core spec, telemetry, and public docs should use the replacement terms above.
