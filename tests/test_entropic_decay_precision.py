import math

from temporal_gradient.memory.decay import decay_strength


def test_decay_floors_negative_epsilon_to_zero():
    assert decay_strength(-1e-12, elapsed_tau=10.0, half_life=10.0) == 0.0


def test_decay_uses_lambda_when_provided():
    observed = decay_strength(1.0, elapsed_tau=2.0, decay_lambda=0.5)
    assert math.isclose(observed, math.exp(-1.0))
