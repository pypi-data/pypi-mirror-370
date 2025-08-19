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

#include <map>

#include "util/visitor_utils.hpp"
#include "util/evaluator.hpp"
#include "symbol_table.hpp"

namespace ale {

  
    /**
     * Returns if the tree with root node is constant.
     * count_parameters_as_constant is set to false in differentiation, since there, we might want to differentiate wrt. parameters
     */
    bool is_tree_constant(value_node_variant node, symbol_table& symbols, bool count_parameters_as_constant = true);

    //
    // get_subtree_value
    //

    /**
     * If the tree starting with node is constant return its evaluation.
     */
    template <typename TType>
    std::optional<owning_ref<TType>> get_subtree_value(value_node<TType>* node, symbol_table& symbols) {
        // if node is constant evaluate it with an empty symbol table and return the value
        if (is_tree_constant(node, symbols)) {
            return util::evaluate_expression(node, symbols);
        }

        // return nothing
        return {};
    }

}    