import time
import sys
import os

# Link to your src folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from chronos_engine import ClockRateModulator
from chronometric_vector import ChronometricVector

def run_twin_experiment():
    print(">>> INITIATING TWIN PARADOX EXPERIMENT...")
    
    # Two identical clocks
    clock_monk = ClockRateModulator(base_dilation_factor=2.0, min_clock_rate=0.05) # Sensitive to complexity
    clock_clerk = ClockRateModulator(base_dilation_factor=2.0, min_clock_rate=0.05)
    
    # The Environments
    # A: High Complexity (Dense Philosophy)
    input_monk = "Time is the emergent tension gradient created by recursive accumulation." * 5
    # B: Low Complexity (Repetitive Noise)
    input_clerk = "Ping. Pong. Ping. Pong."
    
    print(f"\n{'REAL SECONDS':<15} | {'HIGH-LOAD τ':<12} | {'LOW-LOAD τ':<12} | {'DRIFT'}")
    print("=" * 60)
    
    # Run for 10 "Real" Seconds
    for i in range(10):
        time.sleep(1.0) # 1 Wall Second Passes
        
        # 1. Tick the Monk (Heavy Load)
        monk_state = clock_monk.tick(input_monk)
        
        # 2. Tick the Clerk (Light Load)
        clerk_state = clock_clerk.tick(input_clerk)
        
        # 3. Calculate the "Temporal Drift" (How far apart are they?)
        drift = clerk_state['subjective_age'] - monk_state['subjective_age']
        
        print(f"{i+1:<15} | {monk_state['subjective_age']:<10.2f} | {clerk_state['subjective_age']:<10.2f} | {drift:+.2f}s")

    print("=" * 60)
    print("CONCLUSION:")
    print(f"High-load regime accumulated {clock_monk.subjective_age:.2f} internal seconds.")
    print(f"Low-load regime accumulated {clock_clerk.subjective_age:.2f} internal seconds.")
    print("Higher salience load slows internal time accumulation relative to the low-load stream.")

if __name__ == "__main__":
    run_twin_experiment()
