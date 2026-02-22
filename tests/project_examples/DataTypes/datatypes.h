/**
 * @file datatypes.h
 * @brief Public contracts for datatypes containers and graph routines.
 * @details Declares data structures, constants, and API prototypes consumed by
 * stack, fifo, buffer, heap, queue, bst, and graph components.
 */

#ifndef SRC_DATATYPES_H_
#define SRC_DATATYPES_H_

#include <metal/alloc.h>

// ****************************** DATATYPES.H **********************************
#define DATATYPES_WHITE 0
#define DATATYPES_BLACK -1
#define DATATYPES_GREY 1
#define DATATYPES_T 0
#define DATATYPES_B -1
#define DATATYPES_c 1
#define DATATYPES_INF 32000
#define DATATYPES_NEG -1

// ****************************** stack struct ******************************
typedef struct tag_stack_cell {
  void *key;
  struct tag_stack_cell *next;
} t_stack_cell;
typedef struct {
  t_stack_cell *head;
} t_stack;

// ------------------------------ fifo struct -------------------------------
typedef struct tag_fifo_cell {
  void *key;
  struct tag_fifo_cell *next;
  struct tag_fifo_cell *prev;
} t_fifo_cell;
typedef struct {
  t_fifo_cell *head;
  t_fifo_cell *tail;
} t_fifo;

// ------------------------------ buffer struct -----------------------------
typedef t_fifo_cell t_buffer_cell;
typedef struct {
  t_fifo_cell *head;
  t_fifo_cell *tail;
  long int number_of_cell;
  long int counter;
} t_buffer;

// ------------------------------ heap struct -------------------------------
typedef struct tag_cell {
  void *key;
  struct tag_cell *parent;
  struct tag_cell *left;
  struct tag_cell *right;
} t_tree_cell;
typedef struct {
  t_tree_cell *root;
  t_tree_cell *tail;
} t_heap;

// ------------------------------ queue struct ------------------------------
typedef t_heap t_queue;

// ------------------------------ bst struct --------------------------------
typedef struct {
  t_tree_cell *root;
} t_bst;

// ------------------------------ graph struct ------------------------------
typedef struct {
  t_bst *bst_knot;
} t_graph;
typedef struct {
  void *key_knot;
  int val;
  int time_find;
  int time_process;
  char color;
  t_bst *bst_arc;
} t_graph_knot;
typedef struct {
  void *key_arc;
  void *key_knot;
  t_graph_knot *graph_knot;
  int val;
  char type;
} t_graph_arc;

// ****************************** stack function ****************************
/**
 * @brief Declare stack_insert_key contract.
 * @details Prototype-level contract metadata for stack_insert_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_stack **} Parameter declared by stack_insert_key.
 * @param[in,out] arg {void *} Parameter declared by stack_insert_key.
 * @return {void *} Declared return value type for stack_insert_key.
 */
void *stack_insert_key(t_stack **, void *);
/**
 * @brief Declare stack_extract_key contract.
 * @details Prototype-level contract metadata for stack_extract_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_stack **} Parameter declared by stack_extract_key.
 * @return {void *} Declared return value type for stack_extract_key.
 */
void *stack_extract_key(t_stack **);
/**
 * @brief Declare stack_insert contract.
 * @details Prototype-level contract metadata for stack_insert; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_stack **} Parameter declared by stack_insert.
 * @param[in] arg {const void *} Parameter declared by stack_insert.
 * @param[in] size_t {size_t} Parameter declared by stack_insert.
 * @return {int} Declared return value type for stack_insert.
 */
int stack_insert(t_stack **, const void *, size_t);
/**
 * @brief Declare stack_extract contract.
 * @details Prototype-level contract metadata for stack_extract; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_stack **} Parameter declared by stack_extract.
 * @param[in,out] arg {void *} Parameter declared by stack_extract.
 * @param[in] size_t {size_t} Parameter declared by stack_extract.
 * @return {int} Declared return value type for stack_extract.
 */
int stack_extract(t_stack **, void *, size_t);

