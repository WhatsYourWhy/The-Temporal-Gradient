# Temporal Gradient: Internal Timebase + Entropic Memory

## Status
- Current Version: 0.2.0
- License: See LICENSE (proprietary source-available; educational review only; **execution prohibited without permission**)

## Canonical Summary
Temporal Gradient is a simulation framework that models:
1) an **internal time accumulator** (\(\tau\)) whose rate is modulated by a **salience load** signal, and  
2) **memory strength** \(S\) that decays over internal time with optional **reconsolidation** on access.

It provides engineered control signals and **internal state telemetry** to inspect system behavior in simulation.

## What this is not (guardrails)
This project does **not** claim to model consciousness, subjective experience, suffering, moral status, or life.  
Metaphors (if any) belong in appendices only; the core specification is limited to definitions, units/ranges, dynamics, and falsification tests.

## Core Equations

### Internal timebase
\[
\frac{d\tau}{dt}=\frac{1}{1+\Psi(t)}, \quad \Psi(t)=H(x_t)\cdot V(x_t)
\]

### Entropic memory decay + reconsolidation
\[
\frac{dS}{d\tau}=-\lambda S,\quad
S(\tau_k^+)=\min(S_{\max}, S(\tau_k^-)+\Delta_k)
\]

### Symbols (units / ranges)
- \(t\): wall time (seconds)
- \(\tau\): internal time accumulator (internal time unit; dimensionless or “τ-units” by convention; **not age**)
- \(x_t\): input at wall time \(t\) (e.g., token/text/event identifier)
- \(H(x_t)\): surprise/novelty score (dimensionless, normalized; recommended \([0,1]\))
- \(V(x_t)\): imperative/value score (dimensionless, normalized; recommended \([0,1]\))
- \(\Psi(t)\): salience load (dimensionless; typically \([0,1]\) if \(H,V\in[0,1]\))
- \(S\): memory strength (dimensionless; bounded \([0, S_{\max}]\))
- \(\lambda\): decay rate per internal time (units: \(1/\tau\))
- \(\tau_k\): internal time of the \(k\)-th access event
- \(\Delta_k\): reconsolidation boost (dimensionless; bounded; typically diminishing with repeated access)
- \(S_{\max}\): maximum memory strength cap (dimensionless)

## Architecture
- **Clock-rate Reparameterization (`temporal_gradient/clock/chronos.py`)**  
  Maps salience load \(\Psi(t)\) to \(d\tau/dt\). Includes an explicit floor so \(\tau\) always advances.
- **Entropic Memory Decay (`temporal_gradient/memory/decay.py`)**  
  Applies exponential decay over \(\tau\) and reconsolidates on access with diminishing returns and optional cooldown.
- **Chronometric Vector (`temporal_gradient/telemetry/chronometric_vector.py`)**  
  Telemetry packet carrying wall time, internal \(\tau\), salience load, and recursion depth for downstream logging.
- **Simulation Examples (`simulation_run.py`, `twin_paradox.py`)**  
  Demonstrations comparing high-salience vs low-salience regimes and their effects on \(\tau\) and \(S\).

## Minimal usage (library-style)
```python
from temporal_gradient.clock.chronos import ClockRateModulator
from temporal_gradient.telemetry.chronometric_vector import ChronometricVector
from temporal_gradient.salience.pipeline import RollingJaccardNovelty, KeywordImperativeValue, SaliencePipeline

clock = ClockRateModulator(base_dilation_factor=1.0, min_clock_rate=0.05)
salience = SaliencePipeline(RollingJaccardNovelty(), KeywordImperativeValue())

text = "CRITICAL: SECURITY BREACH DETECTED."
sal = salience.evaluate(text)

# Use a fixed wall_delta to avoid relying on real time in a demo.
clock.tick(psi=sal.psi, wall_delta=1.0)

packet = ChronometricVector(
    wall_clock_time=1.0,
    tau=clock.tau,
    psi=sal.psi,
    recursion_depth=0,
    clock_rate=clock.clock_rate_from_psi(sal.psi),
    H=sal.novelty,
    V=sal.value,
    memory_strength=0.0,
).to_packet()

print(packet)
```


## API Stability (v0.2.x)
Stable import paths in the v0.2.x line:
- `import temporal_gradient as tg`
- `tg.clock`, `tg.memory`, `tg.salience`, `tg.telemetry`
- `tg.load_config(...)`

## Testing
Run the same command used by CI:
- `pytest -q`

## Stability Constraints
- **Clock floor:** \(d\tau/dt\) clamps to a minimum value so \(\tau\) cannot stall under extreme salience loads.
- **Reconsolidation diminishing returns:** \(\Delta_k\) decreases as access count rises to avoid runaway reinforcement.
- **Cooldown (optional):** Reconsolidation boosts can be skipped within a configurable cooldown window.

## Telemetry Schema (key columns)
- **WALL_T**: wall time (seconds)
- **TAU**: internal time accumulator \(\tau\)
- **SALIENCE**: \(\Psi(t)\) (surprise×value)
- **CLOCK_RATE**: \(d\tau/dt\)
- **MEMORY_S**: current memory strength \(S\)
- **DEPTH**: recursion depth (if used)

Some CLI tables include a prompt column for readability; it is not part of the packet payload.

## Review-Only Notice
Per LICENSE, this repository is provided for educational and academic review.  
**Running/executing the code is prohibited without explicit written permission from the Author.**

## Glossary
Canonical terms and deprecated terms are defined in **GLOSSARY.md**. Public docs, telemetry headers, and filenames should use canonical terms only.

## Copyright
Copyright (c) 2026 Justin Shank.
