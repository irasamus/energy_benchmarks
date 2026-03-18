defmodule ThreadRing do
  def loop(next_pid) do
    receive do
      0 ->
        # Added LOG_END before halting
        IO.puts("LOG_END:#{System.system_time(:millisecond)}")
        IO.puts("--- FINISHED ---")
        System.halt(0)

      token ->
        send(next_pid, token - 1)
        loop(next_pid)
    end
  end

  def run do
    n_actors = 5_000
    token_value = 100_000_000

    IO.puts("--- STARTING THREAD RING (Elixir) ---")
    IO.puts("LOG_START:#{System.system_time(:millisecond)}")

    first_pid = Enum.reduce(n_actors..2, self(), fn _id, neighbor_pid ->
      spawn(fn -> loop(neighbor_pid) end)
    end)

    send(first_pid, token_value)

    loop(first_pid)
  end
end

ThreadRing.run()
