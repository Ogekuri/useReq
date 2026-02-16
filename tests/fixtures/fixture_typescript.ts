/**
 * @file fixture_typescript.ts
 * @brief Comprehensive TypeScript test fixture for parser validation.
 * @details Covers conditional types, mapped types, template literal types,
 *          satisfies operator, overload signatures, discriminated unions,
 *          module augmentation, decorators, generic constraints, and utility types.
 */
// Single line comment
/* Multi-line comment */
import { Component } from 'react';
import type { ReactNode } from 'react';

/* ── Interfaces ───────────────────────────────────────────────────────── */

/**
 * @interface User
 * @brief Core user entity with identity fields.
 */
interface User {
    /** @brief Display name of the user. */
    name: string;
    /** @brief Age in years; must be non-negative. */
    age: number;
    /** @brief Optional email address. */
    email?: string;
    /** @brief Read-only unique identifier. */
    readonly id: string;
}

/**
 * @interface Repository
 * @brief Generic CRUD repository with type parameter.
 * @tparam T Entity type managed by this repository.
 */
interface Repository<T> {
    /** @brief Find an entity by its ID. */
    findById(id: string): Promise<T | null>;
    /** @brief Persist an entity, returning the saved version. */
    save(entity: T): Promise<T>;
    /** @brief Delete an entity by ID. */
    delete(id: string): Promise<boolean>;
}

/**
 * @interface Serializable
 * @brief Marks objects that can be serialized to JSON.
 */
interface Serializable {
    /** @brief Convert to a JSON-compatible string. */
    toJSON(): string;
}

/* ── Type aliases and utility types ───────────────────────────────────── */

/** @brief Union type for values that can be string or number. */
type StringOrNumber = string | number;

