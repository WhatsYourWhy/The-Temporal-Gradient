#!/usr/bin/env python3
"""Fail when docs present deprecated shim references as canonical surfaces."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_GLOBS = [
    ROOT / "README.md",
    ROOT / "USAGE.md",
    ROOT / "GLOSSARY.md",
]

DOC_DIR = ROOT / "docs"
EXAMPLES_DIR = ROOT / "examples"

SHIM_IMPORT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\s*(from|import)\s+chronos_engine\b"),
    re.compile(r"^\s*(from|import)\s+chronometric_vector\b"),
    re.compile(r"^\s*(from|import)\s+salience_pipeline\b"),
    re.compile(r"^\s*(from|import)\s+entropic_decay\b"),
    re.compile(r"^\s*from\s+temporal_gradient\.policies\.compute_budget\b"),
    re.compile(r"^\s*import\s+temporal_gradient\.policies\.compute_budget\b"),
)


def iter_docs() -> list[Path]:
    files = [p for p in DOC_GLOBS if p.exists()]
    if DOC_DIR.exists():
        files.extend(
            p
            for p in DOC_DIR.rglob("*.md")
            if "archive" not in p.parts
        )
    # deterministic order, deduplicated
    unique = {p.resolve(): p for p in files}
    return [unique[key] for key in sorted(unique)]


def check_file(path: Path) -> list[str]:
    problems: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()

    for idx, line in enumerate(lines, start=1):
        lowered = line.lower()

        if "chronos_engine.py" in lowered and "compatib" not in lowered:
            problems.append(
                f"{path.relative_to(ROOT)}:{idx}: chronos_engine.py must be labeled compatibility-only"
            )

        if re.search(r"\bcompute_budget\s+is\s+canonical\b", lowered):
            problems.append(
                f"{path.relative_to(ROOT)}:{idx}: deprecated shim described as canonical"
            )

    return problems


def _has_shim_import(line: str) -> bool:
    return any(pattern.search(line) for pattern in SHIM_IMPORT_PATTERNS)


def check_canonical_examples_for_shim_imports() -> list[str]:
    """Ensure canonical examples in docs/examples do not import shim modules."""
    problems: list[str] = []
    targets = [ROOT / "README.md", ROOT / "USAGE.md"]

    for path in targets:
        if not path.exists():
            continue
        for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if _has_shim_import(line):
                problems.append(
                    f"{path.relative_to(ROOT)}:{idx}: shim import used in docs example: {line.strip()}"
                )

    if EXAMPLES_DIR.exists():
        for path in sorted(EXAMPLES_DIR.glob("*.py")):
            for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if _has_shim_import(line):
                    problems.append(
                        f"{path.relative_to(ROOT)}:{idx}: shim import used in example: {line.strip()}"
                    )

    return problems


def main() -> int:
    docs = iter_docs()
    problems: list[str] = []
    for doc in docs:
        problems.extend(check_file(doc))

    problems.extend(check_canonical_examples_for_shim_imports())

    if problems:
        print("Deprecated shim canonicalization check failed:")
        for item in problems:
            print(f" - {item}")
        return 1

    print(f"Canonical reference check passed for {len(docs)} documentation files and canonical examples.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
