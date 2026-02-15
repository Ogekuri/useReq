/// @file fixture_rust.rs
/// @brief Comprehensive Rust test fixture for parser stress-testing.
/// @details Covers lifetimes, closures, trait objects, async traits,
///          unsafe blocks, pattern matching, generic impls, where clauses,
///          pub(crate) visibility, and advanced macro rules.
// Single line comment
/* Multi-line
   comment */
use std::io;
use std::collections::HashMap;
use std::fmt::{self, Display, Formatter};
use std::sync::{Arc, Mutex};

/* ── Struct with derive and lifetimes ─────────────────────────────────── */

/// A simple struct for testing derive macros and field parsing.
///
/// @brief Holds a single i32 field with Debug/Clone derives.
#[derive(Debug, Clone, PartialEq)]
pub struct MyStruct {
    /// @brief Primary integer field.
    field: i32,
}

/// Struct with lifetime parameter for borrowed data.
///
/// @brief Demonstrates lifetime annotations in struct definitions.
/// @tparam 'a Lifetime of the borrowed string slice.
#[derive(Debug)]
pub struct BorrowedData<'a> {
    /// @brief Reference to externally-owned string data.
    content: &'a str,
    /// @brief Numeric tag for identification.
    tag: u64,
}

/// Generic struct with multiple type parameters and bounds.
///
/// @tparam K Key type; must implement Hash and Eq.
/// @tparam V Value type; must implement Clone.
pub struct TypedMap<K: std::hash::Hash + Eq, V: Clone> {
    /// @brief Internal hash map storage.
    inner: HashMap<K, V>,
}

/* ── Enum with data variants ──────────────────────────────────────────── */

/// Enum with mixed variant types for discriminated union testing.
///
/// @brief Represents either structured data, a simple flag, or a pair.
pub enum MyEnum {
    /// @brief Unit variant carrying no data.
    A,
    /// @brief Tuple variant holding a string payload.
    B(String),
    /// @brief Struct variant with named fields.
    C { x: i32, y: i32 },
}

/* ── Trait and impls ──────────────────────────────────────────────────── */

/// Trait defining a work execution interface.
///
/// @brief Implementors must provide both sync and optional async execution.
pub trait MyTrait {
    /// Execute a unit of work synchronously.
    fn do_work(&self);

    /// Execute work with a context parameter.
    ///
    /// @param ctx Contextual string passed to the implementation.
    /// @return True if work completed successfully.
    fn do_work_with_ctx(&self, ctx: &str) -> bool {
        /* Default implementation logs and delegates */
        println!("ctx: {}", ctx);
        self.do_work();
        true
    }
}

/// Trait with associated type and lifetime.
///
/// @brief Parsers produce items of an associated Output type.
/// @tparam 'a Lifetime of the input data.
pub trait Parser<'a> {
    /// @brief The output type produced by parsing.
    type Output;

    /// Parse input bytes into the associated output type.
    ///
    /// @param input Byte slice to parse.
    /// @return Parsed output or an IO error.
    fn parse(&self, input: &'a [u8]) -> Result<Self::Output, io::Error>;
}

impl MyStruct {
    /// Create a new MyStruct with default field value.
    ///
    /// @return A MyStruct with field initialized to 0.
    fn new() -> Self {
        Self { field: 0 }
    }

    /// Create a MyStruct with a specific value.
    ///
    /// @param val The initial field value.
    /// @return A new MyStruct.
    pub fn with_value(val: i32) -> Self {
        Self { field: val }
    }

    /// Get the current field value.
    ///
    /// @return The stored integer.
    pub fn value(&self) -> i32 {
        self.field
    }

    /// Conditionally update the field.
    ///
    /// @param new_val New value to set.
    /// @return Old value if updated, None if new_val equals current.
    pub fn try_update(&mut self, new_val: i32) -> Option<i32> {
        if new_val == self.field {
            return None;
        }
        let old = self.field;
        self.field = new_val;
        /* Return the previous value wrapped in Some */
        Some(old)
    }
}

impl MyTrait for MyStruct {
    /// Concrete implementation printing the struct.
    fn do_work(&self) {
        println!("{:?}", self);
    }
}

impl Display for MyStruct {
    /// Format MyStruct for user-facing display.
    ///
    /// @param f Formatter to write into.
    /// @return fmt::Result indicating success or failure.
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "MyStruct({})", self.field)
    }
}

/* ── Generic impl with where clause ───────────────────────────────────── */

