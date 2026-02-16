#!/usr/bin/env python3
# Single line comment
"""
Multi-line docstring comment
spanning multiple lines
"""
import os
import sys
from pathlib import Path
from typing import (
    Optional, List, Dict, Union, Protocol,
    TypeVar, Generic, Iterator, AsyncIterator
)
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from contextlib import contextmanager

MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30.0
_INTERNAL_CACHE: Dict[str, int] = {}

T = TypeVar("T")


@dataclass(slots=True)
class Config:
    """Configuration data holder for the application.

    @brief Stores key-value pairs with optional default fallback.
    @note Immutable after creation when frozen=True is used.
    """
    name: str
    values: Dict[str, str] = field(default_factory=dict)
    debug: bool = False

    def get(self, key: str, default: str = "") -> str:
        """Retrieve a configuration value by key.

        @param key The configuration key to look up.
        @param default Fallback value if key is missing.
        @return The configuration value or default.
        """
        # Check primary values first
        if key in self.values:
            return self.values[key]
        # Fallback to default
        return default

    def __post_init__(self) -> None:
        """Validate configuration after initialization.

        @brief Ensures name is non-empty and normalizes values.
        @raises ValueError If name is empty or whitespace.
        """
        if not self.name.strip():
            raise ValueError("Config name cannot be empty")


class MyClass:
    """Class docstring for MyClass.

    @brief Base class demonstrating various Python constructs.
    @details Includes nested classes, properties, and static methods.
    """

    class InnerHelper:
        """Nested helper class for internal data grouping.

        @brief Handles auxiliary computations within MyClass scope.
        """
        def __init__(self, tag: str):
            """Initialize the helper with a tag identifier.

            @param tag Short label for categorization.
            """
            self.tag = tag

        def describe(self) -> str:
            """Return a formatted description of this helper.

            @return String combining class name and tag.
            """
            return f"Helper({self.tag})"

    def __init__(self, name: str, retries: int = MAX_RETRIES):
        """Initialize MyClass with a name and retry count.

        @param name Identifier for this instance.
        @param retries Maximum retry attempts; defaults to MAX_RETRIES.
        """
        self._name = name
        self._retries = retries
        # Internal counter tracks invocation count
        self._call_count = 0

    @property
    def name(self) -> str:
        """Read-only property exposing the instance name.

        @return The name string set during initialization.
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the instance name after validation.

        @param value New name; must be non-empty.
        @raises ValueError If value is empty.
        """
        if not value:
            raise ValueError("Name cannot be empty")
        self._name = value

    @staticmethod
    def create_default() -> "MyClass":
        """Factory method to build a MyClass with default settings.

        @return A new MyClass instance with name='default'.
        """
        return MyClass("default")

    @classmethod
    def from_dict(cls, data: dict) -> "MyClass":
        """Construct a MyClass from a dictionary payload.

        @param data Dictionary with 'name' and optional 'retries' keys.
        @return A new instance populated from data.
        @raises KeyError If 'name' key is missing.
        """
        return cls(
            name=data["name"],
            retries=data.get("retries", MAX_RETRIES),
        )

    def process(self, items: List[str], *, verbose: bool = False) -> Optional[str]:
        """Process a list of string items with optional logging.

        @param items List of strings to process sequentially.
        @param verbose Enable detailed logging when True.
        @return The first valid item found or None if all are empty.
        """
        self._call_count += 1
        for item in items:
            # Skip empty entries
            if not item.strip():
                continue
            if verbose:
                print(f"Processing: {item}")
            # Conditional return on first valid item
            return item if len(item) > 1 else item.upper()
        return None

    def compute(self, x: int, y: int) -> int:
        """Compute a value using conditional assignment on return.

        @param x First operand.
        @param y Second operand.
        @return Sum if both positive, difference otherwise.
        """
        # Ternary return with compound condition
        return (x + y) if (x > 0 and y > 0) else abs(x - y)


class AbstractProcessor(ABC):
    """Abstract base class for all data processors.

    @brief Defines the interface that concrete processors must implement.
    @see ConcreteProcessor for a working implementation.
    """

    @abstractmethod
    def execute(self, data: bytes) -> bool:
        """Execute processing on raw byte data.

        @param data The raw input bytes to process.
        @return True if processing succeeded, False otherwise.
        """
        ...

    @abstractmethod
    async def execute_async(self, data: bytes) -> bool:
        """Asynchronous variant of execute.

        @param data The raw input bytes to process.
        @return True if processing succeeded.
        """
        ...


class ConcreteProcessor(AbstractProcessor):
    """Concrete implementation of AbstractProcessor.

    @brief Processes byte data by decoding and validating content.
    @extends AbstractProcessor
    """

    def execute(self, data: bytes) -> bool:
        """Decode and validate byte data synchronously.

        @param data Raw bytes, expected UTF-8 encoded text.
        @return True if decoding and validation succeed.
        @raises UnicodeDecodeError Propagated if data is not valid UTF-8.
        """
        try:
            text = data.decode("utf-8")
            # Validate non-empty after decode
            return bool(text.strip())
        except UnicodeDecodeError:
            return False
        finally:
            # Ensure cleanup regardless of outcome
            pass

    async def execute_async(self, data: bytes) -> bool:
        """Async decode and validate byte data.

        @param data Raw bytes to process asynchronously.
        @return True if valid content found.
        """
        return self.execute(data)


