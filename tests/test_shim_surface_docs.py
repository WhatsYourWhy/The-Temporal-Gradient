from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_SURFACES = ROOT / "docs" / "CANONICAL_SURFACES.md"

EXPECTED_DOC_SURFACES = {
    "chronos_engine.py": {"ClockRateModulator"},
    "salience_pipeline.py": {
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
    "entropic_decay.py": {
        "DecayEngine",
        "EntropicMemory",
        "initial_strength_from_psi",
        "should_encode",
        "S_MAX",
        "DecayMemoryStore",
    },
    "chronometric_vector.py": {"ChronometricVector"},
}


def _parse_backticks(text: str) -> set[str]:
    return {token for token in re.findall(r"`([^`]+)`", text) if ".py" not in token}


def test_docs_list_shim_export_surfaces():
    content = CANONICAL_SURFACES.read_text(encoding="utf-8")

    for shim_file, expected_symbols in EXPECTED_DOC_SURFACES.items():
        pattern = re.compile(rf"`{re.escape(shim_file)}` .*exports[^\n]*")
        match = pattern.search(content)
        assert match, f"missing shim export line for {shim_file}"
        exported_symbols = _parse_backticks(match.group(0))
        assert exported_symbols == expected_symbols
