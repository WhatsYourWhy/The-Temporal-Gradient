import json
import pathlib
import pytest

from temporal_gradient.telemetry.chronometric_vector import ChronometricVector

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
    assert "SCHEMA_VERSION" in packet
    assert "WALL_T" in packet
    assert "TAU" in packet
    assert "SALIENCE" in packet
    assert "CLOCK_RATE" in packet
    assert "MEMORY_S" in packet
    assert "DEPTH" in packet

    parsed = ChronometricVector.from_packet(packet)
    assert parsed.wall_clock_time == pytest.approx(1.0)
    assert parsed.tau == pytest.approx(0.9)
    assert parsed.psi == pytest.approx(0.5)
    assert parsed.clock_rate == pytest.approx(0.6667)
    assert parsed.memory_strength == pytest.approx(0.4)


def test_canonical_fixture_round_trip():
    canonical_packet = (FIXTURES / "canonical.jsonl").read_text().strip()
    parsed = ChronometricVector.from_packet(canonical_packet)
    assert parsed.schema_version == "1.0"
    round_trip = ChronometricVector.from_packet(parsed.to_packet())
    assert round_trip.psi == pytest.approx(parsed.psi)


def test_to_packet_json_compatibility_output_matches_mapping_contract():
    vector = ChronometricVector(
        wall_clock_time=1.0,
        tau=0.9,
        psi=0.5,
        recursion_depth=0,
        clock_rate=0.6667,
        memory_strength=0.4,
    )
    assert json.loads(vector.to_packet_json()) == vector.to_packet()


def test_reject_out_of_range_salience():
    packet = {
        "SCHEMA_VERSION": "1.0",
        "WALL_T": 1.0,
        "TAU": 0.9,
        "SALIENCE": 1.5,
        "CLOCK_RATE": 0.6667,
        "MEMORY_S": 0.4,
        "DEPTH": 0,
    }
    with pytest.raises(ValueError, match="SALIENCE"):
        ChronometricVector.from_packet(json.dumps(packet))


def test_reject_wrong_types_for_required_fields():
    packet = {
        "SCHEMA_VERSION": "1.0",
        "WALL_T": "1.0",
        "TAU": 0.9,
        "SALIENCE": 0.5,
        "CLOCK_RATE": 0.6667,
        "MEMORY_S": 0.4,
        "DEPTH": "0",
    }
    with pytest.raises(TypeError):
        ChronometricVector.from_packet(json.dumps(packet))


def test_optional_clock_rate_bounds():
    packet = {
        "SCHEMA_VERSION": "1.0",
        "WALL_T": 1.0,
        "TAU": 0.9,
        "SALIENCE": 0.5,
        "CLOCK_RATE": 2.0,
        "MEMORY_S": 0.4,
        "DEPTH": 0,
    }
    with pytest.raises(ValueError, match="CLOCK_RATE"):
        ChronometricVector.from_packet(json.dumps(packet), clock_rate_bounds=(0.0, 1.0))


def test_to_packet_defaults_to_canonical_schema_version_for_new_objects():
    vector = ChronometricVector(
        wall_clock_time=1.0,
        tau=0.9,
        psi=0.5,
        recursion_depth=0,
    )

    packet = vector.to_packet()
    assert vector.schema_version == "1.0"
    assert packet["SCHEMA_VERSION"] == "1.0"


def test_from_packet_strict_mode_requires_provenance_hash():
    packet = {
        "SCHEMA_VERSION": "1.0",
        "WALL_T": 1.0,
        "TAU": 0.9,
        "SALIENCE": 0.5,
        "CLOCK_RATE": 0.6667,
        "MEMORY_S": 0.4,
        "DEPTH": 0,
    }

    with pytest.raises(ValueError, match="PROVENANCE_HASH is required"):
        ChronometricVector.from_packet(json.dumps(packet), require_provenance_hash=True)


def test_from_packet_allows_missing_provenance_hash_by_default():
    packet = {
        "SCHEMA_VERSION": "1.0",
        "WALL_T": 1.0,
        "TAU": 0.9,
        "SALIENCE": 0.5,
        "CLOCK_RATE": 0.6667,
        "MEMORY_S": 0.4,
        "DEPTH": 0,
    }

    parsed = ChronometricVector.from_packet(json.dumps(packet), require_provenance_hash=False)
    assert parsed.provenance_hash is None
