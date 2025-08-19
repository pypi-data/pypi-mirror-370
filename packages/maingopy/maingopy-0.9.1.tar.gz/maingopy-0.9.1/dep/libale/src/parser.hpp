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

#include <cstddef> // for size_t
#include <iosfwd>  // for istream, ostream
#include <map>
#include <memory> // for unique_ptr
#include <queue>  // for queue
#include <set>    // for set
#include <stack>
#include <string> // for string, basic_string
#include <vector> // for vector

#include "config.hpp"       // for LIBALE_MAX_DIM, LIBALE_MAX_SET_DIM
#include "lexer.hpp"        // for lexer
#include "node.hpp"         // for value_node, iterator_node, kary_node, nary_node
#include "symbol_table.hpp" // for symbol_table
#include "token.hpp"        // for token, token::token_type
#include "token_buffer.hpp" // for token_buffer
#include "value.hpp"        // for real, tensor_type, boolean, set, index, tensor_type<>::basic_type, base_boolean, base_index, base_real, base_set

namespace ale {

class parser {
public:
    parser(std::istream &, symbol_table &);
    bool fail();
    void clear();
    void print_errors();
    void forbid_expressions(std::vector<std::string>);
    void forbid_keywords(std::vector<std::string>);

protected:
    symbol_table &symbols;

    // input handling
    const token& current();
    void consume();
    void discard();
    bool check(token::token_type);
    bool match(token::token_type);
    bool check_keyword(const std::string &);
    bool match_keyword(const std::string &);
    void recover();

    void init();
    bool accept();
    bool reject();

    // parser rules
    // helper rules
    template <typename... TRest>
    bool check_any(token::token_type, TRest...);
    template <typename... TTypes>
    bool match_any(TTypes...);
    template <typename... TRest>
    bool check_any_keyword(const std::string &, const TRest &...);
    template <typename TType>
    bool exists(std::string);
    bool available(std::string);

    // entry points
    template <typename TType>
    bool match_expression(std::unique_ptr<value_node<TType>> &);
    template <typename TType>
    bool match_expression(std::unique_ptr<value_node<TType>> &, std::string &);
    bool match_literal(std::string &);

    // generic dispatch
    template <typename TType>
    bool match_value(std::unique_ptr<value_node<TType>> &);

    // generic primary
    template <typename TType>
    bool match_primary(std::unique_ptr<value_node<TType>> &);

    // generic primary alternatives
    template <typename TType>
    bool match_constant(std::unique_ptr<value_node<TType>> &);
    template <typename TType>
    bool match_parameter(std::unique_ptr<value_node<TType>> &);
    template <typename TType>
    bool match_attribute(std::unique_ptr<value_node<TType>> &);
    template <typename TType>
    bool match_grouping(std::unique_ptr<value_node<TType>> &);
    template <typename TType>
    bool match_partial_entry(std::unique_ptr<value_node<TType>> &);
    template <typename TAtom>
    bool match_partial_entry(
      std::unique_ptr<value_node<tensor_type<TAtom, LIBALE_MAX_DIM - 1>>> &);
    template <typename TAtom>
    bool match_partial_entry(
      std::unique_ptr<value_node<set<TAtom, LIBALE_MAX_SET_DIM - 1>>> &);
    template <typename TType>
    bool match_entry(std::unique_ptr<value_node<TType>> &);
    template <typename TAtom>
    bool match_entry(
      std::unique_ptr<value_node<tensor_type<TAtom, LIBALE_MAX_DIM - 1>>> &);
    template <typename TAtom>
    bool match_entry(
      std::unique_ptr<value_node<set<TAtom, LIBALE_MAX_SET_DIM - 1>>> &);
    template <typename TType>
    bool match_partial_entry(std::unique_ptr<value_node<TType>> &, size_t);
    template <typename TAtom>
    bool match_partial_entry(
      std::unique_ptr<value_node<tensor_type<TAtom, LIBALE_MAX_DIM - 1>>> &,
      size_t);
    template <typename TType>
    bool match_wildcard_entry(std::unique_ptr<value_node<TType>> &result);
    template <typename TAtom>
    bool match_wildcard_entry(
      std::unique_ptr<value_node<tensor_type<TAtom, LIBALE_MAX_DIM - 1>>>
        &result);

