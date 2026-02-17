import pytest

from temporal_gradient.telemetry.schema import validate_packet


def test_validate_packet_accepts_canonical_packet():
    packet = {
        "SCHEMA_VERSION": "1",
        "WALL_T": 1.0,
        "TAU": 0.8,
        "SALIENCE": 0.4,
        "CLOCK_RATE": 0.7,
        "MEMORY_S": 0.2,
        "DEPTH": 0,
    }
    validate_packet(packet)


def test_validate_packet_rejects_unknown_fields():
    packet = {
        "SCHEMA_VERSION": "1",
        "WALL_T": 1.0,
        "TAU": 0.8,
        "SALIENCE": 0.4,
        "CLOCK_RATE": 0.7,
        "MEMORY_S": 0.2,
        "DEPTH": 0,
        "legacy_density": 3.0,
    }
    with pytest.raises(ValueError, match="Unknown telemetry keys"):
        validate_packet(packet)
