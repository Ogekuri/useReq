/**
 * @file fixture_kotlin.kt
 * @brief Comprehensive Kotlin test fixture for parser validation.
 * @details Covers extension functions, inline/reified generics, DSL builders,
 *          delegation, coroutine scope, destructuring, sealed interfaces,
 *          value classes, operator overloading, and lateinit.
 */
// Single line comment
/* Multi-line
   comment */
import kotlin.collections.List
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

/* ── Annotations ──────────────────────────────────────────────────────── */

/** @brief Marks a class or function as deprecated with migration path. */
@Deprecated("Use UserV2 instead", replaceWith = ReplaceWith("UserV2"))
data class User(val name: String, val age: Int = 0)

/* ── Sealed class hierarchy ───────────────────────────────────────────── */

/**
 * @class Result
 * @brief Sealed class representing success/failure outcomes.
 * @tparam T The success value type.
 */
sealed class Result<out T> {
    /**
     * @class Success
     * @brief Successful outcome holding a value.
     * @param value The result data.
     */
    data class Success<T>(val value: T) : Result<T>()

    /**
     * @class Error
     * @brief Failed outcome holding an error message.
     * @param message Description of the failure.
     * @param cause Optional underlying exception.
     */
    data class Error(val message: String, val cause: Throwable? = null) : Result<Nothing>()

    /**
     * @object Loading
     * @brief Singleton state representing an in-progress operation.
     */
    object Loading : Result<Nothing>()

    /**
     * @brief Map the success value using a transform function.
     * @tparam R The target type after transformation.
     * @param transform Function converting T to R.
     * @return Transformed Result or original error/loading state.
     */
    fun <R> map(transform: (T) -> R): Result<R> = when (this) {
        is Success -> Success(transform(value))
        is Error -> Error(message, cause)
        is Loading -> Loading
    }
}

/* ── Interface ────────────────────────────────────────────────────────── */

/**
 * @interface Repository
 * @brief Generic CRUD repository interface.
 * @tparam T Entity type managed by this repository.
 */
interface Repository<T> {
    /**
     * @brief Find an entity by its unique identifier.
     * @param id Entity ID.
     * @return The entity or null if not found.
     */
    fun findById(id: Int): T?

    /**
     * @brief Persist an entity.
     * @param entity The entity to save.
     * @return True if save succeeded.
     */
    fun save(entity: T): Boolean

    /**
     * @brief Retrieve all entities as a Flow stream.
     * @return Flow emitting all stored entities.
     */
    fun findAll(): Flow<T>
}

/**
 * @interface Identifiable
 * @brief Sealed interface requiring an ID property.
 */
sealed interface Identifiable {
    /** @brief Unique entity identifier. */
    val id: Int
}

/* ── Enum class ───────────────────────────────────────────────────────── */

/**
 * @enum Color
 * @brief Color enum with hex value property and companion factory.
 */
enum class Color(val hex: String) {
    /** @brief Red color channel. */
    RED("#FF0000"),
    /** @brief Green color channel. */
    GREEN("#00FF00"),
    /** @brief Blue color channel. */
    BLUE("#0000FF");

    companion object {
        /**
         * @brief Parse a color from its hex string.
         * @param hex Hex color code including '#' prefix.
         * @return Matching Color or null.
         */
        fun fromHex(hex: String): Color? = values().find { it.hex == hex }
    }
}

/* ── Data class implementing interface ────────────────────────────────── */

/**
 * @class Entity
 * @brief Data class combining Identifiable with named properties.
 * @param id Unique identifier.
 * @param name Entity display name.
 * @param status Current lifecycle status.
 */
data class Entity(
    override val id: Int,
    val name: String,
    val status: String = "active",
) : Identifiable

/* ── Value class (inline class) ───────────────────────────────────────── */

/**
 * @class EmailAddress
 * @brief Inline value class wrapping a validated email string.
 * @param value The raw email address string.
 */
@JvmInline
value class EmailAddress(val value: String) {
    init {
        require(value.contains('@')) { "Invalid email: $value" }
    }

    /** @brief Extract the domain part of the email. */
    val domain: String get() = value.substringAfter('@')
}

