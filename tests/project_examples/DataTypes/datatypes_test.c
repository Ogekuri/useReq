/**
 * @file datatypes_test.c
 * @brief DEBUG_DATATYPES debug harness implementation.
 * @details Implements deterministic debug routines that exercise datatypes APIs
 * and print observed behavior for manual validation.
 */

#ifdef DEBUG_DATATYPES

// ******************************** MAIN.C **********************************
#define MAX 20
#define N_KNOT 5
#define N_ARC 3
// -------------------------------- library ---------------------------------
#include "datadefine.h"
#include "datatypes.h"
#include <stdio.h>
#include <stdlib.h>
// ******************************** global variable *************************
t_stack *stack = NULL;
t_fifo *fifo = NULL;
t_heap *heap = NULL;
t_bst *bst = NULL;
t_queue *queue = NULL;
t_buffer *buffer = NULL;
t_graph *graph = NULL;
// -------------------------------- local struct ----------------------------
typedef struct {
  char ord;
  int n;
} t_record;
// -------------------------------- local function --------------------------
/**
 * @brief Execute fcmp operation.
 * @details Implements the fcmp routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in] x {const void *x} Parameter consumed by fcmp.
 * @param[in] y {const void *y} Parameter consumed by fcmp.
 * @return {int} Return value produced by fcmp.
 */
int fcmp(const void *x, const void *y) {
  const t_record *a, *b;
  a = (const t_record *)x;
  b = (const t_record *)y;
  return ((a->n) - (b->n)); // return 0 if equal, >0 if a>b, <0 id a<b;
}
// -------------------------------- local variable --------------------------
t_record data[MAX];
t_record record;
t_record *p_record;
// -------------------------------- local graph struct ----------------------
typedef struct {
  char name;
} t_knot;
typedef struct {
  int knot;
  int val;
} t_arc;
// -------------------------------- local graph function -------------------
/**
 * @brief Execute fcalc operation.
 * @details Implements the fcalc routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @param[in] x {const void *x} Parameter consumed by fcalc.
 * @return {int} Return value produced by fcalc.
 */
int fcalc(const void *x) {
  const t_arc *a;
  a = (const t_arc *)x;
  return (a->val);
}
// -------------------------------- local graph variable --------------------
t_knot *p_knot = NULL;
t_knot knot[N_KNOT] = {{'s'}, {'u'}, {'v'}, {'x'}, {'y'}};
int n_arc[N_KNOT] = {2, 2, 1, 3, 2};
t_arc arc[N_KNOT][N_ARC] = {{{1, 10}, {3, 5}, {-1, 0}},
                            {{2, 1}, {3, 2}, {-1, 0}},
                            {{4, 4}, {-1, 0}, {-1, 0}},
                            {{1, 3}, {2, 9}, {4, 2}},
                            {{0, 7}, {2, 6}, {-1, 0}}};
t_buffer *buffer_knot = NULL;
t_buffer *buffer_result = NULL;
t_buffer *buffer_buffer_knot = NULL;
t_buffer *buffer_buffer_result = NULL;
int *p_result;
// -------------------------------- output formatting -----------------------
const char *format = "%4d,(%3d)";
// -------------------------------- menu calling function prototype ---------
void ins(void);
void ext(void);
void sort(void);
void conv(void);
void bsttest(void);
void visit(void);
void bstheap(void);
void heapvisit(void);
void queuebst(void);
void nearest(void);
void circular(void);
void read_buffer_test(void);
void graphtest(void);
void graphpath(void);
// ******************************** main program ****************************
/*
void main(void)
        {
        int i;
        t_menu *menu=NULL;

        for (i=0; i<MAX; i++)
                {
                data[i].ord=i;
                //data[i].n=1;
                //data[i].n=rand()%(MAX/2);
                data[i].n=rand()%(MAX*2);
                }
        menu_add_item(&menu,"1- Insert",'1',ins);
        menu_add_item(&menu,"2- Extraxt",'2',ext);
        menu_add_item(&menu,"3- Sort",'3',sort);
        menu_add_item(&menu,"4- Stack<->Fifo",'4',conv);
        menu_add_item(&menu,"5- Bst Test",'5',bsttest);
        menu_add_item(&menu,"6- Bst Visit",'6',visit);
        menu_add_item(&menu,"7- Heap->Bst",'7',bstheap);
        menu_add_item(&menu,"8- Heap Extract and Visit",'8',heapvisit);
        menu_add_item(&menu,"9- Queue and Bst Search All",'9',queuebst);
        menu_add_item(&menu,"0- Bst Search Nearest",'0',nearest);
        menu_add_item(&menu,"c- Circular Buffer",'c',circular);
        menu_add_item(&menu,"r- Read Buffer",'r',read);
        menu_add_item(&menu,"g- Graph",'g',graphtest);
        menu_add_item(&menu,"p- Graph Path",'p',graphpath);
        menu_add_item(&menu,"q- Quit",'q',NULL);
        menu_display(menu);
        menu_destroid(&menu);
        };

*/

