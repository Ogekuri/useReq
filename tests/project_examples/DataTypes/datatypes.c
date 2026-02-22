/**
 * @file datatypes.c
 * @brief Datatypes module implementation for container and graph routines.
 * @details Implements stack, fifo, buffer, heap, queue, bst, and graph APIs
 * with pointer-based payload semantics and callback-driven ordering/weight
 * policies.
 */

// ******************************* DATATYPES.C *********************************
#include "datatypes.h"
#include "datadefine.h"
#include <stdlib.h>
#include <string.h>

// ******************************* copy a memory block **********************
/**
 * @brief Execute key_copy operation.
 * @details Implements the key_copy routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in] key {const void *key} Parameter consumed by key_copy.
 * @param[in] key_size {size_t key_size} Parameter consumed by key_copy.
 * @return {void *} Return value produced by key_copy.
 */
void *key_copy(const void *key, size_t key_size) {
  void *key_temp;
  key_temp = metal_allocate_memory(key_size);
  memcpy(key_temp, key, key_size);
  return (key_temp);
}
// ------------------------------- move a memory block ----------------------
/**
 * @brief Execute key_move operation.
 * @details Implements the key_move routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] key_dest {void *key_dest} Parameter consumed by key_move.
 * @param[in,out] key_surce {void *key_surce} Parameter consumed by key_move.
 * @param[in] key_size {size_t key_size} Parameter consumed by key_move.
 * @return {void *} Return value produced by key_move.
 */
void *key_move(void *key_dest, void *key_surce, size_t key_size) {
  memcpy(key_dest, key_surce, key_size);
  metal_free_memory(key_surce);
  return (key_dest);
}
// ******************************* stack insert key *************************
/**
 * @brief Execute stack_insert_key operation.
 * @details Implements the stack_insert_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] stack {t_stack **stack} Parameter consumed by
 * stack_insert_key.
 * @param[in,out] key {void *key} Parameter consumed by stack_insert_key.
 * @return {void *} Return value produced by stack_insert_key.
 */
void *stack_insert_key(t_stack **stack, void *key) {
  t_stack_cell *cell;

  if (key != NULL) {
    if ((*stack) == NULL) {
      (*stack) = (t_stack *)metal_allocate_memory(sizeof(t_stack));
      (*stack)->head =
          (t_stack_cell *)metal_allocate_memory(sizeof(t_stack_cell));
      ((*stack)->head)->next = NULL;
      cell = (*stack)->head;
    } else {
      cell = (t_stack_cell *)metal_allocate_memory(sizeof(t_stack_cell));
      cell->next = ((*stack)->head);
      ((*stack)->head) = cell;
    }
    ((*stack)->head)->key = key;
    return (cell->key);
  }
  return (NULL);
};
// ------------------------------- stack extract key ------------------------
/**
 * @brief Execute stack_extract_key operation.
 * @details Implements the stack_extract_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] stack {t_stack **stack} Parameter consumed by
 * stack_extract_key.
 * @return {void *} Return value produced by stack_extract_key.
 */
void *stack_extract_key(t_stack **stack) {
  if (*stack != NULL) {
    t_stack_cell *cell = NULL;
    void *key = NULL;
    if (((*stack)->head)->next != NULL) {
      key = ((*stack)->head)->key;
      cell = (*stack)->head;
      (*stack)->head = ((*stack)->head)->next;
      metal_free_memory(cell);
    } else {
      key = ((*stack)->head)->key;
      metal_free_memory((*stack)->head);
      metal_free_memory(*stack);
      (*stack) = NULL;
    }
    return (key);
  }
  return (NULL);
};
// ------------------------------- stack insert -----------------------------
/**
 * @brief Execute stack_insert operation.
 * @details Implements the stack_insert routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] stack {t_stack **stack} Parameter consumed by stack_insert.
 * @param[in] key {const void *key} Parameter consumed by stack_insert.
 * @param[in] key_size {size_t key_size} Parameter consumed by stack_insert.
 * @return {int} Return value produced by stack_insert.
 */
int stack_insert(t_stack **stack, const void *key, size_t key_size) {
  if (stack_insert_key(stack, key_copy(key, key_size)) != NULL)
    return (DATA_OK);
  return (DATA_ERROR);
};
// ------------------------------- stack extract ----------------------------
/**
 * @brief Execute stack_extract operation.
 * @details Implements the stack_extract routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] stack {t_stack **stack} Parameter consumed by stack_extract.
 * @param[in,out] key {void *key} Parameter consumed by stack_extract.
 * @param[in] key_size {size_t key_size} Parameter consumed by stack_extract.
 * @return {int} Return value produced by stack_extract.
 */
int stack_extract(t_stack **stack, void *key, size_t key_size) {
  if (*stack != NULL) {
    void *key_temp = stack_extract_key(stack);
    if (key_temp != NULL) {
      key_move(key, key_temp, key_size);
      return (DATA_OK);
    }
  }
  return (DATA_ERROR);
};
// ******************************* fifo insert key **************************
/**
 * @brief Execute fifo_insert_key operation.
 * @details Implements the fifo_insert_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] fifo {t_fifo **fifo} Parameter consumed by fifo_insert_key.
 * @param[in,out] key {void *key} Parameter consumed by fifo_insert_key.
 * @return {void *} Return value produced by fifo_insert_key.
 */
void *fifo_insert_key(t_fifo **fifo, void *key) {
  t_fifo_cell *cell;

  if (key != NULL) {
    cell = (t_fifo_cell *)metal_allocate_memory(sizeof(t_fifo_cell));
    if (*fifo == NULL) {
      cell->next = NULL;
      (*fifo) = (t_fifo *)metal_allocate_memory(sizeof(t_fifo));
      ((*fifo)->tail) = cell;
    } else {
      cell->next = (*fifo)->head;
      ((cell->next)->prev) = cell;
    }
    (*fifo)->head = cell;
    cell->prev = NULL;
    cell->key = key;
    return (cell->key);
  }
  return (NULL);
};
// ------------------------------- fifo extract key -------------------------
/**
 * @brief Execute fifo_extract_key operation.
 * @details Implements the fifo_extract_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] fifo {t_fifo **fifo} Parameter consumed by fifo_extract_key.
 * @return {void *} Return value produced by fifo_extract_key.
 */
void *fifo_extract_key(t_fifo **fifo) {
  t_fifo_cell *cell;
  void *key = NULL;

  if (*fifo != NULL) {
    if (((*fifo)->head) == ((*fifo)->tail)) {
      cell = (*fifo)->tail;
      metal_free_memory(*fifo);
      *fifo = NULL;
    } else {
      cell = (*fifo)->tail;
      ((*fifo)->tail) = cell->prev;
      ((cell->prev)->next) = NULL;
    }
    key = cell->key;
    metal_free_memory(cell);
    return (key);
  }
  return (NULL);
};
// ------------------------------- fifo insert ------------------------------
/**
 * @brief Execute fifo_insert operation.
 * @details Implements the fifo_insert routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] fifo {t_fifo **fifo} Parameter consumed by fifo_insert.
 * @param[in] key {const void *key} Parameter consumed by fifo_insert.
 * @param[in] key_size {size_t key_size} Parameter consumed by fifo_insert.
 * @return {int} Return value produced by fifo_insert.
 */
int fifo_insert(t_fifo **fifo, const void *key, size_t key_size) {
  if (fifo_insert_key(fifo, key_copy(key, key_size)) != NULL)
    return (DATA_OK);
  return (DATA_ERROR);
};
// ------------------------------- fifo extract -----------------------------
/**
 * @brief Execute fifo_extract operation.
 * @details Implements the fifo_extract routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] fifo {t_fifo **fifo} Parameter consumed by fifo_extract.
 * @param[in,out] key {void *key} Parameter consumed by fifo_extract.
 * @param[in] key_size {size_t key_size} Parameter consumed by fifo_extract.
 * @return {int} Return value produced by fifo_extract.
 */
int fifo_extract(t_fifo **fifo, void *key, size_t key_size) {
  if (*fifo != NULL) {
    void *key_temp = fifo_extract_key(fifo);
    if (key_temp != NULL) {
      key_move(key, key_temp, key_size);
      return (DATA_OK);
    }
  }
  return (DATA_ERROR);
};
// ******************************* stack to fifo ****************************
/**
 * @brief Execute stack_to_fifo operation.
 * @details Implements the stack_to_fifo routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] fifo {t_fifo **fifo} Parameter consumed by stack_to_fifo.
 * @param[in,out] stack {t_stack **stack} Parameter consumed by stack_to_fifo.
 * @return {int} Return value produced by stack_to_fifo.
 */
int stack_to_fifo(t_fifo **fifo, t_stack **stack) {
  while ((*stack) != NULL)
    fifo_insert_key(fifo, stack_extract_key(stack));
  if ((*fifo) != NULL)
    return (DATA_OK);
  return (DATA_ERROR);
}
// ------------------------------- fifo to stack ----------------------------
/**
 * @brief Execute fifo_to_stack operation.
 * @details Implements the fifo_to_stack routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] stack {t_stack **stack} Parameter consumed by fifo_to_stack.
 * @param[in,out] fifo {t_fifo **fifo} Parameter consumed by fifo_to_stack.
 * @return {int} Return value produced by fifo_to_stack.
 */
int fifo_to_stack(t_stack **stack, t_fifo **fifo) {
  while ((*fifo) != NULL)
    stack_insert_key(stack, fifo_extract_key(fifo));
  if ((*stack) != NULL)
    return (DATA_OK);
  return (DATA_ERROR);
}
// ******************************* buffer size ******************************
/**
 * @brief Execute buffer_size operation.
 * @details Implements the buffer_size routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by buffer_size.
 * @return {long int} Return value produced by buffer_size.
 */
long int buffer_size(t_buffer **buffer) {
  if ((*buffer) != NULL)
    return ((*buffer)->counter);
  return (DATA_ERROR);
}
// ------------------------------- buffer get head key -------------------
/**
 * @brief Execute buffer_get_head_key operation.
 * @details Implements the buffer_get_head_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_get_head_key.
 * @return {void *} Return value produced by buffer_get_head_key.
 */