/* ── Functions ────────────────────────────────────────────────────────── */

/**
 * @function greet
 * @brief Greet a person by name.
 * @param name The person's name.
 * @return Greeting message string.
 */
fun greet(name: String): String {
    return "Hello $name"
}

/**
 * @function fetchData
 * @brief Suspend function simulating async data retrieval.
 * @return Retrieved data as a string.
 */
suspend fun fetchData(): String {
    /* Simulate network delay */
    return "data"
}

/**
 * @function processItems
 * @brief Higher-order function with trailing lambda syntax.
 * @param items List of strings to process.
 * @param transform Function applied to each item.
 * @return List of transformed results.
 */
fun processItems(items: List<String>, transform: (String) -> String): List<String> {
    return items.map(transform)
}

/* ── Extension functions ──────────────────────────────────────────────── */

/**
 * @brief Extension function adding word count to String.
 * @receiver String The string to count words in.
 * @return Number of whitespace-separated words.
 */
fun String.wordCount(): Int {
    return this.trim().split("\\s+".toRegex()).size
}

/**
 * @brief Extension property returning the last character or null.
 * @receiver String The string to inspect.
 */
val String.lastChar: Char?
    get() = if (this.isEmpty()) null else this[this.length - 1]

/* ── Inline function with reified type ────────────────────────────────── */

/**
 * @function filterByType
 * @brief Filter list elements by reified type parameter.
 * @tparam T The target type to filter for.
 * @param items Mixed list to filter.
 * @return List containing only elements of type T.
 */
inline fun <reified T> filterByType(items: List<Any>): List<T> {
    return items.filterIsInstance<T>()
}

/* ── Operator overloading ─────────────────────────────────────────────── */

/**
 * @class Vector2
 * @brief 2D vector with operator overloading for arithmetic.
 * @param x Horizontal component.
 * @param y Vertical component.
 */
data class Vector2(val x: Double, val y: Double) {
    /**
     * @brief Add two vectors component-wise.
     * @param other The vector to add.
     * @return Resulting sum vector.
     */
    operator fun plus(other: Vector2) = Vector2(x + other.x, y + other.y)

    /**
     * @brief Negate the vector (unary minus).
     * @return Vector with negated components.
     */
    operator fun unaryMinus() = Vector2(-x, -y)

    /**
     * @brief Compute dot product via times operator.
     * @param other The other vector.
     * @return Scalar dot product.
     */
    operator fun times(other: Vector2) = x * other.x + y * other.y
}

/* ── Constants and variables ──────────────────────────────────────────── */

/** @brief Mathematical constant Pi. */
val PI = 3.14159265

/** @brief Mutable package-level counter. */
var counter = 0

/* ── Object (singleton) ───────────────────────────────────────────────── */

/**
 * @object Singleton
 * @brief Application-wide singleton for configuration management.
 */
object Singleton {
    /** @brief Mutable configuration map. */
    private val config = mutableMapOf<String, Any>()

    /**
     * @brief Store a configuration value.
     * @param key Configuration key.
     * @param value Configuration value.
     */
    fun set(key: String, value: Any) {
        config[key] = value
    }

    /**
     * @brief Retrieve a typed configuration value.
     * @tparam T Expected value type.
     * @param key Configuration key.
     * @return The value cast to T, or null.
     */
    @Suppress("UNCHECKED_CAST")
    fun <T> get(key: String): T? = config[key] as? T
}

/**
 * @object Factory
 * @brief Companion object pattern for factory construction.
 */
companion object Factory {
}

/* ── Delegation ───────────────────────────────────────────────────────── */

/**
 * @class DelegatingList
 * @brief List implementation delegating to an inner mutable list.
 * @tparam T Element type.
 * @param inner The backing list.
 */
class DelegatingList<T>(private val inner: MutableList<T>) : List<T> by inner {
    /** @brief Count of accesses to the delegated list. */
    var accessCount = 0
        private set

