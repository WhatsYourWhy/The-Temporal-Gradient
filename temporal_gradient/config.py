from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None


class ConfigValidationError(ValueError):
    """Raised when tg.yaml is malformed or out of bounds."""


DEFAULTS: dict[str, dict[str, Any]] = {
    "salience": {
        "window_size": 5,
        "keywords": ["must", "never", "critical", "always", "don't", "stop", "urgent"],
        "base_value": 0.1,
        "hit_value": 0.2,
        "max_value": 1.0,
    },
    "clock": {
        "base_dilation_factor": 1.0,
        "min_clock_rate": 0.05,
        "salience_mode": "canonical",
        "legacy_density_scale": 100.0,
    },
    "memory": {
        "half_life": 20.0,
        "prune_threshold": 0.2,
        "encode_threshold": 0.3,
        "initial_strength_max": 1.2,
        "decay_lambda": 0.05,
        "s_max": 1.5,
    },
    "policies": {
        "deterministic_seed": 1337,
        "event_wall_delta": 1.0,
        "cooldown_tau": 0.0,
        "calibration_post_sweep_wall_delta": 5.0,
        "replay_require_provenance_hash": False,
    },
}


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
    decay_lambda: float
    s_max: float


@dataclass(frozen=True)
class PoliciesConfig:
    deterministic_seed: int
    event_wall_delta: float
    cooldown_tau: float
    calibration_post_sweep_wall_delta: float
    replay_require_provenance_hash: bool


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


def _reject_unknown_keys(data: Mapping[str, Any], allowed: set[str], section_name: str) -> None:
    unknown = sorted(set(data.keys()) - allowed)
    if unknown:
        raise ConfigValidationError(f"Unknown key(s) in {section_name}: {', '.join(unknown)}")


def _check_range(
    value: float,
    section_name: str,
    key: str,
    lower: float | None = None,
    upper: float | None = None,
    inclusive_lower: bool = True,
    inclusive_upper: bool = True,
) -> None:
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


def _coerce_number(value: Any, section_name: str, key: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ConfigValidationError(f"{section_name}.{key} must be numeric")
    return float(value)


def _coerce_int(value: Any, section_name: str, key: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ConfigValidationError(f"{section_name}.{key} must be an integer")
    return value


def load_config(path: str | Path = "tg.yaml") -> TemporalGradientConfig:
    config_path = Path(path)
    raw_text = config_path.read_text()
    raw = yaml.safe_load(raw_text) if yaml is not None else _parse_simple_yaml(raw_text)
    root = _require_mapping(raw, "root")

    _reject_unknown_keys(root, set(DEFAULTS.keys()), "root")

    normalized: dict[str, dict[str, Any]] = {}
    for section, defaults in DEFAULTS.items():
        section_raw = _require_mapping(root.get(section, {}), section)
        _reject_unknown_keys(section_raw, set(defaults.keys()), section)
        merged = dict(defaults)
        merged.update(section_raw)
        normalized[section] = merged

    salience_raw = normalized["salience"]
    window_size = _coerce_int(salience_raw["window_size"], "salience", "window_size")
    _check_range(window_size, "salience", "window_size", lower=1)
    keywords = salience_raw["keywords"]
    if not isinstance(keywords, list) or not keywords or not all(isinstance(item, str) for item in keywords):
        raise ConfigValidationError("salience.keywords must be a non-empty list of strings")
    base_value = _coerce_number(salience_raw["base_value"], "salience", "base_value")
    hit_value = _coerce_number(salience_raw["hit_value"], "salience", "hit_value")
    max_value = _coerce_number(salience_raw["max_value"], "salience", "max_value")
    for key_name, val in (("base_value", base_value), ("hit_value", hit_value), ("max_value", max_value)):
        _check_range(val, "salience", key_name, lower=0.0, upper=1.0)

    clock_raw = normalized["clock"]
    base_dilation = _coerce_number(clock_raw["base_dilation_factor"], "clock", "base_dilation_factor")
    min_clock_rate = _coerce_number(clock_raw["min_clock_rate"], "clock", "min_clock_rate")
    legacy_density_scale = _coerce_number(clock_raw["legacy_density_scale"], "clock", "legacy_density_scale")
    salience_mode = clock_raw["salience_mode"]
    if salience_mode not in {"canonical", "legacy_density"}:
        raise ConfigValidationError("clock.salience_mode must be 'canonical' or 'legacy_density'")
    _check_range(base_dilation, "clock", "base_dilation_factor", lower=0.0, inclusive_lower=False)
    _check_range(min_clock_rate, "clock", "min_clock_rate", lower=0.0, upper=1.0, inclusive_lower=False)
    _check_range(legacy_density_scale, "clock", "legacy_density_scale", lower=0.0, inclusive_lower=False)

    memory_raw = normalized["memory"]
    half_life = _coerce_number(memory_raw["half_life"], "memory", "half_life")
    prune_threshold = _coerce_number(memory_raw["prune_threshold"], "memory", "prune_threshold")
    encode_threshold = _coerce_number(memory_raw["encode_threshold"], "memory", "encode_threshold")
    initial_strength_max = _coerce_number(memory_raw["initial_strength_max"], "memory", "initial_strength_max")
    decay_lambda = _coerce_number(memory_raw["decay_lambda"], "memory", "decay_lambda")
    s_max = _coerce_number(memory_raw["s_max"], "memory", "s_max")
    _check_range(half_life, "memory", "half_life", lower=0.0, inclusive_lower=False)
    _check_range(prune_threshold, "memory", "prune_threshold", lower=0.0, upper=1.0)
    _check_range(encode_threshold, "memory", "encode_threshold", lower=0.0, upper=1.0)
    _check_range(initial_strength_max, "memory", "initial_strength_max", lower=0.0, inclusive_lower=False)
    _check_range(decay_lambda, "memory", "decay_lambda", lower=0.0)
    _check_range(s_max, "memory", "s_max", lower=0.0, inclusive_lower=False)

    policies_raw = normalized["policies"]
    deterministic_seed = _coerce_int(policies_raw["deterministic_seed"], "policies", "deterministic_seed")
    event_wall_delta = _coerce_number(policies_raw["event_wall_delta"], "policies", "event_wall_delta")
    cooldown_tau = _coerce_number(policies_raw["cooldown_tau"], "policies", "cooldown_tau")
    calibration_post_sweep_wall_delta = _coerce_number(
        policies_raw["calibration_post_sweep_wall_delta"],
        "policies",
        "calibration_post_sweep_wall_delta",
    )
    replay_require_provenance_hash = policies_raw["replay_require_provenance_hash"]
    if not isinstance(replay_require_provenance_hash, bool):
        raise ConfigValidationError("policies.replay_require_provenance_hash must be a boolean")
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
            decay_lambda=decay_lambda,
            s_max=s_max,
        ),
        policies=PoliciesConfig(
            deterministic_seed=deterministic_seed,
            event_wall_delta=event_wall_delta,
            cooldown_tau=cooldown_tau,
            calibration_post_sweep_wall_delta=calibration_post_sweep_wall_delta,
            replay_require_provenance_hash=replay_require_provenance_hash,
        ),
    )