/**
 * @brief Execute init_data operation.
 * @details Implements the init_data routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @return {void} No return value.
 */
void init_data() {
  int i;
  for (i = 0; i < MAX; i++) {
    data[i].ord = i;
    // data[i].n=1;
    // data[i].n=rand()%(MAX/2);
    data[i].n = ((rand() % (MAX * 2)) - MAX);
  }
}

// ******************************** insert test *****************************
/**
 * @brief Execute ins operation.
 * @details Implements the ins routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @return {void} No return value.
 */
void ins() {
  int i;

  printf("\n\n\t<INSERT>\n");
  printf("\n\n\theap\n\n");
  for (i = 0; i < MAX; i++) {
    heap_insert(&heap, &data[i], sizeof(t_record), fcmp);
    printf(format, data[i].ord, data[i].n);
  }
  printf("\n\n\tstack\n\n");
  for (i = 0; i < MAX; i++) {
    stack_insert(&stack, &data[i], sizeof(t_record));
    printf(format, data[i].ord, data[i].n);
  }
  printf("\n\n\tfifo\n\n");
  for (i = 0; i < MAX; i++) {
    fifo_insert(&fifo, &data[i], sizeof(t_record));
    printf(format, data[i].ord, data[i].n);
  }
  printf("\n\n\t...press a key...");
};
// -------------------------------- extract test ----------------------------
/**
 * @brief Execute ext operation.
 * @details Implements the ext routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @return {void} No return value.
 */
void ext() {
  printf("\n\n\t<EXTRACT>\n");
  printf("\n\n\theap\n\n");
  while (heap_extract(&heap, &record, sizeof(t_record), fcmp) == DATA_OK)
    printf(format, record.ord, record.n);
  printf("\n\n\tstack\n\n");
  while (stack_extract(&stack, &record, sizeof(t_record)) == DATA_OK)
    printf(format, record.ord, record.n);
  printf("\n\n\tfifo\n\n");
  while (fifo_extract(&fifo, &record, sizeof(t_record)) == DATA_OK)
    printf(format, record.ord, record.n);
  printf("\n\n\t...press a key...");
};
// -------------------------------- sort test -------------------------------
/**
 * @brief Execute sort operation.
 * @details Implements the sort routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @return {void} No return value.
 */
void sort() {
  int i;

  printf("\n\n\t<SORT>\n");
  for (i = 0; i < MAX; i++)
    heap_insert(&heap, &data[i], sizeof(t_record), fcmp);
  heap_to_sort_buffer(&buffer, &heap, fcmp);
  printf("\n\n\textracting buffer from head\n\n");
  while (buffer_extract_head(&buffer, &record, sizeof(t_record)) == DATA_OK)
    printf(format, record.ord, record.n);
  printf("\n\n\t...press a key...");
};
// -------------------------------- fifo to stack test ----------------------
/**
 * @brief Execute conv operation.
 * @details Implements the conv routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @return {void} No return value.
 */
void conv() {
  int i;

  printf("\n\n\t<STACK<->FIFO>\n");
  printf("\n\n\tinsert to stack\n\n");
  for (i = 0; i < MAX; i++)
    stack_insert(&stack, &data[i], sizeof(t_record));
  printf("\n\n\tstack to fifo\n\n");
  stack_to_fifo(&fifo, &stack);
  printf("\n\n\tfifo to stack\n\n");
  fifo_to_stack(&stack, &fifo);
  printf("\n\n\tstack\n\n");
  while (stack_extract(&stack, &record, sizeof(t_record)) == DATA_OK)
    printf(format, record.ord, record.n);
  printf("\n\n\tfifo\n\n");
  while (fifo_extract(&fifo, &record, sizeof(t_record)) == DATA_OK)
    printf(format, record.ord, record.n);
  printf("\n\t...press a key...");
};
// -------------------------------- bst test --------------------------------
/**
 * @brief Execute bsttest operation.
 * @details Implements the bsttest routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @return {void} No return value.
 */
