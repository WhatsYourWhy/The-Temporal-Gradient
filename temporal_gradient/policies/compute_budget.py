"""Backward-compatible shim for cooldown-based compute policy names.

Canonical API lives in :mod:`temporal_gradient.policies.compute_cooldown`.
"""

from .compute_cooldown import ComputeCooldownPolicy, allows_compute

# Backward-compatible alias retained for v0.2.0 import stability.
ComputeBudgetPolicy = ComputeCooldownPolicy

__all__ = ["ComputeCooldownPolicy", "ComputeBudgetPolicy", "allows_compute"]
