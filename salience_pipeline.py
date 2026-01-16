from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Protocol, Tuple, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from codex_valuation import CodexValuator


class NoveltyScorer(Protocol):
    def score(self, text: str) -> Tuple[float, Dict[str, float]]:
        ...


class ValueScorer(Protocol):
    def score(self, text: str) -> Tuple[float, Dict[str, float]]:
        ...


@dataclass(frozen=True)
class SalienceComponents:
    novelty: float
    value: float
    psi: float
    diagnostics: Dict[str, float] = field(default_factory=dict)

    def telemetry_dict(self) -> Dict[str, float]:
        telemetry = {
            "H": float(self.novelty),
            "V": float(self.value),
            "psi": float(self.psi),
        }
        telemetry.update({key: float(val) for key, val in self.diagnostics.items()})
        return telemetry


class RollingJaccardNovelty:
    def __init__(self, window_size: int = 5) -> None:
        self.window_size = window_size
        self._history: List[set[str]] = []
        self._token_pattern = re.compile(r"[a-z0-9']+")

    def _tokenize(self, text: str) -> set[str]:
        return set(self._token_pattern.findall(text.lower()))

    def score(self, text: str) -> Tuple[float, Dict[str, float]]:
        tokens = self._tokenize(text)
        max_similarity = 0.0

        if tokens and self._history:
            for past_tokens in self._history:
                union = tokens | past_tokens
                if not union:
                    similarity = 0.0
                else:
                    similarity = len(tokens & past_tokens) / len(union)
                max_similarity = max(max_similarity, similarity)

        novelty = 1.0 - max_similarity

        self._history.append(tokens)
        if len(self._history) > self.window_size:
            self._history = self._history[-self.window_size :]

        diagnostics = {
            "H_jaccard_max": max_similarity,
            "H_tokens": float(len(tokens)),
            "H_history": float(len(self._history)),
        }
        return novelty, diagnostics


class KeywordImperativeValue:
    def __init__(
        self,
        keywords: Iterable[str] | None = None,
        base_value: float = 0.1,
        hit_value: float = 0.2,
        max_value: float = 1.0,
    ) -> None:
        if keywords is None:
            keywords = ["must", "never", "critical", "always", "don't", "stop", "urgent"]
        self.keywords = tuple(keywords)
        self.base_value = base_value
        self.hit_value = hit_value
        self.max_value = max_value
        self._patterns = [re.compile(rf"\b{re.escape(keyword.lower())}\b") for keyword in self.keywords]

    def score(self, text: str) -> Tuple[float, Dict[str, float]]:
        lowered = text.lower()
        hits = 0
        for pattern in self._patterns:
            if pattern.search(lowered):
                hits += 1
        value = min(self.max_value, self.base_value + (self.hit_value * hits))
        diagnostics = {
            "V_keyword_hits": float(hits),
            "V_keyword_count": float(len(self.keywords)),
            "V_base_value": float(self.base_value),
        }
        return value, diagnostics


class SaliencePipeline:
    def __init__(self, novelty_scorer: NoveltyScorer, value_scorer: ValueScorer) -> None:
        self.novelty_scorer = novelty_scorer
        self.value_scorer = value_scorer

    def evaluate(self, text: str) -> SalienceComponents:
        novelty, novelty_diag = self.novelty_scorer.score(text)
        value, value_diag = self.value_scorer.score(text)
        psi = novelty * value
        diagnostics: Dict[str, float] = {}
        diagnostics.update(novelty_diag)
        diagnostics.update(value_diag)
        return SalienceComponents(novelty=novelty, value=value, psi=psi, diagnostics=diagnostics)


class CodexNoveltyAdapter:
    def __init__(self, codex: "CodexValuator") -> None:
        self.codex = codex

    def score(self, text: str) -> Tuple[float, Dict[str, float]]:
        return self.codex.score_H(text)


class CodexValueAdapter:
    def __init__(self, codex: "CodexValuator") -> None:
        self.codex = codex

    def score(self, text: str) -> Tuple[float, Dict[str, float]]:
        return self.codex.score_V(text)
