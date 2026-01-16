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
    clock_high_salience = ClockRateModulator(base_dilation_factor=2.0, min_clock_rate=0.05)
    clock_low_salience = ClockRateModulator(base_dilation_factor=2.0, min_clock_rate=0.05)
    
    # The Environments
    # A: High Complexity (Dense Philosophy)
    input_high_salience = "Time is the emergent tension gradient created by recursive accumulation." * 5
    # B: Low Complexity (Repetitive Noise)
    input_low_salience = "Ping. Pong. Ping. Pong."
    
    print(
        f"\n{'WALL_T':<8} | {'TAU_HIGH':<10} | {'TAU_LOW':<10} | "
        f"{'SALIENCE_H':<11} | {'SALIENCE_L':<11} | {'CLOCK_RATE_H':<13} | {'CLOCK_RATE_L':<13} | {'DRIFT'}"
    )
    print("=" * 110)
    
    # Run for 10 "Real" Seconds
    start_time = time.time()
    for i in range(10):
        time.sleep(1.0) # 1 Wall Second Passes
        
        # 1. Tick the high-salience regime (Heavy Load)
        high_psi = min(4.0, len(input_high_salience) / 20)
        high_clock_rate = clock_high_salience.clock_rate_from_psi(high_psi)
        clock_high_salience.tick(high_psi)
        
        # 2. Tick the low-salience regime (Light Load)
        low_psi = min(4.0, len(input_low_salience) / 20)
        low_clock_rate = clock_low_salience.clock_rate_from_psi(low_psi)
        clock_low_salience.tick(low_psi)
        
        # 3. Calculate the "Temporal Drift" (How far apart are they?)
        drift = clock_low_salience.subjective_age - clock_high_salience.subjective_age

        wall_time = time.time() - start_time
        high_packet = ChronometricVector(
            wall_clock_time=wall_time,
            tau=clock_high_salience.subjective_age,
            psi=high_psi,
            recursion_depth=0,
            clock_rate=high_clock_rate,
            H=0.0,
            V=0.0,
        ).to_packet()
        low_packet = ChronometricVector(
            wall_clock_time=wall_time,
            tau=clock_low_salience.subjective_age,
            psi=low_psi,
            recursion_depth=0,
            clock_rate=low_clock_rate,
            H=0.0,
            V=0.0,
        ).to_packet()
        
        print(
            f"{i+1:<8} | {clock_high_salience.subjective_age:<10.2f} | {clock_low_salience.subjective_age:<10.2f} | "
            f"{high_psi:<11.3f} | {low_psi:<11.3f} | {high_clock_rate:<13.4f} | {low_clock_rate:<13.4f} | {drift:+.2f}s"
        )
        print(f"{'HIGH':<15} | {high_packet}")
        print(f"{'LOW':<15} | {low_packet}")

    print("=" * 110)
    print("CONCLUSION:")
    print(f"High-load regime accumulated {clock_high_salience.subjective_age:.2f} internal seconds.")
    print(f"Low-load regime accumulated {clock_low_salience.subjective_age:.2f} internal seconds.")
    print("Higher salience load slows internal time accumulation relative to the low-load stream.")

if __name__ == "__main__":
    run_twin_experiment()
