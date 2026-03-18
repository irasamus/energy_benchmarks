import logging
import enoslib as en

# 1. Setup logging
en.init_logging(level=logging.INFO)

# --- CONFIGURATION ---
# Replace with your actual GitHub repository URL
REPO_URL = "https://github.com/irasamus/energy_benchmarks"
WALLTIME = "06:00:00"

conf = (
    en.G5kConf.from_settings(
        job_name="energy_benchmark_run",
        walltime=WALLTIME,
        env_name="ubuntu2204-x64-min",
        # We use only 'deploy' to ensure the reservation is accepted.
        # Paradoxe nodes are monitored by default.
        job_type=["deploy"] 
    )
    .add_machine(
        roles=["bench_node"],
        # SPECIFIC NODE: paradoxe-10
        servers=["paradoxe-10.rennes.grid5000.fr"]
    )
)

# --- 2. RESERVATION ---
provider = en.G5k(conf)
roles, networks = provider.init()

# --- 3. DEPLOYMENT (Ubuntu) ---
print("--- Starting OS Deployment on Paradoxe-10 ---")


# --- 4. SOFTWARE INSTALLATION ---
print("--- Installing Dependencies ---")
with en.play_on(roles=roles) as p:
    p.apt(update_cache=True)
    p.apt(
        name=["git", "default-jdk", "elixir", "erlang", "maven"],
        state="present"
    )

# --- 5. CLONE CODE & COMPILE ---
print("--- Fetching Code and Preparing Benchmarks ---")
with en.play_on(roles=roles) as p:
    # Clone your GitHub repo to the node
    p.git(repo=REPO_URL, dest="/root/benchmark", force=True)
    
    # Download Akka dependencies
    p.shell("cd /root/benchmark && mvn dependency:copy-dependencies -DoutputDirectory=lib")
    
    # Compile all Java files on the node
    p.shell("cd /root/benchmark && javac -cp 'lib/*' *.java")

# --- 6. RUN THE EXPERIMENT ---
print("--- Running Spawner Benchmark ---")
with en.play_on(roles=roles) as p:
    # Run the Java Spawner and redirect output to a file
    # We use 'nohup' so the process doesn't die if the connection blips
    res = p.shell("cd /root/benchmark && java -cp 'lib/*:.' Spawner > /root/benchmark/java_output.log")

# --- 7. FINISH ---
print("\n" + "="*60)
print("EXPERIMENT FINISHED SUCCESSFULLY")
job_id = provider.jobs[0].id
print(f"Node assigned: {roles['bench_node'][0].address}")
print(f"OAR Job ID: {job_id}")
print(f"Check /root/benchmark/java_output.log on the node for timestamps.")
print("="*60)

# Note: We do NOT run provider.destroy() so you have time to check the files!