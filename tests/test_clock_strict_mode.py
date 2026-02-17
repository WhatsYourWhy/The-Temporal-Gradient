import pytest

from temporal_gradient.clock.chronos import ClockRateModulator


def test_canonical_requires_psi():
    clock = ClockRateModulator(salience_mode="canonical")
    with pytest.raises(ValueError):
        clock.tick(psi=None, wall_delta=1.0)


def test_canonical_rejects_out_of_range_psi():
    clock = ClockRateModulator(salience_mode="canonical")
    with pytest.raises(ValueError):
        clock.tick(psi=1.5, wall_delta=1.0)
