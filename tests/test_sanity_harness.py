import textwrap

from sanity_harness import run_harness


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


def test_harness_summary_bounds():
    events = [
        "System boot sequence initiated.",
        "CRITICAL: SECURITY BREACH DETECTED.",
        "Rain. Water. Liquid.",
        "My name is Sentinel.",
        "System standby.",
    ]
    summary, packets = run_harness(events)
    assert 0.0 <= summary["psi_mean"] <= 1.0
    assert summary["clock_rate_min"] >= 0.05
    assert summary["memories_written"] > 0
    assert len(packets) == len(events)
    for packet in packets:
        for key in {"SCHEMA_VERSION", "WALL_T", "TAU", "SALIENCE", "CLOCK_RATE", "MEMORY_S", "DEPTH"}:
            assert key in packet
        for legacy_key in {"t_obj", "r", "legacy_density", "clock_rate", "psi"}:
            assert legacy_key not in packet


def test_harness_uses_config_path_for_runtime_behavior(tmp_path):
    events = ["normal input", "CRITICAL input", "normal input"]
    default_cfg = _write_config(tmp_path, "tg-default.yaml", event_wall_delta=1.0)
    fast_cfg = _write_config(tmp_path, "tg-fast.yaml", event_wall_delta=2.0)

    summary_default, _ = run_harness(events, config_path=default_cfg)
    summary_faster_wall, _ = run_harness(events, config_path=fast_cfg)

    assert summary_faster_wall["tau_final"] > summary_default["tau_final"]


def test_harness_validates_every_packet(monkeypatch):
    calls = []

    def _capture(packet, **_kwargs):
        calls.append(packet)

    monkeypatch.setattr("sanity_harness.validate_packet_schema", _capture)
    events = ["a", "b", "c"]
    _summary, packets = run_harness(events)
    assert len(calls) == len(packets)
