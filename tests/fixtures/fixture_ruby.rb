# @file fixture_ruby.rb
# @brief Comprehensive Ruby test fixture for parser validation.
# @details Covers blocks, procs, lambdas, method_missing, open classes,
#          mixins, eigenclass, refinements, define_method, and rescue/ensure.
# Single line comment
=begin
Multi-line
comment
=end
require 'json'
require 'set'
require_relative 'helper'

# @brief Maximum retry attempts for transient failures.
MAX_RETRIES = 42

# @brief Frozen string constant for default encoding.
DEFAULT_ENCODING = 'utf-8'.freeze

attr_accessor :name, :age

# ── Concern module for shared behavior ─────────────────────────────────

# @module Loggable
# @brief Mixin providing logging capabilities to including classes.
module Loggable
  # @brief Log a message to stdout with the class name prefix.
  # @param message [String] The message to log.
  def log(message)
    puts "[#{self.class.name}] #{message}"
  end

  # @brief Log an error with backtrace information.
  # @param error [Exception] The exception to log.
  def log_error(error)
    puts "[ERROR] #{error.message}"
    puts error.backtrace.first(5).join("\n") if error.backtrace
  end
end

# ── Main class with nested constructs ──────────────────────────────────

# @class MyClass
# @brief Primary class demonstrating core Ruby patterns.
# @details Includes initializer, class methods, predicate methods,
#          operator overloading, and dynamic method generation.
class MyClass
  include Loggable
  include Comparable

  # @brief Read/write accessor for the instance name.
  attr_accessor :name

  # @brief Read-only accessor for the creation timestamp.
  attr_reader :created_at

  # @brief Initialize a new MyClass instance.
  # @param name [String] The instance identifier.
  # @param options [Hash] Optional configuration hash.
  def initialize(name, **options)
    @name = name
    @options = options
    @created_at = Time.now
    # Set defaults for missing options
    @options[:retries] ||= MAX_RETRIES
  end

  # @brief Factory method creating an instance from a hash.
  # @param attrs [Hash] Attribute hash with :name key required.
  # @return [MyClass] A new instance populated from attrs.
  def self.create(attrs)
    new(attrs[:name], **attrs.except(:name))
  end

  # @brief Build multiple instances from an array of names.
  # @param names [Array<String>] Names to create instances for.
  # @return [Array<MyClass>] Array of new instances.
  def self.bulk_create(names)
    names.map { |n| new(n) }
  end

  # @brief Predicate checking if the instance is valid.
  # @return [Boolean] True if name is non-empty.
  def valid?
    !@name.nil? && !@name.empty?
  end

  # @brief Check if name matches a pattern.
  # @param pattern [Regexp] Regular expression to test against.
  # @return [Boolean] True if name matches the pattern.
  def matches?(pattern)
    return false if @name.nil?
    pattern.match?(@name)
  end

  # @brief Spaceship operator for Comparable mixin.
  # @param other [MyClass] Instance to compare with.
  # @return [Integer] -1, 0, or 1 based on name comparison.
  def <=>(other)
    @name <=> other.name
  end

  # @brief Concatenate two instances into a new one.
  # @param other [MyClass] Instance to merge with.
  # @return [MyClass] New instance with combined name.
  def +(other)
    self.class.new("#{@name}+#{other.name}")
  end

  # @brief Convert to string representation.
  # @return [String] Human-readable description.
  def to_s
    "MyClass(#{@name})"
  end

  # @brief Handle undefined method calls dynamically.
  # @param method [Symbol] The called method name.
  # @param args [Array] Arguments passed to the method.
  # @return [String] Description of the missing method.
  # @raise [NoMethodError] If method doesn't start with 'find_by_'.
  def method_missing(method, *args, &block)
    if method.to_s.start_with?('find_by_')
      field = method.to_s.sub('find_by_', '')
      "Finding by #{field}: #{args.first}"
    else
      super
    end
  end

  # @brief Declare which dynamic methods respond_to? should recognize.
  # @param method [Symbol] The method name to check.
  # @param include_private [Boolean] Whether to include private methods.
  # @return [Boolean] True if the method is handled dynamically.
  def respond_to_missing?(method, include_private = false)
    method.to_s.start_with?('find_by_') || super
  end

  protected

  # @brief Protected helper for internal computations.
  # @return [Hash] Current options hash.
  def internal_config
    @options.dup
  end

  private

  # @brief Private validation running before save.
  # @raise [RuntimeError] If validation fails.
  def validate!
    raise "Invalid name" unless valid?
  end
