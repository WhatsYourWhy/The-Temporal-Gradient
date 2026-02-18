import textwrap

import pytest

from temporal_gradient.config_loader import ConfigValidationError, load_config


def _write(tmp_path, body: str):
    path = tmp_path / "tg.yaml"
    path.write_text(textwrap.dedent(body))
    return path


def test_load_config_rejects_unknown_top_level_key(tmp_path):
    path = _write(tmp_path, """
    salience: {}
    clock: {}
    memory: {}
    policies: {}
    extra: 1
    """)
    with pytest.raises(ConfigValidationError, match=r"Unknown key\(s\) in root"):
        load_config(path)


def test_load_config_rejects_unknown_nested_clock_key(tmp_path):
    path = _write(tmp_path, """
    salience: {}
    clock:
      nope: 1
    memory: {}
    policies: {}
    """)
    with pytest.raises(ConfigValidationError, match=r"Unknown key\(s\) in clock"):
        load_config(path)


@pytest.mark.parametrize("value", [0, -0.1, 1.5])
def test_load_config_rejects_invalid_min_clock_rate(tmp_path, value):
    path = _write(tmp_path, f"""
    salience: {{}}
    clock:
      min_clock_rate: {value}
    memory: {{}}
    policies: {{}}
    """)
    with pytest.raises(ConfigValidationError, match="clock.min_clock_rate"):
        load_config(path)


def test_load_config_rejects_negative_decay_lambda(tmp_path):
    path = _write(tmp_path, """
    salience: {}
    clock: {}
    memory:
      decay_lambda: -0.1
    policies: {}
    """)
    with pytest.raises(ConfigValidationError, match="memory.decay_lambda"):
        load_config(path)


def test_load_config_returns_defaulted_structure(tmp_path):
    path = _write(tmp_path, """
    salience: {}
    clock: {}
    memory: {}
    policies: {}
    """)
    cfg = load_config(path)
    assert cfg.clock.base_dilation_factor > 0
    assert 0 < cfg.clock.min_clock_rate <= 1
    assert cfg.memory.decay_lambda >= 0
    assert cfg.memory.s_max > 0


def test_load_config_fallback_parser_accepts_scientific_notation(tmp_path, monkeypatch):
    import temporal_gradient.config as config

    path = _write(tmp_path, """
    salience:
      base_value: 1e-1
      hit_value: 2e-1
      max_value: 1.0
    clock:
      base_dilation_factor: 1e0
      min_clock_rate: 5e-2
      legacy_density_scale: 1e2
      salience_mode: canonical
    memory:
      half_life: 2e1
      prune_threshold: 2e-1
      encode_threshold: 3e-1
      initial_strength_max: 1.2e0
      decay_lambda: 5e-2
      s_max: 1.5e0
    policies:
      deterministic_seed: 1337
      event_wall_delta: 1e0
      cooldown_tau: 0e0
      calibration_post_sweep_wall_delta: 5e0
    """)

    monkeypatch.setattr(config, "yaml", None)

    cfg = load_config(path)
    assert cfg.clock.min_clock_rate == pytest.approx(0.05)
    assert cfg.memory.decay_lambda == pytest.approx(0.05)
