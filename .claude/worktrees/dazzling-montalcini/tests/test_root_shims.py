from __future__ import annotations

import importlib
import warnings


SHIM_COMPAT_EXPORTS = {
    "chronos_engine": {"ClockRateModulator"},
    "salience_pipeline": {
        "SaliencePipeline",
        "SalienceComponents",
        "RollingJaccardNovelty",
        "KeywordImperativeValue",
        "CodexNoveltyAdapter",
        "CodexValueAdapter",
        "NoveltyScorer",
        "ValueScorer",
        "ResettableScorer",
    },
    "entropic_decay": {
        "DecayEngine",
        "EntropicMemory",
        "initial_strength_from_psi",
        "should_encode",
        "S_MAX",
        "DecayMemoryStore",
    },
    "chronometric_vector": {"ChronometricVector"},
}


def _import_with_deprecation(module_name: str):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        module = importlib.import_module(module_name)
        module = importlib.reload(module)
    return module, caught


def test_root_shims_export_only_compatibility_symbols():
    for module_name, expected_exports in SHIM_COMPAT_EXPORTS.items():
        module, _ = _import_with_deprecation(module_name)
        assert set(module.__all__) == expected_exports


def test_root_shims_keep_compatibility_exports_importable():
    for module_name, expected_exports in SHIM_COMPAT_EXPORTS.items():
        module, _ = _import_with_deprecation(module_name)
        for symbol in expected_exports:
            assert hasattr(module, symbol)


def test_root_shim_imports_emit_deprecation_warnings():
    for module_name in SHIM_COMPAT_EXPORTS:
        _, caught = _import_with_deprecation(module_name)
        assert any(item.category is DeprecationWarning for item in caught)
