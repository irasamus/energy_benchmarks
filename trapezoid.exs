defmodule Trapezoid do

  # Mathematical function
  def fx(x) do
    :math.sin(x) * :math.cos(x) * :math.sqrt(x)
  end

  # --- Worker Logic ---
  def worker(master_pid, left, step, intervals) do
    # Calculate area for this chunk
    area = calculate_chunk(left, step, intervals, 0.0)
    send(master_pid, {:result, area})
  end

  # Tail-recursive math loop
  defp calculate_chunk(_x, _step, 0, acc_area), do: acc_area
  defp calculate_chunk(x, step, count, acc_area) do
    # Trapezoidal rule math
    trap_area = (fx(x) + fx(x + step)) / 2.0 * step
    calculate_chunk(x + step, step, count - 1, acc_area + trap_area)
  end

  # --- Master Logic ---
  def master(total_workers, workers_finished, total_area, start_time) do
    if workers_finished == total_workers do
      end_time = System.system_time(:millisecond)
      IO.puts("LOG_END:#{end_time}")
      IO.puts("Result Area: #{total_area}")
      IO.puts("Time taken: #{end_time - start_time} ms")
      System.halt(0)
    else
      receive do
        {:result, area} ->
          master(total_workers, workers_finished + 1, total_area + area, start_time)
      end
    end
  end

  # --- Main ---
  def run do
    # 100 Million intervals for heavy CPU load
    total_intervals = 100_000_000
    num_workers = 100
    intervals_per_worker = div(total_intervals, num_workers)

    left_boundary = 1.0
    right_boundary = 100.0
    step = (right_boundary - left_boundary) / total_intervals

    IO.puts("--- STARTING TRAPEZOID (Elixir) ---")
    start_time = System.system_time(:millisecond)
    IO.puts("LOG_START:#{start_time}")

    # Spawn Master
    master_pid = spawn(fn -> master(num_workers, 0, 0.0, start_time) end)

    # Spawn Workers
    Enum.each(0..(num_workers - 1), fn i ->
      w_left = left_boundary + (i * intervals_per_worker * step)
      spawn(fn -> worker(master_pid, w_left, step, intervals_per_worker) end)
    end)

    Process.sleep(:infinity)
  end
end

Trapezoid.run()
