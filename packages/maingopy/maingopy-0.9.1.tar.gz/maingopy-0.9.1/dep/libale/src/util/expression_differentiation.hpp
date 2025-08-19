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
#pragma once

#include <array>
#include <cstddef>          // for size_t
#include <string>            // for string
#include "node.hpp"          // for value_node_ptr
#include "value.hpp"         // for real

#include "symbol_table.hpp"

namespace ale {

/**
 * Differentiate value_node_ptr with respect to all unspecified indexes.
 * 
 * VarDim: dimension of the parameter being differentiated (cannot be deduced)
 */
template <unsigned VarDim, unsigned IDim, size_t FixedDim = 0>
value_node_ptr<real<IDim + (VarDim - FixedDim)>> differentiate_expression(const value_node_ptr<real<IDim>>& expr, std::string variable_name, const std::array<size_t, FixedDim>& index, symbol_table& symbols);

}  // namespace ale
