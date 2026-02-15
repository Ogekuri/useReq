// Single line comment
/* Multi-line
   comment */

// Package main is the entry point for the application.
// It demonstrates Go-specific constructs including generics,
// goroutines, channels, embedded structs, and type switches.
package main

import (
	"context"
	"fmt"
	"io"
	"sync"
)

/* ── Constants and variables ──────────────────────────────────────────── */

// MaxSize defines the upper bound for buffer allocation.
const MaxSize = 100

// globalVar is a package-level mutable counter.
var globalVar = 0

// Iota-based enum-like constants for log levels.
const (
	// LogDebug is the most verbose logging level.
	LogDebug = iota
	// LogInfo is the standard informational level.
	LogInfo
	// LogError logs only error conditions.
	LogError
)

/* ── Struct definitions ───────────────────────────────────────────────── */

// Server represents an HTTP server with host and port configuration.
// It embeds sync.Mutex for concurrent access protection.
type Server struct {
	Port int    // Port number the server listens on.
	Host string // Hostname or IP address to bind to.
	sync.Mutex  // Embedded mutex for thread-safe operations.
	handlers map[string]HandlerFunc // Route handler registry.
}

// HandlerFunc defines the signature for HTTP request handlers.
type HandlerFunc func(ctx context.Context, req []byte) ([]byte, error)

// Embedded struct demonstrating composition over inheritance.
type Address struct {
	Street string // Street name and number.
	City   string // City name.
	Zip    string // Postal/ZIP code.
}

// Employee composes Person-like fields with an embedded Address.
type Employee struct {
	Name    string  // Full name of the employee.
	Age     int     // Age in years.
	Address         // Embedded address (promoted fields).
	Manager *Employee // Optional reference to reporting manager.
}

/* ── Interface definitions ────────────────────────────────────────────── */

// Handler defines the interface for request processing components.
type Handler interface {
	// Handle processes a request and returns a response.
	Handle(ctx context.Context, data []byte) error
}

// ReadWriteCloser composes standard io interfaces.
type ReadWriteCloser interface {
	io.Reader
	io.Writer
	io.Closer
}

/* ── Type aliases and definitions ─────────────────────────────────────── */

// MyInt is a custom integer type supporting additional methods.
type MyInt int

// String returns the string representation of MyInt.
func (m MyInt) String() string {
	return fmt.Sprintf("MyInt(%d)", int(m))
}

/* ── Generic types (Go 1.18+) ─────────────────────────────────────────── */

// Pair holds two values of potentially different types.
// @tparam A The type of the first element.
// @tparam B The type of the second element.
type Pair[A any, B any] struct {
	First  A // First element of the pair.
	Second B // Second element of the pair.
}

// Ordered constrains types that support comparison operators.
type Ordered interface {
	~int | ~float64 | ~string
}

/* ── Functions ────────────────────────────────────────────────────────── */

// main is the application entry point.
func main() {
	fmt.Println("hello")
}

// init runs before main for package-level initialization.
func init() {
	// Package initialization — set default global state
	globalVar = 1
}

// Start begins listening on the configured host and port.
// @receiver s Pointer to Server instance.
func (s *Server) Start() error {
	s.Lock()
	defer s.Unlock()
	// Validate port before binding
	if s.Port <= 0 {
		return fmt.Errorf("invalid port: %d", s.Port)
	}
	fmt.Printf("Starting on %s:%d\n", s.Host, s.Port)
	return nil
}

// Register adds a handler function for a specific route path.
// @receiver s Pointer to Server.
// @param path The URL path to register.
// @param handler The function to invoke for this path.
func (s *Server) Register(path string, handler HandlerFunc) {
	if s.handlers == nil {
		s.handlers = make(map[string]HandlerFunc)
	}
	s.handlers[path] = handler
}

/* ── Generic function ─────────────────────────────────────────────────── */

// Max returns the larger of two ordered values.
// @tparam T Type constrained to Ordered interface.
// @param a First value.
// @param b Second value.
// @return The greater of a and b.
func Max[T Ordered](a, b T) T {
	if a > b {
		return a
	}
	return b
}

// Filter returns elements matching a predicate.
// @tparam T Element type (any).
// @param items Slice of items to filter.
// @param pred Predicate function returning true to keep element.
// @return Filtered slice.
func Filter[T any](items []T, pred func(T) bool) []T {
	result := make([]T, 0)
	for _, item := range items {
		if pred(item) {
			result = append(result, item)
		}
	}
	return result
}

/* ── Multiple return values ───────────────────────────────────────────── */

// Divide performs safe integer division with error handling.
// @param a Dividend.
// @param b Divisor; must not be zero.
// @return Quotient and remainder, or error if b is zero.
func Divide(a, b int) (int, int, error) {
	if b == 0 {
		return 0, 0, fmt.Errorf("division by zero")
	}
	return a / b, a % b, nil
}

/* ── Named return values ──────────────────────────────────────────────── */

// ParseConfig extracts host and port from a config string.
// @param input Configuration string in "host:port" format.
// @return Named host and port values, or error.
func ParseConfig(input string) (host string, port int, err error) {
	// Named returns allow bare return in simple cases
	_, scanErr := fmt.Sscanf(input, "%s:%d", &host, &port)
	if scanErr != nil {
		err = scanErr
		return
	}
	return
}

/* ── Closure ──────────────────────────────────────────────────────────── */

// Counter returns a closure that increments and returns a count.
// @return Closure yielding successive integer counts.
func Counter() func() int {
	count := 0
	return func() int {
		// Capture count from enclosing scope
		count++
		return count
	}
}

/* ── Goroutine and channels ───────────────────────────────────────────── */

// FanOut distributes work across n goroutines via channels.
// @param items Slice of strings to process.
// @param workers Number of concurrent worker goroutines.
// @return Channel delivering processed results.
func FanOut(items []string, workers int) <-chan string {
	results := make(chan string, len(items))
	var wg sync.WaitGroup

	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			// Each worker processes items from the slice
			for _, item := range items {
				results <- fmt.Sprintf("[%d] %s", id, item)
			}
		}(i)
	}

	// Close channel when all workers finish
	go func() {
		wg.Wait()
		close(results)
	}()

	return results
}

/* ── Type switch ──────────────────────────────────────────────────────── */

// Describe returns a description string for any value using type switch.
// @param v Any value to describe.
// @return Human-readable type description.
func Describe(v interface{}) string {
	switch val := v.(type) {
	case int:
		return fmt.Sprintf("int: %d", val)
	case string:
		return fmt.Sprintf("string: %q", val)
	case bool:
		if val {
			return "bool: true"
		}
		return "bool: false"
	case nil:
		return "nil"
	default:
		return fmt.Sprintf("unknown: %T", val)
	}
}

/* ── Defer and panic recovery ─────────────────────────────────────────── */

// SafeExecute runs a function with panic recovery.
// @param fn The function to execute safely.
// @return Error if fn panicked, nil otherwise.
func SafeExecute(fn func()) (err error) {
	defer func() {
		if r := recover(); r != nil {
			// Convert panic to error
			err = fmt.Errorf("panic: %v", r)
		}
	}()
	fn()
	return nil
}
