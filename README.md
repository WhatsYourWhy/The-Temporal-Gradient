# Temporal Gradient: Internal Timebase + Entropic Memory

## Status
- Version: 0.2.0
- License: Proprietary source-available (review only; execution requires permission — see LICENSE)

## Contributor Onboarding
- New contributors: start with `docs/DAY1_CONTRIBUTOR_MAP.md` for subsystem ownership, required test commands, first-PR templates, and canonical-vs-legacy gotchas.

## Canonical Summary
Temporal Gradient is a simulation framework modeling:
1. an internal time accumulator \(\tau\) whose rate is modulated by salience load \(\Psi\), and
2. a memory strength variable \(S\) that decays over internal time and may reconsolidate on access.

The system exposes engineered control signals and structured telemetry for simulation inspection.

This is a dynamics framework, not a cognitive model.

## Guardrails
This project does not model:
- consciousness
- subjective experience
- suffering
- moral status
- life

All claims are limited to defined state variables, dynamics, and testable invariants.

## Core Equations

### Internal timebase
\[
\frac{d\tau}{dt}=\frac{1}{1+\texttt{base\_dilation\_factor}\cdot\Psi(t)}, \quad \Psi(t)=H(x_t)\cdot V(x_t)
\]

In code, this is implemented by `ClockRateModulator._clock_rate_from_validated_psi(...)` as:
`clock_rate = 1 / (1 + psi * base_dilation)` with min/max clamping.
To map docs to constructor names in `temporal_gradient/clock/chronos.py`:
- `base_dilation_factor` (constructor arg) is validated and stored as `self.base_dilation`.
- `psi` is the salience load input used by `clock_rate_from_psi(psi)` and `tick(psi=...)`.
- `min_clock_rate` and `max_clock_rate` bound the final clock rate.

Default factor assumption: `base_dilation_factor=1.0`.

### Entropic memory decay
\[
\frac{dS}{d\tau}=-\lambda S
\]

### Reconsolidation on access
\[
S(\tau_k^+)=\min(S_{\max}, S(\tau_k^-)+\Delta_k)
\]

## Architecture (v0.2.x)

Canonical module map: see [`docs/CANONICAL_SURFACES.md`](docs/CANONICAL_SURFACES.md).

The architecture uses canonical package layers for clock, salience, memory, policies, and telemetry.

For canonical-vs-legacy behavior, compatibility scope, and removal timeline, see [`docs/CANONICAL_VS_LEGACY.md`](docs/CANONICAL_VS_LEGACY.md).

### Data-Flow Diagram — Single Evaluation Cycle

```
                         text input
                              │
           ┌──────────────────▼──────────────────┐
           │           SaliencePipeline            │
           │                                       │
           │  ┌────────────────┐  ┌─────────────┐ │
           │  │  NoveltyScorer │  │ ValueScorer │ │
           │  │   H ∈ [0, 1]  │  │  V ∈ [0, 1] │ │
           │  └───────┬────────┘  └──────┬──────┘ │
           │          └─────────┬─────────┘        │
           │               Ψ = H × V               │
           └──────────────────┬──────────────────-─┘
                              │  Ψ (psi) ∈ [0, 1]
           ┌──────────────────▼───────────────────┐
           │          ClockRateModulator            │
           │                                       │
           │  rate = clamp(1 / (1 + α·Ψ),         │
           │               min_rate, max_rate)      │
           │  τ  += wall_delta × rate              │
           └──────────────────┬───────────────────┘
                              │  τ (internal time)
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                      ▼
┌───────────────┐   ┌──────────────────┐   ┌────────────────────┐
│ DecayEngine   │   │ComputeCooldown   │   │ChronometricVector  │
│               │   │Policy            │   │(Telemetry)         │
│ S(τ) decay:   │   │                  │   │                    │
│  S·e^(−λΔτ)  │   │ allow if τ ≥ T_cd│   │ to_packet() → dict │
│               │   │                  │   │ validate_packet_   │
│ reconsolidate │   │                  │   │   schema(packet)   │
│  S = min(S_max│   │                  │   │                    │
│    , S + ΔS)  │   │                  │   │                    │
└───────────────┘   └──────────────────┘   └────────────────────┘
       │                    │                        │
       └────────────────────┴────────────────────────┘
                   structured telemetry / policy gate
```

**Layer responsibilities:**
- `tg.salience` — scores novelty (H) and value (V) from text; computes Ψ = H × V
- `tg.clock` — maps Ψ to a clock rate via the dilation equation; accumulates internal time τ
- `tg.memory` — governs memory encoding, exponential decay, and reconsolidation over τ
- `tg.policies` — gates compute eligibility based on elapsed τ
- `tg.telemetry` — packages all state into a validated canonical packet

