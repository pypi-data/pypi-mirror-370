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

#include "visitor_utils.hpp"
#include "symbol.hpp"
#include "util/expression_to_string.hpp"

namespace ale {
    struct clone_visitor {
        template <typename TType>
        value_node_variant operator()(value_node<TType>* node) {
            return node->clone();
        }
    };

    value_node_variant clone_value_node_ptr_variant(value_node_ptr_variant node) {
        return call_visitor(clone_visitor{}, node);
    }

    value_node_variant clone_value_node_variant(value_node_variant node) {
        return call_visitor(clone_visitor{}, node);
    }

    void reset_value_node_ptr_variant(value_node_ptr_variant old_node, value_node_ptr_variant new_node) {
        reset_value_node_ptr_variant(old_node, clone_value_node_ptr_variant(new_node));
    }

    class reset_visitor {
    public:
        reset_visitor(value_node_ptr_variant old_node): old_node(old_node) {}
        template<class V>
        std::type_info const& var_type(V const& v){
          return std::visit( [](auto&&x)->decltype(auto){ return typeid(x); }, v );
        }

        template <typename TType>
        void operator()(value_node<TType>* new_node) {
            try {
                // try to extract a value_node_ptr with same TType as new_node
                auto old_node_ptr_typed = std::get<std::reference_wrapper<value_node_ptr<TType>>>(old_node);
                old_node_ptr_typed.get().reset(new_node);
            } catch (std::bad_variant_access const& /*ex*/) {
                if constexpr(is_real_node<TType> && ! is_set_node<TType>)
                { 
                throw std::invalid_argument("type of new node " + std::string(symbol_to_string(new expression_symbol<TType>("name",new_node)) ) + " has to match the type " + std::string(var_type(old_node).name()) + "of replaced node " + expression_to_string(old_node));
                }
            }
        }

    private:
        value_node_ptr_variant old_node;
    };

    void reset_value_node_ptr_variant(value_node_ptr_variant old_node, value_node_variant new_node) {
        reset_visitor visitor(old_node);
        std::visit(visitor, new_node);
    }

} // namespace ale