void bsttest() {
  int i;

  printf("\n\n\t<BST>\n");
  printf("\n\n\tinsert\n\n");
  for (i = 0; i < MAX; i++) {
    bst_insert(&bst, &data[i], sizeof(t_record), fcmp);
    printf(format, data[i].ord, data[i].n);
  }
  printf("\n\n\tsearch\n\n");
  for (i = 0; i < MAX; i++) {
    record = data[i];
    if (bst_search(&bst, &record, sizeof(t_record), fcmp) == DATA_OK)
      printf(format, record.ord, record.n);
  }
  printf("\n\n\tmax\t");
  bst_max(&bst, &record, sizeof(t_record));
  printf(format, record.ord, record.n);
  printf("\n\tmin\t");
  bst_min(&bst, &record, sizeof(t_record));
  printf(format, record.ord, record.n);
  printf("\n\n\tnext\n\n");
  for (i = 0; i < MAX; i++) {
    record = data[i];
    if (bst_next(&bst, &record, sizeof(t_record), fcmp) == DATA_OK)
      printf(format, record.ord, record.n);
  }
  printf("\n\n\tprev\n\n");
  for (i = 0; i < MAX; i++) {
    record = data[i];
    if (bst_prev(&bst, &record, sizeof(t_record), fcmp) == DATA_OK)
      printf(format, record.ord, record.n);
  }
  printf("\n\n\textract\n\n");
  for (i = 0; i < MAX; i++) {
    record = data[i];
    if (bst_extract(&bst, &record, sizeof(t_record), fcmp) == DATA_OK)
      printf(format, record.ord, record.n);
  }
  printf("\n\n\textract\n\n");
  for (i = 0; i < MAX; i++) {
    record = data[i];
    if (bst_extract(&bst, &record, sizeof(t_record), fcmp) == DATA_OK)
      printf(format, record.ord, record.n);
  }
  printf("\n\t...press a key...");
};
// -------------------------------- bst visit test --------------------------
/**
 * @brief Execute visit operation.
 * @details Implements the visit routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @return {void} No return value.
 */
void visit() {
  int i;
  printf("\n\n\t<BST VISIT>\n");
  printf("\n\n\tinsert\n\n");
  for (i = 0; i < MAX; i++) {
    bst_insert(&bst, &data[i], sizeof(t_record), fcmp);
    printf(format, data[i].ord, data[i].n);
  }
  printf("\n\n\tbst pre order visit");
  bst_pre_order_visit(&buffer, &bst);
  printf("\n\treading buffer from head\n\n");
  while ((p_record = buffer_extract_head_key(&buffer)) != NULL)
    printf(format, p_record->ord, p_record->n);
  printf("\n\n\tbst in order visit");
  bst_in_order_visit(&buffer, &bst);
  printf("\n\treading buffer from head\n\n");

  int n_elements = buffer_size(&buffer);
  for (int i_element = 0; i_element < n_elements; i_element++) {
    p_record = buffer_read_head_prev_key(&buffer);
    printf(format, p_record->ord, p_record->n);
  }
  printf("\n\tdone\n\n");

  while ((p_record = buffer_extract_head_key(&buffer)) != NULL)
    printf(format, p_record->ord, p_record->n);
  printf("\n\n\tbst post order visit");
  bst_post_order_visit(&buffer, &bst);
  printf("\n\treading buffer from head\n\n");
  while ((p_record = buffer_extract_head_key(&buffer)) != NULL)
    printf(format, p_record->ord, p_record->n);
  printf("\n\n\textract\n\n");
  for (i = 0; i < MAX; i++) {
    record = data[i];
    if (bst_extract(&bst, &record, sizeof(t_record), fcmp) == DATA_OK)
      printf(format, record.ord, record.n);
  }
  printf("\n\n\textract\n\n");
  for (i = 0; i < MAX; i++) {
    record = data[i];
    if (bst_extract(&bst, &record, sizeof(t_record), fcmp) == DATA_OK)
      printf(format, record.ord, record.n);
  }
  printf("\n\t...press a key...");
};
// -------------------------------- bst to heap test ------------------------
/**
 * @brief Execute bstheap operation.
 * @details Implements the bstheap routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @return {void} No return value.
 */