void *buffer_get_head_key(t_buffer **buffer) {
  if ((*buffer) != NULL)
    return ((*buffer)->head->key);
  return (NULL);
}
// ------------------------------- buffer get tail key -------------------
/**
 * @brief Execute buffer_get_tail_key operation.
 * @details Implements the buffer_get_tail_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_get_tail_key.
 * @return {void *} Return value produced by buffer_get_tail_key.
 */
void *buffer_get_tail_key(t_buffer **buffer) {
  if ((*buffer) != NULL)
    return ((*buffer)->tail->key);
  return (NULL);
}
// ------------------------------- buffer insert head key -------------------
/**
 * @brief Execute buffer_insert_head_key operation.
 * @details Implements the buffer_insert_head_key routine in the datatypes
 * module context. Complexity depends on container cardinality and delegated
 * callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_insert_head_key.
 * @param[in,out] key {void *key} Parameter consumed by buffer_insert_head_key.
 * @return {void *} Return value produced by buffer_insert_head_key.
 */
void *buffer_insert_head_key(t_buffer **buffer, void *key) {
  t_buffer_cell *cell;

  if (key != NULL) {
    cell = (t_buffer_cell *)metal_allocate_memory(sizeof(t_buffer_cell));
    if (*buffer == NULL) {
      cell->next = cell;
      cell->prev = cell;
      (*buffer) = (t_buffer *)metal_allocate_memory(sizeof(t_buffer));
      ((*buffer)->head) = cell;
      ((*buffer)->tail) = cell;
      (*buffer)->counter = 1;
    } else {
      cell->prev = (*buffer)->head;
      cell->next = ((*buffer)->head)->next;
      (cell->next)->prev = cell;
      (cell->prev)->next = cell;
      (*buffer)->head = cell;
      (*buffer)->counter++;
    }
    cell->key = key;
    return (cell->key);
  }
  return (NULL);
};
// ------------------------------- buffer insert tail key -------------------
/**
 * @brief Execute buffer_insert_tail_key operation.
 * @details Implements the buffer_insert_tail_key routine in the datatypes
 * module context. Complexity depends on container cardinality and delegated
 * callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_insert_tail_key.
 * @param[in,out] key {void *key} Parameter consumed by buffer_insert_tail_key.
 * @return {void *} Return value produced by buffer_insert_tail_key.
 */
void *buffer_insert_tail_key(t_buffer **buffer, void *key) {
  t_buffer_cell *cell;

  if (key != NULL) {
    cell = (t_buffer_cell *)metal_allocate_memory(sizeof(t_buffer_cell));
    if (*buffer == NULL) {
      cell->next = cell;
      cell->prev = cell;
      (*buffer) = (t_buffer *)metal_allocate_memory(sizeof(t_buffer));
      ((*buffer)->head) = cell;
      ((*buffer)->tail) = cell;
      (*buffer)->counter = 1;
    } else {
      cell->next = (*buffer)->tail;
      cell->prev = ((*buffer)->tail)->prev;
      (cell->next)->prev = cell;
      (cell->prev)->next = cell;
      (*buffer)->tail = cell;
      (*buffer)->counter++;
    }
    cell->key = key;
    return (cell->key);
  }
  return (NULL);
};
// ------------------------------- buffer extract head key ------------------
/**
 * @brief Execute buffer_extract_head_key operation.
 * @details Implements the buffer_extract_head_key routine in the datatypes
 * module context. Complexity depends on container cardinality and delegated
 * callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_extract_head_key.
 * @return {void *} Return value produced by buffer_extract_head_key.
 */
void *buffer_extract_head_key(t_buffer **buffer) {
  t_buffer_cell *cell;
  void *key = NULL;

  if (*buffer != NULL) {
    if (((*buffer)->head) == ((*buffer)->tail)) {
      if ((*buffer)->head == ((*buffer)->head)->next) {
        cell = (*buffer)->head;
        metal_free_memory(*buffer);
        *buffer = NULL;
      } else {
        cell = (*buffer)->head;
        (cell->prev)->next = cell->next;
        (cell->next)->prev = cell->prev;
        ((*buffer)->head) = cell->prev;
        ((*buffer)->tail) = cell->next;
        (*buffer)->counter--;
      }
    } else {
      cell = (*buffer)->head;
      (cell->prev)->next = cell->next;
      (cell->next)->prev = cell->prev;
      ((*buffer)->head) = cell->prev;
      (*buffer)->counter--;
    }
    key = cell->key;
    metal_free_memory(cell);
    return (key);
  }
  return (NULL);
};
// ------------------------------- buffer extract tail key ------------------
/**
 * @brief Execute buffer_extract_tail_key operation.
 * @details Implements the buffer_extract_tail_key routine in the datatypes
 * module context. Complexity depends on container cardinality and delegated
 * callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_extract_tail_key.
 * @return {void *} Return value produced by buffer_extract_tail_key.
 */
void *buffer_extract_tail_key(t_buffer **buffer) {
  t_buffer_cell *cell;
  void *key = NULL;

  if (*buffer != NULL) {
    if (((*buffer)->head) == ((*buffer)->tail)) {
      if ((*buffer)->tail == ((*buffer)->tail)->prev) {
        cell = (*buffer)->tail;
        metal_free_memory(*buffer);
        *buffer = NULL;
      } else {
        cell = (*buffer)->tail;
        (cell->prev)->next = cell->next;
        (cell->next)->prev = cell->prev;
        ((*buffer)->head) = cell->prev;
        ((*buffer)->tail) = cell->next;
        (*buffer)->counter--;
      }
    } else {
      cell = (*buffer)->tail;
      (cell->prev)->next = cell->next;
      (cell->next)->prev = cell->prev;
      ((*buffer)->tail) = cell->next;
      (*buffer)->counter--;
    }
    key = cell->key;
    metal_free_memory(cell);
    return (key);
  }
  return (NULL);
};
// ------------------------------- buffer insert head -----------------------
/**
 * @brief Execute buffer_insert_head operation.
 * @details Implements the buffer_insert_head routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_insert_head.
 * @param[in] key {const void *key} Parameter consumed by buffer_insert_head.
 * @param[in] key_size {size_t key_size} Parameter consumed by
 * buffer_insert_head.
 * @return {int} Return value produced by buffer_insert_head.
 */
int buffer_insert_head(t_buffer **buffer, const void *key, size_t key_size) {
  if (buffer_insert_head_key(buffer, key_copy(key, key_size)) != NULL)
    return (DATA_OK);
  return (DATA_ERROR);
};
// ------------------------------- buffer insert tail -----------------------
/**
 * @brief Execute buffer_insert_tail operation.
 * @details Implements the buffer_insert_tail routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_insert_tail.
 * @param[in] key {const void *key} Parameter consumed by buffer_insert_tail.
 * @param[in] key_size {size_t key_size} Parameter consumed by
 * buffer_insert_tail.
 * @return {int} Return value produced by buffer_insert_tail.
 */
int buffer_insert_tail(t_buffer **buffer, const void *key, size_t key_size) {
  if (buffer_insert_tail_key(buffer, key_copy(key, key_size)) != NULL)
    return (DATA_OK);
  return (DATA_ERROR);
};
// ------------------------------- buffer extract head ----------------------
/**
 * @brief Execute buffer_extract_head operation.
 * @details Implements the buffer_extract_head routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_extract_head.
 * @param[in,out] key {void *key} Parameter consumed by buffer_extract_head.
 * @param[in] key_size {size_t key_size} Parameter consumed by
 * buffer_extract_head.
 * @return {int} Return value produced by buffer_extract_head.
 */
int buffer_extract_head(t_buffer **buffer, void *key, size_t key_size) {
  if (*buffer != NULL) {
    void *key_temp = buffer_extract_head_key(buffer);
    if (key_temp != NULL) {
      key_move(key, key_temp, key_size);
      return (DATA_OK);
    }
  }
  return (DATA_ERROR);
};
// ------------------------------- buffer extract tail ----------------------
/**
 * @brief Execute buffer_extract_tail operation.
 * @details Implements the buffer_extract_tail routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_extract_tail.
 * @param[in,out] key {void *key} Parameter consumed by buffer_extract_tail.
 * @param[in] key_size {size_t key_size} Parameter consumed by
 * buffer_extract_tail.
 * @return {int} Return value produced by buffer_extract_tail.
 */
int buffer_extract_tail(t_buffer **buffer, void *key, size_t key_size) {
  if (*buffer != NULL) {
    void *key_temp = buffer_extract_tail_key(buffer);
    if (key_temp != NULL) {
      key_move(key, key_temp, key_size);
      return (DATA_OK);
    }
  }
  return (DATA_ERROR);
};
// ------------------------------- buffer read head next key ----------------
/**
 * @brief Execute buffer_read_head_next_key operation.
 * @details Implements the buffer_read_head_next_key routine in the datatypes
 * module context. Complexity depends on container cardinality and delegated
 * callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_read_head_next_key.
 * @return {void *} Return value produced by buffer_read_head_next_key.
 */
void *buffer_read_head_next_key(t_buffer **buffer) {
  if ((*buffer) != NULL) {
    (*buffer)->head = ((*buffer)->head)->next;
    return ((((*buffer)->head)->prev)->key);
  }
  return (NULL);
};
// ------------------------------- buffer read head key ----------------
/**
 * @brief Execute buffer_read_head_key operation.
 * @details Implements the buffer_read_head_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_read_head_key.
 * @return {void *} Return value produced by buffer_read_head_key.
 */
void *buffer_read_head_key(t_buffer **buffer) {
  if ((*buffer) != NULL) {
    return (((*buffer)->head)->key);
  }
  return (NULL);
};
// ------------------------------- buffer read head prev key ----------------
/**
 * @brief Execute buffer_read_head_prev_key operation.
 * @details Implements the buffer_read_head_prev_key routine in the datatypes
 * module context. Complexity depends on container cardinality and delegated
 * callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_read_head_prev_key.
 * @return {void *} Return value produced by buffer_read_head_prev_key.
 */
void *buffer_read_head_prev_key(t_buffer **buffer) {
  if ((*buffer) != NULL) {
    (*buffer)->head = ((*buffer)->head)->prev;
    return ((((*buffer)->head)->next)->key);
  }
  return (NULL);
};
// ------------------------------- buffer read tail next key ----------------
/**
 * @brief Execute buffer_read_tail_next_key operation.
 * @details Implements the buffer_read_tail_next_key routine in the datatypes
 * module context. Complexity depends on container cardinality and delegated
 * callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_read_tail_next_key.
 * @return {void *} Return value produced by buffer_read_tail_next_key.
 */
