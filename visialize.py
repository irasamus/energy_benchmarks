import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import numpy as np

# ==========================================
# CONFIGURATION
# ==========================================
# Change this to the experiment you want to analyze (e.g., "elixir_spawn", "java_message")
TARGET_EXP = "java_spawn" 
RESULTS_DIR = "results"
# ==========================================

def get_run_files(exp_name):
    return sorted(glob.glob(f"{RESULTS_DIR}/{exp_name}_run_*.csv"))

def load_and_normalize(file):
    try:
        df = pd.read_csv(file)
        # Normalize time to start at 0
        start_time = df['Time'].iloc[0]
        df['Seconds'] = (df['Time'] - start_time) / 1000.0
        
        # Calculate Total Energy for this run (Riemann Sum approximation)
        # Power (W) * TimeDelta (s) = Energy (J)
        # We assume standard interval is roughly constant, but let's be precise:
        time_diff = df['Seconds'].diff().fillna(0)
        df['Energy_Step'] = df['SYSTEM_POWER (Watts)'] * time_diff
        total_energy = df['Energy_Step'].sum()
        
        return df, total_energy
    except Exception as e:
        print(f"Error reading {file}: {e}")
        return None, None

def plot_stability(files):
    plt.figure(figsize=(10, 6))
    
    energies = []
    
    for f in files:
        df, energy = load_and_normalize(f)
        if df is not None:
            # Alpha=0.5 makes lines semi-transparent so you can see overlap
            plt.plot(df['Seconds'], df['SYSTEM_POWER (Watts)'], alpha=0.5, linewidth=1.5)
            energies.append((energy, df))
            
    plt.title(f"Stability Check: {TARGET_EXP} (All Runs)")
    plt.xlabel("Time (s)")
    plt.ylabel("Power (W)")
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{TARGET_EXP}_stability.png")
    plt.close()
    
    # Sort runs by Total Energy to find the Median run later
    energies.sort(key=lambda x: x[0])
    return energies

def plot_gc_detective(median_run_df):
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot Power (Left Axis)
    color = 'tab:red'
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Power (Watts)', color=color)
    ax1.plot(median_run_df['Seconds'], median_run_df['SYSTEM_POWER (Watts)'], color=color, label='Power')
    ax1.tick_params(axis='y', labelcolor=color)

    # Plot Memory (Right Axis)
    ax2 = ax1.twinx()  
    color = 'tab:blue'
    ax2.set_ylabel('Memory Used (MB)', color=color)
    # Convert Bytes to MB for readability
    memory_mb = median_run_df['USED_MEMORY'] / (1024 * 1024)
    ax2.plot(median_run_df['Seconds'], memory_mb, color=color, linestyle='--', label='Memory')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title(f"Power vs Memory Profile: {TARGET_EXP} (Median Run)")
    fig.tight_layout()  
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{TARGET_EXP}_gc_analysis.png")
    plt.close()

def plot_box_distribution(energies_java, energies_elixir=None):
    plt.figure(figsize=(8, 6))
    
    data = [ [e[0] for e in energies_java] ]
    labels = [TARGET_EXP]
    
    # If you want to compare two lists (Advanced usage later)
    if energies_elixir:
        data.append([e[0] for e in energies_elixir])
        labels.append("Elixir Comparison")

    plt.boxplot(data, labels=labels)
    plt.ylabel("Total Energy (Joules)")
    plt.title(f"Energy Distribution (N={len(energies_java)})")
    plt.grid(True, axis='y', alpha=0.3)
    plt.savefig(f"{TARGET_EXP}_boxplot.png")
    plt.close()

# --- MAIN EXECUTION ---
files = get_run_files(TARGET_EXP)
if not files:
    print(f"No files found for {TARGET_EXP}. Check your folder name.")
else:
    print(f"Analyzing {len(files)} runs for {TARGET_EXP}...")
    
    # 1. Generate Stability Graph & Get Sorted Data
    sorted_runs = plot_stability(files)
    
    # 2. Find Median Run (The middle one)
    median_index = len(sorted_runs) // 2
    median_energy, median_df = sorted_runs[median_index]
    print(f"Median Run Energy: {median_energy:.2f} J")
    
    # 3. Generate GC Analysis Graph (Power vs Memory)
    plot_gc_detective(median_df)
    
    # 4. Generate Box Plot
    plot_box_distribution(sorted_runs)
    
    print("Done! Check the .png files in your folder.")