/** @brief Mapped type making all properties of T optional and readonly. */
type DeepReadonly<T> = {
    readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

/** @brief Conditional type extracting array element type. */
type Unwrap<T> = T extends Array<infer U> ? U : T;

/** @brief Template literal type for CSS pixel values. */
type PixelValue = `${number}px`;

/** @brief Discriminated union tag for API responses. */
type ApiResponse<T> =
    | { status: 'success'; data: T }
    | { status: 'error'; message: string }
    | { status: 'loading' };

/** @brief Extract keys of T whose values extend a given type. */
type KeysOfType<T, V> = {
    [K in keyof T]: T[K] extends V ? K : never;
}[keyof T];

/* ── Enums ────────────────────────────────────────────────────────────── */

/**
 * @enum Direction
 * @brief Const enum for cardinal directions (inlined at compile time).
 */
const enum Direction {
    Up = 'UP',
    Down = 'DOWN',
    Left = 'LEFT',
    Right = 'RIGHT',
}

/**
 * @enum Color
 * @brief Regular enum with numeric values for color channels.
 */
enum Color {
    /** @brief Red channel identifier. */
    Red,
    /** @brief Blue channel identifier. */
    Blue,
    /** @brief Green channel, explicitly set to 10. */
    Green = 10,
}

/**
 * @enum HttpStatus
 * @brief String enum mapping HTTP status codes.
 */
enum HttpStatus {
    OK = '200',
    NotFound = '404',
    ServerError = '500',
}

/* ── Abstract class ───────────────────────────────────────────────────── */

/**
 * @class Base
 * @brief Abstract base class with template method pattern.
 */
export abstract class Base {
    /**
     * @brief Abstract render method to be implemented by subclasses.
     * @return void
     */
    abstract render(): void;

    /**
     * @brief Template method calling render with pre/post hooks.
     */
    execute(): void {
        /* Pre-render hook */
        console.log('before render');
        this.render();
        /* Post-render hook */
        console.log('after render');
    }
}

/* ── Concrete class with generics ─────────────────────────────────────── */

/**
 * @class Derived
 * @extends Base
 * @brief Concrete implementation with typed value storage.
 */
class Derived extends Base {
    /** @brief Stored numeric value. */
    value: number = 0;

    /** @brief Optional label for display. */
    label?: string;

    /**
     * @brief Render the value to console output.
     */
    render(): void {
        console.log(this.value);
    }
}

/**
 * @class TypedContainer
 * @brief Generic container with constraint on Serializable.
 * @tparam T Must implement Serializable interface.
 */
class TypedContainer<T extends Serializable> {
    /** @brief Internal array storage for items. */
    private items: T[] = [];

    /**
     * @brief Add an item to the container.
     * @param item Item conforming to Serializable.
     */
    add(item: T): void {
        this.items.push(item);
    }

    /**
     * @brief Serialize all items to a JSON array string.
     * @return JSON string of all serialized items.
     */
    toJSON(): string {
        return `[${this.items.map(i => i.toJSON()).join(',')}]`;
    }

    /**
     * @brief Find first item matching a predicate.
     * @param predicate Test function applied to each item.
     * @return The first matching item or undefined.
     */
    find(predicate: (item: T) => boolean): T | undefined {
        for (const item of this.items) {
            if (predicate(item)) {
                return item;
            }
        }
        return undefined;
    }
}

/* ── Class implementing multiple interfaces ───────────────────────────── */

/**
 * @class UserEntity
 * @implements User, Serializable
 * @brief Full user entity implementing both User and Serializable.
 */
class UserEntity implements User, Serializable {
    readonly id: string;
    name: string;
    age: number;

    constructor(id: string, name: string, age: number) {
        this.id = id;
        this.name = name;
        this.age = age;
    }

    /**
     * @brief Serialize user to JSON string.
     * @return JSON representation of the user.
     */
    toJSON(): string {
        return JSON.stringify({ id: this.id, name: this.name, age: this.age });
    }
}

/* ── Functions ────────────────────────────────────────────────────────── */

/**
 * @function greet
 * @brief Greet a person by name with type-safe parameter.
 * @param name The person's name to display.
 */
export function greet(name: string): void {
    console.log(`Hello, ${name}`);
}

/* ── Function overloads ───────────────────────────────────────────────── */

/**
 * @function parse
 * @brief Parse input with overloaded signatures for type safety.
 * @overload Parse a string input into a number.
 * @overload Parse a number input into a string.
 */
function parse(input: string): number;
function parse(input: number): string;
function parse(input: string | number): string | number {
    if (typeof input === 'string') {
        return parseInt(input, 10);
    }
    return input.toString();
}

/* ── Arrow function with type annotation ──────────────────────────────── */

/**
 * @function add
 * @brief Add one to a number (arrow function syntax).
 * @param a The input number.
 * @return The incremented value.
 */
const add = (a: number): number => a + 1;

/**
 * @function transform
 * @brief Generic transform function with constraint.
 * @tparam T Must have a toString method.
 * @param value Input value to transform.
 * @return String representation of the value.
 */
const transform = <T extends { toString(): string }>(value: T): string => {
    return value.toString();
};

/* ── Async function with generic return ───────────────────────────────── */

/**
 * @function fetchEntity
 * @brief Fetch and deserialize a typed entity from an API.
 * @tparam T The expected response entity type.
 * @param url Endpoint URL.
 * @return Promise resolving to the typed entity.
 */
async function fetchEntity<T>(url: string): Promise<T> {
    const response = await fetch(url);
    /* Parse JSON and cast to expected type */
    return response.json() as Promise<T>;
}

/* ── Namespace ────────────────────────────────────────────────────────── */

/**
 * @namespace MyNS
 * @brief Namespace grouping related constants and helpers.
 */
export namespace MyNS {
    /** @brief Exported constant within namespace. */
    export const x = 1;

    /**
     * @brief Helper function scoped to namespace.
     * @param val Numeric input to double.
     * @return The doubled value.
     */
    export function double(val: number): number {
        return val * 2;
    }
}

/* ── Module declaration ───────────────────────────────────────────────── */

/**
 * @module MyMod
 * @brief Ambient module declaration for external library typings.
 */
declare module MyMod {
    /** @brief Version string exposed by the external module. */
    export const version: string;
}

/* ── Decorator ────────────────────────────────────────────────────────── */

/**
 * @class Decorated
 * @brief Class using a decorator annotation.
 */
@Component
class Decorated {
    /** @brief Template string for rendering. */
    template: string = '<div></div>';
}

/* ── Type guards and narrowing ────────────────────────────────────────── */

/**
 * @function isUser
 * @brief Type guard narrowing unknown to User interface.
 * @param value Unknown input to validate.
 * @return True if value conforms to User shape.
 */
function isUser(value: unknown): value is User {
    if (typeof value !== 'object' || value === null) {
        return false;
    }
    const obj = value as Record<string, unknown>;
    return typeof obj.name === 'string' && typeof obj.age === 'number';
}

/* ── Satisfies operator (TS 4.9) ──────────────────────────────────────── */

/**
 * @brief Configuration validated with satisfies for type checking
 *        without widening the inferred type.
 */
const config = {
    width: '100px' as PixelValue,
    height: '200px' as PixelValue,
} satisfies Record<string, PixelValue>;

/* ── Mapped type function ─────────────────────────────────────────────── */

/**
 * @function makeOptional
 * @brief Convert all properties of an object to optional at runtime.
 * @tparam T Source object type.
 * @param obj The source object.
 * @return A partial copy of the object.
 */
function makeOptional<T extends object>(obj: T): Partial<T> {
    return { ...obj };
}

/* coverage extension block */
import { Injectable } from 'inversify';
import { Observable } from 'rxjs';
import { FC } from 'react';
@injectable
@sealed
@track
@memoized
interface CacheEntry { key: string; value: string }
export interface Runner { run(): Promise<void> }
enum ModeTs { Fast, Safe }
enum StatusTs { Ready, Busy }
namespace ExtNSOne { export const v = 1; }
namespace ExtNSTwo { export const v = 2; }
namespace ExtNSThree { export const v = 3; }
namespace ExtNSFour { export const v = 4; }
declare module ExtOne { export const one: number; }
module ExtTwo { export const two = 2; }
module ExtThree { export const three = 3; }
module ExtFour { export const four = 4; }
