from dataclasses import dataclass
from typing import Optional
import json

from .schema import validate_packet_schema

@dataclass
class ChronometricVector:
    """
    The Standard Header for Temporal Gradient Communication.
    This object accompanies every message sent by the Agent.
    """
    # 1. The Anchor (Objective Reality)
    wall_clock_time: float
    
    # 2. The Field State (Internal Time Accumulator)
    tau: float
    
    # 3. The Tension Metrics
    recursion_depth: int     # How deep into memory did we reach?
    psi: Optional[float] = None        # Salience load
    salience: Optional[float] = None   # Alias for psi in canonical packets

    # 4. Optional Telemetry Extensions
    clock_rate: Optional[float] = None
    H: Optional[float] = None
    V: Optional[float] = None
    memory_strength: Optional[float] = None
    entropy_cost: float = 0.0  # How much energy did this thought burn?
    schema_version: str = "1"

    def __post_init__(self):
        if self.psi is None and self.salience is None:
            raise ValueError("psi or salience must be provided.")
        if self.psi is None:
            self.psi = self.salience
        if self.salience is None:
            self.salience = self.psi
        if self.psi is None or self.salience is None:
            raise ValueError("psi and salience could not be resolved.")
        if self.psi != self.salience:
            raise ValueError("psi and salience must match when both are provided.")

    def to_packet(self):
        """
        Serializes the vector for transmission.
        """
        packet = {
            "SCHEMA_VERSION": self.schema_version,
            "WALL_T": round(self.wall_clock_time, 2),
            "TAU": round(self.tau, 2),
            "SALIENCE": round(self.psi, 3),
            "CLOCK_RATE": round(self.clock_rate, 4) if self.clock_rate is not None else None,
            "MEMORY_S": round(self.memory_strength, 4) if self.memory_strength is not None else None,
            "DEPTH": self.recursion_depth,
        }
        if self.H is not None:
            packet["H"] = round(self.H, 4)
        if self.V is not None:
            packet["V"] = round(self.V, 4)
        return json.dumps(packet)

    @staticmethod
    def from_packet(json_str, salience_mode="canonical", clock_rate_bounds=None):
        data = json.loads(json_str)
        if salience_mode == "canonical":
            legacy_keys = {"t_obj", "r", "legacy_density", "LEGACY_DENSITY", "clock_rate", "psi"}
            if legacy_keys.intersection(data.keys()):
                raise ValueError("Legacy keys present in canonical packet.")
            validate_packet_schema(
                data,
                salience_mode="canonical",
                clock_rate_bounds=clock_rate_bounds,
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
                schema_version=data.get("SCHEMA_VERSION", "1"),
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
                schema_version=data.get("SCHEMA_VERSION", "0"),
            )
        raise ValueError(f"Unknown salience_mode: {salience_mode}")
