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

        if "compute_budget" in lowered and "canonical" in lowered and "compatib" not in lowered and "not canonical" not in lowered:
            problems.append(
                f"{path.relative_to(ROOT)}:{idx}: compute_budget must not be labeled canonical"
            )

        if re.search(r"\bcompute_budget\s+is\s+canonical\b", lowered):
            problems.append(
                f"{path.relative_to(ROOT)}:{idx}: deprecated shim described as canonical"
            )

    return problems


def main() -> int:
    docs = iter_docs()
    problems: list[str] = []
    for doc in docs:
        problems.extend(check_file(doc))

    if problems:
        print("Deprecated shim canonicalization check failed:")
        for item in problems:
            print(f" - {item}")
        return 1

    print(f"Canonical reference check passed for {len(docs)} documentation files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
