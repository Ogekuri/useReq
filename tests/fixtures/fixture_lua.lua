--- @file fixture_lua.lua
--- @brief Comprehensive Lua test fixture for parser validation.
--- @details Covers metatables, coroutines, closures, OOP patterns,
---          module pattern, varargs, error handling, and table constructors.
-- Single line comment
--[[ Multi-line
comment ]]

-- ── Standard functions ─────────────────────────────────────────────────

--- Compute the successor of a number.
--- @param x number The input value.
--- @return number The input incremented by one.
function globalFunc(x)
    return x + 1
end

--- Multiply a value by two with validation.
--- @param y number The input value; must be a number.
--- @return number The doubled value.
--- @raise error If y is not a number.
local function localFunc(y)
    if type(y) ~= "number" then
        error("expected number, got " .. type(y))
    end
    -- Perform the multiplication
    return y * 2
end

--- Variadic function summing all arguments.
--- @param ... number Variable number of numeric arguments.
--- @return number Sum of all provided values.
local function sumAll(...)
    local total = 0
    local args = {...}
    for _, v in ipairs(args) do
        -- Accumulate each argument
        total = total + v
    end
    return total
end

-- ── Variables and constants ────────────────────────────────────────────

--- @brief Module-level constant for retry limits.
local myVar = 42

--- @brief Configuration table with default settings.
local config = {
    debug = false,
    maxRetries = 3,
    timeout = 30.0,
}

-- ── Function assigned to variable ──────────────────────────────────────

--- Event handler for UI callbacks.
--- @param event table Event object containing type and data fields.
local handler = function(event)
    -- Dispatch based on event type
    if event.type == "click" then
        print("clicked at " .. event.x .. "," .. event.y)
    else
        print("event: " .. event.type)
    end
end

-- ── Module method pattern ──────────────────────────────────────────────

--- @class MyModule
--- @brief Table-based module using method syntax.
local MyModule = {}
MyModule.__index = MyModule

--- Create a new module instance with a name.
--- @param name string Instance identifier.
--- @return table New MyModule instance.
function MyModule.new(name)
    local self = setmetatable({}, MyModule)
    self.name = name
    self._items = {}
    return self
end

--- Get the module instance name using colon method syntax.
--- @param self table The MyModule instance.
--- @return string The instance name.
MyModule.method = function(self)
    return self.name
end

--- Add an item to the internal collection.
--- @param item any The item to store.
function MyModule:addItem(item)
    -- Append to internal list
    table.insert(self._items, item)
end

--- Get count of stored items.
--- @return number Number of items.
function MyModule:count()
    return #self._items
end

-- ── Metatable-based OOP ────────────────────────────────────────────────

--- @class Animal
--- @brief Base class using metatables for inheritance.
local Animal = {}
Animal.__index = Animal

--- Create a new Animal with a species name.
--- @param species string The animal's species.
--- @return table New Animal instance.
function Animal.new(species)
    local self = setmetatable({}, Animal)
    self.species = species
    return self
end

--- Produce the animal's sound.
--- @return string Sound description.
function Animal:speak()
    return self.species .. " says ..."
end

--- @class Dog
--- @brief Dog subclass inheriting from Animal.
local Dog = setmetatable({}, { __index = Animal })
Dog.__index = Dog

--- Create a new Dog instance.
--- @param name string The dog's name.
--- @return table New Dog instance.
function Dog.new(name)
    local self = Animal.new("Dog")
    setmetatable(self, Dog)
    self.dogName = name
    return self
end

--- Override speak for dog-specific behavior.
--- @return string The dog's vocalization.
function Dog:speak()
    return self.dogName .. " says Woof!"
end

-- ── Closure factory ────────────────────────────────────────────────────

--- Create a counter closure with step increment.
--- @param step number Increment amount per call.
--- @return function Closure returning successive counts.
local function makeCounter(step)
    local count = 0
    return function()
        -- Capture and mutate the upvalue
        count = count + step
        return count
    end
end

-- ── Coroutine ──────────────────────────────────────────────────────────

--- Generator coroutine yielding Fibonacci numbers.
--- @param limit number Maximum number of values to yield.
--- @return function Coroutine wrap function.
local function fibonacci(limit)
    return coroutine.wrap(function()
        local a, b = 0, 1
        for _ = 1, limit do
            coroutine.yield(a)
            -- Advance to next Fibonacci number
            a, b = b, a + b
        end
    end)
end

-- ── Error handling with pcall ──────────────────────────────────────────

--- Safely execute a function, catching any errors.
--- @param fn function The function to execute.
--- @param ... any Arguments to pass to fn.
--- @return boolean, any Success flag and result or error message.
local function safeCall(fn, ...)
    local ok, result = pcall(fn, ...)
    if not ok then
        -- Log error and return nil
        print("Error: " .. tostring(result))
        return false, nil
    end
    return true, result
end

-- ── Table constructor with mixed keys ──────────────────────────────────

--- @brief Complex table demonstrating all key types.
local mixedTable = {
    -- Array part
    "first",
    "second",
    -- Hash part with string keys
    name = "test",
    count = 42,
    -- Computed key
    [math.pi] = "pi",
    -- Nested table
    nested = {
        x = 1,
        y = 2,
    },
}

-- ── Iterator pattern ───────────────────────────────────────────────────

--- Create a stateful iterator over a range.
--- @param from number Start of range (inclusive).
--- @param to number End of range (inclusive).
--- @return function Iterator function.
local function range(from, to)
    local i = from - 1
    return function()
        i = i + 1
        if i <= to then
            return i
        end
        -- Implicit nil return terminates iteration
    end
end

-- REQ-COVER-SRS-231 START
-- @REQ-COVER-SRS-231 block 1
-- @brief Coverage helper construct 1.
-- @details Provides deterministic fixture-level Doxygen coverage block 1.
-- @param value Input value for helper construct 1.
-- @return Output value for helper construct 1.
function req_cover_lua_1(value)
    return value + 1
end

-- @REQ-COVER-SRS-231 block 2
-- @brief Coverage helper construct 2.
-- @details Provides deterministic fixture-level Doxygen coverage block 2.
-- @param value Input value for helper construct 2.
-- @return Output value for helper construct 2.
function req_cover_lua_2(value)
    return value + 2
end

-- @REQ-COVER-SRS-231 block 3
-- @brief Coverage helper construct 3.
-- @details Provides deterministic fixture-level Doxygen coverage block 3.
-- @param value Input value for helper construct 3.
-- @return Output value for helper construct 3.
function req_cover_lua_3(value)
    return value + 3
end

-- @REQ-COVER-SRS-231 block 4
-- @brief Coverage helper construct 4.
-- @details Provides deterministic fixture-level Doxygen coverage block 4.
-- @param value Input value for helper construct 4.
-- @return Output value for helper construct 4.
function req_cover_lua_4(value)
    return value + 4
end

-- @REQ-COVER-SRS-231 block 5
-- @brief Coverage helper construct 5.
-- @details Provides deterministic fixture-level Doxygen coverage block 5.
-- @param value Input value for helper construct 5.
-- @return Output value for helper construct 5.
function req_cover_lua_5(value)
    return value + 5
end

-- REQ-COVER-SRS-231 END
