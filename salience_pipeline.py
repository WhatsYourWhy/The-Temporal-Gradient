"""Backward-compatible shim for one release window."""

from __future__ import annotations

import warnings

from temporal_gradient.salience.pipeline import (
    CodexNoveltyAdapter,
    CodexValueAdapter,
    KeywordImperativeValue,
    NoveltyScorer,
    ResettableScorer,
    RollingJaccardNovelty,
    SalienceComponents,
    SaliencePipeline,
    ValueScorer,
)

warnings.warn(
    "`salience_pipeline` is a compatibility shim; import from "
    "`temporal_gradient.salience.pipeline` instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "SaliencePipeline",
    "SalienceComponents",
    "RollingJaccardNovelty",
    "KeywordImperativeValue",
    "CodexNoveltyAdapter",
    "CodexValueAdapter",
    "NoveltyScorer",
    "ValueScorer",
    "ResettableScorer",
]
