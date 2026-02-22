import pytest

from temporal_gradient.clock.chronos import ClockRateModulator
from temporal_gradient.compat.legacy import normalize_legacy_density_to_psi
from temporal_gradient.telemetry.chronometric_vector import ChronometricVector


def test_clock_legacy_density_input_context_matches_normalized_density_policy():
    clock = ClockRateModulator(salience_mode="legacy_density", legacy_density_scale=10.0)

    tau_delta = clock.tick(input_context="aaaaab", wall_delta=2.0)

    expected_density = clock.calculate_information_density("aaaaab")
    expected_psi = normalize_legacy_density_to_psi(expected_density, 10.0)
    expected_rate = clock.clock_rate_from_psi(expected_psi)

    assert tau_delta == pytest.approx(2.0 * expected_rate)
    assert clock.chronology[-1]["psi"] == pytest.approx(round(expected_psi, 4))
    assert clock.chronology[-1]["diagnostic_density"] == pytest.approx(round(expected_density, 2))


def test_telemetry_legacy_packet_fallbacks_still_parse_with_legacy_mode():
    legacy_packet = {
        "SCHEMA_VERSION": "1",
        "t_obj": 10.0,
        "tau": 3.5,
        "LEGACY_DENSITY": 0.42,
        "r": 2,
        "clock_rate": 0.7,
        "S": 0.25,
    }

    parsed = ChronometricVector.from_packet(legacy_packet, salience_mode="legacy_density")

    assert parsed.wall_clock_time == pytest.approx(10.0)
    assert parsed.tau == pytest.approx(3.5)
    assert parsed.psi == pytest.approx(0.42)
    assert parsed.recursion_depth == 2
    assert parsed.clock_rate == pytest.approx(0.7)
    assert parsed.memory_strength == pytest.approx(0.25)
    assert parsed.schema_version == "1.0"


def test_legacy_telemetry_salience_drives_same_clock_rate_as_canonical_path():
    legacy_packet = {
        "t_obj": 5.0,
        "tau": 1.0,
        "legacy_density": 0.3,
        "r": 1,
    }
    parsed = ChronometricVector.from_packet(legacy_packet, salience_mode="legacy_density")

    legacy_clock = ClockRateModulator(salience_mode="legacy_density")
    canonical_clock = ClockRateModulator(salience_mode="canonical")

    legacy_delta = legacy_clock.tick(psi=parsed.psi, wall_delta=1.0)
    canonical_delta = canonical_clock.tick(psi=parsed.psi, wall_delta=1.0)

    assert legacy_delta == pytest.approx(canonical_delta)
