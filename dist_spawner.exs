defmodule DistSpawner do
  def worker_task(parent) do
    send(parent, :done)
  end

  def run_master(worker_node) do
    total_actors = 1_000_000
    batch_size = 5_000
    num_batches = div(total_actors, batch_size)
    parent = self()

    IO.puts("LOG_START:#{System.system_time(:millisecond)}")

    Enum.each(1..num_batches, fn _ ->
      # Spawn batch on remote node
      Enum.each(1..batch_size, fn _ ->
        Node.spawn(worker_node, DistSpawner, :worker_task, [parent])
      end)
      # Wait for batch
      Enum.each(1..batch_size, fn _ -> receive do :done -> :ok end end)
    end)

    IO.puts("LOG_END:#{System.system_time(:millisecond)}")
    System.halt(0)
  end
end

case System.argv() do
  ["worker"] -> Process.sleep(:infinity)
  ["master", node] -> DistSpawner.run_master(String.to_atom(node))
end
