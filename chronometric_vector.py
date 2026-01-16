from dataclasses import dataclass
from typing import Optional
import json

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
    psi: float               # Salience load
    recursion_depth: int     # How deep into memory did we reach?

    # 4. Optional Telemetry Extensions
    clock_rate: Optional[float] = None
    H: Optional[float] = None
    V: Optional[float] = None
    memory_strength: Optional[float] = None
    entropy_cost: float = 0.0  # How much energy did this thought burn?
    schema_version: str = "1"

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
    def from_packet(json_str, salience_mode="canonical"):
        data = json.loads(json_str)
        if salience_mode == "canonical":
            legacy_keys = {"t_obj", "r", "semantic_density", "clock_rate", "psi"}
            if legacy_keys.intersection(data.keys()):
                raise ValueError("Legacy keys present in canonical packet.")
            missing = {
                "SCHEMA_VERSION",
                "WALL_T",
                "TAU",
                "SALIENCE",
                "CLOCK_RATE",
                "MEMORY_S",
                "DEPTH",
            } - set(data.keys())
            if missing:
                raise ValueError(f"Missing required keys: {sorted(missing)}")
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
                psi = data.get("psi", data.get("semantic_density", data.get("SEMANTIC_DENSITY")))
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
