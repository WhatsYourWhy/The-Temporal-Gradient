import pytest

from temporal_gradient.clock.chronos import ClockRateModulator


def test_canonical_requires_psi():
    clock = ClockRateModulator(salience_mode="canonical")
    with pytest.raises(ValueError):
        clock.tick(psi=None, wall_delta=1.0)


def test_canonical_rejects_out_of_range_psi():
    clock = ClockRateModulator(salience_mode="canonical", strict_psi_bounds=True)
    with pytest.raises(ValueError, match=r"within \[0, 1\]"):
        clock.tick(psi=1.5, wall_delta=1.0)


def test_canonical_non_strict_clamps_out_of_range_psi_for_tick_and_rate():
    clock = ClockRateModulator(salience_mode="canonical", strict_psi_bounds=False)
    tick_delta = clock.tick(psi=1.5, wall_delta=1.0)
    assert tick_delta == pytest.approx(clock.clock_rate_from_psi(1.0))
    assert clock.clock_rate_from_psi(1.5) == clock.clock_rate_from_psi(1.0)
