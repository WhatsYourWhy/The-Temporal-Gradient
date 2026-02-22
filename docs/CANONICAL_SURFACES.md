# Canonical Surfaces

This document is the source-of-truth mapping for canonical module surfaces, public symbols, and compatibility aliases/shims.

## clock
- **Canonical module path:** `temporal_gradient.clock.chronos`
- **Canonical public symbols:** `ClockRateModulator`
- **Known compatibility aliases/shims (intentionally supported):**
  - `chronos_engine.py` (root compatibility shim; exports `ClockRateModulator`)

## salience
- **Canonical module path:** `temporal_gradient.salience.pipeline`
- **Canonical public symbols:**
  - `SaliencePipeline`
  - `SalienceComponents`
  - `RollingJaccardNovelty`
  - `KeywordImperativeValue`
  - `CodexNoveltyAdapter`
  - `CodexValueAdapter`
  - `NoveltyScorer`
  - `ValueScorer`
  - `ResettableScorer`
- **Known compatibility aliases/shims (intentionally supported):**
  - `salience_pipeline.py` (root compatibility shim; exports: `SaliencePipeline`, `SalienceComponents`, `RollingJaccardNovelty`, `KeywordImperativeValue`, `CodexNoveltyAdapter`, `CodexValueAdapter`, `NoveltyScorer`, `ValueScorer`, `ResettableScorer`)

## memory
- **Canonical module path:**
  - `temporal_gradient.memory.decay`
  - `temporal_gradient.memory.store`
- **Canonical public symbols:**
  - `DecayEngine`
  - `EntropicMemory`
  - `initial_strength_from_psi`
  - `should_encode`
  - `S_MAX`
  - `MemoryStore`
  - `DecayMemoryStore`
- **Known compatibility aliases/shims (intentionally supported):**
  - `entropic_decay.py` (root compatibility shim; exports: `DecayEngine`, `EntropicMemory`, `initial_strength_from_psi`, `should_encode`, `S_MAX`, `DecayMemoryStore`)

## telemetry
- **Canonical module path:**
  - `temporal_gradient.telemetry.chronometric_vector`
  - `temporal_gradient.telemetry.schema`
- **Canonical public symbols:**
  - `ChronometricVector`
  - `validate_packet_schema`
- **Known compatibility aliases/shims (intentionally supported):**
  - `temporal_gradient.telemetry.validate_packet` (compatibility alias)
  - `chronometric_vector.py` (root compatibility shim; exports `ChronometricVector`)

## policies
- **Canonical module path:** `temporal_gradient.policies.compute_cooldown`
- **Canonical public symbols:**
  - `ComputeCooldownPolicy`
  - `allows_compute`
- **Known compatibility aliases/shims (intentionally supported):**
  - None (removed in v0.3; use canonical cooldown policy module path only)

---

**Maintenance rule:** Any API, module-path, symbol-name, or naming-contract change must update this file in the same PR.
