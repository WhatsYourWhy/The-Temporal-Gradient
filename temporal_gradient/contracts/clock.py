from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ClockTickRequest:
    psi: float
    wall_delta: Optional[float] = None


@dataclass(frozen=True)
class ClockTickResult:
    tau_delta: float
    tau: float
    clock_rate: float
    psi: float