// ------------------------------ fifo function -----------------------------
/**
 * @brief Declare fifo_insert_key contract.
 * @details Prototype-level contract metadata for fifo_insert_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_fifo **} Parameter declared by fifo_insert_key.
 * @param[in,out] arg {void *} Parameter declared by fifo_insert_key.
 * @return {void *} Declared return value type for fifo_insert_key.
 */
void *fifo_insert_key(t_fifo **, void *);
/**
 * @brief Declare fifo_extract_key contract.
 * @details Prototype-level contract metadata for fifo_extract_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_fifo **} Parameter declared by fifo_extract_key.
 * @return {void *} Declared return value type for fifo_extract_key.
 */
void *fifo_extract_key(t_fifo **);
/**
 * @brief Declare fifo_insert contract.
 * @details Prototype-level contract metadata for fifo_insert; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_fifo **} Parameter declared by fifo_insert.
 * @param[in] arg {const void *} Parameter declared by fifo_insert.
 * @param[in] size_t {size_t} Parameter declared by fifo_insert.
 * @return {int} Declared return value type for fifo_insert.
 */
int fifo_insert(t_fifo **, const void *, size_t);
/**
 * @brief Declare fifo_extract contract.
 * @details Prototype-level contract metadata for fifo_extract; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_fifo **} Parameter declared by fifo_extract.
 * @param[in,out] arg {void *} Parameter declared by fifo_extract.
 * @param[in] size_t {size_t} Parameter declared by fifo_extract.
 * @return {int} Declared return value type for fifo_extract.
 */
int fifo_extract(t_fifo **, void *, size_t);

// ------------------------------ fifo vs. stack conversion -----------------
/**
 * @brief Declare fifo_to_stack contract.
 * @details Prototype-level contract metadata for fifo_to_stack; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_stack **} Parameter declared by fifo_to_stack.
 * @param[in,out] arg {t_fifo **} Parameter declared by fifo_to_stack.
 * @return {int} Declared return value type for fifo_to_stack.
 */
int fifo_to_stack(t_stack **, t_fifo **);
/**
 * @brief Declare stack_to_fifo contract.
 * @details Prototype-level contract metadata for stack_to_fifo; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_fifo **} Parameter declared by stack_to_fifo.
 * @param[in,out] arg {t_stack **} Parameter declared by stack_to_fifo.
 * @return {int} Declared return value type for stack_to_fifo.
 */
int stack_to_fifo(t_fifo **, t_stack **);

// ------------------------------ buffer function ---------------------------
/**
 * @brief Declare buffer_size contract.
 * @details Prototype-level contract metadata for buffer_size; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by buffer_size.
 * @return {long int} Declared return value type for buffer_size.
 */
long int buffer_size(t_buffer **);
/**
 * @brief Declare buffer_get_head_key contract.
 * @details Prototype-level contract metadata for buffer_get_head_key;
 * implementation details are defined in source modules.
 * @param[in,out] buffer {t_buffer **buffer} Parameter declared by
 * buffer_get_head_key.
 * @return {void *} Declared return value type for buffer_get_head_key.
 */
void *buffer_get_head_key(t_buffer **buffer);
/**
 * @brief Declare buffer_get_tail_key contract.
 * @details Prototype-level contract metadata for buffer_get_tail_key;
 * implementation details are defined in source modules.
 * @param[in,out] buffer {t_buffer **buffer} Parameter declared by
 * buffer_get_tail_key.
 * @return {void *} Declared return value type for buffer_get_tail_key.
 */
void *buffer_get_tail_key(t_buffer **buffer);
/**
 * @brief Declare buffer_insert_head_key contract.
 * @details Prototype-level contract metadata for buffer_insert_head_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by
 * buffer_insert_head_key.
 * @param[in,out] arg {void *} Parameter declared by buffer_insert_head_key.
 * @return {void *} Declared return value type for buffer_insert_head_key.
 */
