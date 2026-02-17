from numbers import Real
from typing import Any, Mapping, Optional, Tuple

REQUIRED_CANONICAL_KEYS = {
    "SCHEMA_VERSION",
    "WALL_T",
    "TAU",
    "SALIENCE",
    "CLOCK_RATE",
    "MEMORY_S",
    "DEPTH",
}
OPTIONAL_CANONICAL_KEYS = {"H", "V", "entropy_cost"}

NUMERIC_FIELDS = {
    "WALL_T",
    "TAU",
    "SALIENCE",
    "CLOCK_RATE",
    "MEMORY_S",
}


def _is_numeric(value: Any) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool)


def validate_packet_schema(
    packet: Mapping[str, Any],
    *,
    salience_mode: str = "canonical",
    clock_rate_bounds: Optional[Tuple[float, float]] = None,
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
        raise TypeError("SCHEMA_VERSION must be a string")

    for field in NUMERIC_FIELDS:
        if not _is_numeric(packet[field]):
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
