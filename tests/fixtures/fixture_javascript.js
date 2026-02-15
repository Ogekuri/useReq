/**
 * @file fixture_javascript.js
 * @brief Comprehensive JavaScript test fixture for parser validation.
 * @details Covers classes with private fields, generators, async generators,
 *          proxies, symbols, IIFE, dynamic imports, destructuring, computed
 *          properties, and chained promise patterns.
 */
// Single line comment
/* Multi-line
   comment */
import React from 'react';
import { useState, useEffect } from 'react';

/* ── Class with private fields and static blocks ─────────────────────── */

/**
 * @class MyComponent
 * @brief React-like component with private fields and static initialization.
 */
class MyComponent {
    /** @brief Private instance counter, not accessible outside the class. */
    #instanceId;

    /** @brief Static registry of all component instances. */
    static #registry = new Map();

    /* Static initialization block (ES2022) */
    static {
        console.log('MyComponent class loaded');
    }

    /**
     * @brief Construct a new component with an optional ID.
     * @param {number} [id=0] Unique identifier for this instance.
     */
    constructor(id = 0) {
        this.#instanceId = id;
        MyComponent.#registry.set(id, this);
    }

    /**
     * @brief Render the component output.
     * @return {null} Placeholder render returning null.
     */
    render() {
        /* Delegate to internal render pipeline */
        return null;
    }

    /**
     * @brief Retrieve the private instance ID.
     * @return {number} The instance identifier.
     */
    getId() {
        return this.#instanceId;
    }

    /**
     * @brief Check if an ID exists in the static registry.
     * @param {number} id The ID to look up.
     * @return {boolean} True if the ID is registered.
     */
    static has(id) {
        return MyComponent.#registry.has(id);
    }
}

/* ── Subclass with method override ────────────────────────────────────── */

/**
 * @class EnhancedComponent
 * @extends MyComponent
 * @brief Extended component with lifecycle hooks.
 */
class EnhancedComponent extends MyComponent {
    /**
     * @brief Override render to return a div element.
     * @return {Object} A simple virtual DOM node.
     */
    render() {
        /* Call super for side effects then override output */
        super.render();
        return { type: 'div', children: [] };
    }

    /**
     * @brief Lifecycle method called after mounting.
     * @return {void}
     */
    componentDidMount() {
        console.log('mounted');
    }
}

/* ── Regular and arrow functions ──────────────────────────────────────── */

/**
 * @function greet
 * @brief Greet a person by name.
 * @param {string} name The person's name.
 * @return {string} Greeting message.
 */
function greet(name) {
    return "Hello " + name;
}

/**
 * @function fetchData
 * @brief Fetch data from the API endpoint asynchronously.
 * @return {Promise<Response>} The fetch response promise.
 */
async function fetchData() {
    /* Await the fetch and return result */
    return await fetch('/api');
}

/**
 * @function handler
 * @brief Event handler arrow function for UI events.
 * @param {Event} event The DOM event object.
 */
const handler = (event) => {
    /* Log and prevent default browser behavior */
    event.preventDefault();
    console.log(event.type);
};

/**
 * @function processItems
 * @brief Arrow function with destructuring parameter.
 * @param {{ items: Array, count: number }} param0 Destructured config.
 * @return {Array} Processed item list.
 */
const processItems = ({ items, count }) => {
    return items.slice(0, count).map(i => i.toUpperCase());
};

/* ── Constants ────────────────────────────────────────────────────────── */

/** @constant {number} MAX_SIZE Upper bound for buffer allocation. */
const MAX_SIZE = 100;

/** @constant {Symbol} PLUGIN_KEY Unique symbol for plugin registration. */
const PLUGIN_KEY = Symbol('plugin');

/* ── React HOC wrapper ────────────────────────────────────────────────── */

/**
 * @component MyWrapped
 * @brief Memoized functional component demonstrating React.memo usage.
 * @return {null} Renders nothing; serves as a parser test case.
 */
const MyWrapped = React.memo(() => {
    return null;
});

/* ── Generator function ───────────────────────────────────────────────── */

/**
 * @generator idGenerator
 * @brief Infinite generator producing sequential integer IDs.
 * @yields {number} The next unique ID.
 */
function* idGenerator() {
    let id = 0;
    while (true) {
        /* Yield incremented ID indefinitely */
        yield id++;
    }
}

