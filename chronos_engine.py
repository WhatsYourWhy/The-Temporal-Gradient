"""Backward-compatible shim for one release window."""

from __future__ import annotations

import warnings

from temporal_gradient.clock.chronos import ClockRateModulator

warnings.warn(
    "`chronos_engine` is a compatibility shim; import from "
    "`temporal_gradient.clock.chronos` instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ClockRateModulator"]
