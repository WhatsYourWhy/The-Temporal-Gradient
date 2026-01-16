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

    def to_packet(self):
        """
        Serializes the vector for transmission.
        """
        packet = {
            "WALL_T": round(self.wall_clock_time, 2),
            "TAU": round(self.tau, 2),
            "SALIENCE": round(self.psi, 3), # Salience load
            "DEPTH": self.recursion_depth,
        }
        if self.clock_rate is not None:
            packet["CLOCK_RATE"] = round(self.clock_rate, 4)
        if self.H is not None:
            packet["H"] = round(self.H, 4)
        if self.V is not None:
            packet["V"] = round(self.V, 4)
        if self.memory_strength is not None:
            packet["MEMORY_S"] = round(self.memory_strength, 4)
        return json.dumps(packet)

    @staticmethod
    def from_packet(json_str, salience_mode="canonical"):
        data = json.loads(json_str)
        if salience_mode not in {"canonical", "legacy_density"}:
            raise ValueError("salience_mode must be 'canonical' or 'legacy_density'.")
        psi = data.get('SALIENCE')
        if psi is None and salience_mode == "legacy_density":
            psi = data.get('semantic_density', data.get('SEMANTIC_DENSITY'))
        return ChronometricVector(
            wall_clock_time=data['WALL_T'],
            tau=data['TAU'],
            psi=psi,
            recursion_depth=data.get('DEPTH', 0),
            clock_rate=data.get('CLOCK_RATE'),
            H=data.get('H'),
            V=data.get('V'),
            memory_strength=data.get('MEMORY_S', data.get('S')),
            entropy_cost=data.get('entropy_cost', 0.0),
        )
