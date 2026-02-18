from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_canonical_docs_and_examples_avoid_shim_imports():
    result = subprocess.run(
        [sys.executable, "scripts/check_canonical_refs.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
