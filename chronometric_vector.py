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
    entropy_cost: float = 0.0  # How much energy did this thought burn?

    def to_packet(self):
        """
        Serializes the vector for transmission.
        """
        packet = {
            "t_obj": round(self.wall_clock_time, 2),
            "tau": round(self.tau, 2),
            "psi": round(self.psi, 3), # Salience load
            "r": self.recursion_depth
        }
        if self.clock_rate is not None:
            packet["clock_rate"] = round(self.clock_rate, 4)
        if self.H is not None:
            packet["H"] = round(self.H, 4)
        if self.V is not None:
            packet["V"] = round(self.V, 4)
        return json.dumps(packet)

    @staticmethod
    def from_packet(json_str):
        data = json.loads(json_str)
        psi = data.get('psi', data.get('semantic_density'))
        return ChronometricVector(
            wall_clock_time=data['t_obj'],
            tau=data['tau'],
            psi=psi,
            recursion_depth=data['r'],
            clock_rate=data.get('clock_rate'),
            H=data.get('H'),
            V=data.get('V'),
            entropy_cost=data.get('entropy_cost', 0.0)
        )
