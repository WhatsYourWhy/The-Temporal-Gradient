import json
import textwrap

from calibration_harness import run_calibration


def _write_config(tmp_path, filename: str, event_wall_delta: float):
    path = tmp_path / filename
    path.write_text(
        textwrap.dedent(
            f"""
            salience:
              window_size: 5
              keywords: [critical]
              base_value: 0.1
              hit_value: 0.2
              max_value: 1.0
            clock:
              base_dilation_factor: 1.0
              min_clock_rate: 0.05
              salience_mode: canonical
              legacy_density_scale: 100.0
            memory:
              half_life: 20.0
              prune_threshold: 0.2
              encode_threshold: 0.3
              initial_strength_max: 1.2
            policies:
              deterministic_seed: 1337
              event_wall_delta: {event_wall_delta}
              cooldown_tau: 0.0
              calibration_post_sweep_wall_delta: 5.0
            """
        )
    )
    return path


def test_calibration_harness_uses_config_values(tmp_path, capsys):
    baseline_cfg = _write_config(tmp_path, "tg-baseline.yaml", event_wall_delta=1.0)
    slower_cfg = _write_config(tmp_path, "tg-slower.yaml", event_wall_delta=2.0)

    run_calibration(str(baseline_cfg))
    baseline_summary = json.loads(capsys.readouterr().out)

    run_calibration(str(slower_cfg))
    slower_summary = json.loads(capsys.readouterr().out)

    assert slower_summary["TAU"] > baseline_summary["TAU"]
