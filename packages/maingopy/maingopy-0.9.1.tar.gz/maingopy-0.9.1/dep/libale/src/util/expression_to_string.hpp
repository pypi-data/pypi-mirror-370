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

#include <string>

#include "node.hpp"
#include "symbol.hpp"
#include "expression.hpp"

namespace ale {

    std::string expression_to_string(value_node_ptr_variant expr);
    std::string expression_to_string(value_node_variant node);

    template <typename TType>
    std::string expression_to_string(expression<TType>& expr) {
        return expression_to_string(expr.get_root());
    }

    std::string symbol_to_string(base_symbol* sym);

}
