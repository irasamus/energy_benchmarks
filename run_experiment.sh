#!/bin/bash

# Configuration
RUNS=10
COOLDOWN=10

# Compile Java first
echo "Compiling Java..."
javac -cp "lib/*" Spawner.java JavaBaseline.java Message.java Idle.java

# Function to run a test
run_test() {
    NAME=$1
    CMD=$2
    
    echo "------------------------------------------------"
    echo "Starting Experiment: $NAME"
    echo "------------------------------------------------"

    for i in $(seq 1 $RUNS); do
        echo "Run #$i / $RUNS"
        
        # Define output filenames
        CSV_FILE="results/${NAME}_run_${i}.csv"
        LOG_FILE="results/${NAME}_run_${i}.log"

        # Run EnergiBridge
        # We use 'sh -c' to handle complex commands and redirection
        sudo ./energibridge --summary --output "$CSV_FILE" sh -c "$CMD > $LOG_FILE"

        echo "Cooling down for $COOLDOWN seconds..."
        sleep $COOLDOWN
    done
}


# --- EXPERIMENTS ---

# 1. Elixir Spawner
#run_test "elixir_spawn" "elixir Spawner.exs"

# 2. Elixir Baseline
#run_test "elixir_base" "elixir Baseline.exs"

# 3. Java Spawner
#run_test "java_graal_spawn" "java -cp lib/*:. Spawner"

# 4. Java Baseline
#run_test "java_graal_base" "java -cp lib/*:. JavaBaseline"

# 5. Elixir Message
#run_test "elixir_message" "elixir Message.exs"

# 6. Java Message
#run_test "java_graal_message" "java -cp lib/*:. Message"

# 7. Elixir Idle
#run_test "elixir_idle" "elixir Idle.exs"

# 8. Java Idle
run_test "java_idle" "java -cp lib/*:. Idle"

echo "All experiments finished!"