"""Backward-compatible shim for one release window."""

from __future__ import annotations

import warnings

from temporal_gradient.memory.decay import (
    DecayEngine,
    DecayMemoryStore,
    EntropicMemory,
    S_MAX,
    initial_strength_from_psi,
    should_encode,
)

warnings.warn(
    "`entropic_decay` is a compatibility shim; import from "
    "`temporal_gradient.memory.decay` instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "DecayEngine",
    "EntropicMemory",
    "initial_strength_from_psi",
    "should_encode",
    "S_MAX",
    "DecayMemoryStore",
]
