import textwrap

import pytest

from temporal_gradient.clock.chronos import ClockRateModulator
from temporal_gradient.config_loader import ConfigValidationError, load_config


def write_config(tmp_path, body: str):
    path = tmp_path / "tg.yaml"
    path.write_text(textwrap.dedent(body))
    return path


def test_missing_root_sections_are_defaulted(tmp_path):
    config_path = write_config(
        tmp_path,
        """
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
        """,
    )

    cfg = load_config(config_path)
    assert cfg.policies.event_wall_delta > 0


def test_out_of_range_values_fail_fast(tmp_path):
    config_path = write_config(
        tmp_path,
        """
        salience:
          window_size: 5
          keywords: [critical]
          base_value: 0.1
          hit_value: 0.2
          max_value: 1.0
        clock:
          base_dilation_factor: 1.0
          min_clock_rate: 1.5
          salience_mode: canonical
          legacy_density_scale: 100.0
        memory:
          half_life: 20.0
          prune_threshold: 0.2
          encode_threshold: 0.3
          initial_strength_max: 1.2
        policies:
          deterministic_seed: 1337
          event_wall_delta: 1.0
          cooldown_tau: 0.0
          calibration_post_sweep_wall_delta: 5.0
        """,
    )

    with pytest.raises(ConfigValidationError, match=r"clock.min_clock_rate must be <= 1.0"):
        load_config(config_path)


def test_canonical_clock_constraints_remain_enforced(tmp_path):
    config_path = write_config(
        tmp_path,
        """
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
          event_wall_delta: 1.0
          cooldown_tau: 0.0
          calibration_post_sweep_wall_delta: 5.0
        """,
    )

    cfg = load_config(config_path)
    clock = ClockRateModulator(
        base_dilation_factor=cfg.clock.base_dilation_factor,
        min_clock_rate=cfg.clock.min_clock_rate,
        salience_mode=cfg.clock.salience_mode,
        legacy_density_scale=cfg.clock.legacy_density_scale,
    )

    with pytest.raises(ValueError, match=r"psi must be within \[0, 1\] in canonical mode"):
        clock.tick(psi=1.5, wall_delta=1.0)
