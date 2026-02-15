/// @file fixture_swift.swift
/// @brief Comprehensive Swift test fixture for parser validation.
/// @details Covers closures, computed properties, property observers,
///          subscripts, generic constraints, result builders, actors,
///          opaque types, property wrappers, and key paths.
// Single line comment
/* Multi-line comment */
import Foundation
import Combine

/* ── Class with properties and observers ──────────────────────────────── */

/// Animal base class demonstrating inheritance and property patterns.
///
/// @brief Base class with stored, computed, and observed properties.
class Animal {
    /// @brief Species name identifier.
    var species: String

    /// @brief Number of legs; triggers a didSet observer on change.
    var legs: Int = 4 {
        willSet {
            /* Log upcoming change from current to new value */
            print("Legs changing from \(legs) to \(newValue)")
        }
        didSet {
            /* Enforce minimum of zero legs */
            if legs < 0 { legs = 0 }
        }
    }

    /// @brief Computed property returning a descriptive string.
    var description: String {
        return "\(species) with \(legs) legs"
    }

    /// @brief Initialize an Animal with species name.
    /// @param species The species identifier string.
    init(species: String) {
        self.species = species
    }

    /// @brief Produce a sound; subclasses should override.
    func speak() {
        print("...")
    }

    /// @brief Class method creating a generic instance.
    /// @return An Animal with species "Unknown".
    class func createDefault() -> Animal {
        return Animal(species: "Unknown")
    }

    /// @brief Deinitializer for cleanup on deallocation.
    deinit {
        print("\(species) deallocated")
    }
}

/// Dog subclass demonstrating method override and super calls.
///
/// @brief Concrete animal with dog-specific behavior.
class Dog: Animal {
    /// @brief Dog's name.
    let name: String

    /// @brief Initialize a named dog.
    /// @param name The dog's name.
    init(name: String) {
        self.name = name
        super.init(species: "Dog")
    }

    /// @brief Override speak to produce dog-specific sound.
    override func speak() {
        print("\(name) says: Woof!")
    }
}

/* ── Struct with subscript and Equatable ───────────────────────────────── */

/// 2D point with arithmetic operator overloading.
///
/// @brief Value type representing a coordinate pair.
struct Point: Equatable {
    var x: Double = 0.0
    var y: Double = 0.0

    /// @brief Add two points component-wise.
    /// @param lhs Left-hand operand.
    /// @param rhs Right-hand operand.
    /// @return New Point with summed coordinates.
    static func + (lhs: Point, rhs: Point) -> Point {
        return Point(x: lhs.x + rhs.x, y: lhs.y + rhs.y)
    }

    /// @brief Compute Euclidean distance from origin.
    /// @return Distance as a Double.
    var magnitude: Double {
        return (x * x + y * y).squareRoot()
    }
}

/// Matrix structure with subscript access pattern.
///
/// @brief 2D matrix supporting element access via subscript.
struct Matrix {
    /// @brief Flat storage for matrix values.
    private var data: [[Double]]

    /// @brief Number of rows.
    let rows: Int
    /// @brief Number of columns.
    let cols: Int

    /// @brief Initialize a zero-filled matrix.
    /// @param rows Number of rows.
    /// @param cols Number of columns.
    init(rows: Int, cols: Int) {
        self.rows = rows
        self.cols = cols
        data = Array(repeating: Array(repeating: 0.0, count: cols), count: rows)
    }

    /// @brief Access matrix elements using row/column subscript.
    /// @param row Row index (zero-based).
    /// @param col Column index (zero-based).
    /// @return The value at (row, col).
    subscript(row: Int, col: Int) -> Double {
        get { return data[row][col] }
        set { data[row][col] = newValue }
    }
}

/* ── Enum with associated values and methods ──────────────────────────── */

/// Direction enum with raw string values.
///
/// @brief Cardinal directions supporting CaseIterable iteration.
enum Direction: String, CaseIterable {
    case up = "UP"
    case down = "DOWN"
    case left = "LEFT"
    case right = "RIGHT"

    /// @brief Compute the opposite direction.
    /// @return The direction 180 degrees from self.
    var opposite: Direction {
        switch self {
        case .up: return .down
        case .down: return .up
        case .left: return .right
        case .right: return .left
        }
    }
}

/// Result-like enum with associated error types.
///
/// @brief Generic result type for error handling.
/// @tparam T The success value type.
enum AppResult<T> {
    /// @brief Successful result carrying a value.
    case success(T)
    /// @brief Failure carrying an error description.
    case failure(Error)

