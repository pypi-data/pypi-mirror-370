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
 
#include "expression_to_string.hpp"
#include <type_traits>

#include "visitor_utils.hpp"

namespace ale {

    /**
     * Combine strings in an infix-style
     * 
     * returns strings like: (1 + 2 + 3)
     */
    inline std::string combine_strings_infix(const std::string& op_string, const std::vector<std::string>& values) {
        // put everything in brackets
        std::string out = "(";

        if (!values.empty()) {

            // add values to out seperated by op_string
            for (const auto& s : values) {
                out += s + op_string;
            }

            // remove last operator
            out.erase(out.end() - op_string.size(), out.end());

        }

        // close bracket
        out += ")";

        return out;
    }

    /**
     * Combine results in a function-like style
     * 
     * returns strings like: f(x, y, z)
     */
    inline std::string combine_strings_function(const std::string& f_name, const std::vector<std::string>& values) {
        return f_name + combine_strings_infix(", ", values);
    }

    template <typename TType>
    std::string constant_to_string(cref_type<TType> value);

    /**
     * Returns a string representation of any tensor
     */
    template <typename TType>
    std::string tensor_to_string(cref_type<TType> value) {
        if constexpr (get_node_dimension<TType> == 0) {
            return std::to_string(value);
        } else {
            std::vector<std::string> tensor_elements;
            for (size_t i = 0; i < value.shape(0); ++i) {
                tensor_elements.push_back(constant_to_string<entry_of<TType>>(value[i]));
            } 
            return combine_strings_infix(", ", tensor_elements);
        }
    }

    /**
     * Returns a string representation of any tensor or set
     */
    template <typename TType>
    std::string constant_to_string(cref_type<TType> value) {
        if constexpr (is_real_node<TType> || is_boolean_node<TType> || is_index_node<TType>) {
            return tensor_to_string<TType>(value);
        } else {
            using set_elem = typename TType::atom_type::element_type;

            if constexpr (get_node_dimension<TType> == 0) {
                // construct {a, b, c, ...} representation for set
                std::string str_value = "{";
                for (auto it = value.begin(); it != value.end(); ++it) {
                    if (it != value.begin()) {
                        str_value += ", ";
                    }

                    str_value += tensor_to_string<set_elem>(*it);
                }
                str_value += "}";

                return str_value;
            } else {
                return tensor_to_string<TType>(value);
            }
        }
    }

    struct expression_to_string_visitor {
        // nary-nodes
        template <typename TType>
        std::string operator()(nary_node<TType>* node) {
            auto children = evaluate_children(*this, node);
            return combine_strings_function("unprintable_node", children);
        }

        std::string operator()(addition_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_infix(" + ", children_values);
        }

        std::string operator()(multiplication_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_infix(" * ", children_values);
        }

        std::string operator()(exponentiation_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_infix(" ^ ", children_values);
        }

        std::string operator()(min_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("min", children_values);
        }
        
        std::string operator()(max_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("max", children_values);
        }

        std::string operator()(index_addition_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_infix(" + ", children_values);
        }

        std::string operator()(index_multiplication_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_infix(" * ", children_values);
        }

        std::string operator()(disjunction_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_infix(" | ", children_values);
        }

        std::string operator()(conjunction_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_infix(" & ", children_values);
        }

        std::string operator()(sum_div_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("sum_div", children_values);
        }

        std::string operator()(xlog_sum_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("xlog_sum", children_values);
        }

        std::string operator()(single_neuron_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("single_neuron", children_values);
        }

        template <typename TType>
        std::string operator()(tensor_node<TType>* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_infix(", ", children_values);
        }

        template <typename TType>
        std::string operator()(function_node<TType>* node) {
            // see operator()(vector_node)
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function(node->name, children_values);
        }

        template <typename TType>
        std::string operator()(vector_node<TType>* node) {
            // this assumes that a vector node is only encountered as arguments of a function_node
            // so it can just be ignored and evaluated normally 
            return evaluate_child(*this, node);
        }

        // kary-nodes
        template <typename... TTypes>
        std::string operator()(kary_node<TTypes...>* node) {
            auto children = evaluate_children(*this, node);
            return combine_strings_function("unimplemented_node", children);
        }

        // unary nodes
        std::string operator()(round_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("round", children_values);
        }

        std::string operator()(index_to_real_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("as_real", children_values);
        }

        std::string operator()(real_to_index_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("as_index", children_values);
        }

        std::string operator()(minus_node* node) {
            auto child_value = evaluate_child(*this, node);
            return "(- " + child_value + ")";
        }

