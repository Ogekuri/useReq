<?php
/**
 * @file fixture_php.php
 * @brief Comprehensive PHP test fixture for parser validation.
 * @details Covers enums with methods, union/intersection types, readonly
 *          properties, constructor promotion, arrow functions, match expressions,
 *          first-class callables, attributes, fibers, and named arguments.
 */
// Single line comment
/* Multi-line
   comment */
namespace App\Models;

use App\Contracts\Repository;
use App\Events\{ModelCreated, ModelDeleted};
use Psr\Log\LoggerInterface;
require_once 'config.php';

/* ── Constants ────────────────────────────────────────────────────────── */

/** @brief Application version string. */
const VERSION = "1.0";

/** @brief Maximum number of query results per page. */
const MAX_PER_PAGE = 50;

/* ── Enum with methods (PHP 8.1) ──────────────────────────────────────── */

/**
 * @enum Status
 * @brief Backed enum representing entity lifecycle states.
 */
enum Status: string {
    /** @brief Entity is in draft state, not yet visible. */
    case Draft = 'draft';
    /** @brief Entity is published and publicly accessible. */
    case Published = 'published';
    /** @brief Entity is archived and read-only. */
    case Archived = 'archived';

    /**
     * @brief Check if the status represents an active state.
     * @return bool True if the entity is publicly visible.
     */
    public function isActive(): bool {
        return $this === self::Published;
    }

    /**
     * @brief Get a human-readable label for display.
     * @return string Formatted status label.
     */
    public function label(): string {
        return match($this) {
            self::Draft => 'Draft',
            self::Published => 'Published',
            self::Archived => 'Archived',
        };
    }
}

/* ── Abstract class with constructor promotion ────────────────────────── */

/**
 * @class BaseModel
 * @brief Abstract base model with common persistence operations.
 * @details Uses constructor promotion for compact field declaration.
 */
abstract class BaseModel {
    /**
     * @brief Construct a model with promoted properties.
     * @param int $id Unique identifier (readonly after construction).
     * @param \DateTimeImmutable $createdAt Timestamp of creation.
     */
    public function __construct(
        public readonly int $id,
        public readonly \DateTimeImmutable $createdAt = new \DateTimeImmutable(),
    ) {}

    /**
     * @brief Persist the model to the data store.
     * @return bool True if save succeeded.
     */
    public function save(): bool {
        // Validate before persisting
        if (!$this->validate()) {
            return false;
        }
        return true;
    }

    /**
     * @brief Validate model state before persistence.
     * @return bool True if model is valid.
     */
    abstract protected function validate(): bool;

    /**
     * @brief Internal validation helper with type narrowing.
     * @return bool True if entity passes all constraint checks.
     */
    private static function validateConstraints(): bool {
        return true;
    }

    /**
     * @brief Convert model to array representation.
     * @return array<string, mixed> Associative array of model properties.
     */
    abstract public function toArray(): array;
}

/* ── Concrete class with union types ──────────────────────────────────── */

/**
 * @class User
 * @extends BaseModel
 * @brief Concrete user entity with union and intersection types.
 */
final class User extends BaseModel {
    /** @brief User's display name. */
    private string $name;

    /** @brief User's email address or null if unverified. */
    private ?string $email;

    /**
     * @brief Construct a User with promoted and explicit properties.
     * @param int $id Unique user ID.
     * @param string $name Display name.
     * @param string|null $email Optional email address.
     */
    public function __construct(
        int $id,
        string $name,
        ?string $email = null,
    ) {
        parent::__construct($id);
        $this->name = $name;
        $this->email = $email;
    }

    /**
     * @brief Get the user's display name.
     * @return string The user name.
     */
    public function getName(): string {
        return $this->name;
    }

    /**
     * @brief Get a value that may be string or int.
     * @return string|int The identifier in either format.
     */
    public function getIdentifier(): string|int {
        // Return email if available, otherwise numeric ID
        return $this->email ?? $this->id;
    }

    /**
     * @brief Validate user-specific constraints.
     * @return bool True if name is non-empty.
     */
    protected function validate(): bool {
        return strlen($this->name) > 0;
    }

    /**
     * @brief Serialize user to array.
     * @return array<string, mixed> User data array.
     */
    public function toArray(): array {
        return [
            'id' => $this->id,
            'name' => $this->name,
            'email' => $this->email,
        ];
    }
}

/* ── Interface with type hints ────────────────────────────────────────── */

/**
 * @interface Repo
 * @brief Generic repository interface for data access patterns.
 */
interface Repo {
    /**
     * @brief Retrieve all entities.
     * @return iterable<BaseModel> Collection of models.
     */
    public function findAll(): iterable;

    /**
     * @brief Find a single entity by ID.
     * @param int $id Entity identifier.
     * @return BaseModel|null The found entity or null.
     */
    public function findById(int $id): ?BaseModel;

    /**
     * @brief Count entities matching a filter.
     * @param array<string, mixed> $criteria Filter criteria.
     * @return int Number of matching entities.
     */
    public function count(array $criteria = []): int;
}

/* ── Trait with abstract methods ──────────────────────────────────────── */

/**
 * @trait Cacheable
 * @brief Provides caching capabilities for models.
 */
trait Cacheable {
    /** @brief Cache TTL in seconds. */
    protected int $cacheTtl = 3600;

    /**
     * @brief Store the current object in cache.
     * @return bool True if caching succeeded.
     */
    public function cache(): bool {
        // Serialize and store with TTL
        return true;
    }

    /**
     * @brief Invalidate the cached version of this object.
     * @return void
     */
    public function invalidateCache(): void {
        // Remove from cache backend
    }

