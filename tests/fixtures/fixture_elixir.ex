# @file fixture_elixir.ex
# @brief Comprehensive Elixir test fixture for parser validation.
# @details Covers pattern matching, guards, pipe operator, behaviours,
#          GenServer callbacks, supervisors, comprehensions, sigils,
#          structs with enforce_keys, typespecs, and ExUnit testing.
# Single line comment

# ── Main module ───────────────────────────────────────────────────────

defmodule MyApp.Server do
  @moduledoc """
  GenServer implementation for managing application state.

  Handles synchronous calls, asynchronous casts, and info messages.
  Supports state initialization with validated options.
  """

  use GenServer
  import Enum
  alias MyApp.Config
  alias MyApp.Server.State
  require Logger

  @behaviour GenServer

  # ── Constants ───────────────────────────────────────────────────────

  # @brief Default timeout for GenServer calls in milliseconds.
  @default_timeout 5_000

  # @brief Maximum items stored in server state.
  @max_items 1_000

  # ── Struct ──────────────────────────────────────────────────────────

  @doc """
  Internal state struct for the server.

  @field name Server instance name.
  @field port Listening port number.
  @field items List of stored items.
  @field started_at Timestamp of server start.
  """
  defstruct [:name, :port, items: [], started_at: nil]

  # ── Typespecs ───────────────────────────────────────────────────────

  @type t :: %__MODULE__{
    name: String.t(),
    port: non_neg_integer(),
    items: list(any()),
    started_at: DateTime.t() | nil
  }

  @type option :: {:name, String.t()} | {:port, non_neg_integer()}

  # ── Public API ──────────────────────────────────────────────────────

  @doc """
  Start a new server process linked to the caller.

  @param opts Keyword list of options (:name, :port).
  @return {:ok, pid} on success or {:error, reason} on failure.
  """
  @spec start_link(keyword()) :: GenServer.on_start()
  def start_link(opts) do
    name = Keyword.get(opts, :name, "default")
    GenServer.start_link(__MODULE__, opts, name: via_tuple(name))
  end

  @doc """
  Add an item to the server's collection.

  @param server The server PID or registered name.
  @param item The item to store.
  @return :ok
  """
  @spec add_item(GenServer.server(), any()) :: :ok
  def add_item(server, item) do
    GenServer.call(server, {:add_item, item})
  end

  @doc """
  Retrieve all stored items.

  @param server The server PID or registered name.
  @return List of stored items.
  """
  @spec get_items(GenServer.server()) :: list(any())
  def get_items(server) do
    GenServer.call(server, :get_items)
  end

  @doc """
  Asynchronously notify the server of an event.

  @param server The server PID.
  @param event The event data to process.
  @return :ok
  """
  @spec notify(GenServer.server(), any()) :: :ok
  def notify(server, event) do
    GenServer.cast(server, {:notify, event})
  end

  # ── Private helpers ─────────────────────────────────────────────────

  # @brief Generate a via-tuple for process registration.
  # @param name The server name.
  # @return Via-tuple for Registry lookup.
  defp via_tuple(name) do
    {:via, Registry, {MyApp.Registry, name}}
  end

  # ── GenServer callbacks ─────────────────────────────────────────────

  @impl true
  def init(opts) do
    # Validate required options
    name = Keyword.fetch!(opts, :name)
    port = Keyword.get(opts, :port, 4000)

    state = %__MODULE__{
      name: name,
      port: port,
      started_at: DateTime.utc_now()
    }

    Logger.info("Server #{name} started on port #{port}")
    {:ok, state}
  end

  @impl true
  def handle_call({:add_item, item}, _from, state) do
    # Check capacity before adding
    if length(state.items) >= @max_items do
      {:reply, {:error, :capacity_exceeded}, state}
    else
      new_state = %{state | items: [item | state.items]}
      {:reply, :ok, new_state}
    end
  end

  @impl true
  def handle_call(:get_items, _from, state) do
    {:reply, Enum.reverse(state.items), state}
  end

  @impl true
  def handle_cast({:notify, event}, state) do
    Logger.debug("Received event: #{inspect(event)}")
    {:noreply, state}
  end

  @impl true
  def handle_info(:timeout, state) do
    Logger.warn("Server #{state.name} timed out")
    {:noreply, state}
  end

  # @brief Handle internal state cleanup and maintenance.
  # @param state Current server state.
  # @return Updated state with pruned items.
  defp handle_internal(state) do
    # Prune items exceeding max capacity
    pruned = Enum.take(state.items, @max_items)
    %{state | items: pruned}
  end

  @doc """
  Define a macro for compile-time code generation.

  @param expr The expression to wrap.
  @return Quoted AST wrapping the expression.
  """
  defmacro my_macro(expr) do
    quote do
      result = unquote(expr)
      Logger.debug("Macro result: #{inspect(result)}")
      result
    end
  end
