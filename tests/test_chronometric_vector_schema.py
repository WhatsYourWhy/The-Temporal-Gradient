import json
import pathlib
import pytest

from chronometric_vector import ChronometricVector

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "packets"


def test_round_trip_canonical_packet():
    vector = ChronometricVector(
        wall_clock_time=1.0,
        tau=0.9,
        psi=0.5,
        recursion_depth=0,
        clock_rate=0.6667,
        H=0.8,
        V=0.6,
        memory_strength=0.4,
    )
    packet = vector.to_packet()
    data = json.loads(packet)
    assert "SCHEMA_VERSION" in data
    assert "WALL_T" in data
    assert "TAU" in data
    assert "SALIENCE" in data
    assert "CLOCK_RATE" in data
    assert "MEMORY_S" in data
    assert "DEPTH" in data
    for legacy_key in {
        "INPUT",
        "clock_rate",
        "psi",
        "r",
        "legacy_density",
        "t_obj",
    }:
        assert legacy_key not in data

    parsed = ChronometricVector.from_packet(packet, salience_mode="canonical")
    assert parsed.wall_clock_time == pytest.approx(1.0)
    assert parsed.tau == pytest.approx(0.9)
    assert parsed.psi == pytest.approx(0.5)
    assert parsed.clock_rate == pytest.approx(0.6667)
    assert parsed.memory_strength == pytest.approx(0.4)


def test_canonical_fixture_round_trip():
    canonical_packet = (FIXTURES / "canonical.jsonl").read_text().strip()
    parsed = ChronometricVector.from_packet(canonical_packet, salience_mode="canonical")
    assert parsed.schema_version == "1"
    round_trip = ChronometricVector.from_packet(parsed.to_packet(), salience_mode="canonical")
    assert round_trip.psi == pytest.approx(parsed.psi)


def test_legacy_packet_requires_legacy_mode():
    legacy_packet = (FIXTURES / "legacy.jsonl").read_text().strip()
    with pytest.raises(ValueError):
        ChronometricVector.from_packet(legacy_packet, salience_mode="canonical")
    parsed = ChronometricVector.from_packet(legacy_packet, salience_mode="legacy_density")
    assert parsed.psi == pytest.approx(0.5)
