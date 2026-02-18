#!/usr/bin/env python3
"""Fail fast when runtime modules serialize `to_packet()` through `json.loads(...)`."""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_FILES: tuple[Path, ...] = (
    ROOT / "anomaly_poc.py",
    ROOT / "sanity_harness.py",
    ROOT / "simulation_run.py",
    ROOT / "calibration_harness.py",
)

CONTRACT_MESSAGE = (
    "Contract violation: `to_packet()` returns mapping; "
    "`to_packet_json()` is explicit serialization path."
)


@dataclass(frozen=True)
class Violation:
    path: Path
    line_no: int
    context: str

    def render(self) -> str:
        rel = self.path.relative_to(ROOT)
        return f"{rel}:{self.line_no}: {CONTRACT_MESSAGE} Found: {self.context}"


class PacketContractVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.matches: list[tuple[int, str]] = []

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        if _is_json_loads_call(node.func) and any(_contains_to_packet_call(arg) for arg in node.args):
            call_text = ast.unparse(node)
            self.matches.append((node.lineno, call_text))
        self.generic_visit(node)


def _is_json_loads_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "loads"
        and isinstance(node.value, ast.Name)
        and node.value.id == "json"
    )


def _contains_to_packet_call(node: ast.AST) -> bool:
    for nested in ast.walk(node):
        if isinstance(nested, ast.Call) and isinstance(nested.func, ast.Attribute) and nested.func.attr == "to_packet":
            return True
    return False


def _scan_file(path: Path) -> list[Violation]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    visitor = PacketContractVisitor()
    visitor.visit(tree)
    return [Violation(path=path, line_no=line_no, context=context) for line_no, context in visitor.matches]


def main() -> int:
    missing_files = [path for path in TARGET_FILES if not path.exists()]
    if missing_files:
        print("Missing runtime file(s) required for packet contract check:")
        for path in missing_files:
            print(f" - {path.relative_to(ROOT)}")
        return 2

    violations: list[Violation] = []
    for path in TARGET_FILES:
        violations.extend(_scan_file(path))

    if violations:
        print("Runtime packet contract check failed.")
        print(CONTRACT_MESSAGE)
        for violation in violations:
            print(f" - {violation.render()}")
        return 1

    print(f"Runtime packet contract check passed for {len(TARGET_FILES)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