    /**
     * @brief Override size to track access and delegate.
     */
    override val size: Int
        get() {
            accessCount++
            return inner.size
        }
}

/* ── Class with lateinit ──────────────────────────────────────────────── */

/**
 * @class Service
 * @brief Service class demonstrating lateinit and lazy initialization.
 */
class Service {
    /** @brief Late-initialized dependency, set after construction. */
    lateinit var dependency: Repository<Entity>

    /** @brief Lazily computed expensive resource. */
    val resource: String by lazy {
        /* Computed on first access */
        "expensive_resource"
    }

    /**
     * @brief Check if the dependency has been initialized.
     * @return True if dependency is set.
     */
    fun isReady(): Boolean = ::dependency.isInitialized
}

/* ── DSL builder pattern ──────────────────────────────────────────────── */

/**
 * @class HtmlBuilder
 * @brief Simple DSL for building HTML strings.
 */
class HtmlBuilder {
    private val elements = mutableListOf<String>()

    /**
     * @brief Add a div element with content from a lambda.
     * @param block Lambda providing the div content.
     */
    fun div(block: HtmlBuilder.() -> Unit) {
        val inner = HtmlBuilder()
        inner.block()
        elements.add("<div>${inner.build()}</div>")
    }

    /**
     * @brief Add a text node.
     * @param text The text content.
     */
    fun text(text: String) {
        elements.add(text)
    }

    /**
     * @brief Build the accumulated HTML string.
     * @return Concatenated HTML output.
     */
    fun build(): String = elements.joinToString("")
}

/**
 * @function html
 * @brief DSL entry point for building HTML content.
 * @param block Builder lambda receiving HtmlBuilder scope.
 * @return Complete HTML string.
 */
fun html(block: HtmlBuilder.() -> Unit): String {
    val builder = HtmlBuilder()
    builder.block()
    return builder.build()
}

/* coverage extension block */
import kotlin.math.max
import kotlin.math.min
interface Logger
interface Parser
interface Emitter
interface Formatter
enum class ModeKt { FAST, SAFE }
enum class PhaseKt { INIT, RUN }
enum class StatusKt { READY, WAITING }
enum class SignalKt { ON, OFF }
@Synchronized
@PublishedApi
object CacheStore
var retries = 0
var attempts = 0
var state = "idle"

/* REQ-COVER-SRS-231 START */
/**
 * @REQ-COVER-SRS-231 block 1
 * @brief Coverage helper construct 1.
 * @details Provides deterministic fixture-level Doxygen coverage block 1.
 * @param value Input value for helper construct 1.
 * @return Output value for helper construct 1.
 */
fun reqCoverKotlin1(value: Int): Int = value + 1

/**
 * @REQ-COVER-SRS-231 block 2
 * @brief Coverage helper construct 2.
 * @details Provides deterministic fixture-level Doxygen coverage block 2.
 * @param value Input value for helper construct 2.
 * @return Output value for helper construct 2.
 */
fun reqCoverKotlin2(value: Int): Int = value + 2

/**
 * @REQ-COVER-SRS-231 block 3
 * @brief Coverage helper construct 3.
 * @details Provides deterministic fixture-level Doxygen coverage block 3.
 * @param value Input value for helper construct 3.
 * @return Output value for helper construct 3.
 */
fun reqCoverKotlin3(value: Int): Int = value + 3

/**
 * @REQ-COVER-SRS-231 block 4
 * @brief Coverage helper construct 4.
 * @details Provides deterministic fixture-level Doxygen coverage block 4.
 * @param value Input value for helper construct 4.
 * @return Output value for helper construct 4.
 */
fun reqCoverKotlin4(value: Int): Int = value + 4

/**
 * @REQ-COVER-SRS-231 block 5
 * @brief Coverage helper construct 5.
 * @details Provides deterministic fixture-level Doxygen coverage block 5.
 * @param value Input value for helper construct 5.
 * @return Output value for helper construct 5.
 */
fun reqCoverKotlin5(value: Int): Int = value + 5

/* REQ-COVER-SRS-231 END */
