import math
import textwrap
import time
import warnings

from temporal_gradient.salience.pipeline import KeywordImperativeValue, RollingJaccardNovelty, SaliencePipeline
from temporal_gradient.telemetry.chronometric_vector import ChronometricVector


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
        legacy_density_scale=100.0,
        strict_psi_bounds=False,
    ):
        self.start_wall_time = time.time()
        self.tau = 0.0
        self.base_dilation = base_dilation_factor
        self.min_clock_rate = min_clock_rate
        self.last_tick = self.start_wall_time
        self.salience_mode = self._validate_salience_mode(salience_mode)
        self.legacy_density_scale = legacy_density_scale
        self.strict_psi_bounds = strict_psi_bounds
        self.chronology = []

    @property
    def chronolog(self):
        warnings.warn(
            "ClockRateModulator.chronolog is deprecated; use chronology instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.chronology

    @chronolog.setter
    def chronolog(self, value):
        warnings.warn(
            "ClockRateModulator.chronolog is deprecated; use chronology instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.chronology = value

    def _validate_salience_mode(self, salience_mode):
        valid_modes = {"canonical", "legacy_density"}
        if salience_mode not in valid_modes:
            valid = ", ".join(sorted(valid_modes))
            raise ValueError(f"salience_mode must be one of: {valid}")
        return salience_mode

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
        scaled_psi = psi * self.base_dilation
        return max(self.min_clock_rate, 1 / (1 + scaled_psi))

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

        clock_rate = self.clock_rate_from_psi(psi)
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


if __name__ == "__main__":
    agent_clock = ClockRateModulator()
    salience = SaliencePipeline(RollingJaccardNovelty(), KeywordImperativeValue())

    print(
        f"{'EVENT':<20} | {'WALL_T':<8} | {'TAU':<10} | {'SALIENCE':<9} | "
        f"{'CLOCK_RATE':<10} | {'MEMORY_S':<8} | {'DEPTH'}"
    )
    print("-" * 90)

    simulated_events = [
        "",
        "Hello.",
        "The quick brown fox jumps over the dog",
        textwrap.dedent(
            """
            Time is a field gradient formed by memory + change.
            Entropy’s arrow is not time itself, but an emergent
            direction from memory accumulation.
        """
        )
        * 5,
    ]

    start_time = time.time()
    for event in simulated_events:
        time.sleep(1.0)

        sal = salience.evaluate(event)
        psi = sal.psi

        agent_clock.tick(psi)
        wall_time = time.time() - start_time

        label = (event[:15] + "...") if len(event) > 15 else (event if event else "[EMPTY INPUT]")

        packet = ChronometricVector(
            wall_clock_time=wall_time,
            tau=agent_clock.tau,
            psi=psi,
            recursion_depth=0,
            clock_rate=agent_clock.clock_rate_from_psi(psi),
            H=sal.novelty,
            V=sal.value,
            memory_strength=0.0,
        ).to_packet()

        print(
            f"{label:<20} | {wall_time:<8.2f} | {agent_clock.tau:<10.4f} | {psi:<9.3f} | "
            f"{agent_clock.clock_rate_from_psi(psi):<10.4f} | {0.0:<8.2f} | {0}"
        )
        print(f"{'PACKET':<8} | {packet}")