# Lightweight fallback parser retained for environments without PyYAML.
def _parse_simple_yaml(raw_text: str) -> Mapping[str, Any]:
    lines = raw_text.splitlines()

    def strip_inline_comment(token: str) -> str:
        in_single = False
        in_double = False
        for idx, char in enumerate(token):
            if char == "'" and not in_double:
                in_single = not in_single
                continue
            if char == '"' and not in_single:
                in_double = not in_double
                continue
            if char == "#" and not in_single and not in_double:
                return token[:idx].rstrip()
        return token.rstrip()

    def split_inline_array_items(token: str) -> list[str]:
        items: list[str] = []
        current: list[str] = []
        in_single = False
        in_double = False

        for char in token:
            if char == "'" and not in_double:
                in_single = not in_single
                current.append(char)
                continue
            if char == '"' and not in_single:
                in_double = not in_double
                current.append(char)
                continue
            if char == "," and not in_single and not in_double:
                item = "".join(current).strip()
                if not item:
                    raise ConfigValidationError("Malformed YAML inline array: empty item")
                items.append(item)
                current = []
                continue
            current.append(char)

        if in_single or in_double:
            raise ConfigValidationError("Malformed YAML inline array: unterminated quoted item")

        last = "".join(current).strip()
        if not last:
            raise ConfigValidationError("Malformed YAML inline array: trailing comma")
        items.append(last)
        return items

    def parse_scalar(token: str) -> Any:
        token = strip_inline_comment(token.strip())
        if token == "{}":
            return {}
        if token == "[]":
            return []
        if token.startswith("[") ^ token.endswith("]"):
            raise ConfigValidationError("Malformed YAML inline array delimiters")
        if token.startswith("[") and token.endswith("]"):
            inside = token[1:-1].strip()
            if not inside:
                return []
            return [parse_scalar(part) for part in split_inline_array_items(inside)]
        if token.startswith(("'", '"')):
            if not token.endswith(token[0]):
                raise ConfigValidationError("Malformed YAML quoted scalar delimiters")
            return token[1:-1]
        if token.endswith(("'", '"')):
            raise ConfigValidationError("Malformed YAML quoted scalar delimiters")
        lowered = token.lower()
        if lowered in {"true", "false"}:
            return lowered == "true"
        try:
            numeric_token = token.lower()
            if "." in numeric_token or "e" in numeric_token:
                return float(token)
            return int(token)
        except ValueError:
            return token

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
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
                content = strip_inline_comment(content)
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
            value = strip_inline_comment(value.strip())
            index += 1
            if value:
                obj[key] = parse_scalar(value)
            else:
                child, index = parse_block(index, indent + 2)
                obj[key] = child
        return obj, index

    parsed, _ = parse_block(0, 0)
    return parsed
