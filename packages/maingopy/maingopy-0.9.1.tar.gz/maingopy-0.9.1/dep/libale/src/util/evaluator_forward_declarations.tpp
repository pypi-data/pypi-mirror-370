/**********************************************************************************
 * Copyright (c) 2023 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/
#include "config.hpp"

#pragma once

//main generator call, calls all subgenerators
#define GEN_EVALUATOR GEN_EVALUATOR_1 GEN_EVALUATOR_2

//template owning_ref<y<x>> evaluate_expression(expression<y<x>>& node, symbol_table& symbols);
//template owning_ref<y<x>> evaluate_expression(value_node<y<x>>* node, symbol_table& symbols);
#define GEN_EVALUATOR_1 GEN_INT(LIBALE_MAX_DIM, GEN_EVALUATOR_1_1)
#define GEN_EVALUATOR_1_1(x) GEN_TYPE(GEN_EVALUATOR_1_2, x)
#define GEN_EVALUATOR_1_2(x,y) TEMPLATE OWNING_REF(y<x>) EVALUATE_EXPRESSION(expression<y<x>>& node, symbol_table& symbols) TEMPLATE OWNING_REF(y<x>) EVALUATE_EXPRESSION(value_node<y<x>>* node, symbol_table& symbols)

//template owning_ref<set<y<x1>, x2>> evaluate_expression(expression<set<y<x1>, x2>>& node, symbol_table& symbols);
//template owning_ref<set<y<x1>, x2>> evaluate_expression(value_node<set<y<x1>, x2>>* node, symbol_table& symbols);
#define GEN_EVALUATOR_2 GEN_INT(LIBALE_MAX_DIM, GEN_EVALUATOR_2_1)
#define GEN_EVALUATOR_2_1(x) GEN_DOUBLEINT(LIBALE_MAX_SET_DIM, GEN_EVALUATOR_2_2, x)
#define GEN_EVALUATOR_2_2(x1,x2) GEN_SETTYPE(GEN_EVALUATOR_2_3, x1, x2) 
#define GEN_EVALUATOR_2_3(xy) TEMPLATE OWNING_REF(SINGLE_ARG(xy)) EVALUATE_EXPRESSION(SINGLE_ARG(expression<xy>& node), symbol_table& symbols) TEMPLATE OWNING_REF(SINGLE_ARG(xy)) EVALUATE_EXPRESSION(SINGLE_ARG(value_node<xy>* node), symbol_table& symbols)


// EXECUTE -------------------------------------
GEN_EVALUATOR

//For an tutorial on how to add additional forward declarations, see config.hpp