    /// @brief Map the success value using a transform closure.
    /// @param transform Closure converting T to U.
    /// @return A new AppResult with the transformed value.
    func map<U>(_ transform: (T) -> U) -> AppResult<U> {
        switch self {
        case .success(let value):
            return .success(transform(value))
        case .failure(let error):
            return .failure(error)
        }
    }
}

/* ── Protocol ─────────────────────────────────────────────────────────── */

/// Protocol for objects that can render themselves to a string.
///
/// @brief Defines the render contract with a default extension implementation.
protocol Drawable {
    /// @brief Render the object to a string representation.
    /// @return Rendered string output.
    func draw() -> String

    /// @brief Optional priority for render ordering.
    var renderPriority: Int { get }
}

/// Protocol with associated type for generic containers.
///
/// @brief Defines a type-erased container interface.
protocol Container {
    /// @brief The type of element stored in the container.
    associatedtype Item

    /// @brief Add an item to the container.
    /// @param item The element to add.
    mutating func add(_ item: Item)

    /// @brief Number of elements in the container.
    var count: Int { get }
}

/* ── Protocol extension with default implementation ───────────────────── */

extension Drawable {
    /// @brief Default render priority for all Drawable conformants.
    var renderPriority: Int { return 0 }

    /// @brief Debug draw with priority prefix.
    /// @return String with priority and rendered content.
    func debugDraw() -> String {
        return "[\(renderPriority)] \(draw())"
    }
}

/* ── Extension on existing type ───────────────────────────────────────── */

/// Extension adding utility methods to Animal.
extension Animal: Drawable {
    /// @brief Render animal as a descriptive string.
    /// @return Description of the animal.
    func draw() -> String {
        return description
    }

    /// @brief Describe the animal for UI display.
    /// @return A formatted string suitable for labels.
    func describe() -> String {
        return "Animal: \(species)"
    }
}

/* ── Property wrapper ─────────────────────────────────────────────────── */

/// Property wrapper clamping values to a specified range.
///
/// @brief Ensures wrapped values stay within min/max bounds.
/// @tparam Value Must conform to Comparable.
@propertyWrapper
struct Clamped<Value: Comparable> {
    /// @brief Minimum allowed value.
    let min: Value
    /// @brief Maximum allowed value.
    let max: Value
    /// @brief Current stored value.
    private var value: Value

    /// @brief The wrapped value, clamped on set.
    var wrappedValue: Value {
        get { return value }
        set { value = Swift.min(Swift.max(newValue, min), max) }
    }

    /// @brief Initialize with range and starting value.
    init(wrappedValue: Value, min: Value, max: Value) {
        self.min = min
        self.max = max
        /* Clamp initial value to range */
        self.value = Swift.min(Swift.max(wrappedValue, min), max)
    }
}

/* ── Actor (Swift concurrency) ────────────────────────────────────────── */

/// Actor providing thread-safe counter operations.
///
/// @brief Demonstrates Swift structured concurrency with actor isolation.
actor Counter {
    /// @brief Current count value.
    private var value: Int = 0

    /// @brief Increment the counter and return the new value.
    /// @return The incremented count.
    func increment() -> Int {
        value += 1
        return value
    }

    /// @brief Reset the counter to zero.
    func reset() {
        value = 0
    }
}

/* ── Free functions ───────────────────────────────────────────────────── */

/// @brief Greet a person by name.
/// @param name The person's name.
public func greet(name: String) {
    print("Hello \(name)")
}

/// @brief Build an opaque some-typed Drawable.
/// @return An opaque Drawable hiding the concrete type.
func makeDrawable() -> some Drawable {
    return Animal(species: "Cat")
}

/// @brief Generic function with where clause constraint.
/// @tparam T Must be Equatable.
/// @param items Collection of items to search.
/// @param target The item to find.
/// @return True if target exists in items.
func contains<T: Collection>(items: T, target: T.Element) -> Bool where T.Element: Equatable {
    return items.contains(target)
}

/// @brief Higher-order function accepting an escaping closure.
/// @param action The closure to store for later execution.
/// @return A wrapper closure that invokes action.
func deferred(_ action: @escaping () -> Void) -> () -> Void {
    return {
        /* Execute the captured closure */
        action()
    }
}

/* ── Constants and variables ──────────────────────────────────────────── */

/// @brief Application-wide maximum buffer size constant.
let MAX_SIZE = 1024

/// @brief Module-scoped mutable counter with restricted access.
private var counter = 0

/// @brief Lazy computed constant using a closure.
let defaultConfig: [String: Any] = {
    var config: [String: Any] = [:]
    config["debug"] = false
    config["version"] = "1.0"
    return config
}()
