import math
import time

from temporal_gradient.clock.validation import validate_clock_settings


class ClockRateModulator:
    """Clock-rate reparameterization for the internal time accumulator (τ).

    `psi` must be a finite number. `psi < 0` is clamped to 0.0. `psi > 1` is
    either rejected (``strict_psi_bounds=True``) or clamped to 1.0
    (``strict_psi_bounds=False``, the default).
    """

    def __init__(
        self,
        base_dilation_factor: float = 1.0,
        min_clock_rate: float = 0.05,
        max_clock_rate: float = 1.0,
        strict_psi_bounds: bool = False,
    ) -> None:
        self.start_wall_time = time.time()
        self.tau = 0.0
        self.last_tick = self.start_wall_time
        self.base_dilation, self.min_clock_rate, self.max_clock_rate = validate_clock_settings(
            base_dilation_factor=base_dilation_factor,
            min_clock_rate=min_clock_rate,
            max_clock_rate=max_clock_rate,
            error_factory=ValueError,
        )
        self.strict_psi_bounds = strict_psi_bounds
        self.chronology: list[dict] = []

    def _validate_psi(self, psi) -> float:
        if psi is None:
            raise ValueError("psi is required.")
        if not isinstance(psi, (int, float)) or isinstance(psi, bool):
            raise TypeError("psi must be numeric.")
        psi = float(psi)
        if not math.isfinite(psi):
            raise ValueError("psi must be finite.")
        if psi < 0.0:
            psi = 0.0
        if psi > 1.0:
            if self.strict_psi_bounds:
                raise ValueError("psi must be within [0, 1].")
            psi = 1.0
        return psi

    def clock_rate_from_psi(self, psi) -> float:
        return self._clock_rate_from_validated_psi(self._validate_psi(psi))

    def _clock_rate_from_validated_psi(self, psi: float) -> float:
        scaled_psi = psi * self.base_dilation
        return min(self.max_clock_rate, max(self.min_clock_rate, 1 / (1 + scaled_psi)))

    def tick(self, psi, wall_delta: float | None = None) -> float:
        """Advance τ by ``wall_delta`` scaled by the salience-modulated clock rate."""
        psi = self._validate_psi(psi)

        current_wall_time = time.time()
        if wall_delta is None:
            wall_delta = current_wall_time - self.last_tick
        else:
            if wall_delta < 0:
                raise ValueError("wall_delta must be non-negative")
            current_wall_time = self.last_tick + wall_delta

        clock_rate = self._clock_rate_from_validated_psi(psi)
        tau_delta = wall_delta * clock_rate
        self.tau += tau_delta

        self.chronology.append({
            "wall_delta": round(wall_delta, 4),
            "tau": round(self.tau, 4),
            "psi": round(psi, 4),
            "clock_rate": round(clock_rate, 4),
            "d_tau": round(tau_delta, 4),
        })

        self.last_tick = current_wall_time
        return tau_delta