void bstheap() {
  int i;

  printf("\n\n\t<HEAP->BST>\n");
  printf("\n\n\theap\n\n");
  for (i = 0; i < MAX; i++) {
    heap_insert(&heap, &data[i], sizeof(t_record), fcmp);
    printf(format, data[i].ord, data[i].n);
  }
  printf("\n\n\ttrasform heap into bst");
  heap_to_bst(&bst, &heap, fcmp);
  printf("\n\n\tbst in order visit");
  bst_in_order_visit(&buffer, &bst);
  printf("\n\treading buffer from head\n\n");
  while ((p_record = buffer_extract_head_key(&buffer)) != NULL)
    printf(format, p_record->ord, p_record->n);
  printf("\n\n\textract\n\n");
  for (i = 0; i < MAX; i++) {
    record = data[i];
    if (bst_extract(&bst, &record, sizeof(t_record), fcmp) == DATA_OK)
      printf(format, record.ord, record.n);
  }
  printf("\n\n\textract\n\n");
  for (i = 0; i < MAX; i++) {
    record = data[i];
    if (bst_extract(&bst, &record, sizeof(t_record), fcmp) == DATA_OK)
      printf(format, record.ord, record.n);
  }
  printf("\n\t...press a key...");
};
// -------------------------------- heap visit test -------------------------
/**
 * @brief Execute heapvisit operation.
 * @details Implements the heapvisit routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @return {void} No return value.
 */
void heapvisit() {
  int i;

  printf("\n\n\t<HEAP EXTRACT AND VISIT>\n");
  printf("\n\n\theap\n\n");
  for (i = 0; i < MAX; i++) {
    heap_insert(&heap, &data[i], sizeof(t_record), fcmp);
    printf(format, data[i].ord, data[i].n);
  }
  printf("\n\n\theap pre order visit:\n");
  heap_pre_order_visit(&buffer, &heap);
  printf("\n\treading buffer from head\n\n");
  while ((p_record = buffer_extract_head_key(&buffer)) != NULL)
    printf(format, p_record->ord, p_record->n);

  while (heap_extract(&heap, &record, sizeof(t_record), fcmp) == DATA_OK) {
    printf("\n\n\textract:");
    printf(format, record.ord, record.n);
    printf("\n");
    heap_pre_order_visit(&buffer, &heap);
    while ((p_record = buffer_extract_head_key(&buffer)) != NULL)
      printf(format, p_record->ord, p_record->n);
  }

  printf("\n\t...press a key...");
};
// -------------------------------- queue and bst search test ---------------
/**
 * @brief Execute queuebst operation.
 * @details Implements the queuebst routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @return {void} No return value.
 */
void queuebst() {
  int i;

  printf("\n\n\t<QUEUE AND SBT SEARCH ALL>\n");
  printf("\n\n\tqueue insert\n\n");
  for (i = 0; i < MAX; i++) {
    queue_insert(&queue, &data[i], sizeof(t_record), fcmp);
    printf(format, data[i].ord, data[i].n);
  }
  printf("\n\n\tqueue extract\n\n");
  while (queue_extract(&queue, &record, sizeof(t_record), fcmp) == DATA_OK)
    printf(format, record.ord, record.n);
  printf("\n\n\tbst insert\n\n");
  for (i = 0; i < MAX; i++) {
    bst_insert(&bst, &data[i], sizeof(t_record), fcmp);
    printf(format, data[i].ord, data[i].n);
  }
  printf("\n\n\tbst search all\n\n");
  for (i = 0; i < MAX; i++) {
    record = data[i];
    if (bst_search_all(&buffer, &bst, &record, fcmp) == DATA_OK) {
      printf("\n\tfor ");
      printf(format, record.ord, record.n);
      printf(" ... found ->");
      while ((p_record = buffer_extract_head_key(&buffer)) != NULL)
        printf(format, p_record->ord, p_record->n);
    }
  }
  printf("\n\n\tbst search key\n\n");
  for (i = 0; i < MAX; i++) {
    record = data[i];
    if ((p_record = bst_search_key(&bst, &record, fcmp)) != NULL)
      printf(format, p_record->ord, p_record->n);
  }
  printf("\n\n\textract all\n\n");
  for (i = 0; i < MAX; i++) {
    record = data[i];
    bst_extract(&bst, &record, sizeof(t_record), fcmp);
  }
  printf("\n\t...press a key...");
};
// -------------------------------- bst nearest search test -----------------
/**
 * @brief Execute nearest operation.
 * @details Implements the nearest routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @return {void} No return value.
 */
