from temporal_gradient.clock.chronos import ClockRateModulator
from temporal_gradient.contracts.clock import ClockTickRequest


def test_clock_tick_request_and_modulator_round_trip():
    req = ClockTickRequest(psi=0.5, wall_delta=1.0)
    clock = ClockRateModulator(salience_mode="canonical")
    delta = clock.tick(psi=req.psi, wall_delta=req.wall_delta)
    assert delta > 0
    assert clock.tau > 0
