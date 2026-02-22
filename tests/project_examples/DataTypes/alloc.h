/**
 * @file alloc.h
 * @brief Local allocator bridge for datatypes project builds.
 */

#ifndef SRC_METAL_ALLOC_H_
#define SRC_METAL_ALLOC_H_

#include <stddef.h>
#include <stdlib.h>

/**
 * @brief Allocate a contiguous memory block.
 * @details Delegates allocation to the C standard library malloc
 * implementation.
 * @param size Number of bytes to allocate.
 * @return Pointer to allocated memory or NULL.
 */
static inline void *metal_allocate_memory(size_t size) { return malloc(size); }

/**
 * @brief Release a memory block allocated by metal_allocate_memory.
 * @details Delegates release to the C standard library free implementation.
 * @param pointer Pointer to release; NULL is allowed.
 * @return {void} No return value.
 */
static inline void metal_free_memory(void *pointer) { free(pointer); }

#endif /* SRC_METAL_ALLOC_H_ */
