import time
import sys
import os

# Add src to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from chronos_engine import WiltshireClock
from entropic_decay import DecayEngine, EntropicMemory
from codex_valuation import CodexValuator

def run_simulation():
    print(">>> INITIALIZING TEMPORAL GRADIENT ARCHITECTURE...")
    
    # 1. Boot the Systems
    clock = WiltshireClock(base_dilation_factor=1.0)
    decay = DecayEngine(half_life=20.0) # Memories decay fast for demo
    cortex = CodexValuator()
    
    # 2. Simulate a Stream of Consciousness
    inputs = [
        "System boot sequence initiated.",
        "Checking local weather... it is raining.",
        "Rain. Water. Liquid.", # Low novelty, should be valued low
        "CRITICAL: SECURITY BREACH DETECTED.", # High Imperative
        "My name is Sentinel.", # Identity
        "System standby."
    ]

    print(f"\n{'WALL T':<8} | {'SUBJ T':<8} | {'INPUT':<35} | {'VAL':<4} | {'DILATION'}")
    print("=" * 85)

    for i, text in enumerate(inputs):
        time.sleep(1.0) # Wait 1 real second
        
        # A. Valuate (Amygdala)
        importance = cortex.evaluate(text)
        
        # B. Clock Tick (Time Perception)
        # We pass the text so the clock knows the 'Mass' of the moment
        time_data = clock.tick(text)
        subjective_now = time_data['subjective_age']
        dilation = time_data['time_dilation']
        
        # C. Encode Memory (Hippocampus)
        # Only if importance is high enough to bother writing
        if importance > 0.3:
            mem = EntropicMemory(text, initial_weight=importance)
            decay.add_memory(mem, subjective_now)
            
        # D. Print Status
        print(f"{1.0 * (i+1):<8} | {subjective_now:<8.2f} | {text[:35]:<35} | {importance:<4.1f} | {dilation:.2f}x")

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
