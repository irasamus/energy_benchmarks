defmodule Fibonacci do
  # The Worker Actor
  def worker(parent_pid, n) do
    if n <= 1 do
      # Base case: send result back to actual parent
      send(parent_pid, {:result, n})
    else
      # THE FIX: Save our PID before spawning children!
      me = self()

      # Spawn children, passing 'me' as their parent
      spawn(fn -> worker(me, n - 1) end)
      spawn(fn -> worker(me, n - 2) end)

      # Wait for the two responses
      val1 = receive do {:result, v} -> v end
      val2 = receive do {:result, v} -> v end

      # Send the sum back to the parent
      send(parent_pid, {:result, val1 + val2})
    end
  end

  def run do
    n_value = 28

    IO.puts("--- STARTING FIBONACCI (N=#{n_value}) ---")
    IO.puts("LOG_START:#{System.system_time(:millisecond)}")

    {time, result} = :timer.tc(fn ->
      # THE FIX: Save main process PID
      me = self()

      # Spawn the master worker
      spawn(fn -> worker(me, n_value) end)

      # Wait for the final, total result
      receive do
        {:result, val} -> val
      end
    end)

    IO.puts("LOG_END:#{System.system_time(:millisecond)}")
    IO.puts("Result: #{result}")
    IO.puts("Time taken: #{time / 1000} ms")
  end
end

Fibonacci.run()