## Minimal Canonical Usage (v0.2.x)
```python
import temporal_gradient as tg
from temporal_gradient.telemetry.schema import validate_packet_schema
from temporal_gradient.policies.compute_cooldown import ComputeCooldownPolicy

config = tg.load_config("tg.yaml")

clock = tg.clock.ClockRateModulator(
    base_dilation_factor=config.clock.base_dilation_factor,
    min_clock_rate=config.clock.min_clock_rate,
    salience_mode=config.clock.salience_mode,
)

salience = tg.salience.SaliencePipeline(
    tg.salience.RollingJaccardNovelty(),
    tg.salience.KeywordImperativeValue(),
)

cooldown = ComputeCooldownPolicy(cooldown_tau=config.policies.cooldown_tau)

text = "CRITICAL: SECURITY BREACH DETECTED."
sal = salience.evaluate(text)
clock.tick(psi=sal.psi, wall_delta=config.policies.event_wall_delta)

packet = tg.telemetry.ChronometricVector(
    wall_clock_time=config.policies.event_wall_delta,
    tau=clock.tau,
    psi=sal.psi,
    recursion_depth=0,
    clock_rate=clock.clock_rate_from_psi(sal.psi),
    H=sal.novelty,
    V=sal.value,
    memory_strength=0.0,
).to_packet()  # canonical: returns a dict packet mapping

validate_packet_schema(packet, salience_mode=config.clock.salience_mode)

if cooldown.allows_compute(elapsed_tau=clock.tau):
    print("Compute permitted.")
```

## Stable Import Surface (v0.2.x)
Canonical imports:
- `import temporal_gradient as tg`
- `tg.load_config(...)`
- `tg.clock`
- `tg.salience`
- `tg.memory`
- `tg.telemetry`

Policy:
- `from temporal_gradient.policies.compute_cooldown import ComputeCooldownPolicy`

See [`docs/CANONICAL_SURFACES.md`](docs/CANONICAL_SURFACES.md) for the canonical vs compatibility map.
For shim-by-shim replacements and copy/paste migration examples, see [`docs/MIGRATION_SHIMS.md`](docs/MIGRATION_SHIMS.md).
For lifecycle policy and release-labeled deprecation timing, see [`docs/CANONICAL_VS_LEGACY.md`](docs/CANONICAL_VS_LEGACY.md).

## Telemetry Schema (canonical keys)
Canonical telemetry is validated against the required schema keys and should be the default for all new integrations.

### Packet API contract
- `to_packet()` => returns a Python `dict` mapping for schema validation and in-memory processing.
- `to_packet_json()` => returns a JSON `str` for transport, storage, or logging contexts.
- Do not call `json.loads(to_packet())`; `to_packet()` is already the structured mapping.

- `SCHEMA_VERSION`
- `WALL_T`
- `TAU`
- `SALIENCE`
- `CLOCK_RATE`
- `MEMORY_S`
- `DEPTH`

`validate_packet_schema(...)` is the canonical validator; `validate_packet(...)` remains a compatibility alias.
`ChronometricVector.to_packet()` returns the canonical packet mapping (`dict`) and emits canonical `SCHEMA_VERSION` (`"1.0"`); use `to_packet_json()` only when serialized JSON text is explicitly required.

For complete canonical-vs-legacy mode behavior and lifecycle policy, see [`docs/CANONICAL_VS_LEGACY.md`](docs/CANONICAL_VS_LEGACY.md).

## Stability Constraints
- Clock rate has an explicit minimum floor.
- Reconsolidation boost is bounded and diminishes.
- Cooldown window prevents rapid repeated reinforcement.
- Canonical-vs-legacy enforcement details live in [`docs/CANONICAL_VS_LEGACY.md`](docs/CANONICAL_VS_LEGACY.md).


## Documentation Lifecycle
- Active planning and implementation docs remain at the repository root for visibility.
- Completed validation reports are archived under `docs/archive/`:
  - `docs/archive/AUDIT_REPORT.md`
  - `docs/archive/poc_validation_report.md`

## Changelog
See `CHANGELOG.md` for the full release history, including `v0.2.0` canonicalization and policy formalization details.



## Chronos Demo
Run:
- `python scripts/chronos_demo.py`

For fast smoke checks:
- `python scripts/chronos_demo.py --sleep-seconds 0`

## Deterministic Embedding Replay Demo
Run:
- `python examples/embedding_novelty_replay_demo.py`

Expected behavior:
- The script uses a fixed event list and deterministic fake embeddings cached in local JSON files under `examples/.cache/` (no model downloads).
- It runs the salience pipeline in deterministic mode, emits packet summaries including `PROVENANCE_HASH`, resets the pipeline, and reruns with an exact output-equality assertion.
- It then changes novelty configuration (`window_size`) and reruns; at least one `PROVENANCE_HASH` index must change, demonstrating replay provenance sensitivity to config changes.

## Testing
Run:
- `pytest -q`
- `python scripts/check_docs_consistency.py`

Latest document-review validation run (local):
- `pytest -q` (run locally to see current pass count)

CI uses the same command.

### Documentation consistency guard
Run `python scripts/check_docs_consistency.py` before opening a PR to catch drift across `README.md`, `USAGE.md`, and `TASK_PROPOSALS.md` for canonical import guidance and required canonical-reference links.

## License Notice
This repository is provided for educational and academic review.

Code examples illustrate structure only.

Execution of the code requires explicit written permission per LICENSE.

## Glossary
Canonical terms and deprecated terms are defined in `GLOSSARY.md`.

## Copyright
Copyright (c) 2026 Justin Shank.
