import math

import pytest

from temporal_gradient.memory.decay import decay_strength


def test_decay_floors_negative_epsilon_to_zero():
    assert decay_strength(-1e-12, elapsed_tau=10.0, half_life=10.0) == 0.0


def test_decay_uses_lambda_when_provided():
    observed = decay_strength(1.0, elapsed_tau=2.0, decay_lambda=0.5)
    assert math.isclose(observed, math.exp(-1.0))


def test_half_life_and_lambda_parameterizations_are_equivalent():
    half_life = 10.0
    decay_lambda = math.log(2.0) / half_life
    elapsed_tau = 7.5
    strength = 1.3

    from_half_life = decay_strength(strength, elapsed_tau=elapsed_tau, half_life=half_life)
    from_lambda = decay_strength(strength, elapsed_tau=elapsed_tau, decay_lambda=decay_lambda)

    assert math.isclose(from_half_life, from_lambda, rel_tol=1e-12)


@pytest.mark.parametrize(
    ("elapsed_tau", "expected"),
    [
        (0.0, 1.0),
        (1.0, math.exp(-0.3)),
        (2.5, math.exp(-0.75)),
        (8.0, math.exp(-2.4)),
    ],
)
def test_decay_matches_closed_form_lambda(elapsed_tau, expected):
    observed = decay_strength(1.0, elapsed_tau=elapsed_tau, decay_lambda=0.3)
    assert math.isclose(observed, expected, rel_tol=1e-12)
