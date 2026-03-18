import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

# --- 1. DATA ENTRY (Corrected keys: 'run' instead of 'type') ---
experiments = [
    {"bench": "Message", "lang": "Java", "run": "Warmup", "start": 1773759393231, "end": 1773759398579},
    {"bench": "Message", "lang": "Elixir", "run": "Warmup", "start": 1773759411836, "end": 1773759413307},
    {"bench": "Message", "lang": "Java", "run": "Run 1", "start": 1773759427772, "end": 1773759433572},
    {"bench": "Message", "lang": "Elixir", "run": "Run 1", "start": 1773759448284, "end": 1773759449771},
    {"bench": "Message", "lang": "Java", "run": "Run 2", "start": 1773759464236, "end": 1773759468770},
    {"bench": "Message", "lang": "Elixir", "run": "Run 2", "start": 1773759482348, "end": 1773759483498},

    {"bench": "Trapezoid", "lang": "Java", "run": "Warmup", "start": 1773759499886, "end": 1773759500853},
    {"bench": "Trapezoid", "lang": "Elixir", "run": "Warmup", "start": 1773759514615, "end": 1773759515149},
    {"bench": "Trapezoid", "lang": "Java", "run": "Run 1", "start": 1773759530816, "end": 1773759531931},
    {"bench": "Trapezoid", "lang": "Elixir", "run": "Run 1", "start": 1773759545437, "end": 1773759545965},
    {"bench": "Trapezoid", "lang": "Java", "run": "Run 2", "start": 1773759559600, "end": 1773759560299},
    {"bench": "Trapezoid", "lang": "Elixir", "run": "Run 2", "start": 1773759573521, "end": 1773759574045}
]

def analyze_watts():
    try:
        with open("raw_energy_data.json", "r") as f:
            raw_json = json.load(f)
    except:
        print("Error: raw_energy_data.json not found.")
        return

    # Process timestamps in JSON (ISO to Unix)
    points = []
    for entry in raw_json:
        ts = datetime.fromisoformat(entry['timestamp'].split('+')[0]).timestamp()
        points.append((ts, entry['value']))
    points.sort()

    results = []
    for ex in experiments:
        s_sec, e_sec = ex['start']/1000.0, ex['end']/1000.0
        
        # Soft matching: using 1 second padding to capture the data spike
        window_samples = [p[1] for p in points if (s_sec - 1.0) <= p[0] <= (e_sec + 1.0)]
        
        if not window_samples:
            print(f"No samples found for {ex['bench']} {ex['lang']} {ex['run']}")
            continue
            
        avg_watts = np.mean(window_samples)
        
        results.append({
            "Benchmark": ex['bench'],
            "Language": ex['lang'],
            "Run": ex['run'],
            "Average Watts": avg_watts
        })

    df = pd.DataFrame(results)

    # --- PLOTTING ---
    sns.set_theme(style="whitegrid")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Colors: Java=Blue, Elixir=Red
    colors = {"Java": "blue", "Elixir": "red"}

    # Plot 1: Message Passing
    msg_df = df[df['Benchmark'] == "Message"]
    if not msg_df.empty:
        sns.barplot(ax=ax1, data=msg_df, x='Run', y='Average Watts', hue='Language', palette=colors)
        ax1.set_title("Message Passing: Average Power Draw", fontsize=14, fontweight='bold')
        ax1.set_ylabel("Watts")
        ax1.set_ylim(130, 220) # Zoom in to see above the 138W server baseline

    # Plot 2: Trapezoid
    trap_df = df[df['Benchmark'] == "Trapezoid"]
    if not trap_df.empty:
        sns.barplot(ax=ax2, data=trap_df, x='Run', y='Average Watts', hue='Language', palette=colors)
        ax2.set_title("Trapezoid Math: Average Power Draw", fontsize=14, fontweight='bold')
        ax2.set_ylabel("Watts")
        ax2.set_ylim(130, 160) # Different scale for the lighter Trapezoid task

    plt.suptitle("Hardware Wattmeter: Power Consumption Profile (Paradoxe-10)", fontsize=18, y=1.02)
    plt.tight_layout()
    plt.savefig("watts_comparison_final.png", dpi=300)
    
    print("\n--- Summary Table (Average Watts) ---")
    summary = df.groupby(['Benchmark', 'Language'])['Average Watts'].mean().unstack()
    print(summary)
    
    print("\nGraph saved as 'watts_comparison_final.png'")
    plt.show()

if __name__ == "__main__":
    analyze_watts()