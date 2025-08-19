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
#include "util/visitor_utils.hpp"
#include "expression_utils_replace_constant.hpp"
#include "expression_utils_is_constant.hpp"

namespace ale {

        /**
     * replaces all constant subtrees with their evaluation
     */
    class replace_constant_subtrees_visitor {
    public:
        replace_constant_subtrees_visitor(symbol_table& symbols, value_node_ptr_variant root): symbols(symbols), current_node(root) {}

        template <typename TType>
        void operator()(value_node<TType>* node) {
            // get optional value of subtree
            auto tree_value = get_subtree_value(node, symbols);

            if (tree_value) {
                // create new constant node
                auto new_const = new constant_node<TType>(*tree_value);

                // replace node and if it cannot be replaced throw an error
                reset_value_node_ptr_variant(current_node, new_const);
            } else {
                // call this visitor on children as they could be constant
                traverse_children(*this, node, {}, current_node);
            }
        }

    private:
        symbol_table& symbols;
        value_node_ptr_variant current_node;
    };

    /**
     * Replaces all constant subtrees in expr
     */
    void replace_constant_subtrees(value_node_ptr_variant expr, symbol_table& symbols) {
        replace_constant_subtrees_visitor visitor(symbols, expr);
        call_visitor(visitor, expr);
    }

}
