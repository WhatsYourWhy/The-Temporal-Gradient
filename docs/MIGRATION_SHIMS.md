# Migration Guide: Compatibility Shims → Canonical Imports

This guide maps legacy/compatibility shim imports to their canonical v0.2.x equivalents and provides copy/paste migration snippets.

## Shim Mapping

Use canonical imports for all new code. Compatibility shims are migration-only and scheduled for removal.

| Legacy shim / naming | Canonical equivalent | Notes |
| --- | --- | --- |
| `chronos_engine` | `temporal_gradient.clock.chronos` | Root-level shim module retained for migration only. |
| `compute_budget` naming (`ComputeBudgetPolicy`, `temporal_gradient.policies.compute_budget`) | `temporal_gradient.policies.compute_cooldown` (`ComputeCooldownPolicy`) | Canonical policy naming reflects cooldown semantics. |
| `chronometric_vector` | `temporal_gradient.telemetry.chronometric_vector` | Root-level shim module retained for migration only. |
| `salience_pipeline` | `temporal_gradient.salience.pipeline` | Root-level shim module retained for migration only. |
| `entropic_decay` | `temporal_gradient.memory.decay` | Root-level shim module retained for migration only. |

Root-level shim set above is sourced from `CHANGELOG.md` (`v0.2.0` compatibility section).

## Copy/Paste Migration Snippets

### 1) Clock modulator import

**Before (shim):**
```python
from chronos_engine import ClockRateModulator
```

**After (canonical):**
```python
from temporal_gradient.clock.chronos import ClockRateModulator
```

### 2) Policy import + naming

**Before (shim naming):**
```python
from temporal_gradient.policies.compute_budget import ComputeBudgetPolicy

policy = ComputeBudgetPolicy(cooldown_tau=0.5)
```

**After (canonical naming):**
```python
from temporal_gradient.policies.compute_cooldown import ComputeCooldownPolicy

policy = ComputeCooldownPolicy(cooldown_tau=0.5)
```

### 3) Telemetry vector import

**Before (shim):**
```python
from chronometric_vector import ChronometricVector
```

**After (canonical):**
```python
from temporal_gradient.telemetry.chronometric_vector import ChronometricVector
```

### 4) Salience pipeline import

**Before (shim):**
```python
from salience_pipeline import SaliencePipeline, RollingJaccardNovelty, KeywordImperativeValue
```

**After (canonical):**
```python
from temporal_gradient.salience.pipeline import SaliencePipeline, RollingJaccardNovelty, KeywordImperativeValue
```

### 5) Memory decay engine import

**Before (shim):**
```python
from entropic_decay import DecayEngine
```

**After (canonical):**
```python
from temporal_gradient.memory.decay import DecayEngine
```

## Deprecation Timeline

The following timeline defines the explicit version windows for compatibility shims:

- **v0.2.x**: Shims are available for migration and should be treated as compatibility-only.
- **v0.3.x**: Shims enter active deprecation (warnings and docs continue to direct users to canonical imports).
- **v0.4.0+**: Shim removal window. Root-level shim modules and `compute_budget` naming aliases may be removed.

If you maintain downstream integrations, migrate to canonical imports during **v0.2.x–v0.3.x** to avoid breakage.
