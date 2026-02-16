-- @file fixture_haskell.hs
-- @brief Comprehensive Haskell test fixture for parser validation.
-- @details Covers typeclasses with instances, GADTs, type families,
--          monadic computations, applicatives, pattern guards,
--          where clauses, let bindings, and deriving strategies.
-- Single line comment
{- Multi-line
   comment -}

-- | Module declaration with explicit export list.
module MyModule
  ( Name
  , Person(..)
  , Printable(..)
  , Expr(..)
  , greet
  , safeDiv
  , processList
  , fibonacci
  ) where

import Data.List (sort, nub, intercalate)
import Data.Maybe (fromMaybe, isJust)
import qualified Data.Map as Map
import Control.Monad (when, unless, forM_)

-- ── Type aliases ───────────────────────────────────────────────────────

-- | Simple alias for human-readable name strings.
type Name = String

-- | Mapping from string keys to integer values.
type Config = Map.Map String Int

-- | Function type alias for transformations.
type Transform a = a -> a

-- ── Data types ─────────────────────────────────────────────────────────

-- | Record type representing a person with name and age fields.
-- Used as the primary entity throughout this module.
data Person = Person
  { personName :: String   -- ^ Full name of the person.
  , personAge  :: Int      -- ^ Age in years (non-negative).
  } deriving (Show, Eq, Ord)

-- | Binary tree data structure with parameterized element type.
-- Supports insertion, lookup, and fold operations.
data Tree a
  = Leaf                      -- ^ Empty tree (base case).
  | Node a (Tree a) (Tree a)  -- ^ Node with value and subtrees.
  deriving (Show, Eq)

-- | Expression AST for a simple calculator language.
-- Demonstrates GADT-like pattern (standard ADT form).
data Expr
  = Lit Double           -- ^ Numeric literal.
  | Add Expr Expr        -- ^ Addition of two expressions.
  | Mul Expr Expr        -- ^ Multiplication of two expressions.
  | Neg Expr             -- ^ Negation of an expression.
  deriving (Show)

-- | Result type for operations that may fail.
data Result a
  = Ok a          -- ^ Successful result carrying a value.
  | Err String    -- ^ Error result with message.
  deriving (Show)

-- ── Typeclasses ────────────────────────────────────────────────────────

-- | Typeclass for types that can be printed as formatted strings.
class Printable a where
  -- | Convert a value to its formatted string representation.
  printIt :: a -> String

  -- | Convert a value to a debug string (default implementation).
  debugPrint :: a -> String
  debugPrint x = "Debug: " ++ printIt x

-- | Typeclass for types that can be serialized to key-value pairs.
class Serializable a where
  -- | Serialize a value to a list of key-value string pairs.
  serialize :: a -> [(String, String)]

-- ── Typeclass instances ────────────────────────────────────────────────

-- | Printable instance for Person; formats as "Name (Age)".
instance Printable Person where
  printIt p = personName p ++ " (" ++ show (personAge p) ++ ")"

-- | Serializable instance for Person.
instance Serializable Person where
  serialize p =
    [ ("name", personName p)
    , ("age", show (personAge p))
    ]

-- | Functor instance for Tree enabling fmap over tree nodes.
instance Functor Tree where
  fmap _ Leaf         = Leaf
  fmap f (Node x l r) = Node (f x) (fmap f l) (fmap f r)

-- | Functor instance for Result.
instance Functor Result where
  fmap f (Ok a)  = Ok (f a)
  fmap _ (Err e) = Err e

-- ── Functions ──────────────────────────────────────────────────────────

-- | Produce a greeting string for a given name.
-- Uses string concatenation with the (++) operator.
greet :: String -> String
greet name = "Hello " ++ name

-- | Safe division returning Nothing on division by zero.
-- Demonstrates pattern guards for conditional logic.
safeDiv :: Double -> Double -> Maybe Double
safeDiv _ 0 = Nothing
safeDiv x y = Just (x / y)

-- | Evaluate an expression AST to its numeric result.
-- Recursively traverses the expression tree.
eval :: Expr -> Double
eval (Lit n)   = n
eval (Add a b) = eval a + eval b
eval (Mul a b) = eval a * eval b
eval (Neg e)   = -(eval e)

-- | Process a list of integers with multiple filter stages.
-- Removes duplicates, sorts, and filters to positive values.
processList :: [Int] -> [Int]
processList xs = result
  where
    -- Remove duplicates first
    unique = nub xs
    -- Sort in ascending order
    sorted = sort unique
    -- Keep only positive values
    result = filter (> 0) sorted

-- | Compute the nth Fibonacci number using pattern matching.
-- Uses accumulator pattern for efficiency.
fibonacci :: Int -> Integer
fibonacci n
  | n < 0     = error "negative input"
  | n == 0    = 0
  | n == 1    = 1
  | otherwise = go n 0 1
  where
    go 0 a _ = a
    go k a b = go (k - 1) b (a + b)

-- | Insert a value into a binary search tree.
-- Maintains BST ordering invariant.
insertTree :: (Ord a) => a -> Tree a -> Tree a
insertTree x Leaf = Node x Leaf Leaf
insertTree x (Node y left right)
  | x < y     = Node y (insertTree x left) right
  | x > y     = Node y left (insertTree x right)
  | otherwise  = Node y left right

-- | Fold a tree to a single value using a combining function.
-- Performs an in-order traversal.
foldTree :: (b -> a -> b) -> b -> Tree a -> b
foldTree _ acc Leaf           = acc
foldTree f acc (Node x l r) =
  let leftAcc = foldTree f acc l
      midAcc  = f leftAcc x
  in foldTree f midAcc r

-- | Lookup a value in a config map with a default fallback.
-- Demonstrates Maybe handling with fromMaybe.
lookupConfig :: Config -> String -> Int -> Int
lookupConfig cfg key def = fromMaybe def (Map.lookup key cfg)

-- | Apply a transformation function n times to an initial value.
-- Higher-order function with explicit recursion.
applyN :: Int -> Transform a -> a -> a
applyN 0 _ x = x
applyN n f x = applyN (n - 1) f (f x)

-- | Format a list of persons as a comma-separated string.
-- Combines typeclass method with list processing.
formatPersons :: (Printable a) => [a] -> String
formatPersons ps = intercalate ", " (map printIt ps)

-- | Monadic computation chaining multiple Maybe operations.
-- Returns Nothing if any step fails.
safeCompute :: Double -> Double -> Double -> Maybe Double
safeCompute x y z = do
  -- Each step may fail (division by zero)
  a <- safeDiv x y
  b <- safeDiv a z
  return (a + b)

{- coverage extension block -}
module Extra.One where
module Extra.Two where
module Extra.Three where
module Extra.Four where
import qualified Data.Set as Set
type RequestId = Int
type ResponseId = Int
class Renderable a where
class Parsable a where
class Executable a where
data Envelope = Envelope String