        std::string operator()(index_minus_node* node) {
            auto child_value = evaluate_child(*this, node);
            return "(- " + child_value + ")";
        }

        std::string operator()(inverse_node* node) {
            auto child_value = evaluate_child(*this, node);
            return "(1 / " + child_value + ")";
        }

        std::string operator()(negation_node* node) {
            auto child_value = evaluate_child(*this, node);
            return "(! " + child_value + ")";
        }

        std::string operator()(abs_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("abs", children_values);
        }

        std::string operator()(xabsx_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("xabsx", children_values);
        }

        std::string operator()(exp_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("exp", children_values);
        }

        std::string operator()(log_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("log", children_values);
        }

        std::string operator()(xlogx_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("xlogx", children_values);
        }

        std::string operator()(sqrt_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("sqrt", children_values);
        }

        std::string operator()(sin_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("sin", children_values);
        }

        std::string operator()(asin_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("asin", children_values);
        }

        std::string operator()(cos_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("cos", children_values);
        }

        std::string operator()(acos_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("acos", children_values);
        }

        std::string operator()(tan_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("tan", children_values);
        }

        std::string operator()(atan_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("atan", children_values);
        }

        std::string operator()(cosh_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("cosh", children_values);
        }

        std::string operator()(sinh_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("sinh", children_values);
        }

        std::string operator()(tanh_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("tanh", children_values);
        }

        std::string operator()(coth_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("coth", children_values);
        }

        std::string operator()(acosh_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("acosh", children_values);
        }

        std::string operator()(asinh_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("asinh", children_values);
        }

        std::string operator()(atanh_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("atanh", children_values);
        }

        std::string operator()(acoth_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("acoth", children_values);
        }

        std::string operator()(erf_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("erf", children_values);
        }

        std::string operator()(erfc_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("erfc", children_values);
        }

        std::string operator()(pos_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("pos", children_values);
        }

        std::string operator()(neg_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("neg", children_values);
        }

        std::string operator()(schroeder_ethanol_p_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("schroeder_ethanol_p", children_values);
        }

        std::string operator()(schroeder_ethanol_rhovap_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("schroeder_ethanol_rhovap", children_values);
        }

        std::string operator()(schroeder_ethanol_rholiq_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("schroeder_ethanol_rholiq", children_values);
        }

        std::string operator()(covar_matern_1_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("covar_matern_1", children_values);
        }

        std::string operator()(covar_matern_3_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("covar_matern_3", children_values);
        }
        std::string operator()(covar_matern_5_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("covar_matern_5", children_values);
        }
        std::string operator()(covar_sqrexp_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("covar_sqrexp", children_values);
        }

        std::string operator()(gpdf_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("gpdf", children_values);
        }

        template <typename TType>
        std::string operator()(index_shift_node<TType>* node) {
            // this generates [:][:][1] instead of [:,:,1] but should be similiar enough
            auto child_value = evaluate_child(*this, node);
            return child_value + "[:]";
        }

        // binary nodes
        template <typename TType>
        std::string operator()(entry_node<TType>* node) {
            auto [tensor, index] = evaluate_children_tuple(*this, node);
            return tensor + "[" + index + "]";
        }

        std::string operator()(xexpy_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("xexpy", children_values);
        }

        std::string operator()(xexpax_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("xexpax", children_values);
        }

        std::string operator()(lmtd_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("lmtd", children_values);
        }

        std::string operator()(rlmtd_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("rlmtd", children_values);
        }

        std::string operator()(arh_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("arh", children_values);
        }

        std::string operator()(norm2_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("norm2", children_values);
        }

        std::string operator()(lb_func_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("lb_func", children_values);
        }

        std::string operator()(ub_func_node* node) {
            auto children_values = evaluate_children(*this, node);
            return combine_strings_function("ub_func", children_values);
        }

        template <typename TType>
        std::string operator()(equal_node<TType>* node) {
            auto [lhs, rhs] = evaluate_children_tuple(*this, node);
            return "(" + lhs + " == " + rhs + ")";
        }

        template <typename TType>
        std::string operator()(less_node<TType>* node) {
            auto [lhs, rhs] = evaluate_children_tuple(*this, node);
            return "(" + lhs + " < " + rhs + ")";
        }

        template <typename TType>
        std::string operator()(less_equal_node<TType>* node) {
            auto [lhs, rhs] = evaluate_children_tuple(*this, node);
            return "(" + lhs + " <= " + rhs + ")";
        }

        template <typename TType>
        std::string operator()(greater_node<TType>* node) {
            auto [lhs, rhs] = evaluate_children_tuple(*this, node);
            return "(" + lhs + " > " + rhs + ")";
        }