void *buffer_read_tail_next_key(t_buffer **buffer) {
  if ((*buffer) != NULL) {
    (*buffer)->tail = ((*buffer)->tail)->next;
    return ((((*buffer)->tail)->prev)->key);
  }
  return (NULL);
};
// ------------------------------- buffer read tail prev key ----------------
/**
 * @brief Execute buffer_read_tail_prev_key operation.
 * @details Implements the buffer_read_tail_prev_key routine in the datatypes
 * module context. Complexity depends on container cardinality and delegated
 * callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_read_tail_prev_key.
 * @return {void *} Return value produced by buffer_read_tail_prev_key.
 */
void *buffer_read_tail_prev_key(t_buffer **buffer) {
  if ((*buffer) != NULL) {
    (*buffer)->tail = ((*buffer)->tail)->prev;
    return ((((*buffer)->tail)->next)->key);
  }
  return (NULL);
};
// ------------------------------- buffer read head next --------------------
/**
 * @brief Execute buffer_read_head_next operation.
 * @details Implements the buffer_read_head_next routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_read_head_next.
 * @param[in,out] key {void *key} Parameter consumed by buffer_read_head_next.
 * @param[in] key_size {size_t key_size} Parameter consumed by
 * buffer_read_head_next.
 * @return {int} Return value produced by buffer_read_head_next.
 */
int buffer_read_head_next(t_buffer **buffer, void *key, size_t key_size) {
  if (*buffer != NULL) {
    const void *key_temp = buffer_read_head_next_key(buffer);
    if (key_temp != NULL)
      memcpy(key, key_temp, key_size);
    return (DATA_OK);
  }
  return (DATA_ERROR);
};
// ------------------------------- buffer read head prev --------------------
/**
 * @brief Execute buffer_read_head_prev operation.
 * @details Implements the buffer_read_head_prev routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_read_head_prev.
 * @param[in,out] key {void *key} Parameter consumed by buffer_read_head_prev.
 * @param[in] key_size {size_t key_size} Parameter consumed by
 * buffer_read_head_prev.
 * @return {int} Return value produced by buffer_read_head_prev.
 */
int buffer_read_head_prev(t_buffer **buffer, void *key, size_t key_size) {
  if (*buffer != NULL) {
    const void *key_temp = buffer_read_head_prev_key(buffer);
    if (key_temp != NULL)
      memcpy(key, key_temp, key_size);
    return (DATA_OK);
  }
  return (DATA_ERROR);
};
// ------------------------------- buffer read tail next --------------------
/**
 * @brief Execute buffer_read_tail_next operation.
 * @details Implements the buffer_read_tail_next routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_read_tail_next.
 * @param[in,out] key {void *key} Parameter consumed by buffer_read_tail_next.
 * @param[in] key_size {size_t key_size} Parameter consumed by
 * buffer_read_tail_next.
 * @return {int} Return value produced by buffer_read_tail_next.
 */
int buffer_read_tail_next(t_buffer **buffer, void *key, size_t key_size) {
  if (*buffer != NULL) {
    const void *key_temp = buffer_read_tail_next_key(buffer);
    if (key_temp != NULL)
      memcpy(key, key_temp, key_size);
    return (DATA_OK);
  }
  return (DATA_ERROR);
};
// ------------------------------- buffer read tail prev---------------------
/**
 * @brief Execute buffer_read_tail_prev operation.
 * @details Implements the buffer_read_tail_prev routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * buffer_read_tail_prev.
 * @param[in,out] key {void *key} Parameter consumed by buffer_read_tail_prev.
 * @param[in] key_size {size_t key_size} Parameter consumed by
 * buffer_read_tail_prev.
 * @return {int} Return value produced by buffer_read_tail_prev.
 */
int buffer_read_tail_prev(t_buffer **buffer, void *key, size_t key_size) {
  if (*buffer != NULL) {
    const void *key_temp = buffer_read_tail_prev_key(buffer);
    if (key_temp != NULL)
      memcpy(key, key_temp, key_size);
    return (DATA_OK);
  }
  return (DATA_ERROR);
};
// ******************************* binary tree pre order visit **************
/**
 * @brief Execute cell_pre_order_visit operation.
 * @details Implements the cell_pre_order_visit routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * cell_pre_order_visit.
 * @param[in,out] cell {t_tree_cell *cell} Parameter consumed by
 * cell_pre_order_visit.
 * @return {void} No return value.
 */
void cell_pre_order_visit(t_buffer **buffer, t_tree_cell *cell) {
  buffer_insert_tail_key(buffer, cell->key);
  if (cell->left != NULL)
    cell_pre_order_visit(buffer, cell->left);
  if (cell->right != NULL)
    cell_pre_order_visit(buffer, cell->right);
};
// ------------------------------- binary tree in order visit ---------------
/**
 * @brief Execute cell_in_order_visit operation.
 * @details Implements the cell_in_order_visit routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * cell_in_order_visit.
 * @param[in,out] cell {t_tree_cell *cell} Parameter consumed by
 * cell_in_order_visit.
 * @return {void} No return value.
 */
void cell_in_order_visit(t_buffer **buffer, t_tree_cell *cell) {
  if (cell->left != NULL)
    cell_in_order_visit(buffer, cell->left);
  buffer_insert_tail_key(buffer, cell->key);
  if (cell->right != NULL)
    cell_in_order_visit(buffer, cell->right);
};
// ------------------------------- binary tree post order visit -------------
/**
 * @brief Execute cell_post_order_visit operation.
 * @details Implements the cell_post_order_visit routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * cell_post_order_visit.
 * @param[in,out] cell {t_tree_cell *cell} Parameter consumed by
 * cell_post_order_visit.
 * @return {void} No return value.
 */
void cell_post_order_visit(t_buffer **buffer, t_tree_cell *cell) {
  if (cell->left != NULL)
    cell_post_order_visit(buffer, cell->left);
  if (cell->right != NULL)
    cell_post_order_visit(buffer, cell->right);
  buffer_insert_tail_key(buffer, cell->key);
};
// ******************************* heap heapify *****************************
/**
 * @brief Execute heap_heapify operation.
 * @details Implements the heap_heapify routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] cell {t_tree_cell *cell} Parameter consumed by heap_heapify.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by heap_heapify.
 * @return {void} No return value.
 */
void heap_heapify(t_tree_cell *cell, int (*fcmp)(const void *, const void *)) {
  void *key;
  t_tree_cell *largest = NULL;

  if ((cell->left != NULL) && (fcmp((cell->left)->key, cell->key) <= 0))
    largest = cell->left;
  else
    largest = cell;

  if ((cell->right != NULL) && (fcmp((cell->right)->key, largest->key) <= 0))
    largest = cell->right;

  if (largest != cell) {
    key = largest->key;
    largest->key = cell->key;
    cell->key = key;
    heap_heapify(largest, fcmp);
  }
};
// ------------------------------- heap create cell -------------------------
/**
 * @brief Execute heap_create_cell operation.
 * @details Implements the heap_create_cell routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] cell {t_tree_cell *cell} Parameter consumed by
 * heap_create_cell.
 * @return {t_tree_cell *} Return value produced by heap_create_cell.
 */
t_tree_cell *heap_create_cell(t_tree_cell *cell) {
  if (cell == NULL) {
    cell = (t_tree_cell *)metal_allocate_memory(sizeof(t_tree_cell));
    cell->parent = NULL;
  } else {
    if (cell->parent == NULL) {
      if (cell->left == NULL) {
        cell->left = (t_tree_cell *)metal_allocate_memory(sizeof(t_tree_cell));
        (cell->left)->parent = cell;
        cell = cell->left;
      } else {
        cell->right = (t_tree_cell *)metal_allocate_memory(sizeof(t_tree_cell));
        (cell->right)->parent = cell;
        cell = cell->right;
      }
    } else {
      if ((cell->parent)->left == cell) {
        cell = cell->parent;
        cell->right = (t_tree_cell *)metal_allocate_memory(sizeof(t_tree_cell));
        (cell->right)->parent = cell;
        cell = cell->right;
      } else {
        // salgo a destra, vado al fratello destro, scendo a sinistra
        while ((cell->parent != NULL) && ((cell->parent)->right == cell))
          cell = cell->parent;
        if (cell->parent != NULL)
          cell = (cell->parent)->right;
        while (cell->left != NULL)
          cell = cell->left;

        cell->left = (t_tree_cell *)metal_allocate_memory(sizeof(t_tree_cell));
        (cell->left)->parent = cell;
        cell = cell->left;
      }
    }
  }
  cell->left = NULL;
  cell->right = NULL;
  return (cell);
};
// ------------------------------- heap insert key --------------------------
/**
 * @brief Execute heap_insert_key operation.
 * @details Implements the heap_insert_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] heap {t_heap **heap} Parameter consumed by heap_insert_key.
 * @param[in,out] key {void *key} Parameter consumed by heap_insert_key.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by heap_insert_key.
 * @return {void *} Return value produced by heap_insert_key.
 */
void *heap_insert_key(t_heap **heap, void *key,
                      int (*fcmp)(const void *, const void *)) {
  t_tree_cell *cell = NULL;

  if (*heap == NULL) {
    (*heap) = (t_heap *)metal_allocate_memory(sizeof(t_heap));
    cell = heap_create_cell(NULL);
    (*heap)->root = (*heap)->tail = cell;
  } else {
    cell = heap_create_cell((*heap)->tail);
    (*heap)->tail = cell;

    while ((cell->parent != NULL) && (fcmp(key, (cell->parent)->key) < 0)) {
      cell->key = (cell->parent)->key;
      cell = cell->parent;
    }
  }
  cell->key = key;
  return (key);
};
// ------------------------------- heap insert ------------------------------
/**
 * @brief Execute heap_insert operation.
 * @details Implements the heap_insert routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] heap {t_heap **heap} Parameter consumed by heap_insert.
 * @param[in] key {const void *key} Parameter consumed by heap_insert.
 * @param[in] key_size {size_t key_size} Parameter consumed by heap_insert.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by heap_insert.
 * @return {int} Return value produced by heap_insert.
 */
