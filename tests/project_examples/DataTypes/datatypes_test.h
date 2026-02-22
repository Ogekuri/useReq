/**
 * @file datatypes_test.h
 * @brief DEBUG_DATATYPES harness declarations.
 * @details Exposes debug routine entrypoints used by the test-runner main unit.
 */

#ifndef SRC_DATATYPES_TEST_H_
#define SRC_DATATYPES_TEST_H_

#ifdef DEBUG_DATATYPES

/**
 * @brief Declare init_data contract.
 * @details Prototype-level contract metadata for init_data; implementation
 * details are defined in source modules.
 * @return {void} No return value.
 */
void init_data();
/**
 * @brief Declare visit contract.
 * @details Prototype-level contract metadata for visit; implementation details
 * are defined in source modules.
 * @return {void} No return value.
 */
void visit();

#endif

#endif /* SRC_DATATYPES_TEST_H_ */
