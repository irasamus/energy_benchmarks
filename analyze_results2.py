import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
RESULTS_DIR = 'results2'

# Make graphs look academic and clean
sns.set_theme(style="whitegrid", palette="muted")

def parse_data():
    """Reads all CSV files and calculates total energy and time for each run."""
    data =[]
    
    # Find all CSV files in the results directory
    csv_files = glob.glob(os.path.join(RESULTS_DIR, '*.csv'))
    
    if not csv_files:
        print(f"No CSV files found in {RESULTS_DIR}/")
        return pd.DataFrame()

    for filepath in csv_files:
        filename = os.path.basename(filepath)
        # Expected format: elixir_spawn_run_1.csv
        parts = filename.replace('.csv', '').split('_')
        
        if len(parts) < 4:
            continue
            
        lang = parts[0].capitalize()  # Elixir or Java
        bench = parts[1].capitalize() # Spawn, Message, Ring, Trap, Idle, Base
        run_id = int(parts[3])
        
        try:
            df = pd.read_csv(filepath)
            
            # Drop any empty rows just in case
            df = df.dropna(subset=['SYSTEM_POWER (Watts)', 'Delta'])
            
            # ENERGY CALCULATION:
            # Power (Watts) * Time (Seconds) = Energy (Joules)
            # Delta is in milliseconds, so we divide by 1000
            df['Energy_Joules'] = df['SYSTEM_POWER (Watts)'] * (df['Delta'] / 1000.0)
            
            total_energy = df['Energy_Joules'].sum()
            total_time = df['Delta'].sum() / 1000.0
            
            data.append({
                'Language': lang,
                'Benchmark': bench,
                'Run': run_id,
                'Energy (Joules)': total_energy,
                'Time (Seconds)': total_time
            })
            
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            
    return pd.DataFrame(data)

def print_summary_table(df):
    """Prints a formatted academic table with Means and Standard Deviations."""
    print("\n" + "="*70)
    print(" ACADEMIC SUMMARY TABLE: ENERGY AND TIME")
    print("="*70)
    
    # Calculate Mean and Standard Deviation
    summary = df.groupby(['Benchmark', 'Language']).agg(
        Energy_Mean=('Energy (Joules)', 'mean'),
        Energy_SD=('Energy (Joules)', 'std'),
        Time_Mean=('Time (Seconds)', 'mean'),
        Time_SD=('Time (Seconds)', 'std')
    ).reset_index()
    
    # Sort for better readability
    summary = summary.sort_values(by=['Benchmark', 'Language'])
    
    # Print formatted output
    current_bench = ""
    for _, row in summary.iterrows():
        if row['Benchmark'] != current_bench:
            current_bench = row['Benchmark']
            print(f"\n--- {current_bench.upper()} ---")
            
        print(f"  {row['Language']:<7} | Energy: {row['Energy_Mean']:>7.2f} J (±{row['Energy_SD']:>5.2f}) | Time: {row['Time_Mean']:>6.2f} s (±{row['Time_SD']:>4.2f})")

def plot_graphs(df):
    """Generates and saves publication-ready graphs."""
    print("\nGenerating graphs...")
    
    # Rename benchmarks to look better on graphs
    bench_names = {
        'Spawn': '1. Actor Spawning',
        'Message': '2. Message Passing',
        'Ring': '3. Thread Ring',
        'Trap': '4. Trapezoidal Math',
        'Idle': '5. Idle State',
        'Base': '6. Baseline'
    }
    df['Benchmark_Name'] = df['Benchmark'].map(bench_names)

    # 1. BAR CHART: Average Energy Consumption
    # We use a FacetGrid (catplot) so every benchmark gets its own Y-axis scale.
    g1 = sns.catplot(
        data=df, x='Language', y='Energy (Joules)', col='Benchmark_Name',
        kind='bar', col_wrap=3, height=4, aspect=0.8, sharey=False,
        errorbar='sd', capsize=0.1, palette=['#6e4a7e', '#e07a5f'] # Elixir purple, Java orange
    )
    g1.fig.suptitle("Average Energy Consumption by Benchmark (Lower is Better)", y=1.02, fontsize=16)
    g1.set_titles("{col_name}")
    g1.set_axis_labels("", "Energy (Joules)")
    plt.savefig("graph_1_energy_bar.png", bbox_inches='tight', dpi=300)
    plt.close()
    print(" -> Saved graph_1_energy_bar.png")

    # 2. BOX PLOT: Energy Distribution (Shows variance/outliers)
    # Box plots are highly respected in papers because they show the raw spread of the 10 runs.
    g2 = sns.catplot(
        data=df, x='Language', y='Energy (Joules)', col='Benchmark_Name',
        kind='box', col_wrap=3, height=4, aspect=0.8, sharey=False,
        palette=['#6e4a7e', '#e07a5f']
    )
    g2.fig.suptitle("Energy Consumption Variance across 10 Runs", y=1.02, fontsize=16)
    g2.set_titles("{col_name}")
    g2.set_axis_labels("", "Energy (Joules)")
    plt.savefig("graph_2_energy_boxplot.png", bbox_inches='tight', dpi=300)
    plt.close()
    print(" -> Saved graph_2_energy_boxplot.png")

    # 3. BAR CHART: Average Execution Time
    g3 = sns.catplot(
        data=df, x='Language', y='Time (Seconds)', col='Benchmark_Name',
        kind='bar', col_wrap=3, height=4, aspect=0.8, sharey=False,
        errorbar='sd', capsize=0.1, palette=['#6e4a7e', '#e07a5f']
    )
    g3.fig.suptitle("Average Execution Time by Benchmark (Lower is Better)", y=1.02, fontsize=16)
    g3.set_titles("{col_name}")
    g3.set_axis_labels("", "Time (Seconds)")
    plt.savefig("graph_3_time_bar.png", bbox_inches='tight', dpi=300)
    plt.close()
    print(" -> Saved graph_3_time_bar.png")

if __name__ == "__main__":
    df_results = parse_data()
    if not df_results.empty:
        print_summary_table(df_results)
        plot_graphs(df_results)
        print("\nAll done! Check your folder for the PNG images.")