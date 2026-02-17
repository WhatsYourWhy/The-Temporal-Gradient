from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ComputeCooldownPolicy:
    """Cooldown-based gate that allows compute once elapsed τ meets a threshold."""

    cooldown_tau: float = 0.0

    def allows_compute(self, *, elapsed_tau: float) -> bool:
        """Return whether compute is allowed for the elapsed internal time τ."""
        return elapsed_tau >= self.cooldown_tau


def allows_compute(*, elapsed_tau: float, cooldown_tau: float = 0.0) -> bool:
    """Compatibility helper for cooldown gating based on elapsed internal time τ."""
    return ComputeCooldownPolicy(cooldown_tau=cooldown_tau).allows_compute(elapsed_tau=elapsed_tau)
