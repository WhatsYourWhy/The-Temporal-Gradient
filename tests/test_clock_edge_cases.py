import math

import pytest

from temporal_gradient.clock.chronos import ClockRateModulator


def test_clock_rate_from_psi_clamps_negative_psi_to_zero():
    clock = ClockRateModulator()
    assert clock.clock_rate_from_psi(-5.0) == clock.clock_rate_from_psi(0.0)


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_clock_rate_from_psi_rejects_non_finite_values(bad):
    clock = ClockRateModulator()
    with pytest.raises(ValueError, match="finite"):
        clock.clock_rate_from_psi(bad)


def test_tick_rejects_non_finite_psi():
    clock = ClockRateModulator()
    with pytest.raises(ValueError, match="finite"):
        clock.tick(psi=math.inf, wall_delta=1.0)


def test_tick_and_rate_validation_are_consistent_in_strict_mode():
    clock = ClockRateModulator(salience_mode="canonical", strict_psi_bounds=True)
    with pytest.raises(ValueError):
        clock.clock_rate_from_psi(1.5)
    with pytest.raises(ValueError):
        clock.tick(psi=1.5, wall_delta=1.0)


def test_tick_rejects_negative_wall_delta():
    clock = ClockRateModulator()
    with pytest.raises(ValueError, match="wall_delta must be non-negative"):
        clock.tick(psi=0.5, wall_delta=-0.1)
