#pragma once

#include <map>
#include "symbol_table.hpp"

namespace ale {

  


   

    /**
     * Find all parameters with the given name in the expression
     */
    std::vector<value_node_ptr_variant> find_parameter(const std::string& parameter_name, value_node_ptr_variant expr);

    /**
     * Replace any parameter in the expression with a name contained in the map with the corresponding value_node.
     * If the types do not match an error will be thrown.
     */
    void replace_parameters(value_node_ptr_variant node, const std::map<std::string, value_node_variant>& arg_map);

    /**
     * Replace any parameter in the expression with a name contained in the map with the corresponding value_node.
     * If the types do not match an error will be thrown.
     */
    template <typename TType>
    void replace_parameters(expression<TType>& expr, const std::map<std::string, value_node_variant>& arg_map) {
        replace_parameters(expr.get_root(), arg_map);
    }

}