void *buffer_insert_head_key(t_buffer **, void *);
/**
 * @brief Declare buffer_insert_tail_key contract.
 * @details Prototype-level contract metadata for buffer_insert_tail_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by
 * buffer_insert_tail_key.
 * @param[in,out] arg {void *} Parameter declared by buffer_insert_tail_key.
 * @return {void *} Declared return value type for buffer_insert_tail_key.
 */
void *buffer_insert_tail_key(t_buffer **, void *);
/**
 * @brief Declare buffer_extract_head_key contract.
 * @details Prototype-level contract metadata for buffer_extract_head_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by
 * buffer_extract_head_key.
 * @return {void *} Declared return value type for buffer_extract_head_key.
 */
void *buffer_extract_head_key(t_buffer **);
/**
 * @brief Declare buffer_extract_tail_key contract.
 * @details Prototype-level contract metadata for buffer_extract_tail_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by
 * buffer_extract_tail_key.
 * @return {void *} Declared return value type for buffer_extract_tail_key.
 */
void *buffer_extract_tail_key(t_buffer **);
/**
 * @brief Declare buffer_read_head_key contract.
 * @details Prototype-level contract metadata for buffer_read_head_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by buffer_read_head_key.
 * @return {void *} Declared return value type for buffer_read_head_key.
 */
void *buffer_read_head_key(t_buffer **);
/**
 * @brief Declare buffer_read_head_next_key contract.
 * @details Prototype-level contract metadata for buffer_read_head_next_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by
 * buffer_read_head_next_key.
 * @return {void *} Declared return value type for buffer_read_head_next_key.
 */
void *buffer_read_head_next_key(t_buffer **);
/**
 * @brief Declare buffer_read_head_prev_key contract.
 * @details Prototype-level contract metadata for buffer_read_head_prev_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by
 * buffer_read_head_prev_key.
 * @return {void *} Declared return value type for buffer_read_head_prev_key.
 */
void *buffer_read_head_prev_key(t_buffer **);
/**
 * @brief Declare buffer_read_tail_next_key contract.
 * @details Prototype-level contract metadata for buffer_read_tail_next_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by
 * buffer_read_tail_next_key.
 * @return {void *} Declared return value type for buffer_read_tail_next_key.
 */
void *buffer_read_tail_next_key(t_buffer **);
/**
 * @brief Declare buffer_read_tail_prev_key contract.
 * @details Prototype-level contract metadata for buffer_read_tail_prev_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by
 * buffer_read_tail_prev_key.
 * @return {void *} Declared return value type for buffer_read_tail_prev_key.
 */
void *buffer_read_tail_prev_key(t_buffer **);
/**
 * @brief Declare buffer_insert_head contract.
 * @details Prototype-level contract metadata for buffer_insert_head;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by buffer_insert_head.
 * @param[in] arg {const void *} Parameter declared by buffer_insert_head.
 * @param[in] size_t {size_t} Parameter declared by buffer_insert_head.
 * @return {int} Declared return value type for buffer_insert_head.
 */
int buffer_insert_head(t_buffer **, const void *, size_t);
/**
 * @brief Declare buffer_insert_tail contract.
 * @details Prototype-level contract metadata for buffer_insert_tail;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by buffer_insert_tail.
 * @param[in] arg {const void *} Parameter declared by buffer_insert_tail.
 * @param[in] size_t {size_t} Parameter declared by buffer_insert_tail.
 * @return {int} Declared return value type for buffer_insert_tail.
 */
int buffer_insert_tail(t_buffer **, const void *, size_t);
/**
 * @brief Declare buffer_extract_head contract.
 * @details Prototype-level contract metadata for buffer_extract_head;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by buffer_extract_head.
 * @param[in,out] arg {void *} Parameter declared by buffer_extract_head.
 * @param[in] size_t {size_t} Parameter declared by buffer_extract_head.
 * @return {int} Declared return value type for buffer_extract_head.
 */
