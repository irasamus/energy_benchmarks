import logging
import enoslib as en
import time

en.init_logging(level=logging.INFO)

# --- CONFIGURATION ---
REPO_URL = "https://github.com/irasamus/energy_benchmarks"
JOB_NAME = "energy_benchmark_run"

conf = (
    en.G5kConf.from_settings(
        job_name=JOB_NAME, 
        job_type=["deploy"],
        env_name="ubuntu2204-x64-min",
        walltime="08:00:00" # Ensure you have enough time
    )
    .add_machine(roles=["bench_node"], servers=["paradoxe-11.rennes.grid5000.fr"])
)

provider = en.G5k(conf)
roles, _ = provider.init()

print("--- STEP 1: CLEANING AND INSTALLING SOFTWARE ---")
with en.play_on(roles=roles) as p:
    p.shell("apt-get clean && apt-get update -y")
    p.shell("apt-get install -y --fix-missing git default-jdk elixir erlang maven")

print("--- STEP 2: ENSURING CODE IS UP TO DATE ---")
with en.play_on(roles=roles) as p:
    # If folder missing, clone it. If exists, pull latest changes.
    p.shell(f"test -d /root/benchmark || git clone {REPO_URL} /root/benchmark")
    p.shell("cd /root/benchmark && git pull") 
    
    print("Compiling...")
    p.shell("cd /root/benchmark && mvn dependency:copy-dependencies -DoutputDirectory=lib")
    p.shell("cd /root/benchmark && javac -cp 'lib/*' *.java")

print("--- STEP 3: PRE-BENCHMARK SETTLE (10s) ---")
# Increased to 20s because servers take longer to settle power after a heavy install
time.sleep(10)

print("--- STEP 4: RUNNING EXPERIMENTS ---")
with en.play_on(roles=roles) as p:
    # Capture results in variables
    print("Executing Java Trapezoid...")
    java_res = p.shell("cd /root/benchmark && java -cp 'lib/*:.' Trapezoid")
    
    print("Executing Elixir Trapezoid...")
    elixir_res = p.shell("cd /root/benchmark && elixir trapezoid.exs")

# --- STEP 5: PRINT TIMESTAMPS (Crucial for Energy Analysis) ---
print("\n" + "="*30 + " RESULTS " + "="*30)
print(f"JAVA OUTPUT:\n{java_res[0].stdout}")
print(f"ELIXIR OUTPUT:\n{elixir_res[0].stdout}")
print("="*69)

print(f"OAR Job ID: {provider.jobs[0].id}")