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

#include <utility>                       // for index_sequence, make_index_sequence
#include <cstddef>                       // for size_t
#include <functional>                    // for reference_wrapper, invoke
#include <map>                           // for map
#include <optional>                      // for optional
#include <stdexcept>                     // for invalid_argument
#include <string>                        // for string
#include <tuple>                         // for apply, make_tuple
#include <type_traits>                   // for declval, remove_reference_t, is_same
#include <utility>                       // for forward
#include <variant>                       // for visit
#include <vector>                        // for vector
#include "expression.hpp"                // for expression
#include "helper.hpp"                    // for pick
#include "node.hpp"                      // for value_node_ptr_variant, value_node_variant, value_node_ptr, kary_node, value_node, function_node, iterator_...
#include "symbol.hpp"                    // for base_symbol, parameter_symbol, cast_function_symbol, function_symbol, value_symbol
#include "symbol_table.hpp"              // for symbol_table
#include "util/evaluator.hpp"            // for wrongDimensionException, evaluate_expression
#include "util/expression_to_string.hpp" // for expression_to_string
#include "util/renaming_util.hpp"
#include "value.hpp" // for set
#include "util/expression_utils.hpp"



namespace ale {
namespace helper {

    template <typename FuncType, typename TupleType, size_t... Is>
    constexpr decltype(auto) transform_each_impl(FuncType&& func, TupleType&& tuple, std::index_sequence<Is...>) {
        // invoke func on each element and construct a new tuple from the results
        return std::make_tuple(std::invoke(std::forward<FuncType>(func), std::get<Is>(std::forward<TupleType>(tuple)))...);
    }

} // namespace helper

/**
     * Applies a function to each element of a tuple.
     */
template <typename FuncType, typename TupleType>
constexpr decltype(auto) tuple_for_each(FuncType&& func, TupleType&& tuple) {
    // construct an index sequence with the length of the tuple
    using seq = std::make_index_sequence<std::tuple_size_v<std::remove_reference_t<TupleType>>>;

    // forward arguments with index sequence
    return ale::helper::transform_each_impl(std::forward<FuncType>(func), std::forward<TupleType>(tuple), seq {});
}

//allows to construct visitors inline using lambdas
// usage: std::visit(make_visitor([](double sym){//use double},[](std::string){//use string;},[](auto&& a){throw std::invalid_argument();});
//see https://bitbashing.io/std-visit.html  and https://arne-mertz.de/2018/05/overload-build-a-variant-visitor-on-the-fly/ for further information
template <class... Ts>
struct make_visitor : Ts... {
    using Ts::operator()...;
    make_visitor(Ts&&... ts) :
        Ts { std::forward<Ts>(ts) }... { }
    make_visitor(const make_visitor& old) = default;
};

template <class... Ts>
make_visitor(Ts&&...) -> make_visitor<std::remove_reference_t<Ts>...>;

//
// call visitor
//

/**
     * Call visitor on tree starting with node.
     */
template <typename TVisitor, typename TType>
decltype(auto) call_visitor(TVisitor&& visitor, value_node<TType>* node) {
    return std::visit(std::forward<TVisitor>(visitor), node->get_variant());
}

/**
     * Call visitor on root of expression.
     */
template <typename TVisitor, typename TType>
decltype(auto) call_visitor(TVisitor&& visitor, expression<TType>& expr) {
    return call_visitor(std::forward<TVisitor>(visitor), expr.get());
}

/**
     * Call visitor on node stored in node_ptr.
     */
template <typename TVisitor, typename TType>
decltype(auto) call_visitor(TVisitor&& visitor, value_node_ptr<TType>& node_ptr) {
    return call_visitor(std::forward<TVisitor>(visitor), node_ptr.get());
}

/**
     * Call visitor on value symbol.
     */
template <typename TVisitor, typename TType>
decltype(auto) call_visitor(TVisitor&& visitor, value_symbol<TType>* sym) {
    return std::visit(std::forward<TVisitor>(visitor), sym->get_value_variant());
}

/**
     * Call visitor on function symbol.
     */
template <typename TVisitor, typename TType>
decltype(auto) call_visitor(TVisitor&& visitor, function_symbol<TType>* sym) {
    return std::invoke(std::forward<TVisitor>(visitor), sym);
}

/**
     * Call visitor on base symbol.
     */
template <typename TVisitor>
decltype(auto) call_visitor(TVisitor&& visitor, base_symbol* sym) {
    return std::visit([&visitor](auto* s) { return call_visitor(std::forward<TVisitor>(visitor), s); }, sym->get_base_variant());
}

/**
     * Call visitor on value_node_variant.
     */
template <typename TVisitor>
decltype(auto) call_visitor(TVisitor&& visitor, value_node_variant node) {
    return std::visit([&visitor](auto* node) { return call_visitor(std::forward<TVisitor>(visitor), node); }, node);
}

/**
     * Call visitor on value_node_ptr_variant.
     */
template <typename TVisitor>
decltype(auto) call_visitor(TVisitor&& visitor, value_node_ptr_variant node) {
    return std::visit([&visitor](auto node) { return call_visitor(std::forward<TVisitor>(visitor), node.get().get()); }, node);
}

// TODO: reset current_node when exiting evaluate functions

/**
     * Evaluate the children of a nary_node using the visitor and return the results as a vector.
     * If current_node is passed it will always point to the same node that the visitor is called with.
     */
template <typename TVisitor, typename TType>
decltype(auto) evaluate_children(TVisitor&& visitor, nary_node<TType>* node, std::optional<std::reference_wrapper<value_node_ptr_variant>> current_node = {}) {
    // get return type when applying visitor to children
    using TResult = decltype(call_visitor(visitor, std::declval<value_node_ptr<TType>&>()));
    std::vector<TResult> results;

    // apply visitor to children and emplace the results onto the vector
    for(auto& child : node->children) {
        if(current_node) {
            current_node->get() = child;
        }

        results.emplace_back(call_visitor(std::forward<TVisitor>(visitor), child));
    }

    return results;
}

/**
     * Evaluate the children of a kary_node using the visitor and return the results as a vector.
     * So the visitor has to return the same type for every child, otherwise a compiler error will be thrown.
     * If current_node is passed it will always point to the same node that the visitor is called with.
     */
template <typename TVisitor, typename... TTypes>
decltype(auto) evaluate_children(TVisitor&& visitor, kary_node<TTypes...>* node, std::optional<std::reference_wrapper<value_node_ptr_variant>> current_node = {}) {
    // get return type of first child
    using FirstTType = typename pick<0, TTypes...>::type;
    using TResult = decltype(call_visitor(visitor, std::declval<value_node_ptr<FirstTType>&>()));
    std::vector<TResult> results;

    // assert that all children return the same type
    static_assert(std::conjunction_v<std::is_same<TResult, decltype(call_visitor(visitor, std::declval<value_node_ptr<TTypes>&>()))>...>,
      "The visitor does not return the same type for each child");

    // helper function to make the call to apply easier
    auto update_arg_and_traverse = [&visitor, &current_node, &results](auto&& arg) {
        // update current_node before calling the visitor so that current_node actually points to the node currently being evaluated
        if(current_node) {
            current_node->get() = arg;
        }

        // add result of visit to result vector
        results.emplace_back(call_visitor(std::forward<TVisitor>(visitor), arg));
    };

    // apply update_arg_and_traverse to each child
    std::apply([&update_arg_and_traverse](auto&&... args) { (update_arg_and_traverse(args), ...); }, node->children);

    return results;
}

/**
     * Evaluate the iteration-function over each value of the iteration-set and return the results as a vector.
     * If current_node is passed it will always point to the same node that the visitor is called with.
     */
template <typename TVisitor, typename IteratorType, typename TType>
decltype(auto) evaluate_children_iterated(TVisitor&& visitor, iterator_node<IteratorType, TType>* node, symbol_table& symbols, std::optional<std::reference_wrapper<value_node_ptr_variant>> current_node = {}) {
    // get return type when applying visitor to children
    using TResult = decltype(call_visitor(visitor, std::declval<value_node_ptr<TType>&>()));
    std::vector<TResult> results;

    auto elements = util::evaluate_expression(node->template get_child<0>(), symbols);
    symbols.push_scope();

    if(current_node) {
        current_node->get() = std::get<1>(node->children);
    }

    for(const auto& elem : elements) {
        symbols.define(node->name, new parameter_symbol<IteratorType>(node->name, elem));
        results.emplace_back(call_visitor(std::forward<TVisitor>(visitor), node->template get_child<1>()));
    }

    symbols.pop_scope();

    return results;
}

/**
     * Evaluate the children of a kary_node using the visitor and return the results as a tuple.
     * If current_node is passed it will always point to the same node that the visitor is called with.
     */
template <typename TVisitor, typename... TTypes>
decltype(auto) evaluate_children_tuple(TVisitor&& visitor, kary_node<TTypes...>* node, std::optional<std::reference_wrapper<value_node_ptr_variant>> current_node = {}) {
    // helper function to make the call to apply easier
    auto update_arg_and_traverse = [&visitor, &current_node](auto&& arg) {
        // update current_node before calling the visitor so that current_node actually points to the node currently being evaluated
        if(current_node) {
            current_node->get() = arg;
        }

        return call_visitor(std::forward<TVisitor>(visitor), arg);
    };

    // apply update_arg_and_traverse to each child and construct a tuple of the results
    return tuple_for_each(update_arg_and_traverse, node->children);
}

/**
     * Evaluate the child of a unary node and return the result.
     * If current_node is passed it will point to the child when the visitor is called with the child node.
     */
template <typename TVisitor, typename TType>
decltype(auto) evaluate_child(TVisitor&& visitor, kary_node<TType>* node, std::optional<std::reference_wrapper<value_node_ptr_variant>> current_node = {}) {
    if(current_node) {
        current_node->get() = std::get<0>(node->children);
    }
    return call_visitor(std::forward<TVisitor>(visitor), std::get<0>(node->children));
}

