from temporal_gradient.memory.decay import DecayEngine, EntropicMemory


def test_decay_engine_sweep_prunes_low_strength_memories():
    engine = DecayEngine(half_life=10.0, prune_threshold=0.2)
    keep = EntropicMemory("keep", initial_weight=1.2)
    drop = EntropicMemory("drop", initial_weight=0.21)
    engine.add_memory(keep, current_tau=0.0)
    engine.add_memory(drop, current_tau=0.0)
    survivors, forgotten = engine.entropy_sweep(current_tau=20.0)
    assert any(mem.id == keep.id for mem, _ in survivors)
    assert any(mem.id == drop.id for mem in forgotten)
