from dataclasses import dataclass
import json
from typing import Any, Mapping, Optional

from .schema import CANONICAL_SCHEMA_VERSION, normalize_schema_version, validate_packet_schema


@dataclass
class ChronometricVector:
    wall_clock_time: float
    tau: float
    recursion_depth: int
    psi: Optional[float] = None
    salience: Optional[float] = None
    clock_rate: Optional[float] = None
    H: Optional[float] = None
    V: Optional[float] = None
    memory_strength: Optional[float] = None
    entropy_cost: float = 0.0
    provenance_hash: Optional[str] = None
    schema_version: str = CANONICAL_SCHEMA_VERSION

    def __post_init__(self):
        if self.psi is None and self.salience is None:
            raise ValueError("psi or salience must be provided.")
        if self.psi is None:
            self.psi = self.salience
        if self.salience is None:
            self.salience = self.psi
        if self.psi != self.salience:
            raise ValueError("psi and salience must match when both are provided.")

        if not isinstance(self.schema_version, str):
            raise TypeError("schema_version must be a string")
        self.schema_version = normalize_schema_version(self.schema_version)

    def to_packet(self) -> dict[str, Any]:
        packet = {
            "SCHEMA_VERSION": CANONICAL_SCHEMA_VERSION,
            "WALL_T": round(float(self.wall_clock_time), 2),
            "TAU": round(float(self.tau), 2),
            "SALIENCE": round(float(self.psi), 3),
            "CLOCK_RATE": round(float(self.clock_rate), 4) if self.clock_rate is not None else 0.0,
            "MEMORY_S": round(float(self.memory_strength), 4) if self.memory_strength is not None else 0.0,
            "DEPTH": int(self.recursion_depth),
        }
        if self.H is not None:
            packet["H"] = round(float(self.H), 4)
        if self.V is not None:
            packet["V"] = round(float(self.V), 4)
        if self.provenance_hash is not None:
            packet["PROVENANCE_HASH"] = self.provenance_hash

        validate_packet_schema(packet, salience_mode="canonical")
        return packet

    def to_packet_json(self) -> str:
        """Return the canonical packet as a JSON string.

        `to_packet()` is the canonical mapping representation used by schema
        validators and examples. This method is provided for integrations that
        still need serialized JSON.
        """
        return json.dumps(self.to_packet())

    @staticmethod
    def from_packet(
        packet: str | Mapping[str, Any],
        salience_mode="canonical",
        clock_rate_bounds=None,
        require_provenance_hash: bool = False,
    ):
        data = json.loads(packet) if isinstance(packet, str) else dict(packet)
        if salience_mode == "canonical":
            legacy_keys = {"t_obj", "r", "legacy_density", "LEGACY_DENSITY", "clock_rate", "psi"}
            if legacy_keys.intersection(data.keys()):
                raise ValueError("Legacy keys present in canonical packet.")
            validate_packet_schema(
                data,
                salience_mode="canonical",
                clock_rate_bounds=clock_rate_bounds,
                require_provenance_hash=require_provenance_hash,
            )
            return ChronometricVector(
                wall_clock_time=data["WALL_T"],
                tau=data["TAU"],
                psi=data["SALIENCE"],
                recursion_depth=data["DEPTH"],
                clock_rate=data.get("CLOCK_RATE"),
                H=data.get("H"),
                V=data.get("V"),
                memory_strength=data.get("MEMORY_S"),
                entropy_cost=data.get("entropy_cost", 0.0),
                provenance_hash=data.get("PROVENANCE_HASH"),
                schema_version=normalize_schema_version(data.get("SCHEMA_VERSION", CANONICAL_SCHEMA_VERSION)),
            )
        if salience_mode == "legacy_density":
            wall_clock = data.get("WALL_T", data.get("t_obj"))
            tau = data.get("TAU", data.get("tau"))
            psi = data.get("SALIENCE")
            if psi is None:
                psi = data.get("psi", data.get("legacy_density", data.get("LEGACY_DENSITY")))
            if wall_clock is None or tau is None or psi is None:
                raise ValueError("Legacy packet missing required keys.")
            depth = data.get("DEPTH", data.get("r", 0))
            legacy_schema_version = data.get("SCHEMA_VERSION", CANONICAL_SCHEMA_VERSION)
            if isinstance(legacy_schema_version, str):
                try:
                    legacy_schema_version = normalize_schema_version(legacy_schema_version)
                except ValueError:
                    legacy_schema_version = CANONICAL_SCHEMA_VERSION
            else:
                legacy_schema_version = CANONICAL_SCHEMA_VERSION

            return ChronometricVector(
                wall_clock_time=wall_clock,
                tau=tau,
                psi=psi,
                recursion_depth=depth,
                clock_rate=data.get("CLOCK_RATE", data.get("clock_rate")),
                H=data.get("H"),
                V=data.get("V"),
                memory_strength=data.get("MEMORY_S", data.get("S")),
                entropy_cost=data.get("entropy_cost", 0.0),
                schema_version=legacy_schema_version,
            )
        raise ValueError(f"Unknown salience_mode: {salience_mode}")
