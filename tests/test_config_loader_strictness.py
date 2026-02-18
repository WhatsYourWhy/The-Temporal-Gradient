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


def test_load_config_rejects_non_boolean_replay_require_provenance_hash(tmp_path):
    path = _write(tmp_path, """
    salience: {}
    clock: {}
    memory: {}
    policies:
      replay_require_provenance_hash: 1
    """)
    with pytest.raises(ConfigValidationError, match="replay_require_provenance_hash"):
        load_config(path)


def test_load_config_fallback_parser_accepts_inline_comments(tmp_path, monkeypatch):
    import temporal_gradient.config as config

    path = _write(tmp_path, """
    salience:
      base_value: 0.1 # baseline
      hit_value: 0.2 # increment
      max_value: 1.0
      keywords: [critical, urgent] # high-priority markers
    clock:
      base_dilation_factor: 1.0
      min_clock_rate: 0.05 # lower clamp
      legacy_density_scale: 100.0
      salience_mode: canonical
    memory:
      half_life: 20.0
      prune_threshold: 0.2
      encode_threshold: 0.3
      initial_strength_max: 1.2
      decay_lambda: 0.05
      s_max: 1.5
    policies:
      deterministic_seed: 1337
      event_wall_delta: 1.0
      cooldown_tau: 0.0
      calibration_post_sweep_wall_delta: 5.0
      replay_require_provenance_hash: false # optional strict replay mode
    """)

    monkeypatch.setattr(config, "yaml", None)

    cfg = load_config(path)
    assert cfg.clock.min_clock_rate == pytest.approx(0.05)
    assert cfg.salience.keywords == ("critical", "urgent")
    assert cfg.policies.replay_require_provenance_hash is False


def test_load_config_fallback_parser_preserves_hash_inside_quotes(tmp_path, monkeypatch):
    import temporal_gradient.config as config

    path = _write(tmp_path, """
    salience:
      keywords: ['phase#1', "critical#path"]
    clock: {}
    memory: {}
    policies: {}
    """)

    monkeypatch.setattr(config, "yaml", None)

    cfg = load_config(path)
    assert cfg.salience.keywords == ("phase#1", "critical#path")


@pytest.mark.parametrize(
    "body, expected_error",
    [
        (
            """
            salience:
              keywords: ['critical"]
            clock: {}
            memory: {}
            policies: {}
            """,
            "quoted scalar delimiters|Unterminated quoted scalar|unterminated quoted item",
        ),
        (
            """
            salience:
              keywords: [critical, 'urgent"]
            clock: {}
            memory: {}
            policies: {}
            """,
            "inline array|quoted scalar delimiters|Unterminated quoted scalar",
        ),
        (
            """
            salience:
              keywords: [critical,
            clock: {}
            memory: {}
            policies: {}
            """,
            "inline array delimiters",
        ),
    ],
)
def test_load_config_fallback_parser_rejects_malformed_quoted_scalars_and_arrays(
    tmp_path, monkeypatch, body, expected_error
):
    import temporal_gradient.config as config

    path = _write(tmp_path, body)
    monkeypatch.setattr(config, "yaml", None)

    with pytest.raises(ConfigValidationError, match=expected_error):
        load_config(path)


def test_load_config_defaults_replay_require_provenance_hash_to_false(tmp_path):
    path = _write(tmp_path, """
    salience: {}
    clock: {}
    memory: {}
    policies: {}
    """)

    cfg = load_config(path)
    assert cfg.policies.replay_require_provenance_hash is False