int buffer_extract_head(t_buffer **, void *, size_t);
/**
 * @brief Declare buffer_extract_tail contract.
 * @details Prototype-level contract metadata for buffer_extract_tail;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by buffer_extract_tail.
 * @param[in,out] arg {void *} Parameter declared by buffer_extract_tail.
 * @param[in] size_t {size_t} Parameter declared by buffer_extract_tail.
 * @return {int} Declared return value type for buffer_extract_tail.
 */
int buffer_extract_tail(t_buffer **, void *, size_t);
/**
 * @brief Declare buffer_read_head_next contract.
 * @details Prototype-level contract metadata for buffer_read_head_next;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by buffer_read_head_next.
 * @param[in,out] arg {void *} Parameter declared by buffer_read_head_next.
 * @param[in] size_t {size_t} Parameter declared by buffer_read_head_next.
 * @return {int} Declared return value type for buffer_read_head_next.
 */
int buffer_read_head_next(t_buffer **, void *, size_t);
/**
 * @brief Declare buffer_read_head_prev contract.
 * @details Prototype-level contract metadata for buffer_read_head_prev;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by buffer_read_head_prev.
 * @param[in,out] arg {void *} Parameter declared by buffer_read_head_prev.
 * @param[in] size_t {size_t} Parameter declared by buffer_read_head_prev.
 * @return {int} Declared return value type for buffer_read_head_prev.
 */
int buffer_read_head_prev(t_buffer **, void *, size_t);
/**
 * @brief Declare buffer_read_tail_next contract.
 * @details Prototype-level contract metadata for buffer_read_tail_next;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by buffer_read_tail_next.
 * @param[in,out] arg {void *} Parameter declared by buffer_read_tail_next.
 * @param[in] size_t {size_t} Parameter declared by buffer_read_tail_next.
 * @return {int} Declared return value type for buffer_read_tail_next.
 */
int buffer_read_tail_next(t_buffer **, void *, size_t);
/**
 * @brief Declare buffer_read_tail_prev contract.
 * @details Prototype-level contract metadata for buffer_read_tail_prev;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by buffer_read_tail_prev.
 * @param[in,out] arg {void *} Parameter declared by buffer_read_tail_prev.
 * @param[in] size_t {size_t} Parameter declared by buffer_read_tail_prev.
 * @return {int} Declared return value type for buffer_read_tail_prev.
 */
int buffer_read_tail_prev(t_buffer **, void *, size_t);

// ------------------------------ heap function -----------------------------
/**
 * @brief Declare heap_insert_key contract.
 * @details Prototype-level contract metadata for heap_insert_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_heap **} Parameter declared by heap_insert_key.
 * @param[in,out] arg {void *} Parameter declared by heap_insert_key.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * heap_insert_key.
 * @return {void *} Declared return value type for heap_insert_key.
 */
void *heap_insert_key(t_heap **, void *, int (*)(const void *, const void *));
/**
 * @brief Declare heap_extract_key contract.
 * @details Prototype-level contract metadata for heap_extract_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_heap **} Parameter declared by heap_extract_key.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * heap_extract_key.
 * @return {void *} Declared return value type for heap_extract_key.
 */
void *heap_extract_key(t_heap **, int (*)(const void *, const void *));
/**
 * @brief Declare heap_insert contract.
 * @details Prototype-level contract metadata for heap_insert; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_heap **} Parameter declared by heap_insert.
 * @param[in] arg {const void *} Parameter declared by heap_insert.
 * @param[in] size_t {size_t} Parameter declared by heap_insert.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * heap_insert.
 * @return {int} Declared return value type for heap_insert.
 */
int heap_insert(t_heap **, const void *, size_t,
                int (*)(const void *, const void *));
/**
 * @brief Declare heap_extract contract.
 * @details Prototype-level contract metadata for heap_extract; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_heap **} Parameter declared by heap_extract.
 * @param[in,out] arg {void *} Parameter declared by heap_extract.
 * @param[in] size_t {size_t} Parameter declared by heap_extract.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * heap_extract.
 * @return {int} Declared return value type for heap_extract.
 */
int heap_extract(t_heap **, void *, size_t,
                 int (*)(const void *, const void *));