int heap_insert(t_heap **heap, const void *key, size_t key_size,
                int (*fcmp)(const void *, const void *)) {
  if (heap_insert_key(heap, key_copy(key, key_size), fcmp) != NULL)
    return (DATA_OK);
  return (DATA_ERROR);
};
// ------------------------------- heap destroid cell -----------------------
/**
 * @brief Execute heap_destroid_cell operation.
 * @details Implements the heap_destroid_cell routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] heap {t_heap **heap} Parameter consumed by heap_destroid_cell.
 * @return {t_tree_cell *} Return value produced by heap_destroid_cell.
 */
t_tree_cell *heap_destroid_cell(t_heap **heap) {
  t_tree_cell *cell = NULL;

  if ((*heap) != NULL) {
    if ((*heap)->root != (*heap)->tail) {
      cell = (*heap)->tail;
      if ((cell->parent)->right == cell) {
        cell = cell->parent;
        metal_free_memory(cell->right);
        cell->right = NULL;
        cell = cell->left;
      } else {
        cell = cell->parent;
        metal_free_memory(cell->left);
        cell->left = NULL;
        // salgo a sinistra, vado al fratello sinistro, scendo a destra
        while ((cell->parent != NULL) && ((cell->parent)->left == cell))
          cell = cell->parent;
        if (cell->parent != NULL)
          cell = (cell->parent)->left;
        while (cell->right != NULL)
          cell = cell->right;
      }
      (*heap)->tail = cell;
    } else {
      metal_free_memory((*heap)->root);
      metal_free_memory(*heap);
      (*heap) = NULL;
      cell = NULL;
    }
  }
  return (cell);
};
// ------------------------------- heap extract key -------------------------
/**
 * @brief Execute heap_extract_key operation.
 * @details Implements the heap_extract_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] heap {t_heap **heap} Parameter consumed by heap_extract_key.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by heap_extract_key.
 * @return {void *} Return value produced by heap_extract_key.
 */
void *heap_extract_key(t_heap **heap, int (*fcmp)(const void *, const void *)) {
  if ((*heap) != NULL) {
    void *key_temp = ((*heap)->root)->key;
    ((*heap)->root)->key = ((*heap)->tail)->key;
    heap_destroid_cell(heap);
    if ((*heap) != NULL)
      heap_heapify((*heap)->root, fcmp);
    return (key_temp);
  }
  return (NULL);
};
// ------------------------------- heap extract -----------------------------
/**
 * @brief Execute heap_extract operation.
 * @details Implements the heap_extract routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] heap {t_heap **heap} Parameter consumed by heap_extract.
 * @param[in,out] key {void *key} Parameter consumed by heap_extract.
 * @param[in] key_size {size_t key_size} Parameter consumed by heap_extract.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by heap_extract.
 * @return {int} Return value produced by heap_extract.
 */
int heap_extract(t_heap **heap, void *key, size_t key_size,
                 int (*fcmp)(const void *, const void *)) {
  if (*heap != NULL) {
    void *key_temp = heap_extract_key(heap, fcmp);
    if (key_temp != NULL) {
      key_move(key, key_temp, key_size);
      return (DATA_OK);
    }
  }
  return (DATA_ERROR);
}
// ------------------------------- heap sort to buffer ----------------------
/**
 * @brief Execute heap_to_sort_buffer operation.
 * @details Implements the heap_to_sort_buffer routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * heap_to_sort_buffer.
 * @param[in,out] heap {t_heap **heap} Parameter consumed by
 * heap_to_sort_buffer.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by heap_to_sort_buffer.
 * @return {int} Return value produced by heap_to_sort_buffer.
 */
int heap_to_sort_buffer(t_buffer **buffer, t_heap **heap,
                        int (*fcmp)(const void *, const void *)) {
  if (*buffer == NULL) {
    while ((*heap) != NULL) {
      buffer_insert_tail_key(buffer, ((*heap)->root)->key);
      ((*heap)->root)->key = ((*heap)->tail)->key;
      heap_destroid_cell(heap);
      if ((*heap) != NULL)
        heap_heapify((*heap)->root, fcmp);
    }
    if ((*buffer) != NULL)
      return (DATA_OK);
  }
  return (DATA_ERROR);
};
// ------------------------------- heap pre order visit ---------------------
/**
 * @brief Execute heap_pre_order_visit operation.
 * @details Implements the heap_pre_order_visit routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * heap_pre_order_visit.
 * @param[in,out] heap {t_heap **heap} Parameter consumed by
 * heap_pre_order_visit.
 * @return {int} Return value produced by heap_pre_order_visit.
 */
int heap_pre_order_visit(t_buffer **buffer, t_heap **heap) {
  if (*heap != NULL) {
    cell_pre_order_visit(buffer, (*heap)->root);
    return (DATA_OK);
  }
  return (DATA_ERROR);
};
// ******************************* queue insert key *************************
/**
 * @brief Execute queue_insert_key operation.
 * @details Implements the queue_insert_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] queue {t_queue **queue} Parameter consumed by
 * queue_insert_key.
 * @param[in,out] key {void *key} Parameter consumed by queue_insert_key.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by queue_insert_key.
 * @return {void *} Return value produced by queue_insert_key.
 */
void *queue_insert_key(t_queue **queue, void *key,
                       int (*fcmp)(const void *, const void *)) {
  t_heap **heap = NULL;
  heap = queue;
  return (heap_insert_key(heap, key, fcmp));
};
// ------------------------------- queue extract key ------------------------
/**
 * @brief Execute queue_extract_key operation.
 * @details Implements the queue_extract_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] queue {t_queue **queue} Parameter consumed by
 * queue_extract_key.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by queue_extract_key.
 * @return {void *} Return value produced by queue_extract_key.
 */
void *queue_extract_key(t_queue **queue,
                        int (*fcmp)(const void *, const void *)) {
  t_heap **heap = NULL;
  heap = queue;
  return (heap_extract_key(heap, fcmp));
};
// ------------------------------- queue insert -----------------------------
/**
 * @brief Execute queue_insert operation.
 * @details Implements the queue_insert routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] queue {t_queue **queue} Parameter consumed by queue_insert.
 * @param[in] key {const void *key} Parameter consumed by queue_insert.
 * @param[in] key_size {size_t key_size} Parameter consumed by queue_insert.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by queue_insert.
 * @return {int} Return value produced by queue_insert.
 */
int queue_insert(t_queue **queue, const void *key, size_t key_size,
                 int (*fcmp)(const void *, const void *)) {
  if (queue_insert_key(queue, key_copy(key, key_size), fcmp) != NULL)
    return (DATA_OK);
  return (DATA_ERROR);
};
// ------------------------------- queue extract ----------------------------
/**
 * @brief Execute queue_extract operation.
 * @details Implements the queue_extract routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] queue {t_queue **queue} Parameter consumed by queue_extract.
 * @param[in,out] key {void *key} Parameter consumed by queue_extract.
 * @param[in] key_size {size_t key_size} Parameter consumed by queue_extract.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by queue_extract.
 * @return {int} Return value produced by queue_extract.
 */
int queue_extract(t_queue **queue, void *key, size_t key_size,
                  int (*fcmp)(const void *, const void *)) {
  if (*queue != NULL) {
    void *key_temp = queue_extract_key(queue, fcmp);
    if (key_temp != NULL) {
      key_move(key, key_temp, key_size);
      return (DATA_OK);
    }
  }
  return (DATA_ERROR);
};
// ******************************* bst max cell *****************************
/**
 * @brief Execute bst_max_cell operation.
 * @details Implements the bst_max_cell routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] cell {t_tree_cell *cell} Parameter consumed by bst_max_cell.
 * @return {t_tree_cell *} Return value produced by bst_max_cell.
 */
t_tree_cell *bst_max_cell(t_tree_cell *cell) {
  if (cell != NULL) {
    while (cell->right != NULL)
      cell = cell->right;
    return (cell);
  }
  return (NULL);
}
// ------------------------------- bat min cell -----------------------------
/**
 * @brief Execute bst_min_cell operation.
 * @details Implements the bst_min_cell routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] cell {t_tree_cell *cell} Parameter consumed by bst_min_cell.
 * @return {t_tree_cell *} Return value produced by bst_min_cell.
 */
t_tree_cell *bst_min_cell(t_tree_cell *cell) {
  if (cell != NULL) {
    while (cell->left != NULL)
      cell = cell->left;
    return (cell);
  }
  return (NULL);
};
// ------------------------------- bst next cell ----------------------------
/**
 * @brief Execute bst_next_cell operation.
 * @details Implements the bst_next_cell routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] cell {t_tree_cell *cell} Parameter consumed by bst_next_cell.
 * @return {t_tree_cell *} Return value produced by bst_next_cell.
 */
t_tree_cell *bst_next_cell(t_tree_cell *cell) {
  if (cell != NULL) {
    if (cell->right != NULL)
      return (bst_min_cell(cell->right));
    while ((cell->parent != NULL) && (cell == (cell->parent)->right))
      cell = cell->parent;
    cell = cell->parent;
    return (cell);
  }
  return (NULL);
};
// ------------------------------- bst prev cell ----------------------------
/**
 * @brief Execute bst_prev_cell operation.
 * @details Implements the bst_prev_cell routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] cell {t_tree_cell *cell} Parameter consumed by bst_prev_cell.
 * @return {t_tree_cell *} Return value produced by bst_prev_cell.
 */
t_tree_cell *bst_prev_cell(t_tree_cell *cell) {
  if (cell != NULL) {
    if (cell->left != NULL)
      return (bst_max_cell(cell->left));
    while ((cell->parent != NULL) && (cell == (cell->parent)->left))
      cell = cell->parent;
    cell = cell->parent;
    return (cell);
  }
  return (NULL);
}
// ------------------------------- bst search first cell --------------------
/**
 * @brief Execute bst_search_first_cell operation.
 * @details Implements the bst_search_first_cell routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] cell {t_tree_cell *cell} Parameter consumed by
 * bst_search_first_cell.
 * @param[in,out] key {void *key} Parameter consumed by bst_search_first_cell.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by bst_search_first_cell.
 * @return {t_tree_cell *} Return value produced by bst_search_first_cell.
 */
