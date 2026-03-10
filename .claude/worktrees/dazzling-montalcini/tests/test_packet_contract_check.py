from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import scripts.check_to_packet_contract as packet_check


ROOT = Path(__file__).resolve().parents[1]


def test_packet_contract_check_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_to_packet_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_packet_contract_targets_active_v03_entrypoints() -> None:
    target_names = {path.name for path in packet_check.TARGET_FILES}

    assert target_names == {
        "anomaly_poc.py",
        "sanity_harness.py",
        "simulation_run.py",
        "twin_paradox.py",
    }
