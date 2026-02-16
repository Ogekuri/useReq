/**
 * @file fixture_scala.scala
 * @brief Comprehensive Scala test fixture for parser validation.
 * @details Covers implicits/givens, pattern matching, higher-kinded types,
 *          self-types, variance, opaque types, extension methods, enums,
 *          for comprehensions, and cake pattern.
 */
// Single line comment
/* Multi-line
   comment */
import scala.collection.mutable
import scala.concurrent.{Future, ExecutionContext}
import scala.util.{Try, Success, Failure}

/* ── Case class with copy and pattern matching ────────────────────────── */

/**
 * @class Person
 * @brief Immutable data class for person entities.
 * @param name Display name.
 * @param age Age in years; must be non-negative.
 */
case class Person(name: String, age: Int) {
  /**
   * @brief Check if the person is an adult.
   * @return True if age >= 18.
   */
  def isAdult: Boolean = age >= 18

  /**
   * @brief Create a greeting string.
   * @return Formatted greeting including name and age.
   */
  def greet: String = s"Hi, I'm $name, age $age"
}

/* ── Sealed trait hierarchy ───────────────────────────────────────────── */

/**
 * @class Shape
 * @brief Sealed trait for algebraic data type shapes.
 */
sealed trait Shape {
  /**
   * @brief Compute the area of this shape.
   * @return Area as a Double.
   */
  def area: Double
}

/**
 * @class Circle
 * @brief Circle shape with radius.
 * @param radius The circle's radius.
 */
case class Circle(radius: Double) extends Shape {
  override def area: Double = math.Pi * radius * radius
}

/**
 * @class Rectangle
 * @brief Rectangle shape with width and height.
 * @param width The rectangle's width.
 * @param height The rectangle's height.
 */
case class Rectangle(width: Double, height: Double) extends Shape {
  override def area: Double = width * height
}

/* ── Abstract class ───────────────────────────────────────────────────── */

/**
 * @class Animal
 * @brief Abstract base class for animals with sound production.
 */
abstract class Animal {
  /**
   * @brief The sound this animal makes.
   * @return Sound description string.
   */
  def sound: String

  /**
   * @brief Describe the animal including its sound.
   * @return Formatted description string.
   */
  def describe: String = s"I am a ${getClass.getSimpleName} and I say $sound"
}

/* ── Trait with self-type ─────────────────────────────────────────────── */

/**
 * @trait Drawable
 * @brief Trait for rendering objects to string representation.
 */
trait Drawable {
  /**
   * @brief Draw the object as a string.
   * @return Rendered string representation.
   */
  def draw(): Unit
}

/**
 * @trait Logging
 * @brief Self-type trait requiring Drawable to be mixed in.
 * @details Demonstrates the cake pattern for dependency injection.
 */
trait Logging { self: Drawable =>
  /**
   * @brief Log the drawing operation and then draw.
   */
  def logAndDraw(): Unit = {
    println("About to draw")
    draw()
  }
}

/**
 * @trait Serializable
 * @brief Trait for objects convertible to byte arrays.
 */
trait Serializable {
  /**
   * @brief Serialize this object to bytes.
   * @return Byte array representation.
   */
  def serialize: Array[Byte]
}

/* ── Object (singleton) ───────────────────────────────────────────────── */

/**
 * @object Main
 * @brief Application entry point and utility function container.
 */
object Main {
  /**
   * @brief Application entry point.
   * @param args Command-line arguments.
   */
  def main(args: Array[String]): Unit = {
    val people = List(Person("Alice", 30), Person("Bob", 17))
    /* Filter adults using pattern matching */
    val adults = people.filter(_.isAdult)
    adults.foreach(p => println(p.greet))
  }

  /**
   * @brief Override toString for Main object display.
   * @return String representation.
   */
  override def toString: String = "Main"

  /** @brief Mathematical constant pi. */
  val pi = 3.14159265

  /** @brief Mutable counter for tracking operations. */
  var counter = 0

  /**
   * @brief Type alias for lists of strings.
   */
  type StringList = List[String]

  /**
   * @brief Type alias for function transformers.
   */
  type Transformer[A] = A => A

  /**
   * @brief Describe a shape using exhaustive pattern matching.
   * @param shape The shape to describe.
   * @return Human-readable description with area.
   */
  def describeShape(shape: Shape): String = shape match {
    case Circle(r) => s"Circle with radius $r, area=${shape.area}"
    case Rectangle(w, h) => s"Rectangle ${w}x${h}, area=${shape.area}"
  }

