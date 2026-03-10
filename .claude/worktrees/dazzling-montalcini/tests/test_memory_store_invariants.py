import pytest

from temporal_gradient.memory.decay import EntropicMemory
from temporal_gradient.memory.store import DecayMemoryStore


def _store():
    return DecayMemoryStore(calculate_strength=lambda r, _tau: r.strength, prune_threshold=0.2, s_max=1.5)


def test_upsert_rejects_strength_above_s_max():
    store = _store()
    memory = EntropicMemory("x", initial_weight=2.0)
    try:
        store.upsert(memory)
        assert False
    except ValueError:
        assert True


def test_upsert_rejects_negative_strength():
    store = _store()
    memory = EntropicMemory("x", initial_weight=-0.1)
    try:
        store.upsert(memory)
        assert False
    except ValueError:
        assert True


def test_upsert_rejects_last_tau_regression_for_same_key():
    store = _store()
    memory = EntropicMemory("x", initial_weight=1.0)
    memory.last_accessed_tau = 5.0
    store.upsert(memory)
    memory.last_accessed_tau = 4.0
    try:
        store.upsert(memory)
        assert False
    except ValueError:
        assert True


def test_add_accepts_new_id():
    store = _store()
    memory = EntropicMemory("x", initial_weight=1.0)
    store.add(memory)

    assert store.get(memory.id) is memory


def test_add_with_existing_id_and_regressive_tau_requires_force():
    store = _store()
    original = EntropicMemory("x", initial_weight=1.0)
    original.last_accessed_tau = 5.0
    store.add(original)

    replacement = EntropicMemory("replacement", initial_weight=1.0)
    replacement.id = original.id
    replacement.last_accessed_tau = 4.0

    with pytest.raises(ValueError):
        store.add(replacement, on_collision="merge")

    store.add(replacement, on_collision="merge", force=True)
    assert store.get(original.id) is replacement


def test_touch_updates_last_tau_invariant_tracking():
    store = _store()
    memory = EntropicMemory("x", initial_weight=1.0)
    memory.last_accessed_tau = 0.0
    store.upsert(memory)

    store.touch(memory.id, current_tau=5.0)
    memory.last_accessed_tau = 4.0

    try:
        store.upsert(memory)
        assert False
    except ValueError:
        assert True


def test_prune_uses_threshold_rule_exactly():
    store = _store()
    memory = EntropicMemory("x", initial_weight=0.2)
    store.upsert(memory)
    survivors, forgotten = store.sweep(current_tau=0.0)
    assert not survivors
    assert forgotten


def test_decay_engine_add_memory_rejects_collision_without_merge_override():
    from temporal_gradient.memory.decay import DecayEngine

    engine = DecayEngine()
    first = EntropicMemory("first", initial_weight=1.0)
    second = EntropicMemory("second", initial_weight=1.0)
    second.id = first.id

    engine.add_memory(first, current_tau=2.0)

    with pytest.raises(ValueError):
        engine.add_memory(second, current_tau=1.0)
