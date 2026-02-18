import math

from temporal_gradient.memory.decay import DecayEngine, EntropicMemory, S_MAX


def test_decay_strength_nonincreasing_over_time():
    memory = EntropicMemory("stable", initial_weight=1.0)
    memory.last_accessed_tau = 0.0
    engine = DecayEngine(half_life=10.0)

    strengths = [engine.calculate_current_strength(memory, tau) for tau in (0.0, 5.0, 10.0, 20.0)]
    for earlier, later in zip(strengths, strengths[1:]):
        assert later <= earlier


def test_calculate_current_strength_matches_closed_form_half_life():
    memory = EntropicMemory("closed-form", initial_weight=1.2)
    memory.last_accessed_tau = 3.0
    engine = DecayEngine(half_life=10.0)

    observed = engine.calculate_current_strength(memory, current_tau=13.0)
    expected = 1.2 * 0.5

    assert math.isclose(observed, expected, rel_tol=1e-12)


def test_calculate_current_strength_uses_elapsed_tau_not_strength_adjustment():
    engine = DecayEngine(half_life=10.0)

    strong = EntropicMemory("strong", initial_weight=1.0)
    weak = EntropicMemory("weak", initial_weight=0.5)
    strong.last_accessed_tau = weak.last_accessed_tau = 0.0

    strong_now = engine.calculate_current_strength(strong, current_tau=10.0)
    weak_now = engine.calculate_current_strength(weak, current_tau=10.0)

    assert math.isclose(strong_now / strong.strength, weak_now / weak.strength, rel_tol=1e-12)


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


def test_entropy_sweep_evicts_pruned_memories_from_store():
    engine = DecayEngine(half_life=10.0, prune_threshold=0.2)
    persistent = EntropicMemory("persistent", initial_weight=1.2)
    fragile = EntropicMemory("fragile", initial_weight=0.25)

    engine.add_memory(persistent, current_tau=0.0)
    engine.add_memory(fragile, current_tau=0.0)

    survivors, forgotten = engine.entropy_sweep(current_tau=20.0)

    survivor_ids = {memory.id for memory, _ in survivors}
    forgotten_ids = {memory.id for memory in forgotten}

    assert persistent.id in survivor_ids
    assert fragile.id in forgotten_ids

    assert engine.get_memory(persistent.id) is persistent
    assert engine.get_memory(fragile.id) is None
    assert engine.store.active_ids == (persistent.id,)
    assert [memory.id for memory in engine.vault] == [persistent.id]
    assert fragile not in engine.vault


def test_touch_memory_reconsolidates_through_store_api():
    engine = DecayEngine(half_life=10.0, prune_threshold=0.2)
    memory = EntropicMemory("touch", initial_weight=0.9)
    engine.add_memory(memory, current_tau=0.0)

    strength_before = memory.strength
    touched_strength = engine.touch_memory(memory.id, current_tau=5.0, cooldown=0.0)

    assert touched_strength is not None
    assert touched_strength >= strength_before


def test_reconsolidation_then_decay_matches_closed_form_from_touch_time():
    engine = DecayEngine(decay_lambda=0.1)
    memory = EntropicMemory("recon", initial_weight=0.8)
    engine.add_memory(memory, current_tau=0.0)

    boosted = engine.touch_memory(memory.id, current_tau=5.0, cooldown=0.0)
    assert boosted is not None

    observed = engine.calculate_current_strength(memory, current_tau=8.0)
    expected = boosted * math.exp(-0.1 * (8.0 - 5.0))
    assert math.isclose(observed, expected, rel_tol=1e-12)


def test_entropy_sweep_pruning_uses_canonical_exponential_decay():
    engine = DecayEngine(decay_lambda=0.1, prune_threshold=0.2)
    survivor = EntropicMemory("survivor", initial_weight=0.5)
    forgotten = EntropicMemory("forgotten", initial_weight=0.5)
    engine.add_memory(survivor, current_tau=0.0)
    engine.add_memory(forgotten, current_tau=0.0)

    survivor.last_accessed_tau = 9.0

    survivors, forgotten_records = engine.entropy_sweep(current_tau=10.0)
    survivor_ids = {memory.id for memory, _ in survivors}
    forgotten_ids = {memory.id for memory in forgotten_records}

    assert survivor.id in survivor_ids
    assert forgotten.id in forgotten_ids
