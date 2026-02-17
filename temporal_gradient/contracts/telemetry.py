from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TelemetryPacketContract:
    schema_version: str
    wall_clock_time: float
    tau: float
    salience: float
    recursion_depth: int
    clock_rate: Optional[float] = None
    memory_strength: Optional[float] = None
