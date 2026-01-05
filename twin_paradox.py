import time
import sys
import os

# Link to your src folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from chronos_engine import WiltshireClock
from chronometric_vector import ChronometricVector

def run_twin_experiment():
    print(">>> INITIATING TWIN PARADOX EXPERIMENT...")
    
    # Two identical clocks
    clock_monk = WiltshireClock(base_dilation_factor=2.0) # Sensitive to complexity
    clock_clerk = WiltshireClock(base_dilation_factor=2.0)
    
    # The Environments
    # A: High Complexity (Dense Philosophy)
    input_monk = "Time is the emergent tension gradient created by recursive accumulation." * 5
    # B: Low Complexity (Repetitive Noise)
    input_clerk = "Ping. Pong. Ping. Pong."
    
    print(f"\n{'REAL SECONDS':<15} | {'MONK AGE':<10} | {'CLERK AGE':<10} | {'DRIFT'}")
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
    print(f"The Monk aged {clock_monk.subjective_age:.2f} seconds.")
    print(f"The Clerk aged {clock_clerk.subjective_age:.2f} seconds.")
    print("The Monk lived 'less' time because he was burdened by meaning.")

if __name__ == "__main__":
    run_twin_experiment()