    /**
     * Replace all parameter_nodes in expression stored in the matching function_symbol, check
     * their shape and then evaluate that expression using the visitor and check the shape of the returned value.
     * Note: it is assumed that visitor is *this therefore current_node is not needed
     */
template <typename TVisitor, typename TType>
decltype(auto) evaluate_function(TVisitor&& visitor, function_node<TType>* node, symbol_table& symbols, bool checks = true) {
    auto* sym = cast_function_symbol<TType>(symbols.resolve(node->name));
    if(sym == nullptr) {
        throw std::invalid_argument("functionsymbol " + node->name + " is ill-defined");
    }

    std::map<std::string, value_node_variant> arg_map;
    auto args = extract_function_arguments(node);
    for(int i = 0; i < args.size(); ++i) {
        // construct arg_map
        arg_map.emplace(sym->arg_names.at(i), args.at(i));
        if(checks) {
            // check shape
            auto shape = get_expression_shape(args.at(i), symbols);
            const auto& expected_shape = sym->arg_shapes.at(i);
            const auto& expected_wildcards = sym->arg_wildcards.at(i);

            if(shape.size() != sym->arg_dims.at(i)) {
                throw ale::util::wrongDimensionException("Dimension or shape of argument \"" + sym->arg_names.at(i) + "\" does not match in \"" + expression_to_string(node) + "\"");
            }

            for(size_t k = 0; k < shape.size(); k++) {
                if(shape.at(k) != expected_shape.at(k)) {
                    // check for wildcard
                    auto it = std::find(expected_wildcards.begin(), expected_wildcards.end(), k);
                    if(it == expected_wildcards.end()) {
                        throw ale::util::wrongDimensionException("Dimension or shape of argument \"" + sym->arg_names.at(i) + "\" does not match in \"" + expression_to_string(node) + "\"");
                    }
                }
            }
        }
    }


    // check shape of return value
    // this is not done with the actual return value since the type of that depends on the visitor
    if(checks) {
        std::vector<size_t> shape = get_expression_shape(node, symbols);

        for(size_t k = 0; k < shape.size(); k++) {
            if(shape.at(k) != sym->result_shape.at(k)) {
                // check for wildcard
                auto it = std::find(sym->result_wildcards.begin(), sym->result_wildcards.end(), k);
                if(it == sym->result_wildcards.end()) {
                    throw ale::util::wrongDimensionException("Dimension or shape of return value does not match in \"" + expression_to_string(node) + "\"");
                }
            }
        }
    }
    // construct copy of expression with replaced parameters and evaluate it using the given visitor
    auto expr_copy = sym->expr;
    // when replacing the first argument with an expression, we may introduce a symbol which would be replaced by the second argument
    // thus we replace all arguments with special names
    // we only need to ensure that the names are unique from user given symbol names (our children nodes do not see these names)

    std::map<std::string, std::string> local_arg_names = {};
    std::map<std::string, value_node_variant> local_arg_map = {};
    // create map of keys of arg_map to unique names and map of unique names to values of arg_map
    int arg_pos = 1;
    for(const auto& elem : arg_map) {
        std::string arg_name = "__Arg_" + std::to_string(arg_pos++);
        local_arg_names.emplace(elem.first, arg_name);
        local_arg_map.emplace(arg_name, elem.second);
    }
    rename_parameters(expr_copy, local_arg_names);

    replace_parameters(expr_copy, local_arg_map);

    return call_visitor(std::forward<TVisitor>(visitor), expr_copy);
}

namespace helper {

