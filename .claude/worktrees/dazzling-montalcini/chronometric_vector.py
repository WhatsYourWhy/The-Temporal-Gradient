"""Backward-compatible shim for one release window."""

from __future__ import annotations

import warnings

from temporal_gradient.telemetry.chronometric_vector import ChronometricVector

warnings.warn(
    "`chronometric_vector` is a compatibility shim; import from "
    "`temporal_gradient.telemetry.chronometric_vector` instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ChronometricVector"]
