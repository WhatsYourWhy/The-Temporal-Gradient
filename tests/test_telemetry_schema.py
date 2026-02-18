import pytest

from temporal_gradient.telemetry.schema import validate_packet, validate_packet_schema


def _canonical_packet():
    return {
        "SCHEMA_VERSION": "1",
        "WALL_T": 1.0,
        "TAU": 0.8,
        "SALIENCE": 0.4,
        "CLOCK_RATE": 0.7,
        "MEMORY_S": 0.2,
        "DEPTH": 0,
    }


def test_validate_packet_schema_accepts_canonical_packet():
    validate_packet_schema(_canonical_packet())


def test_validate_packet_schema_accepts_string_provenance_hash():
    packet = _canonical_packet()
    packet["PROVENANCE_HASH"] = "sha256:abc123"

    validate_packet_schema(packet)


def test_validate_packet_alias_rejects_unknown_fields():
    packet = _canonical_packet()
    packet["legacy_density"] = 3.0
    with pytest.raises(ValueError, match="Unknown telemetry keys"):
        validate_packet(packet)


def test_validate_packet_schema_requires_provenance_hash_when_requested():
    packet = _canonical_packet()
    packet["PROVENANCE_HASH"] = "abc123"

    validate_packet_schema(packet, require_provenance_hash=True)


def test_validate_packet_schema_allows_missing_provenance_hash_by_default():
    validate_packet_schema(_canonical_packet(), require_provenance_hash=False)