impl<K, V> TypedMap<K, V>
where
    K: std::hash::Hash + Eq + Display,
    V: Clone + Default,
{
    /// Insert a key-value pair, returning the old value if present.
    ///
    /// @param key The lookup key.
    /// @param value The value to associate with the key.
    /// @return Previous value for this key, or None.
    pub fn insert(&mut self, key: K, value: V) -> Option<V> {
        self.inner.insert(key, value)
    }

    /// Get a cloned value by key reference.
    ///
    /// @param key The key to look up.
    /// @return Cloned value if found, or the default for V.
    pub fn get_or_default(&self, key: &K) -> V {
        match self.inner.get(key) {
            Some(v) => v.clone(),
            None => V::default(),
        }
    }
}

/* ── Module ───────────────────────────────────────────────────────────── */

/// @brief Sub-module containing utility helpers.
pub mod my_module;

/// @brief Inline module with pub(crate) scoped items.
pub(crate) mod internal {
    /// Internal counter not exposed outside the crate.
    pub(crate) static COUNTER: std::sync::atomic::AtomicUsize =
        std::sync::atomic::AtomicUsize::new(0);
}

/* ── Macro rules ──────────────────────────────────────────────────────── */

/// Variadic macro generating a HashMap from key-value pairs.
///
/// @brief Usage: `hashmap!{ "a" => 1, "b" => 2 }`.
macro_rules! hashmap {
    ($($key:expr => $val:expr),* $(,)?) => {{
        let mut map = HashMap::new();
        $(map.insert($key, $val);)*
        map
    }};
}

/// Macro with multiple match arms for different patterns.
macro_rules! my_macro {
    () => {};
    ($x:expr) => { println!("{}", $x) };
    ($x:expr, $($rest:expr),+) => {
        print!("{}, ", $x);
        my_macro!($($rest),+);
    };
}

/* ── Constants and statics ────────────────────────────────────────────── */

/// @brief Compile-time constant for maximum retry attempts.
const MY_CONST: i32 = 42;

/// @brief Mutable static requiring unsafe access.
static MY_STATIC: i32 = 0;

/// @brief Thread-safe lazy-initialized global configuration.
static CONFIG: std::sync::LazyLock<HashMap<String, String>> =
    std::sync::LazyLock::new(|| HashMap::new());

/* ── Type alias ───────────────────────────────────────────────────────── */

/// @brief Alias for a common Result type with IO errors.
pub type IoResult<T> = Result<T, io::Error>;

/// @brief Simple integer alias.
pub type MyAlias = i32;

/* ── Functions ────────────────────────────────────────────────────────── */

/// Top-level function demonstrating multiple return paths.
///
/// @param input Optional string to evaluate.
/// @return Processed string or a fallback default.
pub fn my_function(input: Option<&str>) -> String {
    /* Early return on None */
    let text = match input {
        Some(s) if !s.is_empty() => s,
        Some(_) => return String::from("empty"),
        None => return String::from("none"),
    };
    /* Transform and return */
    text.to_uppercase()
}

/// Async function performing simulated IO.
///
/// @return A greeting string after async computation.
pub async fn async_function() -> String {
    /* Simulate async work */
    String::from("hello async")
}

/// Function accepting a closure with trait bounds.
///
/// @param items Slice of integers to filter.
/// @param predicate Closure returning true for items to keep.
/// @return Vector of items passing the predicate.
pub fn filter_with<F>(items: &[i32], predicate: F) -> Vec<i32>
where
    F: Fn(&i32) -> bool,
{
    items.iter().copied().filter(|x| predicate(x)).collect()
}

/// Function returning a boxed trait object.
///
/// @param use_struct If true, returns MyStruct; otherwise panics.
/// @return A heap-allocated trait object implementing MyTrait.
pub fn create_worker(use_struct: bool) -> Box<dyn MyTrait> {
    if use_struct {
        Box::new(MyStruct::new())
    } else {
        panic!("No alternative implementation available");
    }
}

/// Unsafe function wrapping raw pointer dereference.
///
/// @param ptr Raw pointer to an i32 value.
/// @return The value pointed to by ptr.
/// @safety Caller must ensure ptr is valid and aligned.
pub unsafe fn read_raw(ptr: *const i32) -> i32 {
    /* Dereference raw pointer under unsafe contract */
    *ptr
}

/// Extern "C" function for FFI interoperability.
///
/// @param x Integer to double.
/// @return The input multiplied by 2.
pub extern "C" fn ffi_double(x: i32) -> i32 {
    x * 2
}

/// Function demonstrating exhaustive pattern matching.
///
/// @param val An enum variant to match against.
/// @return A description string for the matched variant.
pub fn describe_enum(val: &MyEnum) -> String {
    match val {
        MyEnum::A => String::from("unit"),
        MyEnum::B(s) => format!("string: {}", s),
        MyEnum::C { x, y } => {
            /* Compute magnitude for struct variant */
            let mag = ((x * x + y * y) as f64).sqrt();
            format!("point({}, {}) mag={:.2}", x, y, mag)
        }
    }
}