    /**
         * Specialization of traverse_children for kary_nodes.
         */
    template <typename TVisitor, typename... TTypes>
    void traverse_children(TVisitor&& visitor, kary_node<TTypes...>* node, std::optional<std::reference_wrapper<symbol_table>> symbols = {}, std::optional<std::reference_wrapper<value_node_ptr_variant>> current_node = {}) {
        // helper function to make the call to apply easier
        auto update_arg_and_traverse = [&visitor, &current_node](auto&& arg) {
            // update current_node before calling the visitor so that current_node actually points to the node currently being evaluated
            if(current_node) {
                current_node->get() = arg;
            }

            call_visitor(std::forward<TVisitor>(visitor), arg);
        };

        // apply update_arg_and_traverse to each child of node
        std::apply([&update_arg_and_traverse](auto&&... args) { (update_arg_and_traverse(args), ...); }, node->children);
    }

    /**
         * Specialization of traverse_children for nary_nodes.
         */
    template <typename TVisitor, typename TType>
    void traverse_children(TVisitor&& visitor, nary_node<TType>* node, std::optional<std::reference_wrapper<symbol_table>> symbols = {}, std::optional<std::reference_wrapper<value_node_ptr_variant>> current_node = {}) {
        for(auto& child : node->children) {
            // update current_node before calling the visitor so that current_node actually points to the node currently being evaluated
            if(current_node) {
                current_node->get() = child;
            }

            call_visitor(std::forward<TVisitor>(visitor), child);
        }
    }