void nearest() {
  int i;

  printf("\n\n\t<QUEUE AND SBT SEARCH ALL>\n");
  printf("\n\n\tbst insert\n\n");
  for (i = 0; i < MAX; i++) {
    bst_insert(&bst, &data[i], sizeof(t_record), fcmp);
    printf(format, data[i].ord, data[i].n);
  }
  printf("\n\n\tbst search next and prev nearest\n");
  for (i = 0; i < (MAX * 2); i++) {
    record.n = i;
    printf("\n\tvalue->%d... ", record.n);
    printf("\tprev:");
    if (bst_prev(&bst, &record, sizeof(t_record), fcmp) == DATA_OK)
      printf(format, record.ord, record.n);
    record.n = i;
    printf("\t\tnext:");
    if (bst_next(&bst, &record, sizeof(t_record), fcmp) == DATA_OK)
      printf(format, record.ord, record.n);
  }
  printf("\n\n\textract all\n\n");
  for (i = 0; i < MAX; i++) {
    record = data[i];
    bst_extract(&bst, &record, sizeof(t_record), fcmp);
    printf(format, record.ord, record.n);
  }
  printf("\n\n\t...press a key...");
};
// -------------------------------- circular buffer test --------------------
/**
 * @brief Execute circular operation.
 * @details Implements the circular routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @return {void} No return value.
 */
void circular() {
  int i;

  printf("\n\n\t<CIRCULAR BUFFER>\n");
  printf("\n\n\thead insert\n\n");
  for (i = 0; i < MAX; i++) {
    buffer_insert_head(&buffer, &data[i], sizeof(t_record));
    printf(format, data[i].ord, data[i].n);
  }
  printf("\n\n\thead extract\n\n");
  while (buffer_extract_head(&buffer, &record, sizeof(t_record)) == DATA_OK)
    printf(format, record.ord, record.n);
  printf("\n\n\ttail insert\n\n");
  for (i = 0; i < MAX; i++) {
    buffer_insert_tail(&buffer, &data[i], sizeof(t_record));
    printf(format, data[i].ord, data[i].n);
  }
  printf("\n\n\ttail extract\n\n");
  while (buffer_extract_tail(&buffer, &record, sizeof(t_record)) == DATA_OK)
    printf(format, record.ord, record.n);
  printf("\n\n\thead insert\n\n");
  for (i = 0; i < MAX; i++) {
    buffer_insert_head(&buffer, &data[i], sizeof(t_record));
    printf(format, data[i].ord, data[i].n);
  }
  printf("\n\n\ttail extract\n\n");
  while (buffer_extract_tail(&buffer, &record, sizeof(t_record)) == DATA_OK)
    printf(format, record.ord, record.n);
  printf("\n\n\ttail insert\n\n");
  for (i = 0; i < MAX; i++) {
    buffer_insert_tail(&buffer, &data[i], sizeof(t_record));
    printf(format, data[i].ord, data[i].n);
  }
  printf("\n\n\thead extract\n\n");
  while (buffer_extract_head(&buffer, &record, sizeof(t_record)) == DATA_OK)
    printf(format, record.ord, record.n);
  printf("\n\n\t...press a key...");
};
// -------------------------------- buffer reading test ---------------------
/**
 * @brief Execute read_buffer_test operation.
 * @details Implements the read_buffer_test routine in the datatypes module
 * context. Complexity depends on container cardinality and delegated callbacks.
 * @return {void} No return value.
 */
void read_buffer_test() {
  int i;

  printf("\n\n\t<READ BUFFER>\n");
  printf("\n\n\thead insert\n\n");
  for (i = 0; i < MAX; i++) {
    buffer_insert_head(&buffer, &data[i], sizeof(t_record));
    printf(format, data[i].ord, data[i].n);
  }
  printf("\n\n\tcounter:%ld\n", buffer_size(&buffer));
  printf("\n\n\tread head prev\n\n");
  for (i = 0; i < buffer_size(&buffer); i++) {
    buffer_read_head_prev(&buffer, &record, sizeof(t_record));
    printf(format, record.ord, record.n);
  }
  printf("\n\n\tread tail next\n\n");
  for (i = 0; i < buffer_size(&buffer); i++) {
    buffer_read_tail_next(&buffer, &record, sizeof(t_record));
    printf(format, record.ord, record.n);
  }
  printf("\n\n\tread head next\n\n");
  for (i = 0; i < buffer_size(&buffer); i++) {
    buffer_read_head_next(&buffer, &record, sizeof(t_record));
    printf(format, record.ord, record.n);
  }
  printf("\n\n\tread tail prev\n\n");
  for (i = 0; i < buffer_size(&buffer); i++) {
    buffer_read_tail_prev(&buffer, &record, sizeof(t_record));
    printf(format, record.ord, record.n);
  }
  printf("\n\n\thead extract\n\n");
  while (buffer_extract_head(&buffer, &record, sizeof(t_record)) == DATA_OK)
    printf(format, record.ord, record.n);
  printf("\n\n\tcounter:%ld\n", buffer_size(&buffer));
  printf("\n\n\t...press a key...");
};
// -------------------------------- graph test ------------------------------
/**
 * @brief Execute graphtest operation.
 * @details Implements the graphtest routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @return {void} No return value.
 */
