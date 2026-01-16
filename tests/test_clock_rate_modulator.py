import math

from chronos_engine import ClockRateModulator


def test_clock_rate_monotonic_and_floor():
    modulator = ClockRateModulator(base_dilation_factor=1.0, min_clock_rate=0.05)
    psis = [0.0, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
    rates = [modulator.clock_rate_from_psi(psi) for psi in psis]

    for earlier, later in zip(rates, rates[1:]):
        assert later <= earlier

    assert rates[0] == 1.0
    assert all(rate >= modulator.min_clock_rate for rate in rates)

    high_rate = modulator.clock_rate_from_psi(1e6)
    assert math.isclose(high_rate, modulator.min_clock_rate)
