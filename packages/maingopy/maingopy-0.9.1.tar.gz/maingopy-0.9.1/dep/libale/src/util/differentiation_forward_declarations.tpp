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
#define GEN_DIFFERENTIATION GEN_DIFFERENTIATION_1

//template value_node_ptr<real<x2 + x1 - x3>> differentiate_expression<x1>(const value_node_ptr<real<x2>>& expr, std::string variable_name, const std::array<size_t, x3>& index, symbol_table& symbols);
#define GEN_DIFFERENTIATION_1 GEN_INT(LIBALE_MAX_DIM, GEN_DIFFERENTIATION_1_1) 
#define GEN_DIFFERENTIATION_1_1(idim) GEN_DOUBLEINT(LIBALE_MAX_DIM, GEN_DIFFERENTIATION_1_2, idim)
#define GEN_DIFFERENTIATION_1_2(idim, vardim) GEN_TRIPLEINT(vardim, GEN_DIFFERENTIATION_1_3, idim, vardim)
#define GEN_DIFFERENTIATION_1_3(idim, vardim, fixeddim) TEMPLATE VALUE_NODE_PTR(real<idim+vardim-fixeddim>) DIFFERENTIATE_EXPRESSION(vardim, CONST VALUE_NODE_PTR(real<idim>)& expr, std::string variable_name, SINGLE_ARG(const std::array<size_t, fixeddim>& index), symbol_table& symbols)

// EXECUTE -------------------------------------
GEN_DIFFERENTIATION
