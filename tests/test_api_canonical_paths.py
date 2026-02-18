from temporal_gradient.config import load_config as load_config_from_legacy
from temporal_gradient.config_loader import load_config as load_config_from_canonical
from temporal_gradient.policies.compute_budget import ComputeBudgetPolicy
from temporal_gradient.policies.compute_cooldown import ComputeCooldownPolicy
from temporal_gradient.telemetry.schema import validate_packet, validate_packet_schema


def test_config_loader_canonical_and_legacy_exports_match():
    assert load_config_from_canonical is load_config_from_legacy


def test_policy_canonical_and_compatibility_exports_match():
    assert ComputeCooldownPolicy is ComputeBudgetPolicy


def test_telemetry_validator_canonical_and_compatibility_exports_match():
    assert validate_packet is not validate_packet_schema

    packet = {
        "SCHEMA_VERSION": "1.0",
        "WALL_T": 0.0,
        "TAU": 0.0,
        "SALIENCE": 0.2,
        "CLOCK_RATE": 1.0,
        "MEMORY_S": 0.0,
        "DEPTH": 0,
    }
    validate_packet_schema(packet)
    validate_packet(packet)
