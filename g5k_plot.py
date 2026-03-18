import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- TIMESTAMPS ---
experiments = [
    {"bench": "Spawn",      "lang": "Java",   "start": 1773329294125, "end": 1773329298548},
    {"bench": "Spawn",      "lang": "Elixir", "start": 1773329310676, "end": 1773329315469},
    {"bench": "Message",    "lang": "Elixir", "start": 1773329413629, "end": 1773329415108},
    {"bench": "ThreadRing", "lang": "Java",   "start": 1773329579611, "end": 1773329668002},
    {"bench": "ThreadRing", "lang": "Elixir", "start": 1773329680108, "end": 1773329699886},
    {"bench": "Idle",       "lang": "Java",   "start": 1773329953720, "end": 1773329983733},
    {"bench": "Idle",       "lang": "Elixir", "start": 1773329997434, "end": 1773330027437},
    {"bench": "Trapezoid",  "lang": "Java",   "start": 1773330152479, "end": 1773330153140},
    {"bench": "Trapezoid",  "lang": "Elixir", "start": 1773330165242, "end": 1773330165783},
]

def analyze_and_plot():
    with open("raw_energy_data.json", "r") as f:
        raw_json = json.load(f)

    all_points = []
    for entry in raw_json:
        ts_str = entry['timestamp'].split('+')[0]
        unix_ts = datetime.fromisoformat(ts_str).timestamp()
        all_points.append((unix_ts, entry['value']))
    all_points.sort()

    benchmarks = ["Spawn", "Message", "ThreadRing", "Idle", "Trapezoid"]
    # sharey=False is the FIX for the 'weird' looking Trapezoid
    fig, axes = plt.subplots(1, 5, figsize=(25, 6), sharey=False)
    fig.suptitle("Detailed Power Profiles (Watts) - Independent Scales", fontsize=20, y=1.05)

    colors = {"Java": "blue", "Elixir": "red"}

    print("--- DATA DIAGNOSTICS ---")
    for i, name in enumerate(benchmarks):
        ax = axes[i]
        ax.set_title(f"{name}", fontsize=14, fontweight='bold')
        
        found_data_for_bench = False
        for exp in [e for e in experiments if e['bench'] == name]:
            start_s = exp['start'] / 1000.0
            end_s = exp['end'] / 1000.0
            
            # WIDER PADDING (2 seconds) to find the 'missing' data
            run_data = [p for p in all_points if (start_s - 2.0) <= p[0] <= (end_s + 2.0)]
            
            print(f"Benchmark: {name} | Lang: {exp['lang']} | Samples found: {len(run_data)}")

            if len(run_data) < 2:
                continue
            
            found_data_for_bench = True
            t0 = run_data[0][0]
            ax.plot([p[0] - t0 for p in run_data], [p[1] for p in run_data], 
                    label=exp['lang'], color=colors[exp['lang']], linewidth=2)

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Power (Watts)")
        ax.legend()
        if not found_data_for_bench:
            ax.text(0.5, 0.5, "Insufficient Data", ha='center', va='center', transform=ax.transAxes)

    plt.tight_layout()
    plt.savefig("fixed_wattage_profiles.png", dpi=300)
    print("\nCheck 'fixed_wattage_profiles.png'")
    plt.show()

if __name__ == "__main__":
    analyze_and_plot()