# Temporal Gradient: Internal Timebase + Entropic Memory

## Status
**Current Version:** 0.1.0  
**License:** See `LICENSE` (source available for educational review)

---

## What this is (canonical)
> The Temporal Gradient is a simulation framework that models (1) an internal time coordinate whose rate is modulated by a salience signal, and (2) memory strength that decays over internal time with optional reconsolidation upon access.

Core equations:

\[
\frac{d\tau}{dt}=\frac{1}{1+\Psi(t)},\quad \Psi(t)=H(x_t)\,V(x_t)
\]

\[
\frac{dS}{d\tau}=-\lambda S,\quad S(\tau_k^+)=\min(S_{\max}, S(\tau_k^-) + \Delta_k)
\]

## What this is not (guardrails)
> This project does not claim to model consciousness, subjective experience, suffering, or life. It provides engineered control signals (clock-rate and memory retention) plus telemetry to inspect their effects in simulation.

Metaphors live in an appendix only; the core specification is limited to definitions, units/ranges, dynamics, and falsification tests.

---

## Executive summary
- **What it does:** Simulates an internal time accumulator (τ) whose rate depends on salience, plus memory strength that decays over τ with reconsolidation when accessed.
- **Why it is useful:** Lets you test how prioritization and memory retention respond to changing input salience without invoking identity or consciousness claims.
- **How to configure:** Adjust clock-rate modulation (`base_dilation_factor`, `min_clock_rate`) and decay controls (`half_life`, reconsolidation cooldowns/boosts) in the Python modules.
- **What it does not claim:** No consciousness, no morality, no physical cosmology; it is engineered telemetry and control signals only.

---

## Architecture
- **Clock-rate reparameterization (`chronos_engine.py`)** — Modulates the internal time accumulator based on salience load (surprise × value). Exposes a floor so τ always advances.
- **Entropic memory decay (`entropic_decay.py`)** — Applies exponential decay over internal time and reconsolidates with diminishing returns and cooldowns to prevent runaway reinforcement.
- **Chronometric vector (`chronometric_vector.py`)** — Standard telemetry packet carrying wall time, internal τ, salience load, and recursion depth for downstream logging.
- **Simulation examples (`simulation_run.py`, `twin_paradox.py`)** — Show how high-load vs. low-load inputs change internal time accumulation and memory retention.

---

## Stability constraints
- **Clock floor:** The clock-rate multiplier clamps at a minimum value so τ cannot stall even under extreme salience loads.
- **Reconsolidation diminishing returns:** Each reconsolidation boost shrinks as access count rises to avoid obsession-like growth.
- **Cooldown for boosts (optional):** Reconsolidation boosts are skipped when accesses occur within a configurable cooldown window.

---

## Usage
1. Clone and install dependencies (if any are added later).
2. Run the simulations:
   - `python simulation_run.py` — Streams inputs, prints internal state telemetry, and audits memory decay.
   - `python twin_paradox.py` — Compares high-load vs. low-load processing to illustrate clock-rate modulation.

Key telemetry columns:
- **WALL T:** External time in seconds.
- **INTERNAL τ:** Internal time accumulator.
- **INPUT:** The processed text.
- **PRIORITY:** Surprise×value score from `CodexValuator`.
- **CLOCK RATE (dτ/dt):** Clock-rate multiplier after reparameterization.

---

## Glossary (neutral terms)
- **Internal State Telemetry** (formerly “Subjective Experience Metrics”): The log of τ, salience load, and memory outcomes.
- **Internal Time Accumulator (τ)** (formerly “Subjective Time / Agent’s Age”): The integrated internal time coordinate.
- **Clock-rate Reparameterization** (formerly “Wiltshire Transformation / Time Dilation”): Mapping from salience load to dτ/dt.
- **Salience Load / Surprise×Value Score** (formerly “Semantic Density”): Multiplicative signal combining novelty and imperative weight.
- **High-load event** (formerly “Singularity / Trauma”): Input with outsized salience load.
- **High-load regime / Low-load regime** (formerly “Monk / Clerk”): Processing contexts with high vs. low salience.
- **Pruned / Decayed below threshold** (formerly “Death of memory”): Memory removed after falling under the retention threshold.

Extended definitions live in `GLOSSARY.md` for quick reference.

---

## Safety and license
Copyright (c) 2026 Justin [WhatsYourWhy].

This repository is provided for educational and academic review. See `LICENSE` for terms.
