from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - exercised in environments without PyYAML
    yaml = None


class ConfigValidationError(ValueError):
    """Raised when tg.yaml is malformed or out of bounds."""


@dataclass(frozen=True)
class SalienceConfig:
    window_size: int
    keywords: tuple[str, ...]
    base_value: float
    hit_value: float
    max_value: float


@dataclass(frozen=True)
class ClockConfig:
    base_dilation_factor: float
    min_clock_rate: float
    salience_mode: str
    legacy_density_scale: float


@dataclass(frozen=True)
class MemoryConfig:
    half_life: float
    prune_threshold: float
    encode_threshold: float
    initial_strength_max: float


@dataclass(frozen=True)
class PoliciesConfig:
    deterministic_seed: int
    event_wall_delta: float
    cooldown_tau: float
    calibration_post_sweep_wall_delta: float


@dataclass(frozen=True)
class TemporalGradientConfig:
    salience: SalienceConfig
    clock: ClockConfig
    memory: MemoryConfig
    policies: PoliciesConfig


def _require_mapping(value: Any, section_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ConfigValidationError(f"{section_name} must be a mapping/object")
    return value


def _require_key(data: Mapping[str, Any], key: str, section_name: str) -> Any:
    if key not in data:
        raise ConfigValidationError(f"Missing required key: {section_name}.{key}")
    return data[key]


def _require_number(data: Mapping[str, Any], key: str, section_name: str) -> float:
    value = _require_key(data, key, section_name)
    if not isinstance(value, (int, float)):
        raise ConfigValidationError(f"{section_name}.{key} must be numeric")
    return float(value)


def _require_int(data: Mapping[str, Any], key: str, section_name: str) -> int:
    value = _require_key(data, key, section_name)
    if not isinstance(value, int):
        raise ConfigValidationError(f"{section_name}.{key} must be an integer")
    return value


def _check_range(value: float, section_name: str, key: str, lower: float | None = None, upper: float | None = None, inclusive_lower: bool = True, inclusive_upper: bool = True) -> None:
    if lower is not None:
        if inclusive_lower and value < lower:
            raise ConfigValidationError(f"{section_name}.{key} must be >= {lower}")
        if not inclusive_lower and value <= lower:
            raise ConfigValidationError(f"{section_name}.{key} must be > {lower}")
    if upper is not None:
        if inclusive_upper and value > upper:
            raise ConfigValidationError(f"{section_name}.{key} must be <= {upper}")
        if not inclusive_upper and value >= upper:
            raise ConfigValidationError(f"{section_name}.{key} must be < {upper}")


def load_config(path: str | Path = "tg.yaml") -> TemporalGradientConfig:
    config_path = Path(path)
    raw_text = config_path.read_text()
    if yaml is not None:
        raw = yaml.safe_load(raw_text)
    else:
        raw = _parse_simple_yaml(raw_text)
    root = _require_mapping(raw, "root")

    salience_raw = _require_mapping(_require_key(root, "salience", "root"), "salience")
    clock_raw = _require_mapping(_require_key(root, "clock", "root"), "clock")
    memory_raw = _require_mapping(_require_key(root, "memory", "root"), "memory")
    policies_raw = _require_mapping(_require_key(root, "policies", "root"), "policies")

    window_size = _require_int(salience_raw, "window_size", "salience")
    _check_range(window_size, "salience", "window_size", lower=1)

    keywords = _require_key(salience_raw, "keywords", "salience")
    if not isinstance(keywords, list) or not keywords or not all(isinstance(item, str) for item in keywords):
        raise ConfigValidationError("salience.keywords must be a non-empty list of strings")

    base_value = _require_number(salience_raw, "base_value", "salience")
    hit_value = _require_number(salience_raw, "hit_value", "salience")
    max_value = _require_number(salience_raw, "max_value", "salience")
    for key_name, val in (("base_value", base_value), ("hit_value", hit_value), ("max_value", max_value)):
        _check_range(val, "salience", key_name, lower=0.0, upper=1.0)

    base_dilation = _require_number(clock_raw, "base_dilation_factor", "clock")
    min_clock_rate = _require_number(clock_raw, "min_clock_rate", "clock")
    legacy_density_scale = _require_number(clock_raw, "legacy_density_scale", "clock")
    salience_mode = _require_key(clock_raw, "salience_mode", "clock")
    if salience_mode not in {"canonical", "legacy_density"}:
        raise ConfigValidationError("clock.salience_mode must be 'canonical' or 'legacy_density'")
    _check_range(base_dilation, "clock", "base_dilation_factor", lower=0.0, inclusive_lower=False)
    _check_range(min_clock_rate, "clock", "min_clock_rate", lower=0.0, upper=1.0, inclusive_lower=False)
    _check_range(legacy_density_scale, "clock", "legacy_density_scale", lower=0.0, inclusive_lower=False)

    half_life = _require_number(memory_raw, "half_life", "memory")
    prune_threshold = _require_number(memory_raw, "prune_threshold", "memory")
    encode_threshold = _require_number(memory_raw, "encode_threshold", "memory")
    initial_strength_max = _require_number(memory_raw, "initial_strength_max", "memory")
    _check_range(half_life, "memory", "half_life", lower=0.0, inclusive_lower=False)
    _check_range(prune_threshold, "memory", "prune_threshold", lower=0.0, upper=1.0)
    _check_range(encode_threshold, "memory", "encode_threshold", lower=0.0, upper=1.0)
    _check_range(initial_strength_max, "memory", "initial_strength_max", lower=0.0, inclusive_lower=False)

    deterministic_seed = _require_int(policies_raw, "deterministic_seed", "policies")
    event_wall_delta = _require_number(policies_raw, "event_wall_delta", "policies")
    cooldown_tau = _require_number(policies_raw, "cooldown_tau", "policies")
    calibration_post_sweep_wall_delta = _require_number(
        policies_raw,
        "calibration_post_sweep_wall_delta",
        "policies",
    )
    _check_range(event_wall_delta, "policies", "event_wall_delta", lower=0.0, inclusive_lower=False)
    _check_range(cooldown_tau, "policies", "cooldown_tau", lower=0.0)
    _check_range(
        calibration_post_sweep_wall_delta,
        "policies",
        "calibration_post_sweep_wall_delta",
        lower=0.0,
        inclusive_lower=False,
    )

    return TemporalGradientConfig(
        salience=SalienceConfig(
            window_size=window_size,
            keywords=tuple(keywords),
            base_value=base_value,
            hit_value=hit_value,
            max_value=max_value,
        ),
        clock=ClockConfig(
            base_dilation_factor=base_dilation,
            min_clock_rate=min_clock_rate,
            salience_mode=salience_mode,
            legacy_density_scale=legacy_density_scale,
        ),
        memory=MemoryConfig(
            half_life=half_life,
            prune_threshold=prune_threshold,
            encode_threshold=encode_threshold,
            initial_strength_max=initial_strength_max,
        ),
        policies=PoliciesConfig(
            deterministic_seed=deterministic_seed,
            event_wall_delta=event_wall_delta,
            cooldown_tau=cooldown_tau,
            calibration_post_sweep_wall_delta=calibration_post_sweep_wall_delta,
        ),
    )


def _parse_simple_yaml(raw_text: str) -> Mapping[str, Any]:
    lines = raw_text.splitlines()

    def parse_scalar(token: str) -> Any:
        token = token.strip()
        if token.startswith("[") and token.endswith("]"):
            inside = token[1:-1].strip()
            if not inside:
                return []
            return [parse_scalar(part.strip()) for part in inside.split(",")]
        if token.startswith(("'", '"')) and token.endswith(("'", '"')):
            return token[1:-1]
        lowered = token.lower()
        if lowered in {"true", "false"}:
            return lowered == "true"
        try:
            if "." in token:
                return float(token)
            return int(token)
        except ValueError:
            return token

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        # Skip blank/comment lines.
        while index < len(lines) and (not lines[index].strip() or lines[index].lstrip().startswith("#")):
            index += 1
        if index >= len(lines):
            return {}, index

        is_list = lines[index].lstrip().startswith("-")
        if is_list:
            items: list[Any] = []
            while index < len(lines):
                raw = lines[index]
                if not raw.strip() or raw.lstrip().startswith("#"):
                    index += 1
                    continue
                current_indent = len(raw) - len(raw.lstrip(" "))
                if current_indent < indent:
                    break
                if current_indent != indent or not raw.lstrip().startswith("-"):
                    raise ConfigValidationError("Invalid YAML list indentation")
                content = raw.lstrip()[1:].strip()
                index += 1
                if content:
                    items.append(parse_scalar(content))
                else:
                    child, index = parse_block(index, indent + 2)
                    items.append(child)
            return items, index

        obj: dict[str, Any] = {}
        while index < len(lines):
            raw = lines[index]
            if not raw.strip() or raw.lstrip().startswith("#"):
                index += 1
                continue
            current_indent = len(raw) - len(raw.lstrip(" "))
            if current_indent < indent:
                break
            if current_indent != indent:
                raise ConfigValidationError("Invalid YAML mapping indentation")
            stripped = raw.strip()
            if ":" not in stripped:
                raise ConfigValidationError("Invalid YAML key-value entry")
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            index += 1
            if value:
                obj[key] = parse_scalar(value)
            else:
                child, index = parse_block(index, indent + 2)
                obj[key] = child
        return obj, index

    parsed, _ = parse_block(0, 0)
    return parsed
