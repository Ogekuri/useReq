/**
 * @file fixture_cpp.cpp
 * @brief Comprehensive C++ test fixture for parser stress-testing.
 * @details Covers templates, SFINAE, constexpr, lambdas, concepts, CRTP,
 *          operator overloading, move semantics, nested namespaces, and
 *          modern C++20/23 constructs.
 */
// Single line comment
/* Multi-line
   comment */
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <concepts>
#include <optional>

#define VERSION 2

/** @def LIKELY Branch prediction hint for hot paths. */
#define LIKELY(x) __builtin_expect(!!(x), 1)

/* ── Namespace ────────────────────────────────────────────────────────── */

namespace MyNS {

/* ── Concepts (C++20) ─────────────────────────────────────────────────── */

/**
 * @concept Printable
 * @brief Constrains types that support stream insertion via operator<<.
 */
template<typename T>
concept Printable = requires(std::ostream &os, T val) {
    { os << val } -> std::same_as<std::ostream &>;
};

/**
 * @concept Numeric
 * @brief Constrains types to integral or floating point.
 */
template<typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

/* ── Template class ───────────────────────────────────────────────────── */

/**
 * @class Container
 * @brief Generic container with RAII semantics.
 * @tparam T Element type; must satisfy Printable concept.
 */
template<Printable T>
class Container {
public:
    T value; /**< @brief Stored value of type T. */

    /**
     * @brief Construct container with an initial value.
     * @param v The value to store.
     */
    explicit Container(T v) : value(std::move(v)) {}

    /**
     * @brief Copy constructor performs deep copy.
     * @param other Source container to copy from.
     */
    Container(const Container &other) = default;

    /**
     * @brief Move constructor transfers ownership.
     * @param other Source container; left in valid but unspecified state.
     */
    Container(Container &&other) noexcept = default;

    /**
     * @brief Copy assignment operator.
     * @param other Source container.
     * @return Reference to this container.
     */
    Container &operator=(const Container &other) = default;

    /**
     * @brief Move assignment operator.
     * @param other Source container to move from.
     * @return Reference to this container.
     */
    Container &operator=(Container &&other) noexcept = default;

    /** @brief Destructor; default cleanup. */
    ~Container() = default;

    /**
     * @brief Stream insertion for this container.
     * @param os Output stream.
     * @param c  Container to print.
     * @return The output stream.
     */
    friend std::ostream &operator<<(std::ostream &os, const Container &c) {
        return os << c.value;
    }

    /**
     * @brief Equality comparison between containers.
     * @param other Container to compare with.
     * @return True if values are equal.
     */
    bool operator==(const Container &other) const {
        return value == other.value;
    }
};

/* ── Struct ───────────────────────────────────────────────────────────── */

/**
 * @struct Point
 * @brief 2D coordinate with constexpr arithmetic support.
 */
struct Point {
    double x; /**< @brief X coordinate. */
    double y; /**< @brief Y coordinate. */

    /**
     * @brief Compute Euclidean distance squared to another point.
     * @param other Target point.
     * @return Distance squared (avoids sqrt overhead).
     */
    constexpr double dist_sq(const Point &other) const {
        /* Squared differences avoid floating-point sqrt */
        double dx = x - other.x;
        double dy = y - other.y;
        return dx * dx + dy * dy;
    }