// .............................. heap sorting to a buffer ..................
/**
 * @brief Declare heap_to_sort_buffer contract.
 * @details Prototype-level contract metadata for heap_to_sort_buffer;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by heap_to_sort_buffer.
 * @param[in,out] arg {t_heap **} Parameter declared by heap_to_sort_buffer.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * heap_to_sort_buffer.
 * @return {int} Declared return value type for heap_to_sort_buffer.
 */
int heap_to_sort_buffer(t_buffer **, t_heap **,
                        int (*)(const void *, const void *));
/**
 * @brief Declare heap_pre_order_visit contract.
 * @details Prototype-level contract metadata for heap_pre_order_visit;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by heap_pre_order_visit.
 * @param[in,out] arg {t_heap **} Parameter declared by heap_pre_order_visit.
 * @return {int} Declared return value type for heap_pre_order_visit.
 */
int heap_pre_order_visit(t_buffer **, t_heap **);

// ------------------------------ queue function ----------------------------
/**
 * @brief Declare queue_insert_key contract.
 * @details Prototype-level contract metadata for queue_insert_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_queue **} Parameter declared by queue_insert_key.
 * @param[in,out] arg {void *} Parameter declared by queue_insert_key.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * queue_insert_key.
 * @return {void *} Declared return value type for queue_insert_key.
 */
void *queue_insert_key(t_queue **, void *, int (*)(const void *, const void *));
/**
 * @brief Declare queue_extract_key contract.
 * @details Prototype-level contract metadata for queue_extract_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_queue **} Parameter declared by queue_extract_key.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * queue_extract_key.
 * @return {void *} Declared return value type for queue_extract_key.
 */
void *queue_extract_key(t_queue **, int (*)(const void *, const void *));
/**
 * @brief Declare queue_insert contract.
 * @details Prototype-level contract metadata for queue_insert; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_queue **} Parameter declared by queue_insert.
 * @param[in] arg {const void *} Parameter declared by queue_insert.
 * @param[in] size_t {size_t} Parameter declared by queue_insert.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * queue_insert.
 * @return {int} Declared return value type for queue_insert.
 */
int queue_insert(t_queue **, const void *, size_t,
                 int (*)(const void *, const void *));
/**
 * @brief Declare queue_extract contract.
 * @details Prototype-level contract metadata for queue_extract; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_queue **} Parameter declared by queue_extract.
 * @param[in,out] arg {void *} Parameter declared by queue_extract.
 * @param[in] size_t {size_t} Parameter declared by queue_extract.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * queue_extract.
 * @return {int} Declared return value type for queue_extract.
 */
int queue_extract(t_queue **, void *, size_t,
                  int (*)(const void *, const void *));

// ------------------------------ bst function ------------------------------
/**
 * @brief Declare bst_insert_key contract.
 * @details Prototype-level contract metadata for bst_insert_key; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_insert_key.
 * @param[in,out] arg {void *} Parameter declared by bst_insert_key.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * bst_insert_key.
 * @return {void *} Declared return value type for bst_insert_key.
 */
void *bst_insert_key(t_bst **, void *, int (*)(const void *, const void *));
/**
 * @brief Declare bst_extract_key contract.
 * @details Prototype-level contract metadata for bst_extract_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_extract_key.
 * @param[in,out] arg {void *} Parameter declared by bst_extract_key.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * bst_extract_key.
 * @return {void *} Declared return value type for bst_extract_key.
 */
void *bst_extract_key(t_bst **, void *, int (*)(const void *, const void *));
/**
 * @brief Declare bst_extract_root_key contract.
 * @details Prototype-level contract metadata for bst_extract_root_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_extract_root_key.
 * @return {void *} Declared return value type for bst_extract_root_key.
 */
void *bst_extract_root_key(t_bst **);
/**
 * @brief Declare bst_destroid_all_key contract.
 * @details Prototype-level contract metadata for bst_destroid_all_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_destroid_all_key.
 * @return {void *} Declared return value type for bst_destroid_all_key.
 */
