/// @file fixture_csharp.cs
/// @brief Comprehensive C# test fixture for parser validation.
/// @details Covers records, pattern matching, LINQ, extension methods,
///          async streams, nullable reference types, init-only setters,
///          generic constraints, events, delegates, and indexers.
// Single line comment
/* Multi-line
   comment */
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Threading;

namespace MyApp {

/* ── Delegates and events ─────────────────────────────────────────────── */

/// <summary>
/// Delegate for handling data change notifications.
/// </summary>
/// <param name="sender">The object raising the event.</param>
/// <param name="data">The changed data payload.</param>
public delegate void DataChangedHandler(object sender, string data);

/// <summary>
/// Delegate for value transformation operations.
/// </summary>
/// <typeparam name="T">Input and output type.</typeparam>
/// <param name="value">The value to transform.</param>
/// <returns>Transformed value.</returns>
public delegate T Transform<T>(T value);

/* ── Attributes ───────────────────────────────────────────────────────── */

/// <summary>
/// Custom attribute marking classes that require auditing.
/// </summary>
[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
public class AuditableAttribute : Attribute {
    /// <summary>The audit level (1=low, 3=high).</summary>
    public int Level { get; set; } = 1;
}

/* ── Main class ───────────────────────────────────────────────────────── */

/// <summary>
/// Primary class demonstrating various C# constructs including
/// properties, events, indexers, and async patterns.
/// </summary>
[Serializable]
[Auditable(Level = 2)]
public class Person : IComparable<Person>, IDisposable {
    /// <summary>Maximum age constraint for validation.</summary>
    public const int MAX_AGE = 150;

    /// <summary>Instance counter tracking total allocations.</summary>
    private static int _instanceCount = 0;

    /// <summary>Internal name storage with backing field.</summary>
    private string _name;

    /// <summary>
    /// Full name with validation on set.
    /// </summary>
    /// <value>Non-null, non-empty person name.</value>
    /// <exception cref="ArgumentException">Thrown when value is empty.</exception>
    public string Name {
        get => _name;
        set {
            // Validate non-empty name
            if (string.IsNullOrWhiteSpace(value))
                throw new ArgumentException("Name cannot be empty");
            _name = value;
        }
    }

    /// <summary>Person's age with init-only setter.</summary>
    public int Age { get; init; }

    /// <summary>Optional email address (nullable reference type).</summary>
    public string? Email { get; set; }

    /// <summary>Read-only unique identifier generated at construction.</summary>
    public Guid Id { get; } = Guid.NewGuid();

    /// <summary>
    /// Event raised when person data changes.
    /// </summary>
    public event DataChangedHandler? OnDataChanged;

    /// <summary>
    /// Construct a new Person with name and age.
    /// </summary>
    /// <param name="name">Display name (required).</param>
    /// <param name="age">Age in years (must be 0..MAX_AGE).</param>
    public Person(string name, int age) {
        _name = name;
        Age = age;
        Interlocked.Increment(ref _instanceCount);
    }

    /// <summary>
    /// Greet this person on the console.
    /// </summary>
    public void Greet() {
        // Fire data changed event
        OnDataChanged?.Invoke(this, $"Greeted {Name}");
        Console.WriteLine($"Hello, {Name}!");
    }

    /// <summary>
    /// Fetch person data asynchronously with cancellation support.
    /// </summary>
    /// <param name="token">Cancellation token for cooperative cancellation.</param>
    /// <returns>Formatted data string.</returns>
    public static async Task<string> FetchAsync(CancellationToken token = default) {
        await Task.Delay(100, token);
        return "data";
    }

    /// <summary>
    /// Compare persons by age for sorting.
    /// </summary>
    /// <param name="other">Person to compare with.</param>
    /// <returns>Comparison result: negative, zero, or positive.</returns>
    public int CompareTo(Person? other) {
        if (other is null) return 1;
        return Age.CompareTo(other.Age);
    }

    /// <summary>
    /// Dispose of managed resources.
    /// </summary>
    public void Dispose() {
        // Cleanup managed resources
        Interlocked.Decrement(ref _instanceCount);
        GC.SuppressFinalize(this);
    }

    /// <summary>
    /// Indexer for accessing person properties by name.
    /// </summary>
    /// <param name="propertyName">Name of the property to access.</param>
    /// <returns>Property value as object, or null.</returns>
    public object? this[string propertyName] {
        get {
            return propertyName switch {
                "Name" => Name,
                "Age" => Age,
                "Email" => Email,
                _ => null,
            };
        }
    }

    /// <summary>
    /// Deconstruct for pattern matching support.
    /// </summary>
    /// <param name="name">Output: person name.</param>
    /// <param name="age">Output: person age.</param>
    public void Deconstruct(out string name, out int age) {
        name = Name;
        age = Age;
    }

    /// <summary>
    /// Get total number of Person instances created.
    /// </summary>
    /// <returns>Instance count.</returns>
    public static int GetInstanceCount() => _instanceCount;
}

/* ── Interface ────────────────────────────────────────────────────────── */

/// <summary>
/// Interface for greeting operations with default implementation.
/// </summary>
public interface IGreeter {
    /// <summary>
    /// Say hello to a named person.
    /// </summary>
    /// <param name="name">Person's name.</param>
    void SayHello(string name);

    /// <summary>
    /// Default farewell implementation.
    /// </summary>
    /// <param name="name">Person's name.</param>
    void SayGoodbye(string name) {
        Console.WriteLine($"Goodbye, {name}");
    }
}

/// <summary>
/// Generic repository interface with covariant type parameter.
/// </summary>
/// <typeparam name="T">Entity type, must be a class with parameterless ctor.</typeparam>
public interface IRepository<T> where T : class, new() {
    /// <summary>Find entity by ID.</summary>
    Task<T?> FindByIdAsync(int id);

    /// <summary>Get all entities as async stream.</summary>
    IAsyncEnumerable<T> GetAllAsync(CancellationToken token = default);

    /// <summary>Save an entity.</summary>
    Task<bool> SaveAsync(T entity);
}

/* ── Struct ───────────────────────────────────────────────────────────── */

/// <summary>
/// Immutable 2D point struct with operator overloading.
/// </summary>
public readonly struct Point {
    /// <summary>Horizontal coordinate.</summary>
    public double X { get; init; }
    /// <summary>Vertical coordinate.</summary>
    public double Y { get; init; }

    /// <summary>
    /// Add two points component-wise.
    /// </summary>
    public static Point operator +(Point a, Point b) => new() { X = a.X + b.X, Y = a.Y + b.Y };

    /// <summary>
    /// Compute distance from origin.
    /// </summary>
    public double Magnitude => Math.Sqrt(X * X + Y * Y);
}

/* ── Enum ─────────────────────────────────────────────────────────────── */

/// <summary>
/// Color flags enum supporting bitwise combinations.
/// </summary>
[Flags]
public enum Color {
    /// <summary>No color selected.</summary>
    None = 0,
    /// <summary>Red channel.</summary>
    Red = 1,
    /// <summary>Green channel.</summary>
    Green = 2,
    /// <summary>Blue channel.</summary>
    Blue = 4,
    /// <summary>All channels combined.</summary>
    All = Red | Green | Blue,
}

/* ── Record types ─────────────────────────────────────────────────────── */

/// <summary>
/// Immutable record for configuration entries.
/// </summary>
/// <param name="Key">Configuration key.</param>
/// <param name="Value">Configuration value.</param>
public record ConfigEntry(string Key, string Value);

/// <summary>
/// Record struct for lightweight value records (C# 10).
/// </summary>
/// <param name="X">X coordinate.</param>
/// <param name="Y">Y coordinate.</param>
public record struct Vector2(double X, double Y);

/* ── Extension methods ────────────────────────────────────────────────── */

/// <summary>
/// Extension methods for string manipulation.
/// </summary>
public static class StringExtensions {
    /// <summary>
    /// Truncate a string to the specified maximum length.
    /// </summary>
    /// <param name="str">Source string.</param>
    /// <param name="maxLength">Maximum characters to keep.</param>
    /// <returns>Truncated string with ellipsis if shortened.</returns>
    public static string Truncate(this string str, int maxLength) {
        if (str.Length <= maxLength) return str;
        return str[..maxLength] + "...";
    }

    /// <summary>
    /// Check if a string contains only ASCII characters.
    /// </summary>
    /// <param name="str">The string to check.</param>
    /// <returns>True if all characters are ASCII.</returns>
    public static bool IsAscii(this string str) {
        return str.All(c => c < 128);
    }
}

/* ── Generic class with constraints ───────────────────────────────────── */

/// <summary>
/// Generic collection with filtering and transformation support.
/// </summary>
/// <typeparam name="T">Element type, must be comparable.</typeparam>
public class SortedCollection<T> where T : IComparable<T> {
    private readonly List<T> _items = new();

    /// <summary>
    /// Add an item maintaining sorted order.
    /// </summary>
    /// <param name="item">Item to insert.</param>
    public void Add(T item) {
        // Binary search for insertion point
        var index = _items.BinarySearch(item);
        if (index < 0) index = ~index;
        _items.Insert(index, item);
    }

    /// <summary>
    /// Get items matching a predicate using LINQ.
    /// </summary>
    /// <param name="predicate">Filter condition.</param>
    /// <returns>Filtered enumerable.</returns>
    public IEnumerable<T> Where(Func<T, bool> predicate) {
        return _items.Where(predicate);
    }
}

/* ── Pattern matching utility ─────────────────────────────────────────── */

/// <summary>
/// Utility class demonstrating advanced pattern matching.
/// </summary>
public static class PatternMatcher {
    /// <summary>
    /// Describe any object using C# pattern matching expressions.
    /// </summary>
    /// <param name="obj">Object to describe.</param>
    /// <returns>Description string.</returns>
    public static string Describe(object? obj) {
        return obj switch {
            null => "null",
            int i when i > 0 => $"positive int: {i}",
            int i => $"non-positive int: {i}",
            string { Length: 0 } => "empty string",
            string s => $"string({s.Length}): {s}",
            Person { Age: >= 18 } p => $"adult: {p.Name}",
            Person p => $"minor: {p.Name}",
            _ => $"unknown: {obj.GetType().Name}",
        };
    }
}

} // namespace MyApp

/* coverage extension block */
namespace MyApp.Services {}
namespace MyApp.Core {}
namespace MyApp.Data {}
namespace MyApp.Api {}
public interface ILogger {}
public interface IParser {}
public interface IRunner {}
public enum ModeCs { Fast, Safe }
public enum PhaseCs { Init, Done }
public enum StateCs { Open, Closed }
public enum SignalCs { On, Off }
public struct Size { public int W; public int H; }
public readonly struct Vector { public readonly int X; public readonly int Y; }
public struct Limits { public int Max; }
public struct Cursor { public int Index; }
[DebuggerDisplay("{Value}")]
public const int MIN_AGE = 10;
public const int RETRY_LIMIT = 3;
public const int CACHE_SIZE = 128;
public const int DEFAULT_PAGE = 1;
