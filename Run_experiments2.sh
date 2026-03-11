#!/bin/bash

# --- CONFIGURATION ---
RUNS=10
COOLDOWN=5
OUTPUT_DIR="results2"

# Create the results directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# 1. Compile Java Code
echo "Compiling Java files..."
javac -cp "lib/*" Spawner.java JavaBaseline.java Message.java Idle.java ThreadRing.java Trapezoid.java

# 2. Global JVM Warmup
# We run the Java Baseline once, without measuring, to load the JVM 
# and shared libraries into the OS RAM (File System Cache).
echo "------------------------------------------------"
echo "WARMING UP JVM "
echo "------------------------------------------------"
java -cp "lib/*:." JavaBaseline > /dev/null
echo "JVM Warmup Complete."
echo "------------------------------------------------"

# Function to run a test
run_test() {
    NAME=$1
    CMD=$2
    
    echo ""
    echo ">>> Starting Experiment: $NAME"
    
    for i in $(seq 1 $RUNS); do
        echo "    Run #$i / $RUNS"
        
        # Define output filename
        CSV_FILE="$OUTPUT_DIR/${NAME}_run_${i}.csv"

        # Run EnergiBridge
        # We redirect text output to /dev/null so we only get the CSV
        sudo ./energibridge --summary --output "$CSV_FILE" sh -c "$CMD > /dev/null"

        echo "    Cooling down ($COOLDOWN sec)..."
        sleep $COOLDOWN
    done
}

# --- EXPERIMENTS ---
# Uncomment the ones you want to run

# 1. Spawner
#run_test "elixir_spawn" "elixir Spawner.exs"
#run_test "java_spawn" "java -cp lib/*:. Spawner"

# 2. Message Passing
#run_test "elixir_message" "elixir Message.exs"
#run_test "java_message" "java -cp lib/*:. Message"

# 3. Idle State
#run_test "elixir_idle" "elixir Idle.exs"
#run_test "java_idle" "java -cp lib/*:. Idle"

# 4. Thread Ring
run_test "elixir_ring" "elixir thread_ring.exs"
run_test "java_ring" "java -cp lib/*:. ThreadRing"

# 5. Trapezoid (Math)
run_test "elixir_trap" "elixir trapezoid.exs"
run_test "java_trap" "java -cp lib/*:. Trapezoid"

# 6. Baselines (Optional)
run_test "elixir_base" "elixir Baseline.exs"
run_test "java_base" "java -cp lib/*:. JavaBaseline"

echo ""
echo "All experiments finished! Results are in $OUTPUT_DIR"