t_tree_cell *bst_search_first_cell(t_tree_cell *cell, void *key,
                                   int (*fcmp)(const void *, const void *)) {
  while (cell != NULL) {
    const int result = fcmp(key, cell->key);
    if (result == 0)
      return (cell);
    if (result > 0)
      cell = cell->right;
    else
      cell = cell->left;
  }
  return (cell);
};
// ------------------------------- bst search last cell ---------------------
/**
 * @brief Execute bst_search_last_cell operation.
 * @details Implements the bst_search_last_cell routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] cell {t_tree_cell *cell} Parameter consumed by
 * bst_search_last_cell.
 * @param[in,out] key {void *key} Parameter consumed by bst_search_last_cell.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by bst_search_last_cell.
 * @return {t_tree_cell *} Return value produced by bst_search_last_cell.
 */
t_tree_cell *bst_search_last_cell(t_tree_cell *cell, void *key,
                                  int (*fcmp)(const void *, const void *)) {
  while (cell != NULL) {
    const int result = fcmp(key, cell->key);
    if (result > 0)
      cell = cell->right;
    else {
      if (result < 0)
        cell = cell->left;
      else {
        if (cell->left == NULL)
          return (cell);
        if (fcmp(key, ((cell->left)->key)) != 0)
          return (cell);
        cell = cell->left;
      }
    }
  }
  return (cell);
};
// ------------------------------- bst search nearest next cell -------------
/**
 * @brief Execute bst_search_nearest_next_cell operation.
 * @details Implements the bst_search_nearest_next_cell routine in the datatypes
 * module context. Complexity depends on container cardinality and delegated
 * callbacks.
 * @param[in,out] cell {t_tree_cell *cell} Parameter consumed by
 * bst_search_nearest_next_cell.
 * @param[in,out] key {void *key} Parameter consumed by
 * bst_search_nearest_next_cell.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by bst_search_nearest_next_cell.
 * @return {t_tree_cell *} Return value produced by
 * bst_search_nearest_next_cell.
 */
t_tree_cell *bst_search_nearest_next_cell(t_tree_cell *cell, void *key,
                                          int (*fcmp)(const void *,
                                                      const void *)) {
  int result = 0;

  while (cell != NULL) {
    result = fcmp(key, cell->key);
    if (result > 0) {
      if (cell->right == NULL)
        break;
      cell = cell->right;
    } else {
      if (cell->left == NULL)
        break;
      cell = cell->left;
    }
  }

  if ((cell != NULL) && (result > 0))
    cell = bst_next_cell(cell);
  return (cell);
};
// ------------------------------- bst search nearest next cell -------------
/**
 * @brief Execute bst_search_nearest_prev_cell operation.
 * @details Implements the bst_search_nearest_prev_cell routine in the datatypes
 * module context. Complexity depends on container cardinality and delegated
 * callbacks.
 * @param[in,out] cell {t_tree_cell *cell} Parameter consumed by
 * bst_search_nearest_prev_cell.
 * @param[in,out] key {void *key} Parameter consumed by
 * bst_search_nearest_prev_cell.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by bst_search_nearest_prev_cell.
 * @return {t_tree_cell *} Return value produced by
 * bst_search_nearest_prev_cell.
 */
t_tree_cell *bst_search_nearest_prev_cell(t_tree_cell *cell, void *key,
                                          int (*fcmp)(const void *,
                                                      const void *)) {
  int result = 0;

  while (cell != NULL) {
    result = fcmp(key, cell->key);
    if (result > 0) {
      if (cell->right == NULL)
        break;
      cell = cell->right;
    } else {
      if (cell->left == NULL)
        break;
      cell = cell->left;
    }
  }
  if ((cell != NULL) && (result < 0))
    cell = bst_prev_cell(cell);
  return (cell);
};
// ------------------------------- bst search all cell ----------------------
/**
 * @brief Execute bst_search_all_cell operation.
 * @details Implements the bst_search_all_cell routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * bst_search_all_cell.
 * @param[in,out] cell {t_tree_cell *cell} Parameter consumed by
 * bst_search_all_cell.
 * @param[in,out] key {void *key} Parameter consumed by bst_search_all_cell.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by bst_search_all_cell.
 * @return {t_tree_cell *} Return value produced by bst_search_all_cell.
 */
t_tree_cell *bst_search_all_cell(t_buffer **buffer, t_tree_cell *cell,
                                 void *key,
                                 int (*fcmp)(const void *, const void *)) {
  while (cell != NULL) {
    const int result = fcmp(key, cell->key);
    if (result == 0)
      buffer_insert_tail_key(buffer, cell->key);

    if (result > 0)
      cell = cell->right;
    else
      cell = cell->left;
  }
  return (cell);
};
// ------------------------------- bst insert key ---------------------------
/**
 * @brief Execute bst_insert_key operation.
 * @details Implements the bst_insert_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_insert_key.
 * @param[in,out] key {void *key} Parameter consumed by bst_insert_key.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by bst_insert_key.
 * @return {void *} Return value produced by bst_insert_key.
 */
void *bst_insert_key(t_bst **bst, void *key,
                     int (*fcmp)(const void *, const void *)) {
  t_tree_cell *cell = NULL;

  if (*bst == NULL) {
    (*bst) = (t_bst *)metal_allocate_memory(sizeof(t_bst));
    cell = (t_tree_cell *)metal_allocate_memory(sizeof(t_tree_cell));
    cell->parent = cell->left = cell->right = NULL;
    (*bst)->root = cell;
  } else {
    int result;
    cell = (*bst)->root;
    result = fcmp(key, cell->key);
    while (((result > 0) && (cell->right != NULL)) ||
           (!(result > 0) && (cell->left != NULL))) {
      if (result > 0) {
        if (cell->right != NULL)
          cell = cell->right;
      } else {
        if (cell->left != NULL)
          cell = cell->left;
      }
      result = fcmp(key, cell->key);
    }
    if (result > 0) {
      cell->right = (t_tree_cell *)metal_allocate_memory(sizeof(t_tree_cell));
      (cell->right)->parent = cell;
      cell = cell->right;
      cell->left = cell->right = NULL;
    } else {
      cell->left = (t_tree_cell *)metal_allocate_memory(sizeof(t_tree_cell));
      (cell->left)->parent = cell;
      cell = cell->left;
      cell->left = cell->right = NULL;
    }
  }
  cell->key = key;
  return (key);
};
// ------------------------------- bst insert -------------------------------
/**
 * @brief Execute bst_insert operation.
 * @details Implements the bst_insert routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_insert.
 * @param[in] key {const void *key} Parameter consumed by bst_insert.
 * @param[in] key_size {size_t key_size} Parameter consumed by bst_insert.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by bst_insert.
 * @return {int} Return value produced by bst_insert.
 */
int bst_insert(t_bst **bst, const void *key, size_t key_size,
               int (*fcmp)(const void *, const void *)) {
  if (bst_insert_key(bst, key_copy(key, key_size), fcmp) != NULL)
    return (DATA_OK);
  return (DATA_ERROR);
}
// ------------------------------- bst search key ---------------------------
/**
 * @brief Execute bst_search_key operation.
 * @details Implements the bst_search_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_search_key.
 * @param[in,out] key {void *key} Parameter consumed by bst_search_key.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by bst_search_key.
 * @return {void *} Return value produced by bst_search_key.
 */
void *bst_search_key(t_bst **bst, void *key,
                     int (*fcmp)(const void *, const void *)) {
  if (*bst != NULL) {
    t_tree_cell *cell = bst_search_first_cell((*bst)->root, key, fcmp);
    if (cell != NULL)
      return (cell->key);
  }
  return (NULL);
};
// ------------------------------- bst search -------------------------------
/**
 * @brief Execute bst_search operation.
 * @details Implements the bst_search routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_search.
 * @param[in,out] key {void *key} Parameter consumed by bst_search.
 * @param[in] key_size {size_t key_size} Parameter consumed by bst_search.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by bst_search.
 * @return {int} Return value produced by bst_search.
 */
int bst_search(t_bst **bst, void *key, size_t key_size,
               int (*fcmp)(const void *, const void *)) {
  if (*bst != NULL) {
    const void *key_temp = bst_search_key(bst, key, fcmp);
    if (key_temp != NULL) {
      memcpy(key, key_temp, key_size);
      return (DATA_OK);
    }
  }
  return (DATA_ERROR);
};
// ------------------------------- bst search all ---------------------------
/**
 * @brief Execute bst_search_all operation.
 * @details Implements the bst_search_all routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * bst_search_all.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_search_all.
 * @param[in,out] key {void *key} Parameter consumed by bst_search_all.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by bst_search_all.
 * @return {int} Return value produced by bst_search_all.
 */
int bst_search_all(t_buffer **buffer, t_bst **bst, void *key,
                   int (*fcmp)(const void *, const void *)) {
  if ((*buffer) == NULL)
    if (*bst != NULL) {
      bst_search_all_cell(buffer, (*bst)->root, key, fcmp);
      if ((*buffer) != NULL)
        return (DATA_OK);
    }
  return (DATA_ERROR);
};
// ------------------------------- bst min key ------------------------------
/**
 * @brief Execute bst_min_key operation.
 * @details Implements the bst_min_key routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_min_key.
 * @return {void *} Return value produced by bst_min_key.
 */
void *bst_min_key(t_bst **bst) {
  t_tree_cell *cell;

  if (*bst != NULL) {
    cell = (*bst)->root;
    cell = bst_min_cell(cell);
    return (cell->key);
  }
  return (NULL);
}
// ------------------------------- bst max key ------------------------------
/**
 * @brief Execute bst_max_key operation.
 * @details Implements the bst_max_key routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_max_key.
 * @return {void *} Return value produced by bst_max_key.
 */
void *bst_max_key(t_bst **bst) {
  t_tree_cell *cell;

  if (*bst != NULL) {
    cell = (*bst)->root;
    cell = bst_max_cell(cell);
    return (cell->key);
  }
  return (NULL);
};
// ------------------------------- bst min ----------------------------------
/**
 * @brief Execute bst_min operation.
 * @details Implements the bst_min routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_min.
 * @param[in,out] key {void *key} Parameter consumed by bst_min.
 * @param[in] key_size {size_t key_size} Parameter consumed by bst_min.
 * @return {int} Return value produced by bst_min.
 */
