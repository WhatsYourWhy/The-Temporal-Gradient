from dataclasses import dataclass
import json

@dataclass
class ChronometricVector:
    """
    The Standard Header for Temporal Gradient Communication.
    This object accompanies every message sent by the Agent.
    """
    # 1. The Anchor (Objective Reality)
    wall_clock_time: float
    
    # 2. The Field State (Subjective Reality)
    subjective_time: float
    
    # 3. The Tension Metrics
    entropy_cost: float       # How much energy did this thought burn?
    semantic_density: float   # How complex is the current context?
    recursion_depth: int      # How deep into memory did we reach?

    def to_packet(self):
        """
        Serializes the vector for transmission.
        """
        return json.dumps({
            "t_obj": round(self.wall_clock_time, 2),
            "t_subj": round(self.subjective_time, 2),
            "psi": round(self.semantic_density, 3), # Information Density
            "r": self.recursion_depth
        })

    @staticmethod
    def from_packet(json_str):
        data = json.loads(json_str)
        return ChronometricVector(
            wall_clock_time=data['t_obj'],
            subjective_time=data['t_subj'],
            entropy_cost=0.0, # Usually lost in transmission unless specified
            semantic_density=data['psi'],
            recursion_depth=data['r']
        )
