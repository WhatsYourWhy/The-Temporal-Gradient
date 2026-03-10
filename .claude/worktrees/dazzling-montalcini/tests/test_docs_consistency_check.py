from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import scripts.check_docs_consistency as docs_check


ROOT = Path(__file__).resolve().parents[1]


def test_docs_consistency_check_passes():
    result = subprocess.run(
        [sys.executable, "scripts/check_docs_consistency.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_check_doc_flags_deprecated_compute_budget_import(tmp_path: Path) -> None:
    doc = tmp_path / "README.md"
    doc.write_text(
        "from temporal_gradient.policies.compute_budget import ComputeBudgetPolicy\n",
        encoding="utf-8",
    )

    violations = docs_check.check_doc(doc)

    assert any("deprecated policy shim path" in violation.message for violation in violations)


def test_check_doc_requires_canonical_reference_for_canonical_guidance(tmp_path: Path) -> None:
    doc = tmp_path / "USAGE.md"
    doc.write_text("Canonical entry point guidance goes here.\n", encoding="utf-8")

    original_refs = docs_check.EXPECTED_CANONICAL_REFS
    docs_check.EXPECTED_CANONICAL_REFS = {doc: ("docs/CANONICAL_SURFACES.md",)}
    try:
        violations = docs_check.check_doc(doc)
    finally:
        docs_check.EXPECTED_CANONICAL_REFS = original_refs

    assert any("docs/CANONICAL_SURFACES.md" in violation.message for violation in violations)