    // generic basics
    template <typename TAtom, unsigned IDim>
    bool match_tensor(typename tensor_type<TAtom, IDim>::basic_type &);
    template <typename TAtom>
    bool match_vector(typename tensor_type<TAtom, 1>::basic_type &);
    template <typename TAtom>
    bool match_set(typename set<TAtom, 0>::basic_type &);
    template <typename TAtom>
    bool match_sequence(typename set<TAtom, 0>::basic_type &);

    // tag dispatch overloads for match_basic
    template <typename TType>
    struct basic_tag { };
    template <typename TAtom, unsigned IDim>
    bool match_basic(typename tensor_type<TAtom, IDim>::basic_type &,
      basic_tag<tensor_type<TAtom, IDim>>);
    template <typename TAtom>
    bool match_basic(typename tensor_type<TAtom, 1>::basic_type &,
      basic_tag<tensor_type<TAtom, 1>>);
    template <typename TAtom>
    bool match_basic(typename set<TAtom, 0>::basic_type &,
      basic_tag<set<TAtom, 0>>);
    inline bool match_basic(typename real<0>::basic_type &, basic_tag<real<0>>);
    inline bool match_basic(typename index<0>::basic_type &, basic_tag<index<0>>);
    inline bool match_basic(typename boolean<0>::basic_type &,
      basic_tag<boolean<0>>);
    // same as match_basic but with evaluation for index<0>
    template <typename TType>
    bool match_basic_or_evaluated(typename TType::basic_type &value,
      basic_tag<TType>);
    inline bool match_basic_or_evaluated(typename real<0>::basic_type &value,
      basic_tag<real<0>>);
    inline bool match_basic_or_evaluated(typename index<0>::basic_type &value,
      basic_tag<index<0>>);
    inline bool match_basic_or_evaluated(typename boolean<0>::basic_type &value,
      basic_tag<boolean<0>>);
    template <typename TAtom>
    inline bool match_basic_or_evaluated(typename set<TAtom, 0>::basic_type &value,
      basic_tag<set<TAtom, 0>>);
    // template call to tag dispatch overloads
    template <typename TType>
    bool match_basic_or_evaluated(typename TType::basic_type &);
    template <typename TType>
    bool match_basic(typename TType::basic_type &);

    // set operations
    template <unsigned IDim>
    bool match_any_sum(std::unique_ptr<value_node<real<0>>> &result);
    template <unsigned IDim>
    bool match_any_product(std::unique_ptr<value_node<real<0>>> &result);
    template <unsigned IDim>
    bool match_any_set_min(std::unique_ptr<value_node<real<0>>> &result);
    template <unsigned IDim>
    bool match_any_set_max(std::unique_ptr<value_node<real<0>>> &result);

    // comparisons
    template <typename TType>
    bool match_comparison(std::unique_ptr<value_node<boolean<0>>> &);

    // sets
    template <typename TType>
    bool match_indicator_set(std::unique_ptr<value_node<set<TType, 0>>> &);

    // quantifiers
    template <unsigned IDim>
    bool match_any_quantifier(std::unique_ptr<value_node<boolean<0>>> &);
    template <typename TType>
    bool match_forall(std::unique_ptr<value_node<boolean<0>>> &);

    // definitions
    template <typename TAtom>
    bool match_declarator();
    bool match_declarator(basic_tag<base_real>);
    bool match_declarator(basic_tag<base_index>);
    bool match_declarator(basic_tag<base_boolean>);
    template <typename TElement>
    bool match_declarator(basic_tag<base_set<TElement>>);
    template <unsigned IDim>
    bool match_any_definition();
    template <typename TType>
    bool match_definition();
    template <unsigned IDim>
    bool match_real_definition();
    template <unsigned IDim>
    bool match_integer_definition();
    template <unsigned IDim>
    bool match_binary_definition();
    template <typename TType>
    bool match_set_definition();
    template <typename TType>
    bool match_scalar_set_definition();
    template <typename TType, unsigned IDim>
    bool match_tensor_set_definition();
    template <typename TType>
    bool match_expr_definition();
    template <unsigned IDim>
    bool match_any_function_definition();
    template <typename TType>
    bool match_function_definition();