        template <typename TType>
        std::string operator()(greater_equal_node<TType>* node) {
            auto [lhs, rhs] = evaluate_children_tuple(*this, node);
            return "(" + lhs + " >= " + rhs + ")";
        }

        template <typename TType>
        std::string operator()(element_node<TType>* node) {
            auto [elem, s] = evaluate_children_tuple(*this, node);
            return "(" + elem + " in " + s + ")";
        }

        // iterator nodes
        template <typename IteratorType>
        std::string operator()(sum_node<IteratorType>* node) {
            auto children_values = evaluate_children(*this, node);
            return "sum(" + node->name + " in " + children_values[0] + ": " + children_values[1] + ")";
        }

        template <typename IteratorType>
        std::string operator()(product_node<IteratorType>* node) {
            auto children_values = evaluate_children(*this, node);
            return "product(" + node->name + " in " + children_values[0] + ": " + children_values[1] + ")";
        }

        template <typename IteratorType>
        std::string operator()(set_min_node<IteratorType>* node) {
            auto children_values = evaluate_children(*this, node);
            return "min(" + node->name + " in " + children_values[0] + ": " + children_values[1] + ")";
        }

        template <typename IteratorType>
        std::string operator()(set_max_node<IteratorType>* node) {
            auto children_values = evaluate_children(*this, node);
            return "max(" + node->name + " in " + children_values[0] + ": " + children_values[1] + ")";
        }

        template <typename IteratorType>
        std::string operator()(forall_node<IteratorType>* node) {
            auto children_values = evaluate_children(*this, node);
            return "(forall " + node->name + " in " + children_values[0] + ": " + children_values[1] + ")";
        }

        template <typename IteratorType>
        std::string operator()(indicator_set_node<IteratorType>* node) {
            auto children_values = evaluate_children(*this, node);
            return "{" + node->name + " in " + children_values[0] + ": " + children_values[1] + ")";
        }

        //
        // leaf nodes
        //

        template <typename TType>
        std::string operator()(parameter_node<TType>* node) {
            return node->name;
        }

        template <typename TType>
        std::string operator()(attribute_node<TType> *node) {
            
            std::string attribute_string;
            switch (node->attribute) {
            case variable_attribute_type::INIT:
                attribute_string = "init";
                break;
            case variable_attribute_type::PRIO:
                attribute_string = "prio";
                break;
            case variable_attribute_type::UB:
                attribute_string = "ub";
                break;
            case variable_attribute_type::LB:
                attribute_string = "lb";
                break;
            default:
                throw std::invalid_argument("unknown attribute requested for symbol: " + node->variable_name);
            }
            return node->variable_name + "." + attribute_string;
        }

        template <typename TType>
        std::string operator()(constant_node<TType>* node) {
            return constant_to_string<TType>(node->value);
        }

    };

    struct symbol_to_string_visitor {
        /**
         * Returns the dimension of TType as a wildcard
         * ie index<0> -> ""
         *    real<1> -> "[:]"
         *    boolean<2> -> "[:,:]"
         *    set<real<0>, 2> -> "[:,:]"
         */
        template <typename TType>
        std::string wildcard_string() {
            std::string wildcard;
            if constexpr (get_node_dimension<TType> > 0) {
                wildcard += "[";
                for (size_t i = 0; i < get_node_dimension<TType>; ++i) {
                    if (i != 0) {
                        wildcard += ",";
                    }
                    wildcard += ":";
                }
                wildcard += "]";
            }

            return wildcard;
        }

        /**
         * Returns TType converted to a string without dimension
         * ie real<0> -> "real"
         *    index<1> -> "index"
         *    set<real<0>, 1> -> "set{real}"
         *    set<real<1>, 0> -> "set{real[:]}"
         */
        template <template <typename> typename SymType, typename TType>
        std::string type_to_string(SymType<TType>* sym) {
            std::string type_string;
            if constexpr (is_real_node<TType>) {
                if constexpr (std::is_same_v<SymType<TType>, variable_symbol<TType>>) {
                    if (sym->integral()) {
                        type_string = "integer";
                    } else {
                        type_string = "real";
                    }
                } else {
                    type_string = "real";
                }
            } else if constexpr (is_index_node<TType>) {
                type_string = "index";
            } else if constexpr (is_boolean_node<TType>) {
                type_string = "boolean";
            } else {
                using set_elem = typename TType::atom_type::element_type;
                type_string = "set";
                if constexpr (is_real_node<set_elem>) {
                    type_string += "{real" + wildcard_string<set_elem>() + "}";
                } else if constexpr (is_index_node<set_elem>) {
                    type_string += "{index" + wildcard_string<set_elem>() + "}";
                } else {
                    type_string += "{boolean" + wildcard_string<set_elem>() + "}";
                }
            }

            return type_string;
        }

