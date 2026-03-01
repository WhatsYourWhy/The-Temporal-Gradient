# Code Review Audit — Temporal Gradient v0.2.x
<!-- Generated on 2026-03-01 on branch claude/code-review-audit-xLonQ -->

## Scope

Full-codebase review covering: bugs, optimization candidates, deprecation status, documentation-vs-code accuracy, README quality, and architecture visualization.

Previous audit: `docs/archive/AUDIT_REPORT.md` (structural/architectural focus).
This audit: focused on runtime correctness, performance, API surface accuracy, and documentation gaps.

---

## 1. Bugs

### BUG-01 — `entropy_cost` silently dropped in `to_packet()` (round-trip data loss)
**File:** `temporal_gradient/telemetry/chronometric_vector.py:55-60`
**Severity:** Medium — silent data loss; only affects callers that set `entropy_cost != 0.0`

`OPTIONAL_CANONICAL_KEYS` includes `"entropy_cost"` and `from_packet()` reads it with a default of `0.0`. However, `to_packet()` never writes `entropy_cost` to the packet dict regardless of its value. Any `ChronometricVector` with `entropy_cost > 0.0` that is serialized then deserialized silently loses the value.

**Example:**
```python
cv = ChronometricVector(..., entropy_cost=1.5)
cv2 = ChronometricVector.from_packet(cv.to_packet())
assert cv2.entropy_cost == 1.5  # FAILS: cv2.entropy_cost == 0.0
```

**Status:** Fixed in this PR — `to_packet()` now includes `entropy_cost` when non-zero, matching the conditional pattern used for `H`, `V`, and `PROVENANCE_HASH`.

---

### BUG-02 — `NoveltyScorer` name collision between Protocol and concrete class
**Files:** `temporal_gradient/salience/pipeline.py:11` and `temporal_gradient/salience/embedding_novelty.py:74`
**Severity:** Medium — import path determines which class you receive; silent duck-type confusion

`pipeline.py` defines `class NoveltyScorer(Protocol)` and `embedding_novelty.py` defines `class NoveltyScorer` (a concrete scorer). The `salience/__init__.py` exports the concrete one from `embedding_novelty`, not the Protocol.

Result:
- `from temporal_gradient.salience import NoveltyScorer` → concrete class (full implementation)
- `from temporal_gradient.salience.pipeline import NoveltyScorer` → Protocol (interface only)

`CANONICAL_SURFACES.md` lists `NoveltyScorer` as a canonical symbol from `salience.pipeline`, but the `salience.__init__` re-export points to the concrete class. This creates ambiguity in documentation and can produce confusing `isinstance` checks.

**Recommendation:** Rename the Protocol to `NoveltyProtocol` (or `NoveltyInterface`) in `pipeline.py` to eliminate the name clash. Update `CANONICAL_SURFACES.md` accordingly.

---

### BUG-03 — `CodexValuator` is non-resettable but carries mutable replay state
**Files:** `codex_valuation.py:18`, `temporal_gradient/salience/pipeline.py:200-202`
**Severity:** Medium — deterministic replay fails silently when using `CodexNoveltyAdapter`

`CodexValuator` maintains `self.recent_history` (a mutable list). `CodexNoveltyAdapter` wraps it and is used as a `NoveltyScorer` in the pipeline. `SaliencePipeline.reset()` checks `isinstance(scorer, ResettableScorer)` to clear state before replay. Because neither `CodexNoveltyAdapter` nor `CodexValuator` implements `reset()`, the mutable history is never cleared between runs, making replays non-deterministic.

Contrast with `RollingJaccardNovelty`, which correctly implements `reset()` and is cleared by pipeline reset.

**Recommendation:** Add a `reset()` method to `CodexValuator` (clear `recent_history`) and expose it via `CodexNoveltyAdapter`. This makes `CodexNoveltyAdapter` a valid `ResettableScorer`.

---

### BUG-04 — `codex_valuation.py` __main__ block: `"AXIOM"` classification is unreachable dead code
**File:** `codex_valuation.py:122-128`
**Severity:** Low — demo output is misleading; not a runtime error

