from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_packet_contract_check_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_to_packet_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