int bst_min(t_bst **bst, void *key, size_t key_size) {
  const void *key_temp;

  if ((key_temp = bst_min_key(bst)) != NULL) {
    memcpy(key, key_temp, key_size);
    return (DATA_OK);
  }
  return (DATA_ERROR);
}
// ------------------------------- bst max ----------------------------------
/**
 * @brief Execute bst_max operation.
 * @details Implements the bst_max routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_max.
 * @param[in,out] key {void *key} Parameter consumed by bst_max.
 * @param[in] key_size {size_t key_size} Parameter consumed by bst_max.
 * @return {int} Return value produced by bst_max.
 */
int bst_max(t_bst **bst, void *key, size_t key_size) {
  const void *key_temp;

  if ((key_temp = bst_max_key(bst)) != NULL) {
    memcpy(key, key_temp, key_size);
    return (DATA_OK);
  }
  return (DATA_ERROR);
};
// ------------------------------- bst next key -----------------------------
/**
 * @brief Execute bst_next_key operation.
 * @details Implements the bst_next_key routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_next_key.
 * @param[in,out] key {void *key} Parameter consumed by bst_next_key.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by bst_next_key.
 * @return {void *} Return value produced by bst_next_key.
 */
void *bst_next_key(t_bst **bst, void *key,
                   int (*fcmp)(const void *, const void *)) {
  t_tree_cell *cell;

  if (*bst != NULL) {
    if ((cell = bst_search_first_cell((*bst)->root, key, fcmp)) == NULL)
      if ((cell = bst_search_nearest_next_cell((*bst)->root, key, fcmp)) !=
          NULL)
        return (cell->key);
    if (cell != NULL)
      if ((cell = bst_next_cell(cell)) != NULL)
        return (cell->key);
  }
  return (NULL);
};
// ------------------------------- bst prev key -----------------------------
/**
 * @brief Execute bst_prev_key operation.
 * @details Implements the bst_prev_key routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_prev_key.
 * @param[in,out] key {void *key} Parameter consumed by bst_prev_key.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by bst_prev_key.
 * @return {void *} Return value produced by bst_prev_key.
 */
void *bst_prev_key(t_bst **bst, void *key,
                   int (*fcmp)(const void *, const void *)) {
  t_tree_cell *cell;

  if (*bst != NULL) {
    if ((cell = bst_search_last_cell((*bst)->root, key, fcmp)) == NULL)
      if ((cell = bst_search_nearest_prev_cell((*bst)->root, key, fcmp)) !=
          NULL)
        return (cell->key);
    if (cell != NULL)
      if ((cell = bst_prev_cell(cell)) != NULL)
        return (cell->key);
  }
  return (NULL);
};
// ------------------------------- bst next ---------------------------------
/**
 * @brief Execute bst_next operation.
 * @details Implements the bst_next routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_next.
 * @param[in,out] key {void *key} Parameter consumed by bst_next.
 * @param[in] key_size {size_t key_size} Parameter consumed by bst_next.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by bst_next.
 * @return {int} Return value produced by bst_next.
 */
int bst_next(t_bst **bst, void *key, size_t key_size,
             int (*fcmp)(const void *, const void *)) {
  const void *key_temp;

  if ((key_temp = bst_next_key(bst, key, fcmp)) != NULL) {
    memcpy(key, key_temp, key_size);
    return (DATA_OK);
  }
  return (DATA_ERROR);
};
// ------------------------------- bst prev ---------------------------------
/**
 * @brief Execute bst_prev operation.
 * @details Implements the bst_prev routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_prev.
 * @param[in,out] key {void *key} Parameter consumed by bst_prev.
 * @param[in] key_size {size_t key_size} Parameter consumed by bst_prev.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by bst_prev.
 * @return {int} Return value produced by bst_prev.
 */
int bst_prev(t_bst **bst, void *key, size_t key_size,
             int (*fcmp)(const void *, const void *)) {
  const void *key_temp;

  if ((key_temp = bst_prev_key(bst, key, fcmp)) != NULL) {
    memcpy(key, key_temp, key_size);
    return (DATA_OK);
  }
  return (DATA_ERROR);
};
// ------------------------------- bst destroid cell ------------------------
/**
 * @brief Execute bst_destroid_cell operation.
 * @details Implements the bst_destroid_cell routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_destroid_cell.
 * @param[in,out] cell {t_tree_cell *cell} Parameter consumed by
 * bst_destroid_cell.
 * @return {void} No return value.
 */
void bst_destroid_cell(t_bst **bst, t_tree_cell *cell) {
  t_tree_cell *temp_cell;

  if ((*bst) != NULL) {
    if ((cell == (*bst)->root) && (cell->left == NULL) &&
        (cell->right == NULL)) {
      metal_free_memory(cell);
      metal_free_memory(*bst);
      (*bst) = NULL;
      return;
    }
    if (cell != NULL) {
      if ((cell->left != NULL) && (cell->right != NULL)) {
        if ((temp_cell = bst_next_cell(cell)) == NULL)
          temp_cell = bst_prev_cell(cell);
        cell->key = temp_cell->key;
        cell = temp_cell;
      }
      if ((cell->left != NULL) || (cell->right != NULL)) {
        if (cell->left != NULL) {
          (cell->left)->parent = cell->parent;
          temp_cell = cell->left;
        } else {
          (cell->right)->parent = cell->parent;
          temp_cell = cell->right;
        }
      } else
        temp_cell = NULL;

      if (cell->parent != NULL) {
        if (cell == (cell->parent)->left)
          (cell->parent)->left = temp_cell;
        else
          (cell->parent)->right = temp_cell;
      } else
        (*bst)->root = temp_cell;
      metal_free_memory(cell);
    }
  }
};
// ------------------------------- bst extract key --------------------------
/**
 * @brief Execute bst_extract_key operation.
 * @details Implements the bst_extract_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_extract_key.
 * @param[in,out] key {void *key} Parameter consumed by bst_extract_key.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by bst_extract_key.
 * @return {void *} Return value produced by bst_extract_key.
 */
void *bst_extract_key(t_bst **bst, void *key,
                      int (*fcmp)(const void *, const void *)) {
  if (*bst != NULL) {
    t_tree_cell *cell = bst_search_first_cell((*bst)->root, key, fcmp);
    if (cell != NULL) {
      void *key_temp = cell->key;
      bst_destroid_cell(bst, cell);
      return (key_temp);
    }
  }
  return (NULL);
};
// ------------------------------- bst extract ------------------------------
/**
 * @brief Execute bst_extract operation.
 * @details Implements the bst_extract routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_extract.
 * @param[in,out] key {void *key} Parameter consumed by bst_extract.
 * @param[in] key_size {size_t key_size} Parameter consumed by bst_extract.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by bst_extract.
 * @return {int} Return value produced by bst_extract.
 */
int bst_extract(t_bst **bst, void *key, size_t key_size,
                int (*fcmp)(const void *, const void *)) {
  if (*bst != NULL) {
    void *key_temp = bst_extract_key(bst, key, fcmp);
    if (key_temp != NULL) {
      key_move(key, key_temp, key_size);
      return (DATA_OK);
    }
  }
  return (DATA_ERROR);
};
// ------------------------------- bst extract root key ---------------------
/**
 * @brief Execute bst_extract_root_key operation.
 * @details Implements the bst_extract_root_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_extract_root_key.
 * @return {void *} Return value produced by bst_extract_root_key.
 */
void *bst_extract_root_key(t_bst **bst) {
  if (*bst != NULL) {
    void *key = ((*bst)->root)->key;
    bst_destroid_cell(bst, (*bst)->root);
    return (key);
  }
  return (NULL);
}
// ------------------------------- bst extract root -------------------------
/**
 * @brief Execute bst_extract_root operation.
 * @details Implements the bst_extract_root routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_extract_root.
 * @param[in,out] key {void *key} Parameter consumed by bst_extract_root.
 * @param[in] key_size {size_t key_size} Parameter consumed by bst_extract_root.
 * @return {int} Return value produced by bst_extract_root.
 */
int bst_extract_root(t_bst **bst, void *key, size_t key_size) {
  if (*bst != NULL) {
    void *key_temp = bst_extract_root_key(bst);
    if (key_temp != NULL) {
      key_move(key, key_temp, key_size);
      return (DATA_OK);
    }
  }
  return (DATA_ERROR);
};
// ------------------------------- bst destroid all key ---------------------
/**
 * @brief Execute bst_destroid_all_key operation.
 * @details Implements the bst_destroid_all_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_destroid_all_key.
 * @return {void *} Return value produced by bst_destroid_all_key.
 */
void *bst_destroid_all_key(t_bst **bst) {
  while (*bst != NULL) {
    bst_destroid_cell(bst, (*bst)->root);
  }
  return (NULL);
};
// ------------------------------- bst pre order visit ----------------------
/**
 * @brief Execute bst_pre_order_visit operation.
 * @details Implements the bst_pre_order_visit routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * bst_pre_order_visit.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_pre_order_visit.
 * @return {int} Return value produced by bst_pre_order_visit.
 */
int bst_pre_order_visit(t_buffer **buffer, t_bst **bst) {
  if (*bst != NULL) {
    cell_pre_order_visit(buffer, (*bst)->root);
    return (DATA_OK);
  }
  return (DATA_ERROR);
};
// ------------------------------- bst in order visit -----------------------
/**
 * @brief Execute bst_in_order_visit operation.
 * @details Implements the bst_in_order_visit routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * bst_in_order_visit.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_in_order_visit.
 * @return {int} Return value produced by bst_in_order_visit.
 */
int bst_in_order_visit(t_buffer **buffer, t_bst **bst) {
  if (*bst != NULL) {
    cell_in_order_visit(buffer, (*bst)->root);
    return (DATA_OK);
  }
  return (DATA_ERROR);
};
// ------------------------------- bst post order visit ---------------------
/**
 * @brief Execute bst_post_order_visit operation.
 * @details Implements the bst_post_order_visit routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer {t_buffer **buffer} Parameter consumed by
 * bst_post_order_visit.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by bst_post_order_visit.
 * @return {int} Return value produced by bst_post_order_visit.
 */
