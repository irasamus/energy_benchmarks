defmodule Spawner do
  def run do
    # Total actors to spawn
    total_actors = 1_000_000
    # Process in small batches to keep memory flat/stable
    batch_size = 5_000
    num_batches = div(total_actors, batch_size)

    parent = self()

    IO.puts("--- STARTING SPAWNER (Batched) ---")
    IO.puts("LOG_START:#{System.system_time(:millisecond)}")

    # Loop for the number of batches
    Enum.each(1..num_batches, fn _batch_idx ->

      # 1. Burst: Spawn 5,000 actors
      Enum.each(1..batch_size, fn _ ->
        spawn(fn -> send(parent, :done) end)
      end)

      # 2. Cleanup: Wait for exactly 5,000 messages
      # This clears the mailbox immediately so it never grows large
      Enum.each(1..batch_size, fn _ ->
        receive do
          :done -> :ok
        end
      end)

    end)

    IO.puts("LOG_END:#{System.system_time(:millisecond)}")
  end
end

Spawner.run()