The classification table in the `if __name__ == "__main__"` block:
```python
if weight < 0.4: cls = "NOISE"
elif weight < 0.8: cls = "INFO"
elif weight < 1.3: cls = "IMPORTANT"
else: cls = "AXIOM"  # unreachable
```

`weight = components.psi` is the output of `SaliencePipeline.evaluate()`, which clamps `psi` to `[0.0, 1.0]`. The `AXIOM` branch (weight >= 1.3) can never execute. The class labels were inherited from the legacy `CodexValuator.evaluate()` scale (which returned up to 2.0) and were not updated when the demo was adapted to use the canonical pipeline.

**Recommendation:** Update classification thresholds to match [0, 1] output range, e.g. `< 0.3 NOISE`, `< 0.6 INFO`, `< 0.9 IMPORTANT`, `>= 0.9 AXIOM`.

---

### BUG-05 — `_validate_psi` does not clamp `psi > 1.0` in `legacy_density` mode
**File:** `temporal_gradient/clock/chronos.py:60-63`
**Severity:** Low — clock math still produces bounded output via `min_clock_rate`; behavioral contract is unclear

In `_validate_psi`, the `psi > 1.0` clamp is conditioned on `self.salience_mode == CANONICAL_MODE`. When `salience_mode == LEGACY_DENSITY_MODE` and a caller passes `psi > 1.0` directly to `tick()`, the value passes through unclamped. The clock rate formula `1 / (1 + psi * base_dilation)` still produces a valid (sub-floor) value that gets clamped to `min_clock_rate`, so runtime behavior is bounded — but the method's documented contract (canonicalize psi into [0, 1]) isn't enforced for legacy mode explicit-psi calls.

**Recommendation:** Document that `_validate_psi` does not apply [0, 1] clamping in legacy mode for explicit-psi inputs, or add unconditional clamping with a note that it mirrors the canonical behavior.

---

## 2. Optimization Candidates

### OPT-01 — O(n²) character-frequency computation in `calculate_information_density`
**File:** `temporal_gradient/clock/chronos.py:84`

```python
prob = [float(input_data.count(c)) / len(input_data) for c in dict.fromkeys(list(input_data))]
```

`input_data.count(c)` is O(n) and is called once per unique character, making the overall complexity O(n × unique_chars) ≈ O(n²) for large inputs. A `collections.Counter` computes all frequencies in a single O(n) pass. Also, `dict.fromkeys(list(input_data))` creates an unnecessary intermediate list; `dict.fromkeys(input_data)` works directly on any iterable.

**Suggested approach:**
```python
from collections import Counter
counts = Counter(input_data)
n = len(input_data)
prob = [c / n for c in counts.values()]
```

---

### OPT-02 — Rolling history trimming via list slicing allocates a new list each tick
**Files:** `temporal_gradient/salience/pipeline.py:89,117`, `temporal_gradient/salience/embedding_novelty.py:276`

All three history windows use the pattern:
```python
if len(self._history) > self.window_size:
    self._history = self._history[-self.window_size:]
```

This allocates and GC-collects a new list on every tick after the window fills. A `collections.deque(maxlen=window_size)` maintains the same FIFO semantics with O(1) append and automatic eviction, and avoids per-tick allocation.

---

### OPT-03 — `allows_compute()` function creates a dataclass instance per call
**File:** `temporal_gradient/policies/compute_cooldown.py:17-19`

```python
def allows_compute(*, elapsed_tau: float, cooldown_tau: float = 0.0) -> bool:
    return ComputeCooldownPolicy(cooldown_tau=cooldown_tau).allows_compute(elapsed_tau=elapsed_tau)
```

This instantiates and immediately discards a frozen dataclass on every call. For a hot-path gate this is avoidable. The function could be a direct comparison: `return elapsed_tau >= cooldown_tau`.

---

### OPT-04 — Double-clamping in `SaliencePipeline.evaluate()`
**File:** `temporal_gradient/salience/pipeline.py:173-175`

`novelty` and `value` are clamped after scoring even though both `RollingJaccardNovelty` and `KeywordImperativeValue` already clamp their outputs internally. The outer clamp is a safety net but adds redundant comparisons on every evaluation. Consider consolidating into scorer contracts or document explicitly that the pipeline clamp is the authoritative bound.

---

## 3. Deprecation Status

### DEP-01 — Root-level shim files: no hard removal date bound
**Files:** `chronos_engine.py` (compatibility-only shim), `salience_pipeline.py`, `entropic_decay.py`, `chronometric_vector.py`

CHANGELOG states shims are "retained for one release window" since v0.2.0. `CANONICAL_VS_LEGACY.md` targets v0.4.0+ for removal, with v0.3.x as "staged removal by subsystem." However, no specific shim is targeted for removal in the `V0.3.0_PR_CHECKLIST.md`. The timeline is described but not enforced.

**Recommendation:** Tag each shim removal in the v0.3.0 checklist by subsystem so it's actionable.

---

### DEP-02 — `validate_packet()` alias emits no `DeprecationWarning`
**File:** `temporal_gradient/telemetry/schema.py:124-137`

The function docstring says "backward-compatible alias" but no `DeprecationWarning` is emitted at call time. Users have no programmatic signal to migrate.

**Recommendation:** Add `warnings.warn(..., DeprecationWarning, stacklevel=2)` inside `validate_packet()`.

---

### DEP-03 — `allows_compute()` helper has ambiguous canonical status
**File:** `temporal_gradient/policies/compute_cooldown.py:17`

`CANONICAL_SURFACES.md` lists `allows_compute` as a canonical public symbol, but the docstring describes it as a "Compatibility helper." These two characterizations conflict. Decide: promote it fully to canonical (remove the "compatibility" language) or deprecate it in favor of `ComputeCooldownPolicy`.

---

### DEP-04 — `CodexValuator` has no lifecycle notice despite adapter integration pattern
**File:** `codex_valuation.py`

`CodexValuator` is a root-level module that predates the canonical subsystem structure. It is not re-exported by any canonical package module and has no deprecation notice. Given that `CodexNoveltyAdapter` and `CodexValueAdapter` exist as integration bridges, `CodexValuator` itself could be a candidate for formal deprecation notice pointing users toward the `temporal_gradient.salience` subsystem as the primary scorer path.

---

## 4. Documentation vs. Code Accuracy

### DOC-01 — README core equation omits min/max clamping
**File:** `README.md`, equation block

The README equation:
```
dτ/dt = 1 / (1 + base_dilation_factor · Ψ(t))
```

The actual implementation:
```python
clock_rate = min(max_clock_rate, max(min_clock_rate, 1 / (1 + psi * base_dilation)))
```

The prose after the equation mentions that `min_clock_rate` and `max_clock_rate` bound the rate, but the equation itself does not reflect those bounds. This can mislead readers who use the equation for analysis. The equation should include the clamp notation or link to the prose.

---

### DOC-02 — `max_clock_rate` is unconfigurable via `tg.yaml` but undocumented
**Files:** `temporal_gradient/config.py` (`DEFAULTS`, `ClockConfig`), `temporal_gradient/config_loader.py:172`

`ClockConfig` has no `max_clock_rate` field. `load_config()` hardcodes `max_clock_rate=1.0` when calling `validate_clock_settings`. `tg.yaml` and `DEFAULTS` have no `max_clock_rate` key.

Result: users cannot configure `max_clock_rate` through the canonical config surface. The README describes `max_clock_rate` as a behavioral bound but provides no way to tune it. This undocumented hardcoded default diverges from the documented parameter.

---

### DOC-03 — `CANONICAL_SURFACES.md` `NoveltyScorer` reference is ambiguous
**File:** `docs/CANONICAL_SURFACES.md:18`

Lists `NoveltyScorer` as a canonical symbol from `temporal_gradient.salience.pipeline`. However, `temporal_gradient.salience.__init__` re-exports `NoveltyScorer` from `embedding_novelty` (the concrete class), not from `pipeline` (the Protocol). A developer following `CANONICAL_SURFACES.md` would import the Protocol but receive something different from the package's canonical `__init__` export.

---

### DOC-04 — `entropy_cost` listed in schema but absent from telemetry key documentation
**File:** `README.md: Telemetry Schema` section, `temporal_gradient/telemetry/schema.py:24`

`OPTIONAL_CANONICAL_KEYS` contains `"entropy_cost"` and `from_packet()` supports it. The README telemetry section lists only `H`, `V`, and the 7 required keys as notable fields — `entropy_cost` is not mentioned anywhere in the README or `USAGE.md`, making it an invisible optional key to integrators.