int bst_post_order_visit(t_buffer **buffer, t_bst **bst) {
  if (*bst != NULL) {
    cell_post_order_visit(buffer, (*bst)->root);
    return (DATA_OK);
  }
  return (DATA_ERROR);
};
// ******************************* heap sort to fifo ************************
/**
 * @brief Execute heap_to_sort_fifo operation.
 * @details Implements the heap_to_sort_fifo routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] fifo {t_fifo **fifo} Parameter consumed by heap_to_sort_fifo.
 * @param[in,out] heap {t_heap **heap} Parameter consumed by heap_to_sort_fifo.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by heap_to_sort_fifo.
 * @return {int} Return value produced by heap_to_sort_fifo.
 */
int heap_to_sort_fifo(t_fifo **fifo, t_heap **heap,
                      int (*fcmp)(const void *, const void *)) {
  if (*fifo == NULL) {
    while ((*heap) != NULL) {
      fifo_insert_key(fifo, ((*heap)->root)->key);
      ((*heap)->root)->key = ((*heap)->tail)->key;
      heap_destroid_cell(heap);
      if ((*heap) != NULL)
        heap_heapify((*heap)->root, fcmp);
    }
    if ((*fifo) != NULL)
      return (DATA_OK);
  }
  return (DATA_ERROR);
};
// ------------------------------- heap structure into bst ------------------
/**
 * @brief Execute heap_structure_to_bst operation.
 * @details Implements the heap_structure_to_bst routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst_cell {t_tree_cell *bst_cell} Parameter consumed by
 * heap_structure_to_bst.
 * @param[in,out] heap_cell {t_tree_cell *heap_cell} Parameter consumed by
 * heap_structure_to_bst.
 * @return {void} No return value.
 */
void heap_structure_to_bst(t_tree_cell *bst_cell, t_tree_cell *heap_cell) {
  // ??? pre order visit;
  bst_cell->left = NULL;
  bst_cell->right = NULL;

  if (heap_cell->left != NULL) {
    bst_cell->left = (t_tree_cell *)metal_allocate_memory(sizeof(t_tree_cell));
    (bst_cell->left)->parent = bst_cell;
    heap_structure_to_bst(bst_cell->left, heap_cell->left);
  }
  if (heap_cell->right != NULL) {
    bst_cell->right = (t_tree_cell *)metal_allocate_memory(sizeof(t_tree_cell));
    (bst_cell->right)->parent = bst_cell;
    heap_structure_to_bst(bst_cell->right, heap_cell->right);
  }
};
// ------------------------------- fifo in order to bst ---------------------
/**
 * @brief Execute fifo_in_order_to_bst operation.
 * @details Implements the fifo_in_order_to_bst routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] cell {t_tree_cell *cell} Parameter consumed by
 * fifo_in_order_to_bst.
 * @param[in,out] fifo {t_fifo **fifo} Parameter consumed by
 * fifo_in_order_to_bst.
 * @return {void} No return value.
 */
void fifo_in_order_to_bst(t_tree_cell *cell, t_fifo **fifo) {
  if (cell->left != NULL)
    fifo_in_order_to_bst(cell->left, fifo);

  cell->key = fifo_extract_key(fifo);

  if (cell->right != NULL)
    fifo_in_order_to_bst(cell->right, fifo);
};
// ------------------------------- heap to bst ------------------------------
/**
 * @brief Execute heap_to_bst operation.
 * @details Implements the heap_to_bst routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] bst {t_bst **bst} Parameter consumed by heap_to_bst.
 * @param[in,out] heap {t_heap **heap} Parameter consumed by heap_to_bst.
 * @param[in] fcmp {int (*fcmp)(const void *, const void *)} Parameter consumed
 * by heap_to_bst.
 * @return {int} Return value produced by heap_to_bst.
 */
int heap_to_bst(t_bst **bst, t_heap **heap,
                int (*fcmp)(const void *, const void *)) {
  t_fifo *fifo = NULL;

  if ((*heap) != NULL)
    if ((*bst) == NULL) {
      (*bst) = (t_bst *)metal_allocate_memory(sizeof(t_bst));
      (*bst)->root = (t_tree_cell *)metal_allocate_memory(sizeof(t_tree_cell));
      (*bst)->root->parent = NULL;

      heap_structure_to_bst((*bst)->root, (*heap)->root);
      heap_to_sort_fifo(&fifo, heap, fcmp);
      fifo_in_order_to_bst((*bst)->root, &fifo);
      return (DATA_OK);
    }
  return (DATA_ERROR);
};
// ******************************* graph fcmp knot **************************
/**
 * @brief Execute graph_fcmp_knot operation.
 * @details Implements the graph_fcmp_knot routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in] x {const void *x} Parameter consumed by graph_fcmp_knot.
 * @param[in] y {const void *y} Parameter consumed by graph_fcmp_knot.
 * @return {int} Return value produced by graph_fcmp_knot.
 */
int graph_fcmp_knot(const void *x, const void *y) {
  t_graph_knot *a;
  t_graph_knot *b;

  a = (t_graph_knot *)x;
  b = (t_graph_knot *)y;
  return ((long int)(a->key_knot) - (long int)(b->key_knot));
};
// ------------------------------- graph fcmp knot val ----------------------
/**
 * @brief Execute graph_fcmp_knot_val operation.
 * @details Implements the graph_fcmp_knot_val routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in] x {const void *x} Parameter consumed by graph_fcmp_knot_val.
 * @param[in] y {const void *y} Parameter consumed by graph_fcmp_knot_val.
 * @return {int} Return value produced by graph_fcmp_knot_val.
 */
int graph_fcmp_knot_val(const void *x, const void *y) {
  const t_graph_knot *a;
  const t_graph_knot *b;

  a = (const t_graph_knot *)x;
  b = (const t_graph_knot *)y;
  return (a->val - b->val);
};
// ------------------------------- graph fcmp arc ---------------------------
/**
 * @brief Execute graph_fcmp_arc operation.
 * @details Implements the graph_fcmp_arc routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in] x {const void *x} Parameter consumed by graph_fcmp_arc.
 * @param[in] y {const void *y} Parameter consumed by graph_fcmp_arc.
 * @return {int} Return value produced by graph_fcmp_arc.
 */
int graph_fcmp_arc(const void *x, const void *y) {
  t_graph_arc *a;
  t_graph_arc *b;

  a = (t_graph_arc *)x;
  b = (t_graph_arc *)y;
  return ((long int)(a->key_knot) - (long int)(b->key_knot));
};
// ------------------------------- graph fcmp arc val -----------------------
/**
 * @brief Execute graph_fcmp_arc_val operation.
 * @details Implements the graph_fcmp_arc_val routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in] x {const void *x} Parameter consumed by graph_fcmp_arc_val.
 * @param[in] y {const void *y} Parameter consumed by graph_fcmp_arc_val.
 * @return {int} Return value produced by graph_fcmp_arc_val.
 */
int graph_fcmp_arc_val(const void *x, const void *y) {
  const t_graph_arc *a;
  const t_graph_arc *b;

  a = (const t_graph_arc *)x;
  b = (const t_graph_arc *)y;
  return (a->val - b->val);
};

// ------------------------------- graph insert knot key --------------------
/**
 * @brief Execute graph_insert_knot_key operation.
 * @details Implements the graph_insert_knot_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] graph {t_graph **graph} Parameter consumed by
 * graph_insert_knot_key.
 * @param[in,out] key_knot {void *key_knot} Parameter consumed by
 * graph_insert_knot_key.
 * @return {void *} Return value produced by graph_insert_knot_key.
 */
void *graph_insert_knot_key(t_graph **graph, void *key_knot) {
  t_graph_knot *graph_knot = NULL;

  if ((*graph) == NULL) {
    (*graph) = (t_graph *)metal_allocate_memory(sizeof(t_graph));
    (*graph)->bst_knot = NULL;
  }
  graph_knot = (t_graph_knot *)metal_allocate_memory(sizeof(t_graph_knot));
  graph_knot->key_knot = key_knot;
  graph_knot->val = DATATYPES_INF;
  graph_knot->color = DATATYPES_WHITE;
  graph_knot->time_find = DATATYPES_INF;
  graph_knot->time_process = DATATYPES_INF;
  graph_knot->bst_arc = NULL;
  bst_insert_key(&((*graph)->bst_knot), graph_knot, graph_fcmp_knot);
  return (graph_knot);
};
// ------------------------------- graph insert arc key ---------------------
/**
 * @brief Execute graph_insert_arc_key operation.
 * @details Implements the graph_insert_arc_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] graph {t_graph **graph} Parameter consumed by
 * graph_insert_arc_key.
 * @param[in,out] key_knot_from {void *key_knot_from} Parameter consumed by
 * graph_insert_arc_key.
 * @param[in,out] key_knot_to {void *key_knot_to} Parameter consumed by
 * graph_insert_arc_key.
 * @param[in,out] key_arc {void *key_arc} Parameter consumed by
 * graph_insert_arc_key.
 * @return {void *} Return value produced by graph_insert_arc_key.
 */
void *graph_insert_arc_key(t_graph **graph, void *key_knot_from,
                           void *key_knot_to, void *key_arc) {
  t_graph_knot *graph_knot = NULL;
  t_graph_arc *graph_arc = NULL;
  t_graph_knot graph_knot_src;

  graph_knot_src.key_knot = key_knot_from;
  graph_knot = (t_graph_knot *)bst_search_key(&((*graph)->bst_knot),
                                              &graph_knot_src, graph_fcmp_knot);
  graph_arc = (t_graph_arc *)metal_allocate_memory(sizeof(t_graph_arc));
  graph_arc->key_arc = key_arc;
  graph_arc->key_knot = key_knot_to;
  graph_knot_src.key_knot = key_knot_to;
  graph_arc->graph_knot = (t_graph_knot *)bst_search_key(
      &((*graph)->bst_knot), &graph_knot_src, graph_fcmp_knot);
  graph_arc->type = DATATYPES_T;
  bst_insert_key(&(graph_knot->bst_arc), graph_arc, graph_fcmp_arc);
  return (graph_arc);
};
// ------------------------------- graph reset all key ----------------------
/**
 * @brief Execute graph_reset_all_key operation.
 * @details Implements the graph_reset_all_key routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] graph {t_graph **graph} Parameter consumed by
 * graph_reset_all_key.
 * @return {void *} Return value produced by graph_reset_all_key.
 */