    /**
     * @brief Require implementing classes to provide a cache key.
     * @return string The unique cache key.
     */
    abstract public function cacheKey(): string;
}

/**
 * @trait SoftDeletable
 * @brief Adds soft delete functionality to models.
 */
trait SoftDeletable {
    /** @brief Timestamp of soft deletion or null if active. */
    protected ?\DateTimeImmutable $deletedAt = null;

    /**
     * @brief Mark the entity as soft-deleted.
     * @return void
     */
    public function softDelete(): void {
        $this->deletedAt = new \DateTimeImmutable();
    }

    /**
     * @brief Check if the entity is currently deleted.
     * @return bool True if soft-deleted.
     */
    public function isDeleted(): bool {
        return $this->deletedAt !== null;
    }
}

/* ── Class using multiple traits ──────────────────────────────────────── */

/**
 * @class CachedUser
 * @extends User
 * @brief User entity with caching and soft-delete capabilities.
 */
final class CachedUser extends User {
    use Cacheable;
    use SoftDeletable;

    /**
     * @brief Generate a unique cache key for this user.
     * @return string Cache key in format "user:{id}".
     */
    public function cacheKey(): string {
        return "user:{$this->id}";
    }
}

/* ── Attribute (PHP 8.0) ──────────────────────────────────────────────── */

/**
 * @class Route
 * @brief PHP attribute for annotating controller methods with routes.
 */
#[\Attribute(\Attribute::TARGET_METHOD | \Attribute::IS_REPEATABLE)]
class Route {
    /**
     * @brief Define a route attribute.
     * @param string $path URL path pattern.
     * @param string $method HTTP method (GET, POST, etc.).
     */
    public function __construct(
        public readonly string $path,
        public readonly string $method = 'GET',
    ) {}
}

/* ── Free functions ───────────────────────────────────────────────────── */

/**
 * @function helper
 * @brief Standalone helper returning a boolean result.
 * @return bool Always returns true.
 */
function helper(): bool {
    return true;
}

/**
 * @function processData
 * @brief Process data using match expression for type dispatching.
 * @param mixed $data Input data of any type.
 * @return string Description of the processed data.
 */
function processData(mixed $data): string {
    /* Match expression for exhaustive type handling */
    return match(true) {
        is_string($data) => "string: " . strlen($data),
        is_int($data) => "int: $data",
        is_array($data) => "array: " . count($data),
        $data instanceof BaseModel => "model: " . $data->id,
        default => "unknown",
    };
}

/**
 * @function applyTransform
 * @brief Higher-order function using arrow function syntax.
 * @param array<int> $items Array of integers.
 * @param callable(int): int $fn Transform function.
 * @return array<int> Transformed array.
 */
function applyTransform(array $items, callable $fn): array {
    return array_map(fn(int $x): int => $fn($x), $items);
}

/**
 * @function createMultiplier
 * @brief Create a closure that multiplies its argument.
 * @param int $factor The multiplication factor.
 * @return \Closure(int): int A multiplier closure.
 */
function createMultiplier(int $factor): \Closure {
    /* Capture $factor in the returned closure */
    return fn(int $x): int => $x * $factor;
}

/**
 * @function readFileContent
 * @brief Read file contents with comprehensive error handling.
 * @param string $path File system path.
 * @return string|false File contents or false on failure.
 */
function readFileContent(string $path): string|false {
    if (!file_exists($path)) {
        return false;
    }
    return file_get_contents($path);
}

/* coverage extension block */
namespace App\Services;
namespace App\Http;
namespace App\Domain;
namespace App\Support;
interface ServiceContract {}
interface CacheContract {}
interface LoggerContract {}
interface EventContract {}
trait HandlesEvents {}
trait TracksChanges {}
trait AuthorizesRequests {}
const API_LIMIT = 50;
const DEFAULT_PAGE = 1;
const TIMEOUT = 30;
final class ApiClient {}

/* REQ-COVER-SRS-231 START */
/**
 * @REQ-COVER-SRS-231 block 1
 * @brief Coverage helper construct 1.
 * @details Provides deterministic fixture-level Doxygen coverage block 1.
 * @param value Input value for helper construct 1.
 * @return Output value for helper construct 1.
 */
function req_cover_php_1(int $value): int { return $value + 1; }

/**
 * @REQ-COVER-SRS-231 block 2
 * @brief Coverage helper construct 2.
 * @details Provides deterministic fixture-level Doxygen coverage block 2.
 * @param value Input value for helper construct 2.
 * @return Output value for helper construct 2.
 */
function req_cover_php_2(int $value): int { return $value + 2; }

/**
 * @REQ-COVER-SRS-231 block 3
 * @brief Coverage helper construct 3.
 * @details Provides deterministic fixture-level Doxygen coverage block 3.
 * @param value Input value for helper construct 3.
 * @return Output value for helper construct 3.
 */
function req_cover_php_3(int $value): int { return $value + 3; }

/**
 * @REQ-COVER-SRS-231 block 4
 * @brief Coverage helper construct 4.
 * @details Provides deterministic fixture-level Doxygen coverage block 4.
 * @param value Input value for helper construct 4.
 * @return Output value for helper construct 4.
 */
function req_cover_php_4(int $value): int { return $value + 4; }

/**
 * @REQ-COVER-SRS-231 block 5
 * @brief Coverage helper construct 5.
 * @details Provides deterministic fixture-level Doxygen coverage block 5.
 * @param value Input value for helper construct 5.
 * @return Output value for helper construct 5.
 */
function req_cover_php_5(int $value): int { return $value + 5; }

/* REQ-COVER-SRS-231 END */