void *bst_destroid_all_key(t_bst **);
/**
 * @brief Declare bst_search_key contract.
 * @details Prototype-level contract metadata for bst_search_key; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_search_key.
 * @param[in,out] arg {void *} Parameter declared by bst_search_key.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * bst_search_key.
 * @return {void *} Declared return value type for bst_search_key.
 */
void *bst_search_key(t_bst **, void *, int (*)(const void *, const void *));
/**
 * @brief Declare bst_max_key contract.
 * @details Prototype-level contract metadata for bst_max_key; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_max_key.
 * @return {void *} Declared return value type for bst_max_key.
 */
void *bst_max_key(t_bst **);
/**
 * @brief Declare bst_min_key contract.
 * @details Prototype-level contract metadata for bst_min_key; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_min_key.
 * @return {void *} Declared return value type for bst_min_key.
 */
void *bst_min_key(t_bst **);
/**
 * @brief Declare bst_next_key contract.
 * @details Prototype-level contract metadata for bst_next_key; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_next_key.
 * @param[in,out] arg {void *} Parameter declared by bst_next_key.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * bst_next_key.
 * @return {void *} Declared return value type for bst_next_key.
 */
void *bst_next_key(t_bst **, void *, int (*)(const void *, const void *));
/**
 * @brief Declare bst_prev_key contract.
 * @details Prototype-level contract metadata for bst_prev_key; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_prev_key.
 * @param[in,out] arg {void *} Parameter declared by bst_prev_key.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * bst_prev_key.
 * @return {void *} Declared return value type for bst_prev_key.
 */
void *bst_prev_key(t_bst **, void *, int (*)(const void *, const void *));
/**
 * @brief Declare bst_insert contract.
 * @details Prototype-level contract metadata for bst_insert; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_insert.
 * @param[in] arg {const void *} Parameter declared by bst_insert.
 * @param[in] size_t {size_t} Parameter declared by bst_insert.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * bst_insert.
 * @return {int} Declared return value type for bst_insert.
 */
int bst_insert(t_bst **, const void *, size_t,
               int (*)(const void *, const void *));
/**
 * @brief Declare bst_extract contract.
 * @details Prototype-level contract metadata for bst_extract; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_extract.
 * @param[in,out] arg {void *} Parameter declared by bst_extract.
 * @param[in] size_t {size_t} Parameter declared by bst_extract.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * bst_extract.
 * @return {int} Declared return value type for bst_extract.
 */
int bst_extract(t_bst **, void *, size_t, int (*)(const void *, const void *));
/**
 * @brief Declare bst_extract_root contract.
 * @details Prototype-level contract metadata for bst_extract_root;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_extract_root.
 * @param[in,out] arg {void *} Parameter declared by bst_extract_root.
 * @param[in] size_t {size_t} Parameter declared by bst_extract_root.
 * @return {int} Declared return value type for bst_extract_root.
 */
int bst_extract_root(t_bst **, void *, size_t);
/**
 * @brief Declare bst_search contract.
 * @details Prototype-level contract metadata for bst_search; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_search.
 * @param[in,out] arg {void *} Parameter declared by bst_search.
 * @param[in] size_t {size_t} Parameter declared by bst_search.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * bst_search.
 * @return {int} Declared return value type for bst_search.
 */
int bst_search(t_bst **, void *, size_t, int (*)(const void *, const void *));
/**
 * @brief Declare bst_max contract.
 * @details Prototype-level contract metadata for bst_max; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_max.
 * @param[in,out] arg {void *} Parameter declared by bst_max.
 * @param[in] size_t {size_t} Parameter declared by bst_max.
 * @return {int} Declared return value type for bst_max.
 */
int bst_max(t_bst **, void *, size_t);
/**
 * @brief Declare bst_min contract.
 * @details Prototype-level contract metadata for bst_min; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_min.
 * @param[in,out] arg {void *} Parameter declared by bst_min.
 * @param[in] size_t {size_t} Parameter declared by bst_min.
 * @return {int} Declared return value type for bst_min.
 */
