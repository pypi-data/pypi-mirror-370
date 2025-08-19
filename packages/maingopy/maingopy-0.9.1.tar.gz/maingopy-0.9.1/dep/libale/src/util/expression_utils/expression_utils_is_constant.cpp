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

#include "node.hpp"
#include "util/visitor_utils.hpp"
#include "expression_utils_is_constant.hpp"

namespace ale {

    /**
     * Checks if a tree contains any parameter_nodes
     */
    struct is_tree_constant_visitor {
        is_tree_constant_visitor(symbol_table& symbols, bool parameters_count_as_constant=true): symbols(symbols), count_parameters_as_constant(parameters_count_as_constant) {}
        template <typename TType>
        void operator()(value_node<TType>* node) {
            traverse_children(*this, node, symbols);
        }

        template <typename TType>
        void operator()(function_node<TType>* node) {
            auto* sym = cast_function_symbol<TType>(symbols.resolve(node->name));
            if (sym == nullptr) {
                throw std::invalid_argument("function symbol " + node->name + " is ill-defined");
            }

            std::map<std::string, value_node_variant> arg_map;
            auto args = extract_function_arguments(node);
            for (int i = 0; i < args.size(); ++i) {
                arg_map.emplace(sym->arg_names.at(i), args.at(i));
            }

            auto expr_copy = sym->expr;
            replace_parameters(expr_copy, arg_map);

            return call_visitor(*this, expr_copy);
        }

        template <typename TType>
        void operator()(parameter_node<TType>* node) {
            auto* sym = symbols.resolve(node->name);
            if (sym == nullptr) {
                throw std::invalid_argument("parameter symbol " + node->name + " is ill-defined");
            }
            call_visitor(*this, sym);
        }

        template <typename TType>
        void operator()(parameter_symbol<TType>* sym) {
            if (!count_parameters_as_constant || sym->m_is_placeholder) {
                is_constant = false;
            }
        }

        template <typename TType>
        void operator()(variable_symbol<TType>* sym) {
            is_constant = false;
        }

        template <typename TType>
        void operator()(multiplication_node* node) {
            // iterate over children
            for(const auto& f : node->children) {
                auto f_var = f->get_variant();
                ///if multiply with a constant zero whole expression is constant 0
                if(std::holds_alternative<constant_node<real<0>>*>(f_var)) {
                    constant_node<real<0>>* f_const = std::get<constant_node<real<0>>*>(f_var);
                    if(f_const->value == 0.0) {
                        //no need to look at any other children
                        return;
                    }
                }
            }
            traverse_children(*this, node, symbols);
        }


        template <typename TType>
        void operator()(expression_symbol<TType>* sym) {
            call_visitor(*this, sym->m_value);
        }

        template <typename TType>
        void operator()(function_symbol<TType>* sym) {
            throw std::invalid_argument("function_symbol should not be encountered");
        }

        bool is_constant = true;
        bool count_parameters_as_constant;
        symbol_table& symbols;
    };

    bool is_tree_constant(value_node_variant node, symbol_table& symbols, bool count_parameters_as_constant) {
        is_tree_constant_visitor visitor(symbols, count_parameters_as_constant);
        call_visitor(visitor, node);

        return visitor.is_constant;
    }

}