---

### DOC-05 — Prior audit item still open: `USAGE.md` CLOCK_RATE/MEMORY_S nullability claim
**File:** `USAGE.md`

The prior `AUDIT_REPORT.md` noted that `USAGE.md` describes `CLOCK_RATE` and `MEMORY_S` as potentially null, while `to_packet()` serializes them as `0.0` when absent. This remains unresolved as of this review.

---

## 5. README Review

### Strengths
- **Guardrails section** is precise and appropriately scoped ("this is a dynamics framework, not a cognitive model").
- **Core equations** match actual implementation structure.
- **Packet API contract** section correctly distinguishes `to_packet()` (dict) vs `to_packet_json()` (str) — a subtle but important distinction that prevents a common misuse.
- **Stable Import Surface** clearly separates canonical from legacy paths.
- **Changelog and Documentation Lifecycle** sections are well-maintained.
- Contributor onboarding pointer to `DAY1_CONTRIBUTOR_MAP.md` is a good pattern.

### Issues
| # | Issue | Impact |
|---|-------|--------|
| R1 | No CI status badge | Medium — contributors can't see pipeline health at a glance |
| R2 | No installation/requirements section | Medium — unclear what runtime dependencies are needed (`PyYAML`, `pytest`) |
| R3 | Core equation omits min/max clamping (see DOC-01) | Medium — equation-based analysis will produce wrong results |
| R4 | `entropy_cost` not documented in telemetry key list (see DOC-04) | Low — invisible optional field |
| R5 | "Latest document-review validation run (local): pytest -q (run locally...)" | Low — adds no information; remove or replace with last-run badge |
| R6 | Architecture section has no visual — addressed by diagram added in this PR | Addressed |

---

## 6. Architecture Data-Flow Diagram

See the diagram added to `README.md` under the **Architecture** section.

The diagram shows the four canonical stages of a single evaluation cycle:
1. Text → `SaliencePipeline` (H scorer × V scorer → Ψ)
2. Ψ → `ClockRateModulator` (rate equation → τ accumulation)
3. τ → `DecayEngine` (exponential strength decay + reconsolidation)
4. All state → `ChronometricVector` (canonical telemetry packet + schema validation)

---

## Summary Table

| ID | Category | File | Severity | Status |
|----|----------|------|----------|--------|
| BUG-01 | Bug | `telemetry/chronometric_vector.py` | Medium | **Fixed in this PR** |
| BUG-02 | Bug | `salience/pipeline.py`, `salience/embedding_novelty.py` | Medium | Open — rename recommended |
| BUG-03 | Bug | `codex_valuation.py`, `salience/pipeline.py` | Medium | Open — add `reset()` |
| BUG-04 | Bug | `codex_valuation.py` | Low | Open — update thresholds |
| BUG-05 | Bug | `clock/chronos.py` | Low | Open — document or fix |
| OPT-01 | Optimization | `clock/chronos.py` | Medium | Open |
| OPT-02 | Optimization | `salience/pipeline.py`, `salience/embedding_novelty.py` | Low | Open |
| OPT-03 | Optimization | `policies/compute_cooldown.py` | Low | Open |
| OPT-04 | Optimization | `salience/pipeline.py` | Low | Open |
| DEP-01 | Deprecation | Root shim files | Medium | Open — needs checklist targeting |
| DEP-02 | Deprecation | `telemetry/schema.py` | Medium | Open — add warning |
| DEP-03 | Deprecation | `policies/compute_cooldown.py` | Low | Open — resolve status |
| DEP-04 | Deprecation | `codex_valuation.py` | Low | Open |
| DOC-01 | Doc accuracy | `README.md` | Medium | Partially addressed by diagram |
| DOC-02 | Doc accuracy | `config.py`, `config_loader.py` | Medium | Open |
| DOC-03 | Doc accuracy | `docs/CANONICAL_SURFACES.md` | Medium | Open — linked to BUG-02 |
| DOC-04 | Doc accuracy | `README.md`, `schema.py` | Low | Open |
| DOC-05 | Doc accuracy | `USAGE.md` | Low | Open (prior audit carry) |
