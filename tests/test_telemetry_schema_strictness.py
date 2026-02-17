import json

import pytest

from temporal_gradient.telemetry.chronometric_vector import ChronometricVector
from temporal_gradient.telemetry.schema import validate_packet_schema


def test_validate_packet_rejects_missing_required_fields():
    with pytest.raises(ValueError, match="Missing required keys"):
        validate_packet_schema({"SCHEMA_VERSION": "1"})


def test_validate_packet_rejects_wrong_types_without_coercion():
    packet = {
        "SCHEMA_VERSION": "1",
        "WALL_T": "1.0",
        "TAU": 0.1,
        "SALIENCE": 0.2,
        "CLOCK_RATE": 0.9,
        "MEMORY_S": 0.1,
        "DEPTH": 0,
    }
    with pytest.raises(TypeError):
        validate_packet_schema(packet)


def test_validate_packet_accepts_minimal_valid_packet():
    packet = {
        "SCHEMA_VERSION": "1",
        "WALL_T": 1.0,
        "TAU": 0.1,
        "SALIENCE": 0.2,
        "CLOCK_RATE": 0.9,
        "MEMORY_S": 0.1,
        "DEPTH": 0,
    }
    validate_packet_schema(packet)


def test_chronometric_vector_to_packet_matches_schema():
    packet = json.loads(
        ChronometricVector(
            wall_clock_time=1.0,
            tau=0.1,
            psi=0.2,
            recursion_depth=0,
            clock_rate=0.9,
            memory_strength=0.1,
        ).to_packet()
    )
    validate_packet_schema(packet)