end

# ── Subclass demonstrating inheritance ─────────────────────────────────

# @class SpecialClass
# @extends MyClass
# @brief Specialized subclass with additional behavior.
class SpecialClass < MyClass
  # @brief Initialize with a priority level.
  # @param name [String] Instance name.
  # @param priority [Integer] Processing priority (lower = first).
  def initialize(name, priority: 0, **options)
    super(name, **options)
    @priority = priority
  end

  # @brief Override to_s with priority information.
  # @return [String] Description including priority.
  def to_s
    "SpecialClass(#{@name}, pri=#{@priority})"
  end
end

# ── Module with mixins ─────────────────────────────────────────────────

# @module MyModule
# @brief Utility module providing helper methods.
module MyModule
  # @brief Module-level helper returning a boolean.
  # @return [Boolean] Always returns true.
  def helper
    true
  end

  # @brief Process data with block yield pattern.
  # @param data [Object] Data to process.
  # @yield [Object] Yields data for caller-defined processing.
  # @return [Object] The block's return value or data itself.
  def process_with_block(data)
    if block_given?
      yield(data)
    else
      data
    end
  end

  # ── Module function ──────────────────────────────────────────────────

  # @brief Utility function accessible without mixing in.
  # @param items [Array] Items to format.
  # @return [String] Comma-separated formatted string.
  def self.format_list(items)
    items.map(&:to_s).join(', ')
  end
end

# ── Struct-based class ─────────────────────────────────────────────────

# @class Coordinate
# @brief Struct-based value object for 2D coordinates.
Coordinate = Struct.new(:x, :y) do
  # @brief Compute the Euclidean distance from origin.
  # @return [Float] Distance from (0, 0).
  def distance_from_origin
    Math.sqrt(x**2 + y**2)
  end
end

# ── Dynamic method definition ─────────────────────────────────────────

# @class DynamicModel
# @brief Demonstrates metaprogramming with define_method.
class DynamicModel
  # Generate getter/setter pairs for each field
  %w[title body author].each do |field|
    # @brief Dynamically defined getter for #{field}.
    define_method(field) do
      instance_variable_get("@#{field}")
    end

    # @brief Dynamically defined setter for #{field}.
    define_method("#{field}=") do |value|
      instance_variable_set("@#{field}", value)
    end
  end
end

# ── Proc and Lambda ───────────────────────────────────────────────────

# @brief Lambda for doubling a numeric value.
doubler = ->(x) { x * 2 }

# @brief Proc for formatting a greeting string.
greeting_proc = Proc.new { |name| "Hello, #{name}!" }

# ── Error handling ────────────────────────────────────────────────────

# @brief Execute a block with retry logic and error recovery.
# @param attempts [Integer] Maximum number of attempts.
# @yield The operation to attempt.
# @return [Object] The block's return value on success.
# @raise [RuntimeError] If all attempts fail.
def with_retry(attempts: MAX_RETRIES)
  tries = 0
  begin
    tries += 1
    yield
  rescue StandardError => e
    # Retry if attempts remain
    retry if tries < attempts
    raise "Failed after #{attempts} attempts: #{e.message}"
  ensure
    # Cleanup runs regardless of outcome
    puts "Completed after #{tries} attempt(s)"
  end
end

# ── Refinement ────────────────────────────────────────────────────────

# @module StringExtensions
# @brief Refinement adding utility methods to String.
module StringExtensions
  refine String do
    # @brief Check if the string is a valid email address.
    # @return [Boolean] True if string matches email pattern.
    def email?
      match?(/\A[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+\z/i)
    end
  end
end

=begin
coverage extension block
=end
class ServiceObject; end # inline class comment
class ReportBuilder; end
module Metrics; end
module Extras; end
MAX_LIMIT = 100
API_VERSION = "v2"
CACHE_SIZE = 1024
attr_writer :token
attr_reader :state
require 'yaml'
require 'logger'
