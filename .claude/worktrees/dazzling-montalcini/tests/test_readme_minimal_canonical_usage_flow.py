import pytest
import temporal_gradient as tg
from temporal_gradient.policies.compute_cooldown import ComputeCooldownPolicy
from temporal_gradient.telemetry.schema import validate_packet_schema


def test_readme_minimal_canonical_usage_flow_end_to_end():
    config = tg.load_config("tg.yaml")

    clock = tg.clock.ClockRateModulator(
        base_dilation_factor=config.clock.base_dilation_factor,
        min_clock_rate=config.clock.min_clock_rate,
        salience_mode=config.clock.salience_mode,
    )

    salience = tg.salience.SaliencePipeline(
        tg.salience.RollingJaccardNovelty(),
        tg.salience.KeywordImperativeValue(),
    )

    cooldown = ComputeCooldownPolicy(cooldown_tau=config.policies.cooldown_tau)

    text = "CRITICAL: SECURITY BREACH DETECTED."
    sal = salience.evaluate(text)
    clock.tick(psi=sal.psi, wall_delta=config.policies.event_wall_delta)

    packet = tg.telemetry.ChronometricVector(
        wall_clock_time=config.policies.event_wall_delta,
        tau=clock.tau,
        psi=sal.psi,
        recursion_depth=0,
        clock_rate=clock.clock_rate_from_psi(sal.psi),
        H=sal.novelty,
        V=sal.value,
        memory_strength=0.0,
    ).to_packet()

    validate_packet_schema(packet, salience_mode=config.clock.salience_mode)
    assert isinstance(packet, dict)
    assert packet["SALIENCE"] == pytest.approx(sal.psi, rel=0.0, abs=1e-3)
    assert cooldown.allows_compute(elapsed_tau=clock.tau)
