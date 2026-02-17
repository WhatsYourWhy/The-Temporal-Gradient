from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ComputeBudgetPolicy:
    """Simple cooldown-based compute gating policy."""

    cooldown_tau: float = 0.0

    def allows_compute(self, *, elapsed_tau: float) -> bool:
        return elapsed_tau >= self.cooldown_tau


def allows_compute(*, elapsed_tau: float, cooldown_tau: float = 0.0) -> bool:
    """Return whether compute is allowed under a cooldown budget."""
    return ComputeBudgetPolicy(cooldown_tau=cooldown_tau).allows_compute(elapsed_tau=elapsed_tau)
