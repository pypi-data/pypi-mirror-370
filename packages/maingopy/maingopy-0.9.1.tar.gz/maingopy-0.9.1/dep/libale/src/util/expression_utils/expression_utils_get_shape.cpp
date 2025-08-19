#include "expression_utils_get_shape.hpp"
#include "util/visitor_utils.hpp"
#include "util/evaluator.hpp"
namespace ale {
     /** 
     * Sets the member shape to the shape of the first visited symbol.
     */
    struct get_parameter_shape_visitor {
        get_parameter_shape_visitor(symbol_table& symbols): symbols(symbols) {}

        template <typename TType>
        void operator()(function_symbol<TType>* sym) {
            throw std::invalid_argument("shape of function_symbol cannot be known. Tried to retrieve shape of function_symbol \"" + sym->m_name + "\"");
        }

        template <typename TType>
        void operator()(expression_symbol<TType>* sym) {
            shape = get_expression_shape(sym->m_value.get(), symbols);
        }

        template <typename TType>
        void operator()(parameter_symbol<TType>* sym) {
            if constexpr (get_node_dimension<TType> == 0) {
                if constexpr (is_set_node<TType>) {
                    if constexpr (get_node_dimension<element_type<TType>> == 0) {
                        shape = {};
                        for (const auto& x: sym->m_value) {
                            shape.push_back(0);
                        }
                    } else {
                        shape = {};
                        for (const auto& x: sym->m_value) {
                            auto subshape = x.shape();
                            shape.insert(shape.end(), subshape.begin(), subshape.end());
                        }
                    }
                } else {
                    shape = {};
                }
            } else {
                // convert shape to vector
                auto sym_shape = sym->m_value.shape();
                shape.resize(sym_shape.size());
                std::copy_n(sym_shape.begin(), sym_shape.size(), shape.begin());
            }
        }

        template <typename TType>
        void operator()(variable_symbol<TType>* sym) {
            if constexpr (get_node_dimension<TType> == 0) {
                shape = {};
            } else {
                // convert shape to vector
                auto sym_shape = sym->shape();
                shape.resize(sym_shape.size());
                std::copy_n(sym_shape.begin(), sym_shape.size(), shape.begin());
            }
        }

        std::vector<size_t> shape;
        symbol_table& symbols;
    };

    std::vector<size_t> get_parameter_shape(const std::string& name, symbol_table& symbols) {
        // try to find symbol
        base_symbol* sym = symbols.resolve(name);
        if (sym != nullptr) {
            // get shape of symbol and return it
            get_parameter_shape_visitor visitor(symbols);
            call_visitor(visitor, sym);

            return visitor.shape;
        }
        throw std::invalid_argument("Could not retrieve parameter shape of variable \"" + name + "\" because it does not exist in symbol_table");
    }

    struct get_element_dimension {
        template <typename TType>
        size_t operator()(value_symbol<TType>* node) {
            throw std::invalid_argument("only 0-dimensional sets expected");
        }

        template <typename TType>
        size_t operator()(function_symbol<TType>* node) {
            throw std::invalid_argument("only 0-dimensional sets expected");
        }

        template <typename TType>
        size_t operator()(parameter_symbol<set<TType, 0>>* node) {
            return get_node_dimension<TType>;
        }
    };

    std::vector<std::vector<size_t>> get_set_shape(const std::string& name, symbol_table& symbols) {
        auto dim = call_visitor(get_element_dimension{}, symbols.resolve(name));
        auto flattened_shape = get_parameter_shape(name, symbols);

        if (flattened_shape.size() % dim != 0) {
            throw std::invalid_argument("shape entries not a multiple of entry dimension");
        }

        std::vector<std::vector<size_t>> shape;
        for (int i = 0; i < flattened_shape.size() / dim; i++) {
            for (int j = 0; j < dim; j++) {
                std::vector<size_t> subshape(flattened_shape.begin() + i * dim, flattened_shape.begin() + (i + 1) * dim);
                shape.push_back(subshape);
            }
        }

        return shape;
    }

    class expression_shape_visitor {
    public:
        expression_shape_visitor(symbol_table& symbols): symbols(symbols) {}

        template <typename TType>
        std::vector<size_t> operator()(constant_node<TType>* node) {
            std::vector<size_t> shape;
            
            if constexpr (get_node_dimension<TType> != 0) {
                for (auto k: node->value.shape()) {
                    shape.push_back(k);
                }
            }

            return shape;
        }

        template <typename TType>
        std::vector<size_t> operator()(value_node<TType>* node) {
            if constexpr (get_node_dimension<TType> == 0) {
                return {};
            } else {
                throw std::invalid_argument("any node with non-scalar return type should be overloaded");
            }
        }

        template <typename TType>
        std::vector<size_t> operator()(parameter_node<TType>* node) {
            return get_parameter_shape(node->name, symbols);
        }

        template <unsigned IDim>
        std::vector<size_t> operator()(attribute_node<real<IDim>>* node) {
            variable_symbol<real<IDim>>* sym = cast_variable_symbol<real<IDim>>(symbols.resolve(node->variable_name));
            if (!sym) {
                throw std::invalid_argument("symbol " + node->variable_name + " has unexpected type in attribute call within expression shape visitor");
            }
            return get_parameter_shape(node->variable_name, symbols);
        }

        template <typename TType>
        std::vector<size_t> operator()(entry_node<TType>* node) {
            auto child_shape = call_visitor(*this, node->template get_child<0>());
            return std::vector<size_t>{child_shape.begin() + 1, child_shape.end()};
        }

        template <typename TType>
        std::vector<size_t> operator()(function_node<TType>* node) {
            auto* sym = cast_function_symbol<TType>(symbols.resolve(node->name));
            if (sym == nullptr) {
                throw std::invalid_argument("functionsymbol " + node->name + " is ill-defined");
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
        std::vector<size_t> operator()(tensor_node<TType>* node) {
            if (node->children.size() == 0) {
                throw std::invalid_argument("tensor_node without children encountered");
            }

            // assume all children have equal shape
            auto child_shape = call_visitor(*this, node->children.front());
            child_shape.insert(child_shape.begin(), node->children.size());
            return child_shape;
        }

        template <typename TType>
        std::vector<size_t> operator()(index_shift_node<TType>* node) {
            auto child_shape = call_visitor(*this, node->template get_child<0>());
            std::rotate(child_shape.begin(), child_shape.begin() + 1, child_shape.end());
            return child_shape;
        }

        template <typename TType>
        std::vector<size_t> operator()(vector_node<TType>* node) {
            throw std::invalid_argument("vector_node should not be encountered");
        }

    private:
        symbol_table& symbols;
    };

    std::vector<size_t> get_expression_shape(value_node_variant expr, symbol_table& symbols) {
        return call_visitor(expression_shape_visitor{symbols}, expr);
    }

    std::vector<size_t> get_expression_shape(value_node_ptr_variant expr, symbol_table &symbols){
        return call_visitor(expression_shape_visitor{symbols}, expr);
    }

}