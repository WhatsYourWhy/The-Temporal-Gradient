"""Telemetry packet schema validation for canonical v0.2.0 packets."""

import math
from numbers import Real
from typing import Any, Mapping, Optional, Tuple

CANONICAL_SCHEMA_VERSION = "1.0"
LEGACY_SCHEMA_VERSIONS = {"1"}

REQUIRED_CANONICAL_KEYS = {
    "SCHEMA_VERSION",
    "WALL_T",
    "TAU",
    "SALIENCE",
    "CLOCK_RATE",
    "MEMORY_S",
    "DEPTH",
}
OPTIONAL_CANONICAL_KEYS = {"H", "V", "entropy_cost", "PROVENANCE_HASH"}

NUMERIC_FIELDS = {
    "WALL_T",
    "TAU",
    "SALIENCE",
    "CLOCK_RATE",
    "MEMORY_S",
}


def _is_numeric(value: Any) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool)


def _is_finite_numeric(value: Any) -> bool:
    return _is_numeric(value) and math.isfinite(value)


def normalize_schema_version(schema_version: str) -> str:
    """Normalize schema version values to the canonical version string.

    Canonical packets must serialize as ``"1.0"``. Legacy packets that still
    carry ``"1"`` are accepted for migration and normalized to ``"1.0"``.
    """
    if schema_version == CANONICAL_SCHEMA_VERSION:
        return CANONICAL_SCHEMA_VERSION
    if schema_version in LEGACY_SCHEMA_VERSIONS:
        return CANONICAL_SCHEMA_VERSION

    raise ValueError(
        "SCHEMA_VERSION must be canonical \"1.0\"; accepted legacy values "
        f"for migration: {sorted(LEGACY_SCHEMA_VERSIONS)}. Got: {schema_version!r}"
    )


def validate_packet_schema(
    packet: Mapping[str, Any],
    *,
    salience_mode: str = "canonical",
    clock_rate_bounds: Optional[Tuple[float, float]] = None,
    require_provenance_hash: bool = False,
) -> None:
    """Validate canonical telemetry packets with explicit typing (no coercion)."""
    if salience_mode != "canonical":
        return

    keys = set(packet.keys())
    missing = REQUIRED_CANONICAL_KEYS - keys
    if missing:
        raise ValueError(f"Missing required keys: {sorted(missing)}")

    unknown = keys - REQUIRED_CANONICAL_KEYS - OPTIONAL_CANONICAL_KEYS
    if unknown:
        raise ValueError(f"Unknown telemetry keys: {sorted(unknown)}")

    schema_version = packet["SCHEMA_VERSION"]
    if not isinstance(schema_version, str):
        raise TypeError(
            "SCHEMA_VERSION must be a string equal to canonical \"1.0\" "
            "(legacy \"1\" is accepted for migration input)"
        )
    normalize_schema_version(schema_version)

    provenance_hash = packet.get("PROVENANCE_HASH")
    if require_provenance_hash and provenance_hash is None:
        raise ValueError("PROVENANCE_HASH is required when require_provenance_hash=True")
    if provenance_hash is not None:
        if not isinstance(provenance_hash, str):
            raise TypeError("PROVENANCE_HASH must be a string")
        if not provenance_hash.strip():
            raise ValueError("PROVENANCE_HASH must be a non-empty string")

    for field in NUMERIC_FIELDS:
        if not _is_finite_numeric(packet[field]):
            raise TypeError(f"{field} must be numeric")

    salience = packet["SALIENCE"]
    if not 0.0 <= salience <= 1.0:
        raise ValueError("SALIENCE must be within [0.0, 1.0] in canonical mode")

    depth = packet["DEPTH"]
    if not isinstance(depth, int) or isinstance(depth, bool):
        raise TypeError("DEPTH must be an integer")
    if depth < 0:
        raise ValueError("DEPTH must be non-negative")

    if clock_rate_bounds is not None and packet.get("CLOCK_RATE") is not None:
        lower, upper = clock_rate_bounds
        clock_rate = packet["CLOCK_RATE"]
        if clock_rate < lower or clock_rate > upper:
            raise ValueError(f"CLOCK_RATE must be within [{lower}, {upper}]")


def validate_packet(
    packet: Mapping[str, Any],
    *,
    salience_mode: str = "canonical",
    clock_rate_bounds: Optional[Tuple[float, float]] = None,
    require_provenance_hash: bool = False,
) -> None:
    """Backward-compatible alias for :func:`validate_packet_schema`."""
    validate_packet_schema(
        packet,
        salience_mode=salience_mode,
        clock_rate_bounds=clock_rate_bounds,
        require_provenance_hash=require_provenance_hash,
    )
