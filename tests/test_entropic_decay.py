import math

from entropic_decay import DecayEngine, EntropicMemory, S_MAX


def test_decay_strength_nonincreasing_over_time():
    memory = EntropicMemory("stable", initial_weight=1.0)
    memory.last_accessed_tau = 0.0
    engine = DecayEngine(half_life=10.0)

    strengths = [engine.calculate_current_strength(memory, tau) for tau in (0.0, 5.0, 10.0, 20.0)]
    for earlier, later in zip(strengths, strengths[1:]):
        assert later <= earlier


def test_reconsolidation_capped():
    memory = EntropicMemory("cap", initial_weight=1.4)

    for step in range(1, 40):
        memory.reconsolidate(current_tau=float(step), cooldown=0.0)

    assert memory.strength <= S_MAX


def test_reconsolidation_cooldown_enforced():
    memory = EntropicMemory("cooldown", initial_weight=1.0)
    initial_strength = memory.strength

    strength_after = memory.reconsolidate(current_tau=0.5, cooldown=1.0)

    assert math.isclose(strength_after, initial_strength)