int bst_min(t_bst **, void *, size_t);
/**
 * @brief Declare bst_next contract.
 * @details Prototype-level contract metadata for bst_next; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_next.
 * @param[in,out] arg {void *} Parameter declared by bst_next.
 * @param[in] size_t {size_t} Parameter declared by bst_next.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * bst_next.
 * @return {int} Declared return value type for bst_next.
 */
int bst_next(t_bst **, void *, size_t, int (*)(const void *, const void *));
/**
 * @brief Declare bst_prev contract.
 * @details Prototype-level contract metadata for bst_prev; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_prev.
 * @param[in,out] arg {void *} Parameter declared by bst_prev.
 * @param[in] size_t {size_t} Parameter declared by bst_prev.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * bst_prev.
 * @return {int} Declared return value type for bst_prev.
 */
int bst_prev(t_bst **, void *, size_t, int (*)(const void *, const void *));

// .............................. bst output function .......................
/**
 * @brief Declare bst_search_all contract.
 * @details Prototype-level contract metadata for bst_search_all; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by bst_search_all.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_search_all.
 * @param[in,out] arg {void *} Parameter declared by bst_search_all.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * bst_search_all.
 * @return {int} Declared return value type for bst_search_all.
 */
int bst_search_all(t_buffer **, t_bst **, void *,
                   int (*)(const void *, const void *));
/**
 * @brief Declare bst_pre_order_visit contract.
 * @details Prototype-level contract metadata for bst_pre_order_visit;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by bst_pre_order_visit.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_pre_order_visit.
 * @return {int} Declared return value type for bst_pre_order_visit.
 */
int bst_pre_order_visit(t_buffer **, t_bst **);
/**
 * @brief Declare bst_in_order_visit contract.
 * @details Prototype-level contract metadata for bst_in_order_visit;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by bst_in_order_visit.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_in_order_visit.
 * @return {int} Declared return value type for bst_in_order_visit.
 */
int bst_in_order_visit(t_buffer **, t_bst **);
/**
 * @brief Declare bst_post_order_visit contract.
 * @details Prototype-level contract metadata for bst_post_order_visit;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by bst_post_order_visit.
 * @param[in,out] arg {t_bst **} Parameter declared by bst_post_order_visit.
 * @return {int} Declared return value type for bst_post_order_visit.
 */
int bst_post_order_visit(t_buffer **, t_bst **);

// ------------------------------ heap to bst conversion --------------------
/**
 * @brief Declare heap_to_bst contract.
 * @details Prototype-level contract metadata for heap_to_bst; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_bst **} Parameter declared by heap_to_bst.
 * @param[in,out] arg {t_heap **} Parameter declared by heap_to_bst.
 * @param[in] arg {int (*)(const void *, const void *)} Parameter declared by
 * heap_to_bst.
 * @return {int} Declared return value type for heap_to_bst.
 */
int heap_to_bst(t_bst **, t_heap **, int (*)(const void *, const void *));

// ------------------------------ graph function ----------------------------
/**
 * @brief Declare graph_insert_knot_key contract.
 * @details Prototype-level contract metadata for graph_insert_knot_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_graph **} Parameter declared by graph_insert_knot_key.
 * @param[in,out] arg {void *} Parameter declared by graph_insert_knot_key.
 * @return {void *} Declared return value type for graph_insert_knot_key.
 */
void *graph_insert_knot_key(t_graph **, void *);
/**
 * @brief Declare graph_insert_arc_key contract.
 * @details Prototype-level contract metadata for graph_insert_arc_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_graph **} Parameter declared by graph_insert_arc_key.
 * @param[in,out] arg {void *} Parameter declared by graph_insert_arc_key.
 * @param[in,out] arg {void *} Parameter declared by graph_insert_arc_key.
 * @param[in,out] arg {void *} Parameter declared by graph_insert_arc_key.
 * @return {void *} Declared return value type for graph_insert_arc_key.
 */
