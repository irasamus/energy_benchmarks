import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

# --- 1. THE DATA MAP (Transcribed from your logs) ---
experiments = [
    {"b": "Spawn", "l": "Java", "t": "Warmup", "s": 1773828111849, "e": 1773828117423},
    {"b": "Spawn", "l": "Elixir", "t": "Warmup", "s": 1773828129163, "e": 1773828134019},
    {"b": "Spawn", "l": "Java", "t": "Run 1", "s": 1773828146005, "e": 1773828152809},
    {"b": "Spawn", "l": "Elixir", "t": "Run 1", "s": 1773828164579, "e": 1773828169335},
    {"b": "Spawn", "l": "Java", "t": "Run 2", "s": 1773828181306, "e": 1773828186808},
    {"b": "Spawn", "l": "Elixir", "t": "Run 2", "s": 1773828198602, "e": 1773828203510},
    {"b": "Spawn", "l": "Java", "t": "Run 3", "s": 1773828215471, "e": 1773828219419},
    {"b": "Spawn", "l": "Elixir", "t": "Run 3", "s": 1773828231162, "e": 1773828236432},
    {"b": "Spawn", "l": "Java", "t": "Run 4", "s": 1773828248409, "e": 1773828254459},
    {"b": "Spawn", "l": "Elixir", "t": "Run 4", "s": 1773828266181, "e": 1773828271233},
    {"b": "Message", "l": "Java", "t": "Warmup", "s": 1773828283179, "e": 1773828288066},
    {"b": "Message", "l": "Elixir", "t": "Warmup", "s": 1773828299894, "e": 1773828301353},
    {"b": "Message", "l": "Java", "t": "Run 1", "s": 1773828313279, "e": 1773828314764},
    {"b": "Message", "l": "Elixir", "t": "Run 1", "s": 1773828326549, "e": 1773828328015},
    {"b": "Message", "l": "Java", "t": "Run 2", "s": 1773828340080, "e": 1773828345813},
    {"b": "Message", "l": "Elixir", "t": "Run 2", "s": 1773828357662, "e": 1773828359134},
    {"b": "Message", "l": "Java", "t": "Run 3", "s": 1773828371080, "e": 1773828373902},
    {"b": "Message", "l": "Elixir", "t": "Run 3", "s": 1773828385728, "e": 1773828387219},
    {"b": "Message", "l": "Java", "t": "Run 4", "s": 1773828399257, "e": 1773828401010},
    {"b": "Message", "l": "Elixir", "t": "Run 4", "s": 1773828412830, "e": 1773828414300},
    {"b": "ThreadRing", "l": "Java", "t": "Warmup", "s": 1773828426260, "e": 1773828570830},
    {"b": "ThreadRing", "l": "Elixir", "t": "Warmup", "s": 1773828582688, "e": 1773828602426},
    {"b": "ThreadRing", "l": "Java", "t": "Run 1", "s": 1773828614290, "e": 1773828717998},
    {"b": "ThreadRing", "l": "Elixir", "t": "Run 1", "s": 1773828729893, "e": 1773828749735},
    {"b": "ThreadRing", "l": "Java", "t": "Run 2", "s": 1773828761691, "e": 1773828869034},
    {"b": "ThreadRing", "l": "Elixir", "t": "Run 2", "s": 1773828880927, "e": 1773828900530},
    {"b": "ThreadRing", "l": "Java", "t": "Run 3", "s": 1773828912392, "e": 1773829020757},
    {"b": "ThreadRing", "l": "Elixir", "t": "Run 3", "s": 1773829032596, "e": 1773829052345},
    {"b": "ThreadRing", "l": "Java", "t": "Run 4", "s": 1773829064352, "e": 1773829182935},
    {"b": "ThreadRing", "l": "Elixir", "t": "Run 4", "s": 1773829194814, "e": 1773829213768},
    {"b": "Idle", "l": "Java", "t": "Warmup", "s": 1773829226395, "e": 1773829256408},
    {"b": "Idle", "l": "Elixir", "t": "Warmup", "s": 1773829270123, "e": 1773829300125},
    {"b": "Idle", "l": "Java", "t": "Run 1", "s": 1773829313078, "e": 1773829343093},
    {"b": "Idle", "l": "Elixir", "t": "Run 1", "s": 1773829356690, "e": 1773829386693},
    {"b": "Idle", "l": "Java", "t": "Run 2", "s": 1773829399639, "e": 1773829429655},
    {"b": "Idle", "l": "Elixir", "t": "Run 2", "s": 1773829443205, "e": 1773829473208},
    {"b": "Idle", "l": "Java", "t": "Run 3", "s": 1773829486265, "e": 1773829516282},
    {"b": "Idle", "l": "Elixir", "t": "Run 3", "s": 1773829529926, "e": 1773829559929},
    {"b": "Idle", "l": "Java", "t": "Run 4", "s": 1773829572846, "e": 1773829602865},
    {"b": "Idle", "l": "Elixir", "t": "Run 4", "s": 1773829616296, "e": 1773829646299},
    {"b": "Trapezoid", "l": "Java", "t": "Warmup", "s": 1773829658571, "e": 1773829659469},
    {"b": "Trapezoid", "l": "Elixir", "t": "Warmup", "s": 1773829671160, "e": 1773829671689},
    {"b": "Trapezoid", "l": "Java", "t": "Run 1", "s": 1773829683678, "e": 1773829684579},
    {"b": "Trapezoid", "l": "Elixir", "t": "Run 1", "s": 1773829696262, "e": 1773829696758},
    {"b": "Trapezoid", "l": "Java", "t": "Run 2", "s": 1773829708705, "e": 1773829709343},
    {"b": "Trapezoid", "l": "Elixir", "t": "Run 2", "s": 1773829721057, "e": 1773829721582},
    {"b": "Trapezoid", "l": "Java", "t": "Run 3", "s": 1773829733467, "e": 1773829734456},
    {"b": "Trapezoid", "l": "Elixir", "t": "Run 3", "s": 1773829746134, "e": 1773829746654},
    {"b": "Trapezoid", "l": "Java", "t": "Run 4", "s": 1773829758596, "e": 1773829759450},
    {"b": "Trapezoid", "l": "Elixir", "t": "Run 4", "s": 1773829771135, "e": 1773829771668}
]

