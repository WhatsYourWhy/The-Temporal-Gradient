from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryEncodingDecision:
    should_encode: bool
    psi: float
    threshold: float
    initial_strength: float


@dataclass(frozen=True)
class MemoryDecaySnapshot:
    memory_id: str
    current_strength: float
    pruned: bool
