from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

CANONICAL_MODE = "canonical"
LEGACY_DENSITY_MODE = "legacy_density"
SALIENCE_MODES = {CANONICAL_MODE, LEGACY_DENSITY_MODE}

LEGACY_REJECTED_CANONICAL_KEYS = {
    "t_obj",
    "r",
    "legacy_density",
    "LEGACY_DENSITY",
    "clock_rate",
    "psi",
}

LEGACY_PACKET_FALLBACK_KEYS: dict[str, tuple[str, ...]] = {
    "wall_clock_time": ("WALL_T", "t_obj"),
    "tau": ("TAU", "tau"),
    "psi": ("SALIENCE", "psi", "legacy_density", "LEGACY_DENSITY"),
    "recursion_depth": ("DEPTH", "r"),
    "clock_rate": ("CLOCK_RATE", "clock_rate"),
    "memory_strength": ("MEMORY_S", "S"),
}


def legacy_packet_value(data: Mapping[str, Any], key_path: Sequence[str]) -> Any:
    for key in key_path:
        if key in data:
            return data[key]
    return None


def normalize_legacy_density_to_psi(density: Any, legacy_density_scale: float) -> float | None:
    if density is None:
        return None
    scaled = float(density) / float(legacy_density_scale)
    return max(0.0, min(1.0, scaled))


def coerce_legacy_schema_version(
    value: Any,
    *,
    canonical_schema_version: str,
    normalizer: Callable[[str], str],
) -> str:
    if not isinstance(value, str):
        return canonical_schema_version
    try:
        return normalizer(value)
    except ValueError:
        return canonical_schema_version
