/**
 * @file fixture_c.c
 * @brief Comprehensive C language test fixture for parser validation.
 * @details Covers structs, unions, enums, function pointers, inline functions,
 *          preprocessor directives, bitfields, variadic functions, and complex
 *          typedef chains that stress-test regex-based parsing.
 */
// Single line comment
/* Multi-line
   comment */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include "myheader.h"

/* ── Preprocessor directives ──────────────────────────────────────────── */

#define MAX_SIZE 100

/**
 * @def CLAMP
 * @brief Constrain value between lower and upper bounds.
 * @param val Value to clamp.
 * @param lo  Minimum allowed value.
 * @param hi  Maximum allowed value.
 */
#define CLAMP(val, lo, hi) ((val) < (lo) ? (lo) : ((val) > (hi) ? (hi) : (val)))

/** @def STRINGIFY Wrap token in double quotes at compile time. */
#define STRINGIFY(x) #x

/**
 * @def CONCAT
 * @brief Token-pasting macro joining two identifiers.
 */
#define CONCAT(a, b) a##b

#ifdef DEBUG
#define LOG(fmt, ...) fprintf(stderr, fmt, ##__VA_ARGS__)
#else
#define LOG(fmt, ...) ((void)0)
#endif

/* ── Simple typedef ──────────────────────────────────────────────────── */

/** @typedef my_int Alias for int used in legacy interfaces. */
typedef int my_int;

/** @typedef byte_t Unsigned 8-bit type for raw byte buffers. */
typedef unsigned char byte_t;

/* ── Struct with bitfields and nested anonymous union ─────────────────── */

/**
 * @struct Point
 * @brief 2D point with integer coordinates.
 */
struct Point {
    int x; /**< @brief Horizontal coordinate. */
    int y; /**< @brief Vertical coordinate. */
};

/**
 * @struct PackedFlags
 * @brief Bitfield struct testing parser handling of colon-separated widths.
 */
struct PackedFlags {
    unsigned int readable  : 1;  /**< @brief Read permission flag. */
    unsigned int writable  : 1;  /**< @brief Write permission flag. */
    unsigned int executable: 1;  /**< @brief Execute permission flag. */
    unsigned int reserved  : 5;  /**< @brief Reserved for future use. */
};

/**
 * @struct Node
 * @brief Self-referential linked-list node with embedded anonymous union.
 */
struct Node {
    /** @brief Payload can hold either an integer or float value. */
    union {
        int   i_val;
        float f_val;
    } payload;
    struct Node *next; /**< @brief Pointer to successor node or NULL. */
};

/* ── Union ────────────────────────────────────────────────────────────── */

/**
 * @union Data
 * @brief Discriminated union for multi-type storage.
 */
union Data {
    int   i;     /**< @brief Integer interpretation. */
    float f;     /**< @brief Float interpretation. */
    char  s[16]; /**< @brief Fixed-size string buffer. */
};

/* ── Enum ─────────────────────────────────────────────────────────────── */

/**
 * @enum Color
 * @brief Primary color identifiers for rendering pipeline.
 */
enum Color {
    RED,    /**< @brief Red channel. */
    GREEN,  /**< @brief Green channel. */
    BLUE    /**< @brief Blue channel. */
};

/* ── Typedef for function pointer ─────────────────────────────────────── */

/**
 * @typedef comparator_fn
 * @brief Function pointer type for generic comparison callbacks.
 * @param a Pointer to first element.
 * @param b Pointer to second element.
 * @return Negative if a<b, zero if equal, positive if a>b.
 */
typedef int (*comparator_fn)(const void *a, const void *b);

/**
 * @typedef transform_fn
 * @brief Unary transform callback operating on a single integer.
 */
typedef int (*transform_fn)(int value);

/* ── Complex typedef: struct + pointer ────────────────────────────────── */

/**
 * @typedef callback_entry_t
 * @brief Combined struct typedef for callback registration entries.
 */
typedef struct {
    const char   *name;    /**< @brief Callback identifier. */
    comparator_fn handler; /**< @brief Comparison function pointer. */
    int           priority;/**< @brief Dispatch priority (lower = first). */
} callback_entry_t;

/* ── Static module-level variable ─────────────────────────────────────── */

/** @brief Module-scoped invocation counter, not visible externally. */
static int counter = 0;