class GenericContainer(Generic[T]):
    """Generic container holding items of type T.

    @brief Type-safe collection with iteration and lookup support.
    @tparam T The element type stored in this container.
    """

    def __init__(self) -> None:
        """Initialize an empty container."""
        self._items: List[T] = []

    def add(self, item: T) -> None:
        """Append an item to the container.

        @param item Element of type T to add.
        """
        self._items.append(item)

    def __iter__(self) -> Iterator[T]:
        """Iterate over contained items.

        @return Iterator yielding items of type T.
        """
        yield from self._items

    def find(self, predicate) -> Optional[T]:
        """Find the first item matching a predicate function.

        @param predicate Callable accepting T and returning bool.
        @return The first matching item or None.
        """
        for item in self._items:
            if predicate(item):
                return item
        return None


class Renderable(Protocol):
    """Protocol defining objects that can render to string.

    @brief Structural typing interface for render-capable objects.
    """

    def render(self) -> str:
        """Produce a string representation.

        @return Rendered string output.
        """
        ...


@property
def regular_function(x: int) -> int:
    """Simple function demonstrating decorator and return.

    @param x Input integer value.
    @return The input value unchanged.
    """
    return x


def function_with_walrus(data: List[int]) -> Optional[int]:
    """Demonstrate the walrus operator in conditional expressions.

    @param data List of integers to scan.
    @return The first value greater than 10, or None.
    """
    # Walrus operator assigns and tests in one expression
    if (n := next((x for x in data if x > 10), None)) is not None:
        return n
    return None


def multi_return_paths(value: int) -> Union[str, int, None]:
    """Function with multiple return paths and match statement.

    @param value Integer selector for branching logic.
    @return A string, integer, or None depending on value.
    """
    match value:
        case 0:
            return "zero"
        case n if n < 0:
            # Negative values return absolute
            return abs(n)
        case n if n > 100:
            return None
        case _:
            return str(value)


def generator_function(limit: int) -> Iterator[int]:
    """Generator yielding squared values up to a limit.

    @param limit Upper bound (exclusive) for generation.
    @yield Squared integers from 0 to limit-1.
    """
    for i in range(limit):
        # Yield computed square
        yield i * i


async def async_generator(items: List[str]) -> AsyncIterator[str]:
    """Async generator that yields processed strings.

    @param items Source strings to process.
    @yield Upper-cased non-empty strings.
    """
    for item in items:
        if item.strip():
            yield item.upper()


@contextmanager
def managed_resource(path: str):
    """Context manager for safe resource acquisition and release.

    @param path File system path to the resource.
    @yield The opened file handle.
    @raises IOError If the resource cannot be opened.
    """
    f = open(path, "r")
    try:
        yield f
    finally:
        f.close()


def closure_factory(multiplier: int):
    """Create a closure that multiplies its argument.

    @param multiplier The fixed multiplier for the returned function.
    @return A callable that multiplies input by multiplier.
    """
    def inner(x: int) -> int:
        """Inner closure performing the multiplication.

        @param x Value to multiply.
        @return Product of x and the captured multiplier.
        """
        # Captures multiplier from enclosing scope
        return x * multiplier
    return inner


def uses_unpacking(*args: int, **kwargs: str) -> Dict[str, Union[int, str]]:
    """Demonstrate variadic arguments and unpacking.

    @param args Positional integer arguments.
    @param kwargs Named string arguments.
    @return Combined dictionary of all arguments.
    """
    result: Dict[str, Union[int, str]] = {}
    for i, val in enumerate(args):
        result[f"arg_{i}"] = val
    result.update(kwargs)
    return result


# Lambda assigned to a variable for inline transforms
transform = lambda x: x * 2 + 1

# List comprehension with conditional filtering
EVEN_SQUARES = [x ** 2 for x in range(20) if x % 2 == 0]


async def async_function():
    """Standalone async coroutine awaiting a no-op.

    @brief Minimal async function for testing async detection.
    """
    await None


def deeply_nested_logic(matrix: List[List[int]]) -> int:
    """Process a matrix with deeply nested control flow.

    @param matrix 2D list of integers.
    @return Cumulative sum of positive even values.
    """
    total = 0
    for row in matrix:
        for val in row:
            if val > 0:
                if val % 2 == 0:
                    # Accumulate positive evens
                    total += val
                else:
                    continue
            else:
                # Skip non-positive values
                pass
    return total


def exception_handling_example(path: str) -> Optional[str]:
    """Demonstrate comprehensive exception handling patterns.

    @param path File path to attempt reading.
    @return File contents or None on failure.
    """
    try:
        with open(path, "r") as f:
            content = f.read()
        if not content:
            raise ValueError("Empty file")
        return content
    except FileNotFoundError:
        # File does not exist
        return None
    except (PermissionError, OSError) as e:
        # Access denied or OS-level error
        sys.exit(1)
    except Exception:
        raise
    finally:
        # Cleanup runs regardless of outcome
        pass

# coverage extension pre-line comment
MAX_BATCH = 64  # inline extension comment
# another variable comment
CACHE_LIMIT = 128
"""coverage extension multiline comment for parser fixtures"""
MAX_USERS = 500
