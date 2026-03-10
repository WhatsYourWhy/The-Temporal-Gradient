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


@pytest.mark.parametrize(
    "strict, psi, should_raise",
    [
        (False, -0.5, False),
        (False, 0.3, False),
        (False, 1.5, False),
        (True, -0.5, False),
        (True, 0.3, False),
        (True, 1.5, True),
    ],
)
def test_tick_and_rate_have_identical_canonical_psi_policy(strict, psi, should_raise):
    clock = ClockRateModulator(salience_mode="canonical", strict_psi_bounds=strict)

    if should_raise:
        with pytest.raises(ValueError, match=r"within \[0, 1\]"):
            clock.clock_rate_from_psi(psi)
        with pytest.raises(ValueError, match=r"within \[0, 1\]"):
            clock.tick(psi=psi, wall_delta=1.0)
    else:
        rate = clock.clock_rate_from_psi(psi)
        tick_delta = clock.tick(psi=psi, wall_delta=1.0)
        assert tick_delta == pytest.approx(rate)


def test_tick_rejects_negative_wall_delta():
    clock = ClockRateModulator()
    with pytest.raises(ValueError, match="wall_delta must be non-negative"):
        clock.tick(psi=0.5, wall_delta=-0.1)


def test_tick_validates_psi_once_before_internal_rate_calculation(monkeypatch):
    clock = ClockRateModulator()
    calls = {"count": 0}
    original_validate = clock._validate_psi

    def spy_validate(psi):
        calls["count"] += 1
        return original_validate(psi)

    monkeypatch.setattr(clock, "_validate_psi", spy_validate)

    tick_delta = clock.tick(psi=0.3, wall_delta=1.0)
    assert calls["count"] == 1
    assert tick_delta == pytest.approx(clock.clock_rate_from_psi(0.3))
