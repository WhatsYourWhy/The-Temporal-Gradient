import math
import time

from temporal_gradient.clock.validation import validate_clock_settings


class ClockRateModulator:
    """Clock-rate reparameterization for the internal time accumulator (τ).

    Canonical psi policy (`salience_mode="canonical"`):
    - `psi` is required, numeric (excluding bool), and finite.
    - `psi < 0` is clamped to `0.0`.
    - `psi > 1` is handled by `strict_psi_bounds`:
      - `True`: reject with `ValueError`.
      - `False`: clamp to `1.0`.

    The same canonicalization/rejection path is used by both
    :meth:`clock_rate_from_psi` and :meth:`tick`.
    """

    def __init__(
        self,
        base_dilation_factor=1.0,
        min_clock_rate=0.05,
        salience_mode="canonical",
        max_clock_rate=1.0,
        legacy_density_scale=100.0,
        strict_psi_bounds=False,
    ):
        self.start_wall_time = time.time()
        self.tau = 0.0
        self.last_tick = self.start_wall_time
        self.base_dilation, self.min_clock_rate, self.max_clock_rate, self.salience_mode, self.legacy_density_scale = validate_clock_settings(
            base_dilation_factor=base_dilation_factor,
            min_clock_rate=min_clock_rate,
            max_clock_rate=max_clock_rate,
            salience_mode=salience_mode,
            legacy_density_scale=legacy_density_scale,
            error_factory=ValueError,
        )
        self.strict_psi_bounds = strict_psi_bounds
        self.chronology = []


    def _validate_psi(self, psi):
        if psi is None:
            raise ValueError("psi is required in canonical mode.")
        if not isinstance(psi, (int, float)) or isinstance(psi, bool):
            raise TypeError("psi must be numeric.")
        psi = float(psi)
        if not math.isfinite(psi):
            raise ValueError("psi must be finite.")
        if psi < 0.0:
            psi = 0.0
        if self.salience_mode == "canonical" and psi > 1.0:
            if self.strict_psi_bounds:
                raise ValueError("psi must be within [0, 1] in canonical mode.")
            psi = 1.0
        return psi

    def clock_rate_from_psi(self, psi):
        """Map salience load (Ψ) to a clock-rate with a minimum floor.

        In canonical mode, this applies the same psi policy as :meth:`tick`:
        strict mode rejects `psi > 1`, non-strict mode clamps it to `1.0`.
        """
        psi = self._validate_psi(psi)
        return self._clock_rate_from_validated_psi(psi)

    def _clock_rate_from_validated_psi(self, psi):
        """Compute clock-rate from a psi value already canonicalized by `_validate_psi`."""
        scaled_psi = psi * self.base_dilation
        return min(self.max_clock_rate, max(self.min_clock_rate, 1 / (1 + scaled_psi)))

    def calculate_information_density(self, input_data):
        if not input_data:
            return 0.0
        mass = len(input_data)
        prob = [float(input_data.count(c)) / len(input_data) for c in dict.fromkeys(list(input_data))]
        entropy = -sum([p * math.log(p) / math.log(2.0) for p in prob])
        return mass * entropy

    def _psi_from_legacy_density(self, density):
        if density is None:
            return None
        scaled = density / self.legacy_density_scale
        return max(0.0, min(1.0, scaled))

    def tick(self, psi=None, input_context=None, wall_delta=None):
        """Advance τ by one tick.

        In canonical mode, psi validation/canonicalization is identical to
        :meth:`clock_rate_from_psi` (same exceptions and clamping behavior for
        `strict_psi_bounds=True/False`).
        """
        density = None
        if self.salience_mode == "legacy_density" and psi is None:
            if input_context is None:
                raise ValueError("legacy_density mode requires psi or input_context to derive psi.")
            density = self.calculate_information_density(input_context)
            psi = self._psi_from_legacy_density(density)

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

        telemetry = {
            "wall_delta": round(wall_delta, 4),
            "tau": round(self.tau, 4),
            "psi": round(psi, 4),
            "clock_rate": round(clock_rate, 4),
            "d_tau": round(tau_delta, 4),
        }
        if density is not None:
            telemetry["diagnostic_density"] = round(density, 2)
        self.chronology.append(telemetry)

        self.last_tick = current_wall_time
        return tau_delta

