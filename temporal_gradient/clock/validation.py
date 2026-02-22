from __future__ import annotations

from typing import Any, Callable


def _raise(error_factory: Callable[[str], Exception], message: str) -> None:
    raise error_factory(message)


def coerce_clock_number(
    value: Any,
    key: str,
    *,
    error_factory: Callable[[str], Exception],
    section_name: str = "clock",
) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        _raise(error_factory, f"{section_name}.{key} must be numeric")
    return float(value)


def validate_clock_settings(
    *,
    base_dilation_factor: Any,
    min_clock_rate: Any,
    max_clock_rate: Any,
    salience_mode: str,
    legacy_density_scale: Any,
    error_factory: Callable[[str], Exception],
    section_name: str = "clock",
) -> tuple[float, float, float, str, float]:
    base_dilation = coerce_clock_number(
        base_dilation_factor,
        "base_dilation_factor",
        error_factory=error_factory,
        section_name=section_name,
    )
    min_rate = coerce_clock_number(
        min_clock_rate,
        "min_clock_rate",
        error_factory=error_factory,
        section_name=section_name,
    )
    max_rate = coerce_clock_number(
        max_clock_rate,
        "max_clock_rate",
        error_factory=error_factory,
        section_name=section_name,
    )
    density_scale = coerce_clock_number(
        legacy_density_scale,
        "legacy_density_scale",
        error_factory=error_factory,
        section_name=section_name,
    )

    if salience_mode not in {"canonical", "legacy_density"}:
        _raise(error_factory, f"{section_name}.salience_mode must be 'canonical' or 'legacy_density'")

    if base_dilation <= 0.0:
        _raise(error_factory, f"{section_name}.base_dilation_factor must be > 0.0")
    if min_rate <= 0.0:
        _raise(error_factory, f"{section_name}.min_clock_rate must be > 0.0")
    if min_rate > 1.0:
        _raise(error_factory, f"{section_name}.min_clock_rate must be <= 1.0")
    if max_rate <= 0.0:
        _raise(error_factory, f"{section_name}.max_clock_rate must be > 0.0")
    if max_rate > 1.0:
        _raise(error_factory, f"{section_name}.max_clock_rate must be <= 1.0")
    if min_rate > max_rate:
        _raise(error_factory, f"{section_name}.min_clock_rate must be <= {section_name}.max_clock_rate")
    if density_scale <= 0.0:
        _raise(error_factory, f"{section_name}.legacy_density_scale must be > 0.0")

    return base_dilation, min_rate, max_rate, salience_mode, density_scale
