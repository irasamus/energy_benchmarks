defmodule Baseline do
  def run do
    n_actors = 1_000_000

    IO.puts("LOG_START:#{System.system_time(:millisecond)}")

    Enum.each(1..n_actors, fn _ ->
      # Do nothing
      :ok
    end)

    IO.puts("LOG_END:#{System.system_time(:millisecond)}")
  end
end
Baseline.run()
