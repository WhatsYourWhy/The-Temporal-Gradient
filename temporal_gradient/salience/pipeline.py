from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Protocol, Tuple, TYPE_CHECKING, runtime_checkable
import re

if TYPE_CHECKING:
    from codex_valuation import CodexValuator


class NoveltyScorer(Protocol):
    def score(self, text: str) -> Tuple[float, Dict[str, float], Dict[str, str]]:
        ...


class ValueScorer(Protocol):
    def score(self, text: str) -> Tuple[float, Dict[str, float], Dict[str, str]]:
        ...


@runtime_checkable
class ResettableScorer(Protocol):
    """Protocol for scorers that keep mutable runtime history.

    Reset contract:
    - ``reset()`` clears mutable runtime history only.
    - ``reset()`` must not alter scorer configuration parameters.
    - ``reset()`` is required to support deterministic replay when scorer
      instances are reused across multiple runs.
    """

    def reset(self) -> None:
        ...


@dataclass(frozen=True)
class SalienceComponents:
    novelty: float
    value: float
    psi: float
    diagnostics: Dict[str, float] = field(default_factory=dict)
    provenance: Dict[str, str] = field(default_factory=dict)

    def telemetry_dict(self) -> Dict[str, float]:
        telemetry = {
            "H": float(self.novelty),
            "V": float(self.value),
            "psi": float(self.psi),
        }
        telemetry.update({key: float(val) for key, val in self.diagnostics.items()})
        return telemetry

    def provenance_dict(self) -> Dict[str, str]:
        return dict(self.provenance)


class RollingJaccardNovelty:
    def __init__(self, window_size: int = 5) -> None:
        self.window_size = window_size
        self._history: List[set[str]] = []
        self._token_pattern = re.compile(r"[a-z0-9']+")

    def _tokenize(self, text: str) -> set[str]:
        return set(self._token_pattern.findall(text.lower()))

    def reset(self) -> None:
        self._history.clear()

    def score(self, text: str) -> Tuple[float, Dict[str, float], Dict[str, str]]:
        tokens = self._tokenize(text)
        if not tokens:
            self._history.append(tokens)
            if len(self._history) > self.window_size:
                self._history = self._history[-self.window_size :]
            return (
                0.0,
                {
                    "H_jaccard_max": 0.0,
                    "H_tokens": 0.0,
                    "H_history": float(len(self._history)),
                },
                {
                    "window_size": str(self.window_size),
                    "token_count": str(len(tokens)),
                },
            )
        max_similarity = 0.0

        if tokens and self._history:
            for past_tokens in self._history:
                union = tokens | past_tokens
                if not union:
                    similarity = 0.0
                else:
                    similarity = len(tokens & past_tokens) / len(union)
                max_similarity = max(max_similarity, similarity)

        novelty = max(0.0, min(1.0, 1.0 - max_similarity))

        self._history.append(tokens)
        if len(self._history) > self.window_size:
            self._history = self._history[-self.window_size :]

        diagnostics = {
            "H_jaccard_max": max_similarity,
            "H_tokens": float(len(tokens)),
            "H_history": float(len(self._history)),
        }
        return novelty, diagnostics, {
            "window_size": str(self.window_size),
            "token_count": str(len(tokens)),
        }


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

    def score(self, text: str) -> Tuple[float, Dict[str, float], Dict[str, str]]:
        lowered = text.lower()
        hits = 0
        for pattern in self._patterns:
            if pattern.search(lowered):
                hits += 1
        value = min(self.max_value, self.base_value + (self.hit_value * hits))
        value = max(0.0, min(1.0, value))
        diagnostics = {
            "V_keyword_hits": float(hits),
            "V_keyword_count": float(len(self.keywords)),
            "V_base_value": float(self.base_value),
        }
        return value, diagnostics, {
            "keyword_count": str(len(self.keywords)),
            "keyword_hits": str(hits),
        }


class SaliencePipeline:
    def __init__(self, novelty_scorer: NoveltyScorer, value_scorer: ValueScorer) -> None:
        self.novelty_scorer = novelty_scorer
        self.value_scorer = value_scorer

    def evaluate(self, text: str) -> SalienceComponents:
        novelty, novelty_diag, novelty_provenance = self.novelty_scorer.score(text)
        value, value_diag, value_provenance = self.value_scorer.score(text)
        novelty = max(0.0, min(1.0, novelty))
        value = max(0.0, min(1.0, value))
        psi = max(0.0, min(1.0, novelty * value))
        diagnostics: Dict[str, float] = {}
        provenance: Dict[str, str] = {}
        diagnostics.update(novelty_diag)
        diagnostics.update(value_diag)
        provenance.update({f"H_{key}": val for key, val in novelty_provenance.items()})
        provenance.update({f"V_{key}": val for key, val in value_provenance.items()})
        return SalienceComponents(
            novelty=novelty,
            value=value,
            psi=psi,
            diagnostics=diagnostics,
            provenance=provenance,
        )

    def reset(self) -> None:
        """Reset runtime scorer state while preserving configured components.

        The pipeline reset contract is intentionally narrow:
        - clears mutable runtime history in resettable scorers only,
        - does not alter scorer configuration (for example ``window_size`` or
          keyword configuration), and
        - enables deterministic replay when the same scorer instances are
          reused for a subsequent run.
        """
        for scorer in (self.novelty_scorer, self.value_scorer):
            if isinstance(scorer, ResettableScorer):
                scorer.reset()


class CodexNoveltyAdapter:
    def __init__(self, codex: "CodexValuator") -> None:
        self.codex = codex

    def score(self, text: str) -> Tuple[float, Dict[str, float], Dict[str, str]]:
        score, diagnostics = self.codex.score_H(text)
        return score, diagnostics, {
            "method": "codex_novelty",
            "codex_version": str(getattr(self.codex, "version", "unknown")),
            "adapter_class": self.__class__.__name__,
        }


class CodexValueAdapter:
    def __init__(self, codex: "CodexValuator") -> None:
        self.codex = codex

    def score(self, text: str) -> Tuple[float, Dict[str, float], Dict[str, str]]:
        score, diagnostics = self.codex.score_V(text)
        return score, diagnostics, {
            "method": "codex_value",
            "codex_version": str(getattr(self.codex, "version", "unknown")),
            "adapter_class": self.__class__.__name__,
        }
