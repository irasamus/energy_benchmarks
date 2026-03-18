defmodule Ponger do
  use GenServer

  # Public API
  def start_link(_opts), do: GenServer.start_link(__MODULE__, nil, name: __MODULE__)

  # Callbacks
  @impl true
  def init(state), do: {:ok, state}

  # Handle asynchronous messages
  @impl true
  def handle_info({:ping, pinger_pid}, state) do
    send(pinger_pid, :pong)
    {:noreply, state}
  end
end

defmodule Pinger do
  use GenServer

  # Public API
  def start_link(opts) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  def run(pid, limit) do
    GenServer.cast(pid, {:run, limit})
  end

  # Callbacks
  @impl true
  def init(_opts) do
    # State: {count, limit, start_time}
    {:ok, {0, 0, 0}}
  end

  # Handle the initial "run" command
  @impl true
  def handle_cast({:run, limit}, _state) do
    IO.puts("LOG_START:#{System.system_time(:millisecond)}")

    # Send the first ping
    send(Ponger, {:ping, self()})

    # Set the initial state
    {:noreply, {1, limit, System.system_time(:millisecond)}}
  end

  # Handle the asynchronous "pong" reply
  @impl true
  def handle_info(:pong, {count, limit, start_time}) when count < limit do
    # Send the next ping
    send(Ponger, {:ping, self()})
    # Increment the count
    {:noreply, {count + 1, limit, start_time}}
  end

  # Handle the final "pong"
  @impl true
  def handle_info(:pong, {count, limit, start_time}) when count == limit do
    IO.puts("LOG_END:#{System.system_time(:millisecond)}")
    IO.puts("Time taken: #{System.system_time(:millisecond) - start_time} ms")
    System.halt(0)
    # Stop the server
    {:stop, :normal, {count, limit, start_time}}
  end
end

defmodule PingPong do
  def run do
    n_messages = 5_000_000

    # Start both servers
    {:ok, _ponger} = Ponger.start_link([])
    {:ok, pinger} = Pinger.start_link([])

    # Kick off the process
    Pinger.run(pinger, n_messages)

    # Keep the main process alive until the Pinger is done
    Process.sleep(:infinity)
  end
end

PingPong.run()