void *graph_insert_arc_key(t_graph **, void *, void *, void *);
/**
 * @brief Declare graph_reset_all_key contract.
 * @details Prototype-level contract metadata for graph_reset_all_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_graph **} Parameter declared by graph_reset_all_key.
 * @return {void *} Declared return value type for graph_reset_all_key.
 */
void *graph_reset_all_key(t_graph **);
/**
 * @brief Declare graph_destroid_all_key contract.
 * @details Prototype-level contract metadata for graph_destroid_all_key;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_graph **} Parameter declared by graph_destroid_all_key.
 * @return {void *} Declared return value type for graph_destroid_all_key.
 */
void *graph_destroid_all_key(t_graph **);
/**
 * @brief Declare graph_dijstra contract.
 * @details Prototype-level contract metadata for graph_dijstra; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_graph **} Parameter declared by graph_dijstra.
 * @param[in,out] arg {void *} Parameter declared by graph_dijstra.
 * @param[in] arg {int (*)(const void *)} Parameter declared by graph_dijstra.
 * @return {int} Declared return value type for graph_dijstra.
 */
int graph_dijstra(t_graph **, void *, int (*)(const void *));
/**
 * @brief Declare graph_knot_result contract.
 * @details Prototype-level contract metadata for graph_knot_result;
 * implementation details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by graph_knot_result.
 * @param[in,out] arg {t_buffer **} Parameter declared by graph_knot_result.
 * @param[in,out] arg {t_graph **} Parameter declared by graph_knot_result.
 * @return {int} Declared return value type for graph_knot_result.
 */
int graph_knot_result(t_buffer **, t_buffer **, t_graph **);

// ------------------------------ graph path function -----------------------
/**
 * @brief Declare graph_min_path contract.
 * @details Prototype-level contract metadata for graph_min_path; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by graph_min_path.
 * @param[in,out] arg {t_buffer **} Parameter declared by graph_min_path.
 * @param[in,out] arg {t_graph **} Parameter declared by graph_min_path.
 * @param[in,out] arg {void *} Parameter declared by graph_min_path.
 * @param[in,out] arg {void *} Parameter declared by graph_min_path.
 * @param[in] arg {int (*)(const void *)} Parameter declared by graph_min_path.
 * @return {int} Declared return value type for graph_min_path.
 */
int graph_min_path(t_buffer **, t_buffer **, t_graph **, void *, void *,
                   int (*)(const void *));
/**
 * @brief Declare graph_max_path contract.
 * @details Prototype-level contract metadata for graph_max_path; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by graph_max_path.
 * @param[in,out] arg {t_buffer **} Parameter declared by graph_max_path.
 * @param[in,out] arg {t_graph **} Parameter declared by graph_max_path.
 * @param[in,out] arg {void *} Parameter declared by graph_max_path.
 * @param[in,out] arg {void *} Parameter declared by graph_max_path.
 * @param[in] arg {int (*)(const void *)} Parameter declared by graph_max_path.
 * @return {int} Declared return value type for graph_max_path.
 */
int graph_max_path(t_buffer **, t_buffer **, t_graph **, void *, void *,
                   int (*)(const void *));
/**
 * @brief Declare graph_all_path contract.
 * @details Prototype-level contract metadata for graph_all_path; implementation
 * details are defined in source modules.
 * @param[in,out] arg {t_buffer **} Parameter declared by graph_all_path.
 * @param[in,out] arg {t_buffer **} Parameter declared by graph_all_path.
 * @param[in,out] arg {t_graph **} Parameter declared by graph_all_path.
 * @param[in,out] arg {void *} Parameter declared by graph_all_path.
 * @param[in,out] arg {void *} Parameter declared by graph_all_path.
 * @param[in] arg {int (*)(const void *)} Parameter declared by graph_all_path.
 * @return {int} Declared return value type for graph_all_path.
 */
int graph_all_path(t_buffer **, t_buffer **, t_graph **, void *, void *,
                   int (*)(const void *));

#endif /* SRC_DATATYPES_H_ */
