"""Compatibility helpers shared across temporal-gradient modules."""

from .legacy import (
    CANONICAL_MODE,
    LEGACY_DENSITY_MODE,
    LEGACY_PACKET_FALLBACK_KEYS,
    LEGACY_REJECTED_CANONICAL_KEYS,
    SALIENCE_MODES,
    coerce_legacy_schema_version,
    legacy_packet_value,
    normalize_legacy_density_to_psi,
)

__all__ = [
    "CANONICAL_MODE",
    "LEGACY_DENSITY_MODE",
    "LEGACY_PACKET_FALLBACK_KEYS",
    "LEGACY_REJECTED_CANONICAL_KEYS",
    "SALIENCE_MODES",
    "coerce_legacy_schema_version",
    "legacy_packet_value",
    "normalize_legacy_density_to_psi",
]
