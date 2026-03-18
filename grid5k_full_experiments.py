import logging
import enoslib as en
import time
from datetime import datetime

# 1. Setup logging
en.init_logging(level=logging.INFO)

# --- CONFIGURATION ---
REPO_URL = "https://github.com/irasamus/energy_benchmarks"
JOB_NAME = "energy_benchmark_run"
# Total runs: 1 warmup + 4 measured = 10
ITERATIONS = 5 
SETTLE_TIME = 10 # Seconds between runs to see a flat line in Kwollect

# Define the benchmarks
# Note: Ensure the 'elixir' filenames match your GitHub repository exactly
benchmarks = [
    {"name": "Spawn",      "java": "Spawner",    "elixir": "Spawner.exs"},
    {"name": "Message",    "java": "Message",    "elixir": "Message.exs"},
    {"name": "ThreadRing", "java": "ThreadRing", "elixir": "thread_ring.exs"},
    {"name": "Idle",       "java": "Idle",       "elixir": "Idle.exs"},
    {"name": "Trapezoid",  "java": "Trapezoid",  "elixir": "trapezoid.exs"}
]

conf = (
    en.G5kConf.from_settings(
        job_name=JOB_NAME, 
        job_type=["deploy"],
        env_name="ubuntu2204-x64-min"
    )
    .add_machine(roles=["bench_node"], servers=["paradoxe-11.rennes.grid5000.fr"])
)

provider = en.G5k(conf)
roles, _ = provider.init()

# --- STEP 1: PREPARE NODE ---
print("--- PREPARING NODE AND COMPILING ---")
# run_command returns a result list immediately, avoiding the NoneType error
en.run_command("apt-get update && apt-get install -y git default-jdk elixir erlang maven", roles=roles)
en.run_command(f"test -d /root/benchmark || git clone {REPO_URL} /root/benchmark", roles=roles)
en.run_command("cd /root/benchmark && git pull", roles=roles)
en.run_command("cd /root/benchmark && mvn dependency:copy-dependencies -DoutputDirectory=lib && javac -cp 'lib/*' *.java", roles=roles)

all_results = []

# --- STEP 2: LOOP THROUGH BENCHMARKS ---
for bench in benchmarks:
    print(f"\n>>> BENCHMARK: {bench['name']}")
    
    for i in range(ITERATIONS):
        label = "WARMUP" if i == 0 else f"RUN {i}"
        
        # --- A. JAVA RUN ---
        print(f"  {label} - Java...")
        res_java = en.run_command(f"cd /root/benchmark && java -cp 'lib/*:.' {bench['java']}", roles=roles)
        
        # Save the result (res_java[0] is the result for paradoxe-10)
        all_results.append({
            "bench": bench['name'], "lang": "Java", "type": label,
            "output": res_java[0].stdout.strip()
        })
        time.sleep(SETTLE_TIME)

        # --- B. ELIXIR RUN ---
        print(f"  {label} - Elixir...")
        res_elixir = en.run_command(f"cd /root/benchmark && elixir {bench['elixir']}", roles=roles)
        
        all_results.append({
            "bench": bench['name'], "lang": "Elixir", "type": label,
            "output": res_elixir[0].stdout.strip()
        })
        time.sleep(SETTLE_TIME)

# --- STEP 3: FINAL SUMMARY TABLE ---
print("\n" + "="*90)
print("EXPERIMENT COMPLETE - TIMESTAMPS FOR KWOLLECT")
print("="*90)
print(f"{'Benchmark':<12} | {'Lang':<7} | {'Type':<8} | {'Timestamps'}")
print("-" * 90)

for r in all_results:
    # This cleans the output so we only see the LOG_START and LOG_END lines
    lines = r['output'].split('\n')
    ts_lines = [line for line in lines if "LOG_" in line]
    ts_display = " | ".join(ts_lines)
    
    print(f"{r['bench']:<12} | {r['lang']:<7} | {r['type']:<8} | {ts_display}")

print("="*90)
print(f"Job ID: {provider.jobs[0].id}")