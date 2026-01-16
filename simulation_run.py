import time
import sys
import os

# Add src to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from chronos_engine import ClockRateModulator
from entropic_decay import DecayEngine, EntropicMemory
from salience_pipeline import (
    KeywordImperativeValue,
    RollingJaccardNovelty,
    SaliencePipeline,
)

def run_simulation():
    print(">>> INITIALIZING TEMPORAL GRADIENT ARCHITECTURE...")
    
    # 1. Boot the Systems
    clock = ClockRateModulator(base_dilation_factor=1.0, min_clock_rate=0.05)
    decay = DecayEngine(half_life=20.0, prune_threshold=0.2) # Memories decay fast for demo
    salience = SaliencePipeline(RollingJaccardNovelty(), KeywordImperativeValue())
    
    # 2. Simulate a stream of inputs
    inputs = [
        "System boot sequence initiated.",
        "Checking local weather... it is raining.",
        "Rain. Water. Liquid.", # Low novelty, should be valued low
        "CRITICAL: SECURITY BREACH DETECTED.", # High Imperative
        "My name is Sentinel.", # Identity
        "System standby."
    ]

    print(f"\n{'WALL T':<8} | {'INTERNAL τ':<12} | {'INPUT':<35} | {'PRIO':<4} | {'CLOCK RATE'}")
    print("=" * 85)

    for i, text in enumerate(inputs):
        time.sleep(1.0) # Wait 1 real second
        
        # A. Valuate (salience/priority)
        sal = salience.evaluate(text)
        
        # B. Clock tick (clock-rate reparameterization)
        # We pass the text so the clock can estimate salience load of the moment
        clock.tick(sal.psi, input_context=text)
        subjective_now = clock.subjective_age
        dilation = clock.clock_rate_from_psi(sal.psi)
        
        # C. Encode memory
        # Only if importance is high enough to write
        if sal.psi > 0.3:
            mem = EntropicMemory(text, initial_weight=sal.psi)
            decay.add_memory(mem, subjective_now)
            
        # D. Print Status
        print(f"{1.0 * (i+1):<8} | {subjective_now:<12.2f} | {text[:35]:<35} | {sal.psi:<4.1f} | {dilation:.2f}x")

    print("=" * 85)
    print(">>> MEMORY AUDIT (Post-Simulation)")
    
    # E. Check what survived
    current_subj_time = clock.subjective_age
    survivors, dead = decay.entropy_sweep(current_subj_time)
    
    for mem, str_val in survivors:
        print(f"[ALIVE] Strength: {str_val:.2f} | Content: {mem.content}")
        
    for mem in dead:
        print(f"[DEAD ] Content: {mem.content}")

if __name__ == "__main__":
    run_simulation()
