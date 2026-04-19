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
            "SCHEMA_VERSION": self.schema_version,
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
        if self.entropy_cost != 0.0:
            packet["entropy_cost"] = round(float(self.entropy_cost), 4)
        if self.provenance_hash is not None:
            packet["PROVENANCE_HASH"] = self.provenance_hash

        validate_packet_schema(packet)
        return packet

    def to_packet_json(self) -> str:
        return json.dumps(self.to_packet())

    @staticmethod
    def from_packet(
        packet: str | Mapping[str, Any],
        clock_rate_bounds=None,
        require_provenance_hash: bool = False,
    ) -> "ChronometricVector":
        data = json.loads(packet) if isinstance(packet, str) else dict(packet)
        validate_packet_schema(
            data,
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
