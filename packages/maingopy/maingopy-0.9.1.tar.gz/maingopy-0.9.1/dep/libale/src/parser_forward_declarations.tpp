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

// main generator call, calls all subgenerators
#define GEN_PARSER                                                             \
  GEN_PARSER_1 GEN_PARSER_2 GEN_PARSER_3 GEN_PARSER_4 GEN_PARSER_5 GEN_PARSER_6

// template bool
// parser::match_derivative<real<x>>(std::unique_ptr<value_node<real<x>>>&
// result);
#define GEN_PARSER_1 GEN_INT(LIBALE_MAX_DIM, GEN_PARSER_1_1)
#define GEN_PARSER_1_1(x)                                                      \
  TEMPLATE GENBOOL PARSER_MATCH_DERIVATIVE(                                    \
      real<x>, UNIQUE_PTR_VALUE_NODE_2(real<x>, result))

// template bool parser::match_any_definition<x>();
#define GEN_PARSER_2 GEN_INT_N0(LIBALE_MAX_DIM, GEN_PARSER_2_1)
#define GEN_PARSER_2_1(x) TEMPLATE GENBOOL PARSER_MATCH_ANY_DEFINITION(x)

// template bool parser::match_any_assignment<x>();
#define GEN_PARSER_3 GEN_INT_N0(LIBALE_MAX_DIM, GEN_PARSER_3_1)
#define GEN_PARSER_3_1(x) TEMPLATE GENBOOL PARSER_MATCH_ANY_ASSIGNMENT(x)

// template bool parser::match_any_function_definition<x>();
#define GEN_PARSER_4 GEN_INT(LIBALE_MAX_DIM, GEN_PARSER_4_1)
#define GEN_PARSER_4_1(x) TEMPLATE GENBOOL PARSER_MATCH_ANY_FUNCTION_DEFINITION(x)

// template bool
// parser::match_expression<y<x>>(std::unique_ptr<value_node<y<x>>>& result);
// template bool
// parser::match_expression<y<x>>(std::unique_ptr<value_node<y<x>>>& result,
// std::string& lit);
#define GEN_PARSER_5 GEN_INT(LIBALE_MAX_DIM, GEN_PARSER_5_1)
#define GEN_PARSER_5_1(x) GEN_TYPE(GEN_PARSER_5_2, x)
#define GEN_PARSER_5_2(x, y)                                                   \
  TEMPLATE GENBOOL PARSER_MATCH_EXPRESSION(                                    \
      y<x>, UNIQUE_PTR_VALUE_NODE_1(x, y, result)) TEMPLATE GENBOOL            \
  PARSER_MATCH_EXPRESSION(                                                     \
      y<x>,                                                                    \
      SINGLE_ARG(UNIQUE_PTR_VALUE_NODE_1(x, y, result), std::string &lit))

// template bool parser::match_expression<set<y<x1>,
// x2>>(std::unique_ptr<value_node<set<y<x1>, x2>>>& result); template bool
// parser::match_expression<set<y<x1>,
// x2>>(std::unique_ptr<value_node<set<y<x1>, x2>>>& result, std::string& lit);
#define GEN_PARSER_6 GEN_INT(LIBALE_MAX_DIM, GEN_PARSER_6_1)
#define GEN_PARSER_6_1(x) GEN_DOUBLEINT(LIBALE_MAX_SET_DIM, GEN_PARSER_6_2, x)
#define GEN_PARSER_6_2(x1, x2) GEN_SETTYPE(GEN_PARSER_6_3, x1, x2)
#define GEN_PARSER_6_3(xy)                                                     \
  TEMPLATE GENBOOL PARSER_MATCH_EXPRESSION(                                    \
      SINGLE_ARG(xy), UNIQUE_PTR_VALUE_NODE_2(SINGLE_ARG(xy), result))         \
      TEMPLATE GENBOOL                                                         \
      PARSER_MATCH_EXPRESSION(                                                 \
          SINGLE_ARG(xy),                                                      \
          SINGLE_ARG(UNIQUE_PTR_VALUE_NODE_2(SINGLE_ARG(xy), result),          \
                     std::string &lit))

// EXECUTE -------------------------------------
GEN_PARSER

// For an tutorial on how to add additional forward declarations, see config.hpp
