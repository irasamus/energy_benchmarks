defmodule Idle do
  def run do
    n_actors = 100_000
    duration_seconds = 30
    parent = self()

    # Spawn actors and have them signal when they are fully booted
    Enum.each(1..n_actors, fn _ ->
      spawn(fn ->
        send(parent, :ready)
        receive do :stop -> :ok end
      end)
    end)

    # Wait until all 100,000 processes are alive and resting
    Enum.each(1..n_actors, fn _ ->
      receive do :ready -> :ok end
    end)

    # NOW the system is truly idle. Start the measurement.
    IO.puts("LOG_START:#{System.system_time(:millisecond)}")

    # Sleep for 30 seconds
    Process.sleep(duration_seconds * 1000)

    IO.puts("LOG_END:#{System.system_time(:millisecond)}")
  end
end

Idle.run()