void *graph_reset_all_key(t_graph **graph) {
  t_graph_knot *graph_knot = NULL;
  t_graph_arc *graph_arc = NULL;
  t_buffer *buffer_graph_knot = NULL;
  t_buffer *buffer_graph_arc = NULL;

  if ((*graph) != NULL) {
    bst_in_order_visit(&buffer_graph_knot, &((*graph)->bst_knot));
    while ((graph_knot = (t_graph_knot *)buffer_extract_head_key(
                &buffer_graph_knot)) != NULL) {
      bst_in_order_visit(&buffer_graph_arc, &(graph_knot->bst_arc));
      while ((graph_arc = (t_graph_arc *)buffer_extract_head_key(
                  &buffer_graph_arc)) != NULL)
        graph_arc->type = DATATYPES_T;
      graph_knot->val = DATATYPES_INF;
      graph_knot->time_find = DATATYPES_INF;
      graph_knot->time_process = DATATYPES_INF;
      graph_knot->color = DATATYPES_WHITE;
    }
  }
  return (NULL);
};
// ------------------------------- graph destroid all key -------------------
/**
 * @brief Execute graph_destroid_all_key operation.
 * @details Implements the graph_destroid_all_key routine in the datatypes
 * module context. Complexity depends on container cardinality and delegated
 * callbacks.
 * @param[in,out] graph {t_graph **graph} Parameter consumed by
 * graph_destroid_all_key.
 * @return {void *} Return value produced by graph_destroid_all_key.
 */
void *graph_destroid_all_key(t_graph **graph) {
  t_graph_knot *graph_knot = NULL;
  t_graph_arc *graph_arc = NULL;

  if ((*graph) != NULL) {
    while (((*graph)->bst_knot) != NULL) {
      graph_knot = (t_graph_knot *)((((*graph)->bst_knot)->root)->key);
      while (graph_knot->bst_arc != NULL) {
        graph_arc = (t_graph_arc *)((graph_knot->bst_arc)->root)->key;
        metal_free_memory(graph_arc);
        bst_destroid_cell(&(graph_knot->bst_arc), (graph_knot->bst_arc)->root);
      }
      metal_free_memory(graph_knot);
      bst_destroid_cell(&((*graph)->bst_knot), (((*graph)->bst_knot)->root));
    }
  }
  metal_free_memory(*graph);
  (*graph) = NULL;
  return (NULL);
};
// ------------------------------- graph dijstra ----------------------------
/**
 * @brief Execute graph_dijstra operation.
 * @details Implements the graph_dijstra routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] graph {t_graph **graph} Parameter consumed by graph_dijstra.
 * @param[in,out] key_knot {void *key_knot} Parameter consumed by graph_dijstra.
 * @param[in] fcalc {int (*fcalc)(const void *)} Parameter consumed by
 * graph_dijstra.
 * @return {int} Return value produced by graph_dijstra.
 */
int graph_dijstra(t_graph **graph, void *key_knot, int (*fcalc)(const void *)) {
  t_graph_knot *graph_knot = NULL;
  t_graph_arc *graph_arc = NULL;
  t_buffer *buffer_graph_knot = NULL;
  t_buffer *buffer_graph_arc = NULL;
  t_queue *queue_graph_knot = NULL;
  t_queue *queue_graph_arc = NULL;
  t_fifo *fifo_graph_knot = NULL;

  t_graph_knot graph_knot_src;

  if ((*graph) != NULL) {
    graph_reset_all_key(graph);
    graph_knot_src.key_knot = key_knot;
    graph_knot = (t_graph_knot *)bst_search_key(
        &((*graph)->bst_knot), &graph_knot_src, graph_fcmp_knot);
    graph_knot->val = 0;
    bst_in_order_visit(&buffer_graph_knot, &((*graph)->bst_knot));
    while ((graph_knot = (t_graph_knot *)buffer_extract_head_key(
                &buffer_graph_knot)) != NULL)
      queue_insert_key(&queue_graph_knot, graph_knot, graph_fcmp_knot_val);
    while ((graph_knot = (t_graph_knot *)queue_extract_key(
                &queue_graph_knot, graph_fcmp_knot_val)) != NULL) {
      graph_knot->color = DATATYPES_GREY;
      bst_in_order_visit(&buffer_graph_arc, &(graph_knot->bst_arc));

      while ((graph_arc = (t_graph_arc *)buffer_extract_head_key(
                  &buffer_graph_arc)) != NULL) {
        if (((graph_arc->graph_knot)->color) == DATATYPES_WHITE) {
          graph_arc->val = fcalc(graph_arc->key_arc);
          queue_insert_key(&queue_graph_arc, graph_arc, graph_fcmp_arc_val);
        }
      }

      while ((graph_arc = (t_graph_arc *)queue_extract_key(
                  &queue_graph_arc, graph_fcmp_arc_val)) != NULL) {
        if (((graph_arc->graph_knot)->val) == DATATYPES_INF)
          (graph_arc->graph_knot)->val = graph_knot->val + graph_arc->val;
        else if ((graph_arc->graph_knot)->val >
                 (graph_knot->val + graph_arc->val))
          (graph_arc->graph_knot)->val = graph_knot->val + graph_arc->val;
      }

      graph_knot->color = DATATYPES_BLACK;
      // riordino coda?
      while ((graph_knot = (t_graph_knot *)queue_extract_key(
                  &queue_graph_knot, graph_fcmp_knot_val)) != NULL)
        fifo_insert_key(&fifo_graph_knot, graph_knot);
      while ((graph_knot =
                  (t_graph_knot *)fifo_extract_key(&fifo_graph_knot)) != NULL)
        queue_insert_key(&queue_graph_knot, graph_knot, graph_fcmp_knot_val);
    }
    return (DATA_OK);
  }
  return (DATA_ERROR);
};
// ------------------------------- graph knot result to buffer --------------
/**
 * @brief Execute graph_knot_result operation.
 * @details Implements the graph_knot_result routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer_knot {t_buffer **buffer_knot} Parameter consumed by
 * graph_knot_result.
 * @param[in,out] buffer_result {t_buffer **buffer_result} Parameter consumed by
 * graph_knot_result.
 * @param[in,out] graph {t_graph **graph} Parameter consumed by
 * graph_knot_result.
 * @return {int} Return value produced by graph_knot_result.
 */
int graph_knot_result(t_buffer **buffer_knot, t_buffer **buffer_result,
                      t_graph **graph) {
  t_graph_knot *graph_knot = NULL;
  t_buffer *buffer_graph_knot = NULL;

  if ((*graph) != NULL) {
    bst_in_order_visit(&buffer_graph_knot, &((*graph)->bst_knot));
    while ((graph_knot = (t_graph_knot *)buffer_extract_head_key(
                &buffer_graph_knot)) != NULL) {
      buffer_insert_tail_key(buffer_knot, graph_knot->key_knot);
      buffer_insert_tail_key(buffer_result, &(graph_knot->val));
    }
    return (DATA_OK);
  }
  return (DATA_ERROR);
};
// ------------------------------- graph minimum path to buffer -------------
/**
 * @brief Execute graph_min_path operation.
 * @details Implements the graph_min_path routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer_knot {t_buffer **buffer_knot} Parameter consumed by
 * graph_min_path.
 * @param[in,out] buffer_result {t_buffer **buffer_result} Parameter consumed by
 * graph_min_path.
 * @param[in,out] graph {t_graph **graph} Parameter consumed by graph_min_path.
 * @param[in,out] key_knot_from {void *key_knot_from} Parameter consumed by
 * graph_min_path.
 * @param[in,out] key_knot_to {void *key_knot_to} Parameter consumed by
 * graph_min_path.
 * @param[in] fcalc {int (*fcalc)(const void *)} Parameter consumed by
 * graph_min_path.
 * @return {int} Return value produced by graph_min_path.
 */
int graph_min_path(t_buffer **buffer_knot, t_buffer **buffer_result,
                   t_graph **graph, void *key_knot_from, void *key_knot_to,
                   int (*fcalc)(const void *)) {
  return (DATA_OK);
};
// ------------------------------- graph maximus path to buffer -------------
/**
 * @brief Execute graph_max_path operation.
 * @details Implements the graph_max_path routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer_knot {t_buffer **buffer_knot} Parameter consumed by
 * graph_max_path.
 * @param[in,out] buffer_result {t_buffer **buffer_result} Parameter consumed by
 * graph_max_path.
 * @param[in,out] graph {t_graph **graph} Parameter consumed by graph_max_path.
 * @param[in,out] key_knot_from {void *key_knot_from} Parameter consumed by
 * graph_max_path.
 * @param[in,out] key_knot_to {void *key_knot_to} Parameter consumed by
 * graph_max_path.
 * @param[in] fcalc {int (*fcalc)(const void *)} Parameter consumed by
 * graph_max_path.
 * @return {int} Return value produced by graph_max_path.
 */
int graph_max_path(t_buffer **buffer_knot, t_buffer **buffer_result,
                   t_graph **graph, void *key_knot_from, void *key_knot_to,
                   int (*fcalc)(const void *)) {
  return (DATA_OK);
};
// ------------------------------- graph all path to double buffer ----------
/**
 * @brief Execute graph_all_path operation.
 * @details Implements the graph_all_path routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @param[in,out] buffer_buffer_knot {t_buffer **buffer_buffer_knot} Parameter
 * consumed by graph_all_path.
 * @param[in,out] buffer_buffer_result {t_buffer **buffer_buffer_result}
 * Parameter consumed by graph_all_path.
 * @param[in,out] graph {t_graph **graph} Parameter consumed by graph_all_path.
 * @param[in,out] key_knot_from {void *key_knot_from} Parameter consumed by
 * graph_all_path.
 * @param[in,out] key_knot_to {void *key_knot_to} Parameter consumed by
 * graph_all_path.
 * @param[in] fcalc {int (*fcalc)(const void *)} Parameter consumed by
 * graph_all_path.
 * @return {int} Return value produced by graph_all_path.
 */
int graph_all_path(t_buffer **buffer_buffer_knot,
                   t_buffer **buffer_buffer_result, t_graph **graph,
                   void *key_knot_from, void *key_knot_to,
                   int (*fcalc)(const void *)) {
  return (DATA_OK);
};
// ******************************* STRUCT.C *********************************