    template <typename TType, unsigned IDim>
    void define_symbol(const std::string &name, size_t dim,
      const std::vector<size_t> &shape);

    // parser rules for self defined functions
    template <typename TType>
    bool match_function(std::unique_ptr<value_node<TType>> &result);
    template <typename AtomType, unsigned IDim>
    bool match_vectorized_arg(
      std::unique_ptr<value_node<tensor_type<AtomType, 1>>> &result,
      size_t expected_dim);

    // assignments
    template <unsigned IDim>
    bool match_any_assignment();
    template <typename TType>
    bool match_assignment();
    template <unsigned IDim>
    bool match_bound_assignment();
    template <unsigned IDim>
    bool match_init_assignment();
    template <unsigned IDim>
    bool match_prio_assignment();
    template <unsigned IDim>
    bool match_forall_assignment();

    // match internal functions
    template <typename NodeType, typename ResultType>
    bool match_internal_function(std::unique_ptr<value_node<ResultType>> &result,
      const std::string &function_name);

    template <typename NodeType, typename ResultType, typename... TTypes>
    bool
    match_internal_function_impl(std::unique_ptr<value_node<ResultType>> &result,
      const std::string &function_name,
      kary_node<TTypes...> *node);

    template <typename NodeType, typename ResultType, typename TType>
    bool
    match_internal_function_impl(std::unique_ptr<value_node<ResultType>> &result,
      const std::string &function_name,
      nary_node<TType> *node);

    template <typename NodeType, typename ResultType, typename IteratorType,
      typename TType>
    bool
    match_internal_function_impl(std::unique_ptr<value_node<ResultType>> &result,
      const std::string &function_name,
      iterator_node<IteratorType, TType> *node);

    template <typename ResultType>
    bool
    match_any_internal_function(std::unique_ptr<value_node<ResultType>> &result);

    bool match_addition(std::unique_ptr<value_node<real<0>>> &result);
    bool match_multiplication(std::unique_ptr<value_node<real<0>>> &result);
    bool match_exponentiation(std::unique_ptr<value_node<real<0>>> &result);
    bool match_pow(std::unique_ptr<value_node<real<0>>> &result);
    bool match_sqr(std::unique_ptr<value_node<real<0>>> &result);

    bool match_addition(std::unique_ptr<value_node<index<0>>> &);
    bool match_multiplication(std::unique_ptr<value_node<index<0>>> &);

    bool match_disjunction(std::unique_ptr<value_node<boolean<0>>> &);
    bool match_conjunction(std::unique_ptr<value_node<boolean<0>>> &);
    bool match_negation(std::unique_ptr<value_node<boolean<0>>> &);

    template <typename TType>
    bool match_element(std::unique_ptr<value_node<boolean<0>>> &);

    template <typename ResultType>
    bool match_addition_impl(std::unique_ptr<value_node<ResultType>> &result);

    // match tensor node
    template <typename TType>
    bool match_tensor_node(std::unique_ptr<value_node<TType>> &result);

    // match derivative
    template <unsigned VarDim, size_t FixedDim, unsigned IDimGrad>
    bool
    match_derivative_arguments(std::unique_ptr<value_node<real<IDimGrad>>> &);

    template <unsigned VarDim, size_t FixedDim, unsigned IDimGrad>
    bool
    match_derivative_arguments_any(std::unique_ptr<value_node<real<IDimGrad>>> &);

    template <typename TType>
    bool match_derivative(std::unique_ptr<value_node<TType>> &);

    // token handling
    lexer lex;
    token_buffer buf;

    // error reporting
    void set_expected_token(token::token_type);
    void set_expected_keyword(std::string);
    void set_expected_symbol();
    void set_semantic(std::string);
    void report_empty();
    void report_lexical(token);
    void report_internal(std::string, token);
    void report_syntactical();

    std::vector<std::string> forbidden_expressions;
    std::vector<std::string> forbidden_keywords;

    bool had_error = false;
    std::queue<std::string> errors;
    std::ostream &error_stream;
    // unexpected token
    std::set<std::string> expected;

    // std::set<token::token_type> expected;

    token unexpected_token;
    // unexpected symbol
    token unexpected_symbol;
    // semantic issue
    std::string semantic_issue;
    token semantic_token;
};

} // namespace ale

#include "parser.tpp"