    /**
     * @brief Add two points component-wise.
     * @param rhs Right-hand operand.
     * @return New Point with summed coordinates.
     */
    constexpr Point operator+(const Point &rhs) const {
        return {x + rhs.x, y + rhs.y};
    }
};

/* ── Enum class ───────────────────────────────────────────────────────── */

/**
 * @enum Direction
 * @brief Cardinal movement directions with strong typing.
 */
enum class Direction {
    Up,    /**< @brief Move upward. */
    Down,  /**< @brief Move downward. */
    Left,  /**< @brief Move left. */
    Right  /**< @brief Move right. */
};

/* ── Type aliases ─────────────────────────────────────────────────────── */

/** @typedef StringVec Convenience alias for string vectors. */
using StringVec = std::vector<std::string>;

/** @typedef my_int_t Legacy alias for integer type. */
typedef int my_int_t;

/** @typedef Callback Function wrapper for void callbacks. */
using Callback = std::function<void(int)>;

/* ── CRTP pattern ─────────────────────────────────────────────────────── */

/**
 * @class Cloneable
 * @brief CRTP base providing a polymorphic clone method.
 * @tparam Derived The concrete class inheriting this base.
 */
template<typename Derived>
class Cloneable {
public:
    /**
     * @brief Create a heap-allocated copy of the derived object.
     * @return Unique pointer to the cloned instance.
     */
    std::unique_ptr<Derived> clone() const {
        /* static_cast down to Derived is safe under CRTP contract */
        return std::make_unique<Derived>(static_cast<const Derived &>(*this));
    }
};

/* ── Virtual inheritance ──────────────────────────────────────────────── */

/**
 * @class Base
 * @brief Abstract base with a pure virtual method.
 */
class Base {
public:
    /**
     * @brief Identify the concrete type at runtime.
     * @return A non-owning string literal naming the type.
     */
    virtual const char *type_name() const = 0;
    virtual ~Base() = default;
};

/**
 * @class DerivedA
 * @brief First concrete implementation of Base.
 */
class DerivedA : public virtual Base {
public:
    const char *type_name() const override {
        return "DerivedA";
    }
};

/**
 * @class DerivedB
 * @brief Second concrete implementation for diamond inheritance testing.
 */
class DerivedB : public virtual Base {
public:
    const char *type_name() const override {
        return "DerivedB";
    }
};

/**
 * @class Diamond
 * @brief Diamond inheritance: inherits from both DerivedA and DerivedB.
 */
class Diamond : public DerivedA, public DerivedB {
public:
    const char *type_name() const override {
        return "Diamond";
    }
};

/* ── Constexpr function ───────────────────────────────────────────────── */

/**
 * @brief Compute factorial at compile time.
 * @param n Non-negative input.
 * @return n! computed via recursive constexpr evaluation.
 */
constexpr unsigned long long constexpr_factorial(unsigned int n) {
    /* Compile-time recursion terminates at n <= 1 */
    return n <= 1 ? 1ULL : n * constexpr_factorial(n - 1);
}

/* ── Function with structured binding return ──────────────────────────── */

/**
 * @brief Parse a key=value string into its components.
 * @param input String in "key=value" format.
 * @return Pair of key and value; empty strings if malformed.
 */
std::pair<std::string, std::string> parse_kv(const std::string &input) {
    auto pos = input.find('=');
    if (pos == std::string::npos) {
        /* No delimiter found — return empty pair */
        return {"", ""};
    }
    return {input.substr(0, pos), input.substr(pos + 1)};
}

/* ── Free functions ───────────────────────────────────────────────────── */

/**
 * @brief Greet a person by name on stdout.
 * @param name The person's name to display.
 */
void greet(std::string name) {
    std::cout << "Hello, " << name << "\n";
}

/**
 * @brief Program entry point.
 * @return 0 on success.
 */
int main() {
    /* Structured binding from parse_kv */
    auto [key, val] = parse_kv("lang=cpp");
    greet(key);
    return 0;
}

/* ── Lambda stored in variable ────────────────────────────────────────── */

/**
 * @brief Inline lambda for squaring values.
 *
 * Demonstrates constexpr lambda with auto parameter (C++20 generic lambda).
 */
constexpr auto square = [](auto x) { return x * x; };

/* ── Nested namespace (C++17) ─────────────────────────────────────────── */

namespace Inner::Detail {

/**
 * @brief Internal helper formatting integers to strings.
 * @param v The integer to format.
 * @return Formatted string representation.
 */
inline std::string format_int(int v) {
    return std::to_string(v);
}

} // namespace Inner::Detail

} // namespace MyNS

/* ── Template with SFINAE ─────────────────────────────────────────────── */

/**
 * @brief SFINAE-enabled serialize function for Numeric types.
 * @tparam T Numeric type.
 * @param value The numeric value to serialize.
 * @return String representation of the value.
 */
template<MyNS::Numeric T>
std::string serialize(T value) {
    return std::to_string(value);
}

/**
 * @brief Overload for string serialization (identity transform).
 * @param value The string to serialize.
 * @return The input string unchanged.
 */
inline std::string serialize(const std::string &value) {
    return value;
}
