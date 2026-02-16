/**
 * @file fixture_java.java
 * @brief Comprehensive Java test fixture for parser validation.
 * @details Covers generics with wildcards, sealed classes, records, inner classes,
 *          anonymous classes, lambdas, method references, switch expressions,
 *          try-with-resources, annotations, and default interface methods.
 */
// Single line comment
/* Multi-line
   comment */
package com.example.app;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import static java.lang.Math.PI;

/* ── Annotation ───────────────────────────────────────────────────────── */

/**
 * @brief Marks a method as requiring authentication before invocation.
 * @param role The minimum role level required for access.
 */
@interface RequiresAuth {
    String role() default "user";
}

/* ── Main class ───────────────────────────────────────────────────────── */

/**
 * @class MyClass
 * @brief Primary class demonstrating various Java constructs.
 * @param <T> Generic type parameter for flexible data handling.
 */
@SuppressWarnings("unchecked")
public class MyClass<T extends Comparable<T>> {

    /** @brief Maximum buffer size constant. */
    public static final int MAX_SIZE = 100;

    /** @brief Type-safe internal storage for items. */
    private List<T> items;

    /**
     * @brief Construct MyClass with an initial item list.
     * @param items The starting collection of items.
     */
    public MyClass(List<T> items) {
        this.items = items;
    }

    /**
     * @brief Greet a person by name on standard output.
     * @param name The person's name; must not be null.
     */
    public void greet(String name) {
        /* Null check before output */
        if (name == null) {
            return;
        }
        System.out.println("Hello, " + name);
    }

    /**
     * @brief Helper method returning a status string.
     * @return Always returns "ok".
     */
    private static String helper() {
        return "ok";
    }

    /**
     * @brief Find the first item matching a predicate.
     * @param predicate Filter condition for items.
     * @return Optional containing the first match, or empty.
     */
    public Optional<T> findFirst(Predicate<T> predicate) {
        for (T item : items) {
            /* Test each item against predicate */
            if (predicate.test(item)) {
                return Optional.of(item);
            }
        }
        return Optional.empty();
    }

    /**
     * @brief Transform all items using a mapping function.
     * @param <R> The result type after transformation.
     * @param mapper Function to apply to each item.
     * @return List of transformed results.
     */
    public <R> List<R> map(Function<T, R> mapper) {
        return items.stream()
                .map(mapper)
                .collect(Collectors.toList());
    }

    /**
     * @brief Process items with a wildcard-bounded list.
     * @param source List of items extending Number.
     * @return Sum of all numeric values as double.
     */
    public double sumWildcard(List<? extends Number> source) {
        double total = 0.0;
        for (Number n : source) {
            total += n.doubleValue();
        }
        return total;
    }

    /* ── Inner class ──────────────────────────────────────────────────── */

    /**
     * @class Builder
     * @brief Inner builder class for constructing MyClass instances.
     */
    public class Builder {
        private List<T> pending;

        /**
         * @brief Add an item to the builder.
         * @param item Item to include in the built instance.
         * @return This builder for chaining.
         */
        public Builder add(T item) {
            pending.add(item);
            return this;
        }

        /**
         * @brief Finalize and create the MyClass instance.
         * @return A new MyClass populated with accumulated items.
         */
        public MyClass<T> build() {
            return new MyClass<>(pending);
        }
    }

    /* ── Static nested class ──────────────────────────────────────────── */

    /**
     * @class Config
     * @brief Static configuration holder with validation.
     */
    public static class Config {
        /** @brief Configuration key string. */
        public final String key;
        /** @brief Configuration value. */
        public final Object value;

        /**
         * @brief Construct a Config entry.
         * @param key   The configuration key.
         * @param value The associated value.
         */
        public Config(String key, Object value) {
            this.key = key;
            this.value = value;
        }
    }
}

/* ── Interface with default methods ───────────────────────────────────── */

/**
 * @interface Greeter
 * @brief Functional interface for greeting operations.
 */
public interface Greeter {
    /**
     * @brief Perform a greeting to the named person.
     * @param name Recipient of the greeting.
     */
    void sayHello(String name);

    /**
     * @brief Default farewell method with implementation.
     * @param name Person to bid farewell.
     */
    default void sayGoodbye(String name) {
        System.out.println("Goodbye, " + name);
    }

    /**
     * @brief Static factory creating a simple Greeter.
     * @return A Greeter that prints to stdout.
     */
    static Greeter simple() {
        /* Lambda implementing the functional interface */
        return name -> System.out.println("Hi, " + name);
    }
}

/* ── Enum with methods ────────────────────────────────────────────────── */

/**
 * @enum Color
 * @brief Color enum with associated hex values and behavior.
 */
public enum Color {
    /** @brief Red color with hex #FF0000. */
    RED("#FF0000"),
    /** @brief Green color with hex #00FF00. */
    GREEN("#00FF00"),
    /** @brief Blue color with hex #0000FF. */
    BLUE("#0000FF");

    /** @brief The hexadecimal color code. */
    private final String hex;

    /**
     * @brief Private constructor for enum constants.
     * @param hex The hex string for this color.
     */
    Color(String hex) {
        this.hex = hex;
    }

    /**
     * @brief Get the hex code of this color.
     * @return Hex string including '#' prefix.
     */
    public String getHex() {
        return hex;
    }
}

/* ── Record (Java 16+) ────────────────────────────────────────────────── */

/**
 * @record Point
 * @brief Immutable 2D coordinate record.
 * @param x Horizontal coordinate.
 * @param y Vertical coordinate.
 */
public record Point(double x, double y) {
    /**
     * @brief Compact constructor validating coordinates.
     * @throws IllegalArgumentException If either coordinate is NaN.
     */
    public Point {
        if (Double.isNaN(x) || Double.isNaN(y)) {
            throw new IllegalArgumentException("NaN coordinates");
        }
    }

    /**
     * @brief Compute distance to another point.
     * @param other Target point.
     * @return Euclidean distance.
     */
    public double distanceTo(Point other) {
        double dx = this.x - other.x;
        double dy = this.y - other.y;
        return Math.sqrt(dx * dx + dy * dy);
    }
}

/* ── Sealed class hierarchy (Java 17+) ────────────────────────────────── */

/**
 * @class Shape
 * @brief Sealed class permitting only Circle and Rectangle subtypes.
 */
public sealed class Shape permits Circle, Rectangle {
    /**
     * @brief Compute the area of this shape.
     * @return Area as a double; subclasses provide implementation.
     */
    public double area() {
        return 0.0;
    }
}

/**
 * @class Circle
 * @extends Shape
 * @brief Circle shape with radius-based area computation.
 */
public final class Circle extends Shape {
    /** @brief Radius of the circle. */
    private final double radius;

    /**
     * @brief Construct a circle with a given radius.
     * @param radius Non-negative radius value.
     */
    public Circle(double radius) {
        this.radius = radius;
    }

    /**
     * @brief Compute circle area using π×r².
     * @return The area of the circle.
     */
    @Override
    public double area() {
        return PI * radius * radius;
    }
}

/**
 * @class Rectangle
 * @extends Shape
 * @brief Rectangle shape with width and height.
 */
public final class Rectangle extends Shape {
    private final double width;
    private final double height;

    public Rectangle(double width, double height) {
        this.width = width;
        this.height = height;
    }

    @Override
    public double area() {
        return width * height;
    }
}

/* ── Utility class with switch expression ─────────────────────────────── */

/**
 * @class Evaluator
 * @brief Demonstrates switch expressions and try-with-resources.
 */
public class Evaluator {

    /**
     * @brief Describe a shape using pattern matching switch expression.
     * @param shape The shape to describe.
     * @return Human-readable description string.
     */
    public static String describe(Shape shape) {
        /* Switch expression with pattern matching (Java 21) */
        return switch (shape) {
            case Circle c -> "Circle with radius " + c.area();
            case Rectangle r -> "Rectangle with area " + r.area();
            default -> "Unknown shape";
        };
    }

    /**
     * @brief Read a file safely with try-with-resources.
     * @param path File system path to read.
     * @return File contents as a string.
     * @throws java.io.IOException If the file cannot be read.
     */
    @RequiresAuth(role = "admin")
    public static String readFile(String path) throws java.io.IOException {
        /* Auto-closeable resource management */
        try (var reader = new java.io.BufferedReader(new java.io.FileReader(path))) {
            return reader.lines().collect(Collectors.joining("\n"));
        }
    }
}

/* coverage extension block */
package com.example.extra.one;
package com.example.extra.two;
package com.example.extra.three;
package com.example.extra.four;
interface Runner {}
public interface Mapper {}
public interface Handler {}
public interface Auditor {}
enum ModeJava { FAST, SAFE }
enum PhaseJava { INIT, RUN }
enum StatusJava { OPEN, CLOSED }
enum KindJava { A, B }
public static final int DEFAULT_LIMIT = 10;
public static final int RETRY_LIMIT = 3;
public static final int BUFFER_SIZE = 512;
public static final int MAX_USERS = 99;
@Trace
