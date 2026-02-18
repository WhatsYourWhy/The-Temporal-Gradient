import math

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


def test_validate_packet_rejects_non_string_provenance_hash():
    packet = {
        "SCHEMA_VERSION": "1",
        "WALL_T": 1.0,
        "TAU": 0.1,
        "SALIENCE": 0.2,
        "CLOCK_RATE": 0.9,
        "MEMORY_S": 0.1,
        "DEPTH": 0,
        "PROVENANCE_HASH": 101,
    }

    with pytest.raises(TypeError, match="PROVENANCE_HASH must be a string"):
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


@pytest.mark.parametrize("bad_value", [math.nan, math.inf, -math.inf])
def test_validate_packet_rejects_non_finite_numeric_fields(bad_value):
    packet = {
        "SCHEMA_VERSION": "1",
        "WALL_T": bad_value,
        "TAU": 0.1,
        "SALIENCE": 0.2,
        "CLOCK_RATE": 0.9,
        "MEMORY_S": 0.1,
        "DEPTH": 0,
    }

    with pytest.raises(TypeError, match="WALL_T must be numeric"):
        validate_packet_schema(packet)


def test_chronometric_vector_to_packet_matches_schema():
    packet = ChronometricVector(
        wall_clock_time=1.0,
        tau=0.1,
        psi=0.2,
        recursion_depth=0,
        clock_rate=0.9,
        memory_strength=0.1,
        provenance_hash="sha256:feedbeef",
    ).to_packet()
    validate_packet_schema(packet)
    assert packet["PROVENANCE_HASH"] == "sha256:feedbeef"


def test_validate_packet_rejects_missing_provenance_hash_when_required():
    packet = {
        "SCHEMA_VERSION": "1",
        "WALL_T": 1.0,
        "TAU": 0.1,
        "SALIENCE": 0.2,
        "CLOCK_RATE": 0.9,
        "MEMORY_S": 0.1,
        "DEPTH": 0,
    }

    with pytest.raises(ValueError, match="PROVENANCE_HASH is required"):
        validate_packet_schema(packet, require_provenance_hash=True)


def test_validate_packet_rejects_empty_provenance_hash_string_when_required():
    packet = {
        "SCHEMA_VERSION": "1",
        "WALL_T": 1.0,
        "TAU": 0.1,
        "SALIENCE": 0.2,
        "CLOCK_RATE": 0.9,
        "MEMORY_S": 0.1,
        "DEPTH": 0,
        "PROVENANCE_HASH": "   ",
    }

    with pytest.raises(ValueError, match="non-empty string"):
        validate_packet_schema(packet, require_provenance_hash=True)


def test_validate_packet_accepts_missing_provenance_hash_in_compatibility_mode():
    packet = {
        "SCHEMA_VERSION": "1",
        "WALL_T": 1.0,
        "TAU": 0.1,
        "SALIENCE": 0.2,
        "CLOCK_RATE": 0.9,
        "MEMORY_S": 0.1,
        "DEPTH": 0,
    }

    validate_packet_schema(packet, require_provenance_hash=False)