end

# ── Protocol ──────────────────────────────────────────────────────────

defprotocol Printable do
  @moduledoc """
  Protocol for types that can be printed as formatted strings.
  """

  @doc """
  Convert a value to its formatted string representation.

  @param data The value to format.
  @return Formatted string.
  """
  @spec print(t) :: String.t()
  def print(data)
end

# ── Protocol implementation ───────────────────────────────────────────

defimpl Printable, for: MyApp.Server do
  @doc """
  Format a server struct for display.

  @param server The server struct to format.
  @return String in format "Server(name:port)".
  """
  def print(server) do
    "Server(#{server.name}:#{server.port})"
  end
end

defimpl Printable, for: BitString do
  def print(str) do
    "String(#{str})"
  end
end

# ── Utility module with guards and pipes ──────────────────────────────

defmodule MyApp.Utils do
  @moduledoc """
  Utility functions demonstrating pattern matching, guards,
  pipe operators, and comprehensions.
  """

  @doc """
  Classify a value using guard clauses and pattern matching.

  @param value The value to classify.
  @return Atom describing the value's category.
  """
  @spec classify(any()) :: atom()
  def classify(value) when is_integer(value) and value > 0, do: :positive
  def classify(value) when is_integer(value) and value < 0, do: :negative
  def classify(0), do: :zero
  def classify(value) when is_binary(value), do: :string
  def classify(value) when is_list(value), do: :list
  def classify(_), do: :unknown

  @doc """
  Process a list using pipe operator for data transformation.

  @param items List of strings to process.
  @return Sorted list of unique uppercase strings.
  """
  @spec process_list(list(String.t())) :: list(String.t())
  def process_list(items) do
    items
    |> Enum.map(&String.trim/1)
    |> Enum.reject(&(&1 == ""))
    |> Enum.map(&String.upcase/1)
    |> Enum.uniq()
    |> Enum.sort()
  end

  @doc """
  Demonstrate for-comprehension with multiple generators and filters.

  @param range Upper bound for the search space.
  @return List of Pythagorean triples.
  """
  @spec pythagorean_triples(pos_integer()) :: list(tuple())
  def pythagorean_triples(range) do
    for a <- 1..range,
        b <- a..range,
        c <- b..range,
        a * a + b * b == c * c do
      {a, b, c}
    end
  end

  @doc """
  Safe division returning :error tuple on zero divisor.

  @param a Dividend.
  @param b Divisor.
  @return {:ok, result} or {:error, :division_by_zero}.
  """
  @spec safe_divide(number(), number()) :: {:ok, float()} | {:error, atom()}
  def safe_divide(_, 0), do: {:error, :division_by_zero}
  def safe_divide(a, b), do: {:ok, a / b}

  @doc """
  Recursively compute factorial with guard clause.

  @param n Non-negative integer.
  @return Factorial of n.
  """
  @spec factorial(non_neg_integer()) :: pos_integer()
  def factorial(0), do: 1
  def factorial(n) when n > 0, do: n * factorial(n - 1)
end

# ── Behaviour definition ─────────────────────────────────────────────

defmodule MyApp.Plugin do
  @moduledoc """
  Behaviour defining the plugin interface.
  """

  @doc "Initialize the plugin with configuration options."
  @callback init(opts :: keyword()) :: {:ok, any()} | {:error, String.t()}

  @doc "Execute the plugin's main logic."
  @callback execute(state :: any()) :: :ok | {:error, String.t()}

  @doc "Clean up plugin resources."
  @callback cleanup(state :: any()) :: :ok

  @optional_callbacks [cleanup: 1]
end
