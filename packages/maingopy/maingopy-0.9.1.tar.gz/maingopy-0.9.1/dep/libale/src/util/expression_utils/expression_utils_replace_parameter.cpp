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
#include "expression_utils_replace_parameter.hpp"
namespace ale {

    

 

    class find_parameter_visitor {
    public:
        find_parameter_visitor(const std::string& parameter_name, value_node_ptr_variant root): parameter_name(parameter_name), current_node(root) {}

        template <typename TType>
        void operator()(value_node<TType>* node) {
            traverse_children(*this, node, {}, current_node);
        }

        template <typename TType>
        void operator()(parameter_node<TType>* node) {
            if (node->name == parameter_name) {
                found_parameters.push_back(current_node);
            }
        }

        std::vector<value_node_ptr_variant> get_found_parameters() {
            return found_parameters;
        }

    private:
        std::string parameter_name;
        std::vector<value_node_ptr_variant> found_parameters{};
        value_node_ptr_variant current_node;
    };

    std::vector<value_node_ptr_variant> find_parameter(const std::string& parameter_name, value_node_ptr_variant expr) {
        find_parameter_visitor visitor(parameter_name, expr);
        call_visitor(visitor, expr);
        return visitor.get_found_parameters();
    }

    void replace_parameters(value_node_ptr_variant node, const std::map<std::string, value_node_variant>& arg_map) {
        for (const auto& [arg_name, arg_value]: arg_map) {
            auto parameters = find_parameter(arg_name, node);
            for (const auto& par: parameters) {
                reset_value_node_ptr_variant(par, clone_value_node_variant(arg_value));
            }
        }
    }
}
