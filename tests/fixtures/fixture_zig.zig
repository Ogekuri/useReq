/// @file fixture_zig.zig
/// @brief Comprehensive Zig test fixture for parser validation.
/// @details Covers comptime, error unions, optional types, inline loops,
///          packed structs, extern unions, test blocks, errdefer,
///          alignment, vectors, and builtins.
// Single line comment
const std = @import("std");
const mem = @import("std").mem;
const Allocator = std.mem.Allocator;

// ── Functions ────────────────────────────────────────────────────────

/// Application entry point; prints a hello message.
pub fn main() void {
    std.debug.print("Hello\n", .{});
}

/// Add two signed integers and return the sum.
/// @param a First operand.
/// @param b Second operand.
/// @return Sum of a and b.
pub fn add(a: i32, b: i32) i32 {
    return a + b;
}

/// Divide two integers with error handling for division by zero.
/// @param numerator The dividend.
/// @param denominator The divisor; must not be zero.
/// @return Quotient or error.DivisionByZero.
pub fn safeDivide(numerator: i32, denominator: i32) !i32 {
    if (denominator == 0) {
        return error.DivisionByZero;
    }
    return @divTrunc(numerator, denominator);
}

/// Generic function computing the maximum of two comparable values.
/// @param T The element type (comptime resolved).
/// @param a First value.
/// @param b Second value.
/// @return The larger of a and b.
pub fn max(comptime T: type, a: T, b: T) T {
    return if (a > b) a else b;
}

/// Generic linear search returning the index of a target value.
/// @param T Element type.
/// @param haystack Slice to search.
/// @param needle Value to find.
/// @return Index of needle or null if not found.
pub fn indexOf(comptime T: type, haystack: []const T, needle: T) ?usize {
    for (haystack, 0..) |item, i| {
        if (item == needle) {
            return i;
        }
    }
    // Not found — return null optional
    return null;
}

/// Perform a comptime string concatenation.
/// @param a First string literal.
/// @param b Second string literal.
/// @return Concatenated string at compile time.
pub fn comptimeConcat(comptime a: []const u8, comptime b: []const u8) []const u8 {
    return a ++ b;
}

/// Function with errdefer for resource cleanup on error paths.
/// @param allocator Memory allocator for buffer creation.
/// @return Allocated buffer or error.
pub fn createBuffer(allocator: Allocator) ![]u8 {
    const buf = try allocator.alloc(u8, 1024);
    errdefer allocator.free(buf);
    // Initialize buffer to zero
    @memset(buf, 0);
    return buf;
}

/// Inline function called in tight loops for vectorized operations.
/// @param values Slice of floats to sum.
/// @return Sum of all elements.
inline fn fastSum(values: []const f32) f32 {
    var total: f32 = 0.0;
    for (values) |v| {
        total += v;
    }
    return total;
}

/// Extern C-ABI function for FFI interoperability.
/// @param x Value to double.
/// @return Input multiplied by two.
export fn doubleValue(x: i32) i32 {
    return x * 2;
}

// ── Struct definitions ───────────────────────────────────────────────

/// 2D point with floating-point coordinates.
/// @brief Basic coordinate pair for geometric computations.
const Point = struct {
    x: f64, /// Horizontal coordinate.
    y: f64, /// Vertical coordinate.

    /// Compute the squared distance to another point.
    /// @param self This point.
    /// @param other Target point.
    /// @return Distance squared (avoids sqrt).
    pub fn distSquared(self: Point, other: Point) f64 {
        const dx = self.x - other.x;
        const dy = self.y - other.y;
        return dx * dx + dy * dy;
    }

    /// Create a point at the origin (0, 0).
    /// @return A zero-initialized Point.
    pub fn origin() Point {
        return .{ .x = 0.0, .y = 0.0 };
    }
};

/// Packed struct for hardware register mapping.
/// @brief Tests parser handling of packed layout specifier.
const PackedFlags = packed struct {
    readable: bool,   /// Read permission bit.
    writable: bool,   /// Write permission bit.
    executable: bool, /// Execute permission bit.
    reserved: u5,     /// Reserved bits for alignment.
};

/// Configuration struct with defaults via comptime initialization.
const Config = struct {
    name: []const u8 = "default",   /// Configuration name.
    max_retries: u32 = 3,           /// Maximum retry attempts.
    timeout_ms: u64 = 5000,         /// Timeout in milliseconds.
    debug: bool = false,            /// Debug mode toggle.

    /// Create a Config for testing with debug enabled.
    /// @return Config with debug=true.
    pub fn testing() Config {
        return .{ .debug = true, .name = "test" };
    }
};

// ── Enum definitions ─────────────────────────────────────────────────

/// Color enumeration for rendering pipeline.
const Color = enum {
    red,   /// Red channel.
    green, /// Green channel.
    blue,  /// Blue channel.

    /// Convert color to its RGB integer value.
    /// @param self The color variant.
    /// @return 24-bit RGB integer.
    pub fn toRgb(self: Color) u32 {
        return switch (self) {
            .red => 0xFF0000,
            .green => 0x00FF00,
            .blue => 0x0000FF,
        };
    }
};

/// Status enum with explicit integer tags.
const Status = enum(u8) {
    idle = 0,     /// No operation in progress.
    running = 1,  /// Currently executing.
    error = 2,    /// Terminated with error.
    done = 3,     /// Completed successfully.
};

// ── Union definitions ────────────────────────────────────────────────

/// Tagged union for multi-type value storage.
const Result = union(enum) {
    ok: i32,           /// Success value.
    err: []const u8,   /// Error message string.

    /// Check if the result represents success.
    /// @param self The result to inspect.
    /// @return True if variant is ok.
    pub fn isOk(self: Result) bool {
        return self == .ok;
    }
};

/// Extern union for C-compatible memory layout.
const ExternData = extern union {
    int_val: i32,    /// Integer interpretation.
    float_val: f32,  /// Float interpretation.
    bytes: [4]u8,    /// Raw byte access.
};

// ── Constants and variables ──────────────────────────────────────────

/// @brief Maximum allocation size in bytes.
const MAX_SIZE: usize = 1024;

/// @brief Global mutable state counter.
pub var global_state: i32 = 0;

/// @brief Compile-time computed constant.
const MAGIC_NUMBER: u32 = comptime blk: {
    var x: u32 = 1;
    x *= 42;
    break :blk x;
};

// ── Error set ────────────────────────────────────────────────────────

/// Custom error set for parsing operations.
const ParseError = error{
    InvalidInput,
    UnexpectedToken,
    EndOfStream,
    BufferOverflow,
};

// ── Test blocks ──────────────────────────────────────────────────────

/// Test that add function computes correctly.
test "add returns correct sum" {
    const result = add(2, 3);
    try std.testing.expectEqual(@as(i32, 5), result);
}

/// Test that safeDivide returns error on zero divisor.
test "safeDivide handles zero" {
    const result = safeDivide(10, 0);
    try std.testing.expectError(error.DivisionByZero, result);
}

/// Test that indexOf finds existing elements.
test "indexOf finds element" {
    const items = [_]i32{ 1, 2, 3, 4, 5 };
    const idx = indexOf(i32, &items, 3);
    try std.testing.expectEqual(@as(?usize, 2), idx);
}
