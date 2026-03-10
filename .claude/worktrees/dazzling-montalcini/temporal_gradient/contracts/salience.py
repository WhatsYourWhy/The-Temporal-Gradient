from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class SalienceEvaluationRequest:
    text: str


@dataclass(frozen=True)
class SalienceEvaluationResult:
    novelty: float
    value: float
    psi: float
    diagnostics: Dict[str, float]
    provenance: Dict[str, str]