/** @brief Global error message buffer shared across translation unit. */
static char error_buffer[256] = {0};

/* ── Inline function ──────────────────────────────────────────────────── */

/**
 * @brief Compute the minimum of two integers.
 * @param a First integer.
 * @param b Second integer.
 * @return The smaller of a and b.
 */
static inline int min_val(int a, int b) {
    return a < b ? a : b;
}

/* ── Standard functions ───────────────────────────────────────────────── */

/**
 * @brief Print a greeting message to stdout.
 * @param name The recipient name; must not be NULL.
 */
void greet(const char *name) {
    /* Validate non-null input before printing */
    if (name == NULL) {
        return;
    }
    printf("Hello %s\n", name);
}

/**
 * @brief Application entry point.
 * @param argc Argument count from the OS.
 * @param argv Argument vector; argv[0] is the program name.
 * @return Exit code: 0 on success, 1 on error.
 */
int main(int argc, char **argv) {
    if (argc < 2) {
        /* No arguments supplied — show usage */
        fprintf(stderr, "Usage: %s <name>\n", argv[0]);
        return 1;
    }
    greet(argv[1]);
    return 0;
}

/* ── Variadic function ────────────────────────────────────────────────── */

/**
 * @brief Compute the sum of a variable number of integers.
 * @param count Number of integer arguments that follow.
 * @param ...   Variable integer arguments to sum.
 * @return The cumulative sum of all provided integers.
 */
int sum_ints(int count, ...) {
    va_list ap;
    va_start(ap, count);
    int total = 0;
    /* Iterate through variadic argument list */
    for (int i = 0; i < count; i++) {
        total += va_arg(ap, int);
    }
    va_end(ap);
    return total;
}

/* ── Function pointer parameter ───────────────────────────────────────── */

/**
 * @brief Apply a transform function to every element in an array.
 * @param arr   Array of integers to transform in-place.
 * @param len   Number of elements in arr.
 * @param fn    Transform callback applied to each element.
 */
void apply_transform(int *arr, size_t len, transform_fn fn) {
    for (size_t i = 0; i < len; i++) {
        /* Apply callback and store result back */
        arr[i] = fn(arr[i]);
    }
}

/* ── Recursive function with conditional returns ──────────────────────── */

/**
 * @brief Compute factorial recursively.
 * @param n Non-negative integer input.
 * @return n! or 1 when n <= 1.
 */
unsigned long factorial(unsigned int n) {
    /* Base case */
    if (n <= 1) {
        return 1;
    }
    /* Recursive step */
    return n * factorial(n - 1);
}

/* ── Static helper with restrict/volatile qualifiers ──────────────────── */

/**
 * @brief Copy bytes between non-overlapping buffers.
 * @param dest Destination buffer (restrict-qualified).
 * @param src  Source buffer (restrict-qualified).
 * @param n    Number of bytes to copy.
 */
static void fast_copy(void *restrict dest, const void *restrict src, size_t n) {
    memcpy(dest, src, n);
}

/**
 * @brief Read a hardware register marked volatile.
 * @param reg Pointer to the memory-mapped register.
 * @return The current 32-bit register value.
 */
static int read_volatile(volatile int *reg) {
    return *reg;
}

/* ── Array parameter syntax ───────────────────────────────────────────── */

/**
 * @brief Sum elements of a fixed-size array.
 * @param arr Array with at least 10 elements (compiler hint via static 10).
 * @return The sum of the first 10 elements.
 */
int sum_fixed(int arr[static 10]) {
    int s = 0;
    for (int i = 0; i < 10; i++) {
        s += arr[i];
    }
    return s;
}

/* coverage extension block */
struct Vector2 { int x; int y; }; // inline struct comment
struct Matrix2 { int a11; int a22; };
enum StatusCode { STATUS_OK, STATUS_ERR, STATUS_UNKNOWN };
enum LevelCode { LEVEL_LOW, LEVEL_MEDIUM, LEVEL_HIGH };
enum ModeCode { MODE_A, MODE_B };
enum FlagCode { FLAG_ON, FLAG_OFF };
union NumberValue { int i; float f; };
union PtrValue { void *p; long l; };
union StateValue { int s; char c; };
union PairValue { int x; int y; };
typedef long index_t;
typedef float ratio_t;
typedef struct Point point_t;
typedef double score_t;