def analyze():
    with open("raw_g5k_data.json", "r") as f:
        raw_json = json.load(f)

    # Convert ISO strings to Unix float seconds
    points = []
    for entry in raw_json:
        ts = datetime.fromisoformat(entry['timestamp'].split('+')[0]).timestamp()
        points.append((ts, entry['value']))
    points.sort()

    results = []
    
    # 1. Main Analysis Loop
    for ex in experiments:
        s, e = ex['s']/1000.0, ex['e']/1000.0
        
        # Soft matching: Use 1.0s padding to ensure the Trapezoid peaks are found
        # but only integrate energy between exactly s and e
        window = [p for p in points if (s - 1.0) <= p[0] <= (e + 1.0)]
        
        if len(window) < 2:
            print(f"Skipping {ex['b']} {ex['l']} - no data")
            continue
            
        # Calculate Joules (Integration)
        joules = 0.0
        for i in range(1, len(window)):
            # Only count energy consumed inside the actual experiment window
            t_curr, w_curr = window[i]
            t_prev, w_prev = window[i-1]
            
            # Boundary correction
            calc_start = max(t_prev, s)
            calc_end = min(t_curr, e)
            
            if calc_start < calc_end:
                dt = calc_end - calc_start
                avg_p = (w_curr + w_prev) / 2.0
                joules += avg_p * dt

        results.append({
            "Benchmark": ex['b'], "Language": ex['l'], "Type": ex['t'],
            "Joules": joules, "Peak_Watts": np.max([p[1] for p in window]),
            "Time": e - s, "Data": window
        })

    df = pd.DataFrame(results)

    # --- 2. PLOT POWER PROFILES (WATTS) ---
    benchmarks = ["Spawn", "Message", "ThreadRing", "Idle", "Trapezoid"]
    fig, axes = plt.subplots(1, 5, figsize=(25, 6), sharey=False) # Independent Y axes!
    fig.suptitle("Power Profiles: Intensity Comparison (Watts)", fontsize=22, y=1.05)
    
    colors = {"Java": "blue", "Elixir": "red"}

    for i, name in enumerate(benchmarks):
        ax = axes[i]
        ax.set_title(name, fontsize=16, fontweight='bold')
        for lang in ["Java", "Elixir"]:
            # Plot Run 1 for each
            subset = df[(df['Benchmark'] == name) & (df['Language'] == lang) & (df['Type'] == "Run 1")]
            if not subset.empty:
                raw_pts = subset.iloc[0]['Data']
                t0 = raw_pts[0][0]
                ax.plot([p[0]-t0 for p in raw_pts], [p[1] for p in raw_pts], 
                        label=lang, color=colors[lang], linewidth=2)
        ax.set_xlabel("Time (s)")
        if i == 0: ax.set_ylabel("Watts")
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("g5k_power_profiles_watts.png")

    # --- 3. PLOT TOTAL ENERGY (JOULES) ---
    plt.figure(figsize=(12, 6))
    # Filter out Warmups for a cleaner comparison
    df_runs = df[df['Type'] != "Warmup"]
    sns.barplot(data=df_runs, x='Benchmark', y='Joules', hue='Language', palette={"Java": "blue", "Elixir": "red"})
    plt.title("Total Energy Consumption (Average of 4 Runs)", fontsize=18)
    plt.ylabel("Energy (Joules)")
    plt.savefig("g5k_energy_joules.png")

    print("\n" + "="*50)
    print("AVERAGE JOULES (Excluding Warmup)")
    print("="*50)
    print(df_runs.groupby(['Benchmark', 'Language'])['Joules'].mean().unstack())
    print("="*50)

if __name__ == "__main__":
    analyze()