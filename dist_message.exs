defmodule PingPong do
  def ponger do
    receive do
      {:ping, sender_pid} ->
        send(sender_pid, :pong)
        ponger()
    end
  end

  def run_master(worker_node, n) do
    # Spawn the Ponger on the worker node
    ponger_pid = Node.spawn(worker_node, PingPong, :ponger, [])

    IO.puts("LOG_START:#{System.system_time(:millisecond)}")

    # Start the sequence
    send(ponger_pid, {:ping, self()})
    loop(ponger_pid, n)
  end

  defp loop(ponger_pid, n) when n > 0 do
    receive do
      :pong ->
        send(ponger_pid, {:ping, self()})
        loop(ponger_pid, n - 1)
    end
  end
  defp loop(_, _) do
    IO.puts("LOG_END:#{System.system_time(:millisecond)}")
    System.halt(0)
  end
end

case System.argv() do
  ["worker"] -> Process.sleep(:infinity)
  ["master", node] -> PingPong.run_master(String.to_atom(node), 1_000_000)
end
