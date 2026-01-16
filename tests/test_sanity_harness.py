from sanity_harness import run_harness


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
        for legacy_key in {"t_obj", "r", "semantic_density", "clock_rate", "psi"}:
            assert legacy_key not in packet
