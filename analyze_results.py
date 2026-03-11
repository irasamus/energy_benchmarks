import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# --- CONFIGURATION ---
# Define the experiments you want to compare
experiments = ["elixir_spawn", "java_spawn"] 
# (You can add "elixir_base", "java_base", etc. later)

# --- THE SCRIPT ---
def analyze():
    plt.figure(figsize=(12, 6))

    for exp_name in experiments:
        print(f"Processing {exp_name}...")
        
        # Find all CSV files for this experiment (run_1, run_2, etc.)
        files = glob.glob(f"results/{exp_name}_run_*.csv")
        
        if not files:
            print(f"  No files found for {exp_name}!")
            continue

        # We will calculate the average power across all runs to plot a "smooth" line
        # But first, let's just plot the FIRST run to see the shape
        first_file = files[0]
        df = pd.read_csv(first_file)

        # 1. Normalize Time (Start at 0 seconds)
        # EnergiBridge gives Unix timestamps (e.g., 177134...). We want 0.0, 0.2, 0.4...
        start_time = df['Time'].iloc[0]
        df['Seconds'] = (df['Time'] - start_time) / 1000.0

        # 2. Plot Power vs Time
        plt.plot(df['Seconds'], df['SYSTEM_POWER (Watts)'], label=f"{exp_name} (Run 1)")

        # 3. Print Stats
        avg_power = df['SYSTEM_POWER (Watts)'].mean()
        max_mem = df['USED_MEMORY'].max() / (1024 * 1024 * 1024) # Convert to GB
        print(f"  -> Avg Power: {avg_power:.2f} W")
        print(f"  -> Max Memory: {max_mem:.2f} GB")

    # Graph Formatting
    plt.title("Power Consumption Over Time (Comparison)")
    plt.xlabel("Time (Seconds)")
    plt.ylabel("System Power (Watts)")
    plt.legend()
    plt.grid(True)
    
    # Save the graph
    plt.savefig("power_comparison.png")
    print("\nGraph saved as 'power_comparison.png'")
    plt.show()

if __name__ == "__main__":
    analyze()