#!/usr/bin/env python3
"""Check docs for required canonical references."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_FILES: tuple[Path, ...] = (
    ROOT / "README.md",
    ROOT / "USAGE.md",
    ROOT / "TASK_PROPOSALS.md",
)

CANONICAL_IMPORT_RE = re.compile(r"^\s*(?:import|from)\s+temporal_gradient(?:\.|\s|$)")

# Canonical reference expectations per file.
EXPECTED_CANONICAL_REFS: dict[Path, tuple[str, ...]] = {
    ROOT / "README.md": (
        "docs/CANONICAL_SURFACES.md",
    ),
    ROOT / "USAGE.md": ("docs/CANONICAL_SURFACES.md",),
    ROOT / "TASK_PROPOSALS.md": ("docs/CANONICAL_SURFACES.md",),
}

# Rule set for lines that imply canonical/compatibility guidance; when matched,
# at least one expected canonical reference for that file should exist.
REFERENCE_TRIGGER_RE = re.compile(
    r"\b(canonical|import\s+surface|entry\s*point)\b",
    re.IGNORECASE,
)


@dataclass
class Violation:
    path: Path
    line_no: int | None
    message: str
    context: str

    def render(self) -> str:
        rel = self.path.relative_to(ROOT)
        if self.line_no is None:
            return f"{rel}: {self.message} | context: {self.context}"
        return f"{rel}:{self.line_no}: {self.message} | context: {self.context}"


def check_doc(path: Path) -> list[Violation]:
    violations: list[Violation] = []
    lines = path.read_text(encoding="utf-8").splitlines()

    for idx, line in enumerate(lines, start=1):
        if CANONICAL_IMPORT_RE.search(line) and "temporal_gradient.policies.compute_budget" in line:
            violations.append(
                Violation(
                    path=path,
                    line_no=idx,
                    message="deprecated policy shim path shown in import example; use compute_cooldown",
                    context=line.strip(),
                )
            )

    expected_refs = EXPECTED_CANONICAL_REFS.get(path, ())
    if expected_refs:
        content = "\n".join(lines)
        needs_ref = any(REFERENCE_TRIGGER_RE.search(line) for line in lines)
        if needs_ref:
            missing = [ref for ref in expected_refs if ref not in content]
            for ref in missing:
                violations.append(
                    Violation(
                        path=path,
                        line_no=None,
                        message=f"missing expected canonical reference `{ref}`",
                        context="add an explicit markdown link near canonical/compatibility guidance",
                    )
                )

    return violations


def main() -> int:
    missing_files = [p for p in DOC_FILES if not p.exists()]
    if missing_files:
        for path in missing_files:
            print(f"Missing required docs file: {path.relative_to(ROOT)}")
        return 2

    violations: list[Violation] = []
    for path in DOC_FILES:
        violations.extend(check_doc(path))

    if violations:
        print("Documentation consistency check failed:")
        for violation in violations:
            print(f" - {violation.render()}")
        return 1

    print(f"Documentation consistency check passed for {len(DOC_FILES)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