    /**
         * Specialization of traverse_children for iterator_nodes.
         */
    template <typename TVisitor, typename IteratorType, typename TType>
    void traverse_children(TVisitor&& visitor, iterator_node<IteratorType, TType>* node, std::optional<std::reference_wrapper<symbol_table>> symbols = {}, std::optional<std::reference_wrapper<value_node_ptr_variant>> current_node = {}) {
        if(symbols) {
            auto elements = util::evaluate_expression(node->template get_child<0>(), *symbols);
            symbols->get().push_scope();

            if(current_node) {
                current_node->get() = std::get<1>(node->children);
            }

            for(const auto& elem : elements) {
                symbols->get().define(node->name, new parameter_symbol<IteratorType>(node->name, elem));
                call_visitor(std::forward<TVisitor>(visitor), node->template get_child<1>());
            }

            symbols->get().pop_scope();
        } else {
            traverse_children<TVisitor, set<IteratorType, 0>, TType>(std::forward<TVisitor>(visitor), node, symbols, current_node);
        }
    }

    /**
         * Specialization of traverse_children for terminal_nodes.
         * 
         * Nothing needs to be done here since there are no children to traverse.
         */
    template <typename TVisitor>
    void traverse_children(TVisitor&& visitor, terminal_node* node, std::optional<std::reference_wrapper<symbol_table>> symbols = {}, std::optional<std::reference_wrapper<value_node_ptr_variant>> current_node = {}) { }

} // namespace helper

/**
     * Call visitor on children of node.
     * If current_node is passed it will always point to the same node that the visitor is called with.
     *
     * Any return values will be discarded.
     */
template <typename TVisitor, typename TType>
void traverse_children(TVisitor&& visitor, value_node<TType>* node, std::optional<std::reference_wrapper<symbol_table>> symbols = {}, std::optional<std::reference_wrapper<value_node_ptr_variant>> current_node = {}) {
    std::visit([&visitor, &current_node, &symbols](auto* n) { return ale::helper::traverse_children(std::forward<TVisitor>(visitor), n, symbols, current_node); }, node->get_variant());
}

/**
     * Clone value_node referenced in value_node_ptr_variant
     */
value_node_variant clone_value_node_ptr_variant(value_node_ptr_variant node);

/**
     * Clone value_node referenced in value_node_variant
     */
value_node_variant clone_value_node_variant(value_node_variant node);

/**
     * Reset the value_node_ptr stored in ptr with a clone of new_node.
     * This only works if the type of value_node_ptr and new_node match, otherwise an error will be thrown.
     */
void reset_value_node_ptr_variant(value_node_ptr_variant old_node, value_node_ptr_variant new_node);

/**
     * Reset the value_node_ptr stored in ptr with new_node.
     * This only works if the type of value_node_ptr and new_node match, otherwise an error will be thrown.
     */
void reset_value_node_ptr_variant(value_node_ptr_variant old_node, value_node_variant new_node);

namespace helper {

