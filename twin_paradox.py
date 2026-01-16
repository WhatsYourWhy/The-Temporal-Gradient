import time
import sys
import os

# Link to your src folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from chronos_engine import ClockRateModulator
from chronometric_vector import ChronometricVector
from salience_pipeline import KeywordImperativeValue, RollingJaccardNovelty, SaliencePipeline

def run_twin_experiment():
    print(">>> INITIATING TWIN PARADOX EXPERIMENT...")
    
    # Two identical clocks
    clock_high_salience = ClockRateModulator(base_dilation_factor=2.0, min_clock_rate=0.05)
    clock_low_salience = ClockRateModulator(base_dilation_factor=2.0, min_clock_rate=0.05)
    
    salience_high = SaliencePipeline(RollingJaccardNovelty(), KeywordImperativeValue())
    salience_low = SaliencePipeline(RollingJaccardNovelty(), KeywordImperativeValue())

    # The Environments
    # A: High Complexity (Dense Philosophy)
    input_high_salience = "Time is the emergent tension gradient created by recursive accumulation." * 5
    # B: Low Complexity (Repetitive Noise)
    input_low_salience = "Ping. Pong. Ping. Pong."
    
    print(
        f"\n{'WALL_T':<8} | {'TAU (HIGH)':<11} | {'SALIENCE (HIGH)':<15} | {'CLOCK_RATE (HIGH)':<18} | "
        f"{'TAU (LOW)':<10} | {'SALIENCE (LOW)':<14} | {'CLOCK_RATE (LOW)':<17} | {'DRIFT'}"
    )
    print("=" * 126)
    
    # Run for 10 "Real" Seconds
    start_time = time.time()
    for i in range(10):
        time.sleep(1.0) # 1 Wall Second Passes
        
        # 1. Tick the high-salience regime (Heavy Load)
        high_sal = salience_high.evaluate(input_high_salience)
        high_psi = high_sal.psi
        high_clock_rate = clock_high_salience.clock_rate_from_psi(high_psi)
        clock_high_salience.tick(high_psi)
        
        # 2. Tick the low-salience regime (Light Load)
        low_sal = salience_low.evaluate(input_low_salience)
        low_psi = low_sal.psi
        low_clock_rate = clock_low_salience.clock_rate_from_psi(low_psi)
        clock_low_salience.tick(low_psi)
        
        # 3. Calculate the "Temporal Drift" (How far apart are they?)
        drift = clock_low_salience.tau - clock_high_salience.tau

        wall_time = time.time() - start_time
        high_packet = ChronometricVector(
            wall_clock_time=wall_time,
            tau=clock_high_salience.tau,
            psi=high_psi,
            recursion_depth=0,
            clock_rate=high_clock_rate,
            memory_strength=0.0,
            H=high_sal.novelty,
            V=high_sal.value,
        ).to_packet()
        low_packet = ChronometricVector(
            wall_clock_time=wall_time,
            tau=clock_low_salience.tau,
            psi=low_psi,
            recursion_depth=0,
            clock_rate=low_clock_rate,
            memory_strength=0.0,
            H=low_sal.novelty,
            V=low_sal.value,
        ).to_packet()
        
        print(
            f"{i+1:<8} | {clock_high_salience.tau:<11.2f} | {high_psi:<15.3f} | {high_clock_rate:<18.4f} | "
            f"{clock_low_salience.tau:<10.2f} | {low_psi:<14.3f} | {low_clock_rate:<17.4f} | {drift:+.2f}s"
        )
        print(f"{'PACKET(HIGH)':<13} | {high_packet}")
        print(f"{'PACKET(LOW)':<13} | {low_packet}")

    print("=" * 126)
    print("CONCLUSION:")
    print(f"High-load regime accumulated {clock_high_salience.tau:.2f} internal seconds.")
    print(f"Low-load regime accumulated {clock_low_salience.tau:.2f} internal seconds.")
    print("Higher salience load slows internal time accumulation relative to the low-load stream.")

if __name__ == "__main__":
    run_twin_experiment()