        template <typename TType>
        std::string operator()(parameter_symbol<TType>* sym) {
            if constexpr (get_node_dimension<TType> == 0) {
                if (sym->m_is_placeholder) {
                    return type_to_string(sym) + " " + sym->m_name + "(Placeholder)";
                }
                return type_to_string(sym) + " " + sym->m_name + " <- " + constant_to_string<TType>(sym->m_value);
            } else {
                std::string shape_string = std::to_string(sym->m_value.shape(0));
                for (size_t i = 1; i < get_node_dimension<TType>; ++i) {
                    shape_string += ", " + std::to_string(sym->m_value.shape(i));
                }

                if (sym->m_is_placeholder) {
                    return type_to_string(sym) + "[" + shape_string + "] " + sym->m_name + "(Placeholder)";
                }
                return type_to_string(sym) + "[" + shape_string + "] " + sym->m_name + " <- " + constant_to_string<TType>(sym->m_value);
            }
        }

        template <typename TType>
        std::string operator()(variable_symbol<TType>* sym) {
            std::string comment = "";
            if (!(sym->comment().empty())) {
                comment = " \"" + sym->comment() + "\"";
            }

            if constexpr (get_node_dimension<TType> == 0) {
                return type_to_string(sym) + " " + sym->m_name + " in [" + std::to_string(sym->lower()) + ", " + std::to_string(sym->upper()) + "] <- " + std::to_string(sym->init()) + comment;
            } else {
                std::string shape_string = std::to_string(sym->shape(0));
                for (size_t i = 1; i < get_node_dimension<TType>; ++i) {
                    shape_string += ", " + std::to_string(sym->shape(i));
                }
                return type_to_string(sym) + " " + sym->m_name + "[" + shape_string + "]" + " in [" + tensor_to_string<TType>(sym->lower()) + ", " + tensor_to_string<TType>(sym->upper()) + "] <- " + tensor_to_string<TType>(sym->init()) + comment;
            }
        }

        template <typename TType>
        std::string operator()(expression_symbol<TType>* sym) {
            return "(expression symbol) " + type_to_string(sym) + wildcard_string<TType>() + " " + sym->m_name + " := " + expression_to_string(sym->m_value); 
        }

        template <typename TType>
        std::string operator()(function_symbol<TType>* sym) {
            std::vector<std::string> func_args;
            for (size_t i = 0; i < sym->arg_names.size(); ++i) {
                std::string arg = type_to_string(sym) + " " + sym->arg_names.at(i);
                
                if (sym->arg_dims.at(i) > 0) {
                    arg += "[";

                    const auto& shape = sym->arg_shapes.at(i);
                    const auto& wildcards = sym->arg_wildcards.at(i);
                    for (int j = 0; j < shape.size(); ++j) {
                        // check wether dimension j is a wildcard
                        if (std::find(wildcards.begin(), wildcards.end(), j) != wildcards.end()) {
                            arg += ":";
                        } else {
                            arg += std::to_string(shape.at(j));
                        }

                        if (j + 1 < shape.size()) {
                            arg += ", ";
                        }
                    }

                    arg += "]";
                }
                func_args.push_back(arg);
            }

            std::string result_shape;
            if (get_node_dimension<TType> > 0) {
                result_shape += "[";

                for (int j = 0; j < sym->result_shape.size(); ++j) {
                    // check wether dimension j is a wildcard
                    if (std::find(sym->result_wildcards.begin(), sym->result_wildcards.end(), j) != sym->result_wildcards.end()) {
                        result_shape += ":";
                    } else {
                        result_shape += std::to_string(sym->result_shape.at(j));
                    }

                    if (j + 1 < sym->result_shape.size()) {
                        result_shape += ", ";
                    }
                }

                result_shape += "]";
            }

            return "(function symbol) " + type_to_string(sym) + result_shape + " " + combine_strings_function(sym->m_name, func_args) + ":= " + expression_to_string(sym->expr);
        }
    };

    std::string expression_to_string(value_node_ptr_variant expr) {
        return call_visitor(expression_to_string_visitor{}, expr);
    }

    std::string expression_to_string(value_node_variant node) {
        return call_visitor(expression_to_string_visitor{}, node);
    }

    std::string symbol_to_string(base_symbol* sym) {
        return call_visitor(symbol_to_string_visitor{}, sym);
    }

} // namespace ale