    struct extract_function_arguments_visitor {
        extract_function_arguments_visitor(std::vector<value_node_variant>& children) :
            children(children) { }

        template <typename TType>
        void operator()(value_node<TType>* node) {
            throw std::invalid_argument("arguments should be stored in vector_nodes");
        }

        template <typename TType>
        void operator()(vector_node<TType>* node) {
            children.push_back(node->template get_child<0>());
        }

        std::vector<value_node_variant>& children;
    };

} // namespace helper

/**
     * Extracts the arguments from a function_node which are stored inside a vector_node
     */
template <typename TType>
std::vector<value_node_variant> extract_function_arguments(function_node<TType>* node) {
    std::vector<value_node_variant> children;
    for(auto& child : node->children) {
        call_visitor(ale::helper::extract_function_arguments_visitor(children), child);
    }
    return children;
}

// namespace helper {
//     template <typename TType>
//     void push_scope(symbol_table& symbols, nary_node<TType>* node) {}

//     template <typename... TTypes>
//     void push_scope(symbol_table& symbols, kary_node<TTypes...>* node) {}

//     inline void push_scope(symbol_table& symbols, terminal_node* node) {}

//     template <typename IteratorType, typename TType>
//     void push_scope(symbol_table& symbols, iterator_node<IteratorType, TType>* node) {
//         symbols.push_scope();
//         symbols.define(node->name, new parameter_symbol<IteratorType>(node->name));
//     }

//     template <typename TType>
//     void pop_scope(symbol_table& symbols, nary_node<TType>* node) {}

//     template <typename... TTypes>
//     void pop_scope(symbol_table& symbols, kary_node<TTypes...>* node) {}

//     inline void pop_scope(symbol_table& symbols, terminal_node* node) {}

//     template <typename IteratorType, typename TType>
//     void pop_scope(symbol_table& symbols, iterator_node<IteratorType, TType>* node) {
//         symbols.pop_scope();
//     }
// }

// /**
//  * If node is an iterator_node a new scope is pushed and the iterator variable is defined
//  */
// template <typename TType>
// void maybe_define_scoped_iterator_variable(symbol_table& symbols, value_node<TType>* node) {
//     call_visitor([&symbols](auto* node){ale::helper::push_scope(symbols, node);}, node);
// }

// /**
//  * If node is an iterator_node a scope is popped. This should be used together with
//  * maybe_define_scoped_iterator_variable
//  */
// template <typename TType>
// void maybe_remove_scope(symbol_table& symbols, value_node<TType>* node) {
//     call_visitor([&symbols](auto* node){ale::helper::push_scope(symbols, node);}, node);
// }

namespace helper {
    template <unsigned IDim>
    std::string serialize_indexes(size_t* indexes, char delimiter) {
        return std::to_string(indexes[0] + 1) + delimiter + serialize_indexes<IDim - 1>(indexes + 1, delimiter);
    }

    template <>
    inline std::string serialize_indexes<1>(size_t* indexes, char /*delimiter*/) {
        return std::to_string(indexes[0] + 1);
    }
} // namespace helper

} // namespace ale