  /**
   * @brief Process a value with multiple match guards.
   * @param x Integer input to classify.
   * @return Classification string.
   */
  def classify(x: Int): String = x match {
    case 0 => "zero"
    case n if n < 0 => "negative"
    case n if n > 100 => "large"
    case _ => "positive"
  }
}

/* ── Companion object with apply ──────────────────────────────────────── */

/**
 * @class Config
 * @brief Configuration holder with companion factory.
 * @param entries Key-value pairs.
 */
class Config private (val entries: Map[String, String]) {
  /**
   * @brief Retrieve a value by key.
   * @param key The configuration key.
   * @return Optional value.
   */
  def get(key: String): Option[String] = entries.get(key)
}

/**
 * @object Config
 * @brief Companion object with factory methods for Config.
 */
object Config {
  /**
   * @brief Create a Config from key-value pairs.
   * @param entries Variable number of key-value tuples.
   * @return A new Config instance.
   */
  def apply(entries: (String, String)*): Config = new Config(entries.toMap)

  /**
   * @brief Create an empty Config.
   * @return Config with no entries.
   */
  def empty: Config = new Config(Map.empty)
}

/* ── Generic class with variance ──────────────────────────────────────── */

/**
 * @class Container
 * @brief Covariant generic container.
 * @tparam +A Element type (covariant).
 */
class Container[+A](val value: A) {
  /**
   * @brief Map the contained value.
   * @tparam B Target type.
   * @param f Transform function.
   * @return New Container with transformed value.
   */
  def map[B](f: A => B): Container[B] = new Container(f(value))

  /**
   * @brief Flat-map the contained value.
   * @tparam B Target type.
   * @param f Transform function returning a Container.
   * @return Flattened Container.
   */
  def flatMap[B](f: A => Container[B]): Container[B] = f(value)
}

/* ── Implicit conversions and classes ─────────────────────────────────── */

/**
 * @class RichInt
 * @brief Implicit class extending Int with utility methods.
 * @param n The wrapped integer value.
 */
implicit class RichInt(val n: Int) extends AnyVal {
  /**
   * @brief Check if the number is even.
   * @return True if n is divisible by 2.
   */
  def isEven: Boolean = n % 2 == 0

  /**
   * @brief Repeat a string n times.
   * @param s The string to repeat.
   * @return Concatenated result.
   */
  def times(s: String): String = s * n
}

/* ── For comprehension example ────────────────────────────────────────── */

/**
 * @object ForCompExample
 * @brief Demonstrates for-comprehension with multiple generators.
 */
object ForCompExample {
  /**
   * @brief Compute all pairs of integers whose sum equals target.
   * @param range Upper bound of the search space.
   * @param target Desired sum.
   * @return List of pairs summing to target.
   */
  def findPairs(range: Int, target: Int): List[(Int, Int)] = {
    for {
      x <- (1 to range).toList
      y <- (x to range).toList
      if x + y == target
    } yield (x, y)
  }
}

/* ── Higher-order and curried functions ────────────────────────────────── */

/**
 * @object FuncUtils
 * @brief Utility functions demonstrating functional patterns.
 */
object FuncUtils {
  /**
   * @brief Curried addition function.
   * @param a First operand.
   * @param b Second operand.
   * @return Sum of a and b.
   */
  def add(a: Int)(b: Int): Int = a + b

  /**
   * @brief Apply a function twice to an initial value.
   * @tparam A Value type.
   * @param f Function to apply.
   * @param x Initial value.
   * @return Result of f(f(x)).
   */
  def twice[A](f: A => A)(x: A): A = f(f(x))

  /**
   * @brief Compose two functions left to right.
   * @tparam A Input type.
   * @tparam B Intermediate type.
   * @tparam C Output type.
   * @param f First function.
   * @param g Second function.
   * @return Composed function.
   */
  def compose[A, B, C](f: A => B, g: B => C): A => C = a => g(f(a))
}

/* coverage extension block */
import scala.util.Random
import scala.concurrent.duration._
trait Runner
trait Parser
object Metrics
val MaxUsers = 100
val RetryLimit = 3
type UserKey = String
type ErrorCode = Int
type Mapper = String => String
var attempts = 0
var cursor = 1
var stage = "init"
var status = "ready"