/**
 * @generator rangeGenerator
 * @brief Generator yielding integers in a bounded range.
 * @param {number} start Inclusive lower bound.
 * @param {number} end Exclusive upper bound.
 * @yields {number} Each integer from start to end-1.
 */
function* rangeGenerator(start, end) {
    for (let i = start; i < end; i++) {
        yield i;
    }
}

/* ── Async generator ──────────────────────────────────────────────────── */

/**
 * @async
 * @generator asyncDataStream
 * @brief Asynchronously yield paginated API results.
 * @param {string} url Base URL for pagination.
 * @yields {Object} Each page's parsed JSON data.
 */
async function* asyncDataStream(url) {
    let page = 0;
    while (true) {
        const response = await fetch(`${url}?page=${page}`);
        const data = await response.json();
        if (data.length === 0) {
            /* No more pages — terminate stream */
            return;
        }
        yield data;
        page++;
    }
}

/* ── IIFE for isolated scope ──────────────────────────────────────────── */

/**
 * @brief Immediately invoked function expression for module initialization.
 */
const initResult = (() => {
    /* Self-contained initialization logic */
    const config = { debug: false };
    return Object.freeze(config);
})();

/* ── Proxy ────────────────────────────────────────────────────────────── */

/**
 * @function createProxy
 * @brief Create a logging proxy around any target object.
 * @param {Object} target The object to wrap with proxy traps.
 * @return {Proxy} Proxied object that logs property access.
 */
function createProxy(target) {
    return new Proxy(target, {
        get(obj, prop) {
            /* Log every property access */
            console.log(`Access: ${String(prop)}`);
            return Reflect.get(obj, prop);
        },
        set(obj, prop, value) {
            /* Log every property mutation */
            console.log(`Set: ${String(prop)} = ${value}`);
            return Reflect.set(obj, prop, value);
        },
    });
}

/* ── Computed property names ──────────────────────────────────────────── */

/**
 * @function buildDynamic
 * @brief Build an object with computed property keys.
 * @param {string} prefix Key prefix for dynamic properties.
 * @return {Object} Object with dynamically named properties.
 */
function buildDynamic(prefix) {
    return {
        [`${prefix}_name`]: 'value',
        [`${prefix}_id`]: 42,
        [Symbol.toPrimitive](hint) {
            return hint === 'string' ? prefix : 0;
        },
    };
}

/* ── Promise chain ────────────────────────────────────────────────────── */

/**
 * @function fetchAndProcess
 * @brief Demonstrate chained promise pattern with error recovery.
 * @param {string} url The resource URL to fetch.
 * @return {Promise<Object>} Processed data or fallback on error.
 */
function fetchAndProcess(url) {
    return fetch(url)
        .then(res => res.json())
        .then(data => {
            /* Transform the response payload */
            return { ...data, processed: true };
        })
        .catch(err => {
            /* Fallback on fetch failure */
            console.error(err);
            return { error: true, processed: false };
        });
}

/* ── Destructuring and defaults ───────────────────────────────────────── */

/**
 * @function configureApp
 * @brief Configure application with deep destructuring defaults.
 * @param {Object} options Configuration object with nested defaults.
 * @return {Object} Resolved configuration.
 */
function configureApp({ host = 'localhost', port = 3000, db: { url: dbUrl = 'sqlite://' } = {} } = {}) {
    return { host, port, dbUrl };
}

/* ── CommonJS require ─────────────────────────────────────────────────── */

/** @brief Load the Node.js filesystem module via CommonJS. */
const fs = require('fs');

/* ── WeakMap for private state ────────────────────────────────────────── */

/** @brief WeakMap storing private state keyed by object reference. */
const _privateState = new WeakMap();

/**
 * @function setPrivate
 * @brief Store private data associated with an object.
 * @param {Object} obj The key object.
 * @param {*} data The private data to associate.
 */
function setPrivate(obj, data) {
    _privateState.set(obj, data);
}

/* ── Dynamic import ───────────────────────────────────────────────────── */

/**
 * @function loadPlugin
 * @brief Dynamically import a module at runtime.
 * @param {string} name Module specifier to import.
 * @return {Promise<Module>} The loaded module namespace.
 */
async function loadPlugin(name) {
    /* Dynamic import for code-splitting */
    const mod = await import(`./${name}.js`);
    return mod;
}
