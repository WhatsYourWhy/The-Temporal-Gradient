import json
import re
from pathlib import Path

from calibration_harness import run_calibration
from sanity_harness import run_harness


def test_sanity_harness_outputs_stable_summary_shape(capsys):
    events = ["a", "CRITICAL b", "c"]
    summary, _ = run_harness(events)
    expected = {
        "psi_min",
        "psi_max",
        "psi_mean",
        "clock_rate_min",
        "clock_rate_max",
        "clock_rate_mean",
        "tau_final",
        "memories_written",
        "memories_alive_after_tau",
    }
    assert expected.issubset(summary.keys())


def test_calibration_harness_deterministic_given_fixed_inputs(tmp_path, capsys):
    cfg = tmp_path / "tg.yaml"
    cfg.write_text(
        """
salience: {}
clock: {}
memory: {}
policies: {}
""".strip()
    )
    run_calibration(str(cfg))
    first = json.loads(capsys.readouterr().out)
    run_calibration(str(cfg))
    second = json.loads(capsys.readouterr().out)
    assert first == second


def test_harnesses_use_only_config_loader_imports():
    harness_files = ["sanity_harness.py", "calibration_harness.py"]
    for harness_file in harness_files:
        source = Path(harness_file).read_text()
        assert "temporal_gradient.config_loader" in source
        assert not re.search(r"(?:from|import)\s+temporal_gradient\.config\b", source)
