from temporal_gradient.memory.decay import decay_strength


def test_decay_floors_negative_epsilon_to_zero():
    assert decay_strength(-1e-12, elapsed_tau=10.0, half_life=10.0) == 0.0
