from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_chronos_demo_smoke_output_sections() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/chronos_demo.py", "--sleep-seconds", "0"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "EVENT" in result.stdout
    assert "CLOCK_RATE" in result.stdout
    assert "PACKET" in result.stdout
    assert "[EMPTY INPUT]" in result.stdout
