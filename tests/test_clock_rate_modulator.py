import math

from temporal_gradient.clock.chronos import ClockRateModulator


def test_clock_rate_monotonic_and_floor():
    modulator = ClockRateModulator(base_dilation_factor=1.0, min_clock_rate=0.05, salience_mode="legacy_density")
    psis = [0.0, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
    rates = [modulator.clock_rate_from_psi(psi) for psi in psis]

    for earlier, later in zip(rates, rates[1:]):
        assert later <= earlier

    assert rates[0] == 1.0
    assert all(rate >= modulator.min_clock_rate for rate in rates)

    high_rate = modulator.clock_rate_from_psi(1e6)
    assert math.isclose(high_rate, modulator.min_clock_rate)


def test_clock_chronology_is_canonical_and_chronolog_is_deprecated_alias():
    import pytest

    modulator = ClockRateModulator()
    modulator.tick(psi=0.0, wall_delta=1.0)

    assert len(modulator.chronology) == 1
    with pytest.deprecated_call(match="chronolog is deprecated"):
        assert modulator.chronolog is modulator.chronology