void graphtest() {
  int i;
  int t;

  printf("\n\n\t<GRAPH>\n");
  for (i = 0; i < N_KNOT; i++)
    graph_insert_knot_key(&graph, &knot[i]);
  for (i = 0; i < N_KNOT; i++)
    for (t = 0; t < n_arc[i]; t++)
      graph_insert_arc_key(&graph, &knot[i], &knot[arc[i][t].knot], &arc[i][t]);

  graph_knot_result(&buffer_knot, &buffer_result, &graph);
  while ((p_knot = buffer_extract_head_key(&buffer_knot)) != NULL) {
    p_result = buffer_extract_head_key(&buffer_result);
    printf("%c - %d\n", p_knot->name, *p_result);
  }
  graph_dijstra(&graph, &knot[0], fcalc);
  graph_knot_result(&buffer_knot, &buffer_result, &graph);
  while ((p_knot = buffer_extract_head_key(&buffer_knot)) != NULL) {
    p_result = buffer_extract_head_key(&buffer_result);
    printf("%c - %d\n", p_knot->name, *p_result);
  }
  graph_reset_all_key(&graph);
  graph_knot_result(&buffer_knot, &buffer_result, &graph);
  while ((p_knot = buffer_extract_head_key(&buffer_knot)) != NULL) {
    p_result = buffer_extract_head_key(&buffer_result);
    printf("%c - %d\n", p_knot->name, *p_result);
  }
  graph_destroid_all_key(&graph);
  printf("\n\n\t...press a key...");
};
// -------------------------------- graph path search test ------------------
/**
 * @brief Execute graphpath operation.
 * @details Implements the graphpath routine in the datatypes module context.
 * Complexity depends on container cardinality and delegated callbacks.
 * @return {void} No return value.
 */
void graphpath() {
  int i;
  int t;

  printf("\n\n\t<GRAPH PATH>\n");
  for (i = 0; i < N_KNOT; i++)
    graph_insert_knot_key(&graph, &knot[i]);
  for (i = 0; i < N_KNOT; i++)
    for (t = 0; t < n_arc[i]; t++)
      graph_insert_arc_key(&graph, &knot[i], &knot[arc[i][t].knot], &arc[i][t]);

  if (graph_min_path(&buffer_knot, &buffer_result, &graph, &knot[0], &knot[2],
                     fcalc) == DATA_OK) {
    while ((p_knot = buffer_extract_head_key(&buffer_knot)) != NULL) {
      p_result = buffer_extract_head_key(&buffer_result);
      printf("%c - %d\n", p_knot->name, *p_result);
    }
  }
  if (graph_max_path(&buffer_knot, &buffer_result, &graph, &knot[0], &knot[2],
                     fcalc) == DATA_OK) {
    while ((p_knot = buffer_extract_head_key(&buffer_knot)) != NULL) {
      p_result = buffer_extract_head_key(&buffer_result);
      printf("%c - %d\n", p_knot->name, *p_result);
    }
  }
  if (graph_all_path(&buffer_buffer_knot, &buffer_buffer_result, &graph,
                     &knot[0], &knot[2], fcalc) == DATA_OK) {
    while ((buffer_knot = buffer_extract_head_key(&buffer_buffer_knot)) !=
           NULL) {
      buffer_result = buffer_extract_head_key(&buffer_buffer_result);
      while ((p_knot = buffer_extract_head_key(&buffer_knot)) != NULL) {
        p_result = buffer_extract_head_key(&buffer_result);
        printf("%c - %d\n", p_knot->name, *p_result);
      }
      printf("\n");
    }
  }
  graph_destroid_all_key(&graph);
  printf("\n\n\t...press a key...");
};

#endif // #ifdef DEBUG_DATATYPES
