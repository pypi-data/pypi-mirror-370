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
#include "util/evaluator.hpp"

#include <assert.h>

#include "util/expression_differentiation.hpp"
#include "util/expression_utils.hpp"
#include "util/visitor_utils.hpp"
#include "value.hpp"

namespace ale {

// parser rules
// helper rules
template <typename... TRest>
bool parser::check_any(token::token_type expect, TRest... rest) {
  if (check(expect)) {
    return true;
  }
  return check_any(rest...);
}

template <> inline bool parser::check_any(token::token_type expect) {
  return check(expect);
}

template <typename... TTypes> bool parser::match_any(TTypes... types) {
  if (check_any(types...)) {
    buf.consume();
    return true;
  }
  return false;
}

template <typename... TRest>
bool parser::check_any_keyword(const std::string &expect,
                               const TRest &...rest) {
  if (check_keyword(expect)) {
    return true;
  }
  return check_any_keyword(rest...);
}

template <> inline bool parser::check_any_keyword(const std::string &expect) {
  return check_keyword(expect);
}

template <typename TType> bool parser::exists(std::string name) {
  if (symbols.resolve<TType>(name)) {
    return true;
  }
  set_expected_symbol();
  return false;
}

inline bool parser::available(std::string name) {
  if (symbols.resolve(name)) {
    return false;
  }
  return true;
}

// generic dispatch
template <typename TType>
bool parser::match_value(std::unique_ptr<value_node<TType>> &result) {
  if constexpr (is_real_node<TType> && get_node_dimension<TType> == 0) {
    return match_addition(result);
  }
  if constexpr (is_index_node<TType> && get_node_dimension<TType> == 0) {
    return match_addition(result);
  }
  if constexpr (is_boolean_node<TType> && get_node_dimension<TType> == 0) {
    return match_disjunction(result);
  } else {
    return match_primary(result);
  }
}

// generic primary
template <typename TType>
bool parser::match_primary(std::unique_ptr<value_node<TType>> &result) {
  if constexpr (is_real_node<TType>) {
    if constexpr (get_node_dimension<TType> == 0) {
      return match_constant(result) || match_attribute(result) ||
             match_parameter(result) || match_derivative(result) ||
             match_any_internal_function(result) ||
             match_any_sum<LIBALE_MAX_DIM>(result) ||
             match_any_product<LIBALE_MAX_DIM>(result) ||
             match_any_set_min<LIBALE_MAX_DIM>(result) ||
             match_any_set_max<LIBALE_MAX_DIM>(result) ||
             match_grouping(result) || match_entry(result) ||
             match_function(result);
    } else if constexpr (get_node_dimension<TType> == LIBALE_MAX_DIM) {
      return match_constant(result) || match_attribute(result) ||
             match_parameter(result) || match_function(result) ||
             match_tensor_node(result);
    } else {
      return match_constant(result) || match_attribute(result) ||
             match_parameter(result) || match_function(result) ||
             match_derivative(result) || match_tensor_node(result) ||
             match_entry(result) || match_wildcard_entry(result);
    }
  } else if constexpr (is_index_node<TType> && get_node_dimension<TType> == 0) {
    return match_constant(result) || match_parameter(result) ||
           match_any_internal_function(result) || match_grouping(result) ||
           match_entry(result) || match_function(result);
  } else if constexpr (is_boolean_node<TType> &&
                       get_node_dimension<TType> == 0) {
    // match_element<boolean<0>>(result) would cause infinite recursion

    return match_constant(result) || match_parameter(result) ||
           match_negation(result) || match_comparison<real<0>>(result) ||
           match_comparison<index<0>>(result) || match_entry(result) ||
           match_element<real<0>>(result) || match_element<index<0>>(result) ||
           match_any_quantifier<LIBALE_MAX_DIM>(result) ||
           match_function(result) || match_grouping(result);
  } else if constexpr (is_set_node<TType>) {
    using elem = element_type<TType>;
    if constexpr ((is_real_node<elem> ||
                   is_index_node<elem>)&&get_node_dimension<elem> == 0 &&
                  get_node_dimension<TType> == 0) {
      return match_constant(result) || match_parameter(result) ||
             match_entry(result) || match_indicator_set(result);
    } else if constexpr (get_node_dimension<TType> == LIBALE_MAX_SET_DIM) {
      return match_constant(result) || match_parameter(result);
    } else {
      return match_constant(result) || match_parameter(result) ||
             match_entry(result);
    }
  } else if constexpr (get_node_dimension<TType> == LIBALE_MAX_DIM) {
    return match_constant(result) || match_parameter(result) ||
           match_function(result) || match_tensor_node(result);
  } else {
    return match_constant(result) || match_parameter(result) ||
           match_function(result) || match_tensor_node(result) ||
           match_entry(result) || match_wildcard_entry(result);
  }
}

// generic primary alternatives
template <typename TType>
bool parser::match_constant(std::unique_ptr<value_node<TType>> &result) {
  init();
  typename value_node<TType>::basic_type value;
  if (match_basic<TType>(value)) {
    result.reset(new constant_node<TType>(value));
    return accept();
  }
  return reject();
}

template <typename TType>
bool parser::match_parameter(std::unique_ptr<value_node<TType>> &result) {
  init();
  if (check(token::IDENT)) {
    std::string name = current().lexeme;
    if (exists<TType>(name)) {
      consume();
      result.reset(new parameter_node<TType>(name));
      return accept();
    }
  }
  return reject();
}

template <typename TType>
bool parser::match_attribute(std::unique_ptr<value_node<TType>> &result) {
  init();
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!exists<TType>(name)) {
    set_semantic("ERROR: Undefined symbol \"" + name + "\"");
    return reject();
  }
  variable_symbol<real<TType::dim>> *sym =
      cast_variable_symbol<real<TType::dim>>(symbols.resolve(name));
  if (!sym) {
    if (!symbols.resolve(name)) {
      set_semantic("ERROR: Undefined symbol \"" + name + "\"");
    } else {
      set_semantic("ERROR: Symbol \"" + name + "\" of unexpected type");
    }
    return reject();
  }
  consume();
  if (!match(token::DOT)) {
    return reject();
  }
  variable_attribute_type attribute;
  if (match_keyword("ub")) {
    attribute = variable_attribute_type::UB;
  } else if (match_keyword("lb")) {
    attribute = variable_attribute_type::LB;
  } else if (match_keyword("init")) {
    attribute = variable_attribute_type::INIT;
  } else if (match_keyword("prio")) {
    attribute = variable_attribute_type::PRIO;
  } else {
    set_semantic("ERROR: unsupported attribute \"." + current().lexeme +
                 "\" of symbol \"" + name + "\"");
    return reject();
  }
  std::unique_ptr<attribute_node<TType>> attr_node(
      new attribute_node<TType>(name, attribute));
  result.reset(attr_node.release());

  return accept();
}

template <typename TType>
bool parser::match_function(std::unique_ptr<value_node<TType>> &result) {
  init();

  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  function_symbol<TType> *sym =
      cast_function_symbol<TType>(symbols.resolve(name));
  if (!sym) {
    if (!symbols.resolve(name)) {
      set_semantic("ERROR: Undefined symbol \"" + name + "\"");
    } else {
      set_semantic("ERROR: Symbol \"" + name + "\" of unexpected type");
    }
    return reject();
  }
  consume();
  if (!match(token::LPAREN)) {
    return reject();
  }
  std::unique_ptr<function_node<TType>> function(
      new function_node<TType>(name));
  for (int i = 0; i < sym->arg_names.size(); ++i) {
    std::unique_ptr<value_node<tensor_type<atom_type<TType>, 1>>>
        vectorized_arg;
    if (!match_vectorized_arg<atom_type<TType>, LIBALE_MAX_DIM>(
            vectorized_arg, sym->arg_dims.at(i))) {
      return reject();
    }
    function->add_child(vectorized_arg.release());
    if (i + 1 < sym->arg_names.size()) {
      if (!match(token::COMMA)) {
        return reject();
      }
    }
  }

  if (!match(token::RPAREN)) {
    return reject();
  }

  result.reset(function.release());
  return accept();
}

template <typename TType>
bool parser::match_partial_entry(std::unique_ptr<value_node<TType>> &result) {
  init();
  std::unique_ptr<value_node<vector_of<TType>>> first_child;
  if (match_partial_entry(first_child)) {
    std::unique_ptr<value_node<index<0>>> second_child;
    if (!match_value(second_child)) {
      return reject();
    }
    if (!match(token::COMMA)) {
      return reject();
    }
    result.reset(
        new entry_node<TType>(first_child.release(), second_child.release()));
    return accept();
  }
  if (match_value(first_child)) {
    if (!match(token::LBRACK)) {
      return reject();
    }
    std::unique_ptr<value_node<index<0>>> second_child;
    if (!match_value(second_child)) {
      return reject();
    }
    if (!match(token::COMMA)) {
      return reject();
    }
    result.reset(
        new entry_node<TType>(first_child.release(), second_child.release()));
    return accept();
  }
  return reject();
}

template <typename TAtom>
bool parser::match_partial_entry(
    std::unique_ptr<value_node<tensor_type<TAtom, LIBALE_MAX_DIM - 1>>>
        &result) {
  using TType = tensor_type<TAtom, LIBALE_MAX_DIM - 1>;
  init();
  std::unique_ptr<value_node<vector_of<TType>>> first_child;
  if (match_value(first_child)) {
    if (!match(token::LBRACK)) {
      return reject();
    }
    std::unique_ptr<value_node<index<0>>> second_child;
    if (!match_value(second_child)) {
      return reject();
    }
    if (!match(token::COMMA)) {
      return reject();
    }
    result.reset(
        new entry_node<TType>(first_child.release(), second_child.release()));
    return accept();
  }
  return reject();
}

template <typename TAtom>
bool parser::match_partial_entry(
    std::unique_ptr<value_node<set<TAtom, LIBALE_MAX_SET_DIM - 1>>> &result) {
  using TType = set<TAtom, LIBALE_MAX_SET_DIM - 1>;
  init();
  std::unique_ptr<value_node<vector_of<TType>>> first_child;
  if (match_value(first_child)) {
    if (!match(token::LBRACK)) {
      return reject();
    }
    std::unique_ptr<value_node<index<0>>> second_child;
    if (!match_value(second_child)) {
      return reject();
    }
    if (!match(token::COMMA)) {
      return reject();
    }
    result.reset(
        new entry_node<TType>(first_child.release(), second_child.release()));
    return accept();
  }
  return reject();
}

template <typename TType>
bool parser::match_entry(std::unique_ptr<value_node<TType>> &result) {
  init();
  std::unique_ptr<value_node<vector_of<TType>>> first_child;
  if (match_partial_entry(first_child)) {
    std::unique_ptr<value_node<index<0>>> second_child;
    if (!match_value(second_child)) {
      return reject();
    }
    while (match(token::COMMA)) {
      if (!match(token::COLON)) {
        return reject();
      }
    }
    if (!match(token::RBRACK)) {
      return reject();
    }
    result.reset(
        new entry_node<TType>(first_child.release(), second_child.release()));
    return accept();
  }
  if (match_value(first_child)) {
    if (!match(token::LBRACK)) {
      return reject();
    }
    std::unique_ptr<value_node<index<0>>> second_child;
    if (!match_value(second_child)) {
      return reject();
    }
    while (match(token::COMMA)) {
      if (!match(token::COLON)) {
        return reject();
      }
    }
    if (!match(token::RBRACK)) {
      return reject();
    }
    result.reset(
        new entry_node<TType>(first_child.release(), second_child.release()));
    return accept();
  }
  return reject();
}

template <typename TAtom>
bool parser::match_entry(
    std::unique_ptr<value_node<tensor_type<TAtom, LIBALE_MAX_DIM - 1>>>
        &result) {
  using TType = tensor_type<TAtom, LIBALE_MAX_DIM - 1>;
  init();
  std::unique_ptr<value_node<vector_of<TType>>> first_child;
  if (match_value(first_child)) {
    if (!match(token::LBRACK)) {
      return reject();
    }
    std::unique_ptr<value_node<index<0>>> second_child;
    if (!match_value(second_child)) {
      return reject();
    }
    while (match(token::COMMA)) {
      if (!match(token::COLON)) {
        return reject();
      }
    }
    if (!match(token::RBRACK)) {
      return reject();
    }
    result.reset(
        new entry_node<TType>(first_child.release(), second_child.release()));
    return accept();
  }
  return reject();
}

template <typename TAtom>
bool parser::match_entry(
    std::unique_ptr<value_node<set<TAtom, LIBALE_MAX_SET_DIM - 1>>> &result) {
  using TType = set<TAtom, LIBALE_MAX_SET_DIM - 1>;
  init();
  std::unique_ptr<value_node<vector_of<TType>>> first_child;
  if (match_value(first_child)) {
    if (!match(token::LBRACK)) {
      return reject();
    }
    std::unique_ptr<value_node<index<0>>> second_child;
    if (!match_value(second_child)) {
      return reject();
    }
    if (!match(token::RBRACK)) {
      return reject();
    }
    result.reset(
        new entry_node<TType>(first_child.release(), second_child.release()));
    return accept();
  }
  return reject();
}

template <typename TType>
bool parser::match_wildcard_entry(std::unique_ptr<value_node<TType>> &result) {
  init();
  std::unique_ptr<value_node<vector_of<TType>>> first_child;
  if (match_partial_entry(first_child, TType::dim)) {
    std::unique_ptr<value_node<index<0>>> second_child;
    if (!match_value(second_child)) {
      return reject();
    }
    if (!match(token::RBRACK)) {
      return reject();
    }
    result.reset(
        new entry_node<TType>(first_child.release(), second_child.release()));
    return accept();
  }
  if (match_value(first_child)) {
    if (!match(token::LBRACK)) {
      return reject();
    }
    for (int i = 0; i < TType::dim; ++i) {
      if (!match(token::COLON)) {
        return reject();
      }
      if (!match(token::COMMA)) {
        return reject();
      }
    }
    std::unique_ptr<value_node<index<0>>> second_child;
    if (!match_value(second_child)) {
      return reject();
    }
    if (!match(token::RBRACK)) {
      return reject();
    }
    for (int i = 0; i < TType::dim; ++i) {
      first_child.reset(
          new index_shift_node<vector_of<TType>>(first_child.release()));
    }
    result.reset(
        new entry_node<TType>(first_child.release(), second_child.release()));
    return accept();
  }
  return reject();
}

template <typename TAtom>
bool parser::match_wildcard_entry(
    std::unique_ptr<value_node<tensor_type<TAtom, LIBALE_MAX_DIM - 1>>>
        &result) {
  using TType = tensor_type<TAtom, LIBALE_MAX_DIM - 1>;
  init();
  std::unique_ptr<value_node<vector_of<TType>>> first_child;
  if (match_value(first_child)) {
    if (!match(token::LBRACK)) {
      return reject();
    }
    for (int i = 0; i < LIBALE_MAX_DIM - 1; ++i) {
      if (!match(token::COLON)) {
        return reject();
      }
      if (!match(token::COMMA)) {
        return reject();
      }
    }
    std::unique_ptr<value_node<index<0>>> second_child;
    if (!match_value(second_child)) {
      return reject();
    }
    if (!match(token::RBRACK)) {
      return reject();
    }
    for (int i = 0; i < LIBALE_MAX_DIM - 1; ++i) {
      first_child.reset(
          new index_shift_node<vector_of<TType>>(first_child.release()));
    }
    result.reset(
        new entry_node<TType>(first_child.release(), second_child.release()));
    return accept();
  }
  return reject();
}

template <typename TType>
bool parser::match_partial_entry(std::unique_ptr<value_node<TType>> &result,
                                 size_t wildcard_count) {
  init();
  std::unique_ptr<value_node<vector_of<TType>>> first_child;
  if (match_partial_entry(first_child, wildcard_count)) {
    std::unique_ptr<value_node<index<0>>> second_child;
    if (!match_value(second_child)) {
      return reject();
    }
    if (!match(token::COMMA)) {
      return reject();
    }
    result.reset(
        new entry_node<TType>(first_child.release(), second_child.release()));
    return accept();
  }
  if (match_value(first_child)) {
    if (!match(token::LBRACK)) {
      return reject();
    }
    for (int i = 0; i < wildcard_count; ++i) {
      if (!match(token::COLON)) {
        return reject();
      }
      if (!match(token::COMMA)) {
        return reject();
      }
    }
    std::unique_ptr<value_node<index<0>>> second_child;
    if (!match_value(second_child)) {
      return reject();
    }
    if (!match(token::COMMA)) {
      return reject();
    }
    for (size_t i = 0; i < wildcard_count; ++i) {
      first_child.reset(
          new index_shift_node<vector_of<TType>>(first_child.release()));
    }
    result.reset(
        new entry_node<TType>(first_child.release(), second_child.release()));
    return accept();
  }
  return reject();
}

template <typename TAtom>
bool parser::match_partial_entry(
    std::unique_ptr<value_node<tensor_type<TAtom, LIBALE_MAX_DIM - 1>>> &result,
    size_t wildcard_count) {
  using TType = tensor_type<TAtom, LIBALE_MAX_DIM - 1>;
  init();
  std::unique_ptr<value_node<vector_of<TType>>> first_child;
  if (match_value(first_child)) {
    if (!match(token::LBRACK)) {
      return reject();
    }
    for (int i = 0; i < wildcard_count; ++i) {
      if (!match(token::COLON)) {
        return reject();
      }
      if (!match(token::COMMA)) {
        return reject();
      }
    }
    std::unique_ptr<value_node<index<0>>> second_child;
    if (!match_value(second_child)) {
      return reject();
    }
    if (!match(token::COMMA)) {
      return reject();
    }
    for (size_t i = 0; i < wildcard_count; ++i) {
      first_child.reset(
          new index_shift_node<vector_of<TType>>(first_child.release()));
    }
    result.reset(
        new entry_node<TType>(first_child.release(), second_child.release()));
    return accept();
  }
  return reject();
}

template <typename TType>
bool parser::match_grouping(std::unique_ptr<value_node<TType>> &result) {
  init();
  if (!match(token::LPAREN)) {
    return reject();
  }
  if (!match_value(result)) {
    return reject();
  }
  if (!match(token::RPAREN)) {
    return reject();
  }
  return accept();
}

// generic basics
template <typename TAtom, unsigned IDim>
bool parser::match_tensor(
    typename tensor_type<TAtom, IDim>::basic_type &value) {
  using TType = tensor_type<TAtom, IDim>;
  init();
  if (!match(token::LPAREN)) {
    return reject();
  }
  size_t shape[IDim];
  for (int i = 0; i < IDim; ++i) {
    shape[i] = 0;
  }
  std::vector<typename entry_of<TType>::basic_type> entries;
  typename entry_of<TType>::basic_type ent;
  if (match_basic_or_evaluated<tensor_type<TAtom, IDim - 1>>(ent)) {
    entries.push_back(ent);
    for (int i = 1; i < IDim; ++i) {
      shape[i] = ent.shape(i - 1);
    }
    while (match(token::COMMA)) {
      if (!match_basic_or_evaluated<tensor_type<TAtom, IDim - 1>>(ent)) {
        return reject();
      }
      for (int i = 1; i < IDim; ++i) {
        if (shape[i] != ent.shape(i - 1)) {
          return reject();
        }
      }
      entries.push_back(ent);
    }
  }
  if (!match(token::RPAREN)) {
    return reject();
  }
  shape[0] = entries.size();
  value.resize(shape);
  for (int i = 0; i < entries.size(); ++i) {
    value[i].assign(entries[i]);
  }
  return accept();
}

template <typename TAtom>
bool parser::match_vector(typename tensor_type<TAtom, 1>::basic_type &value) {
  using TType = tensor_type<TAtom, 1>;
  init();
  if (!match(token::LPAREN)) {
    return reject();
  }
  std::vector<typename entry_of<TType>::basic_type> entries;
  typename entry_of<TType>::basic_type ent;
  if (match_basic_or_evaluated<tensor_type<TAtom, 0>>(ent)) {
    entries.push_back(ent);
    while (match(token::COMMA)) {
      if (!match_basic_or_evaluated<tensor_type<TAtom, 0>>(ent)) {
        return reject();
      }
      entries.push_back(ent);
    }
  }
  if (!match(token::RPAREN)) {
    return reject();
  }
  value.resize({entries.size()});
  for (int i = 0; i < entries.size(); ++i) {
    value[i] = entries[i];
  }
  return accept();
}

// evaluated only exists for index<0>
//  template call to tag dispatch overloads
template <typename TType>
bool parser::match_basic_or_evaluated(typename TType::basic_type &value) {
  return match_basic_or_evaluated(value, basic_tag<TType>{});
}

template <typename TType>
inline bool parser::match_basic_or_evaluated(typename TType::basic_type &value,
                                             basic_tag<TType> tag) {
  return match_basic(value, tag);
}

inline bool
parser::match_basic_or_evaluated(typename real<0>::basic_type &value,
                                 basic_tag<real<0>> tag) {
  init();
  std::unique_ptr<value_node<real<0>>> realExpression;
  if (match_value(realExpression)) {
    try {
      if (!is_tree_constant(realExpression.get(), symbols)) {
        return reject();
      }
      value = util::evaluate_expression(realExpression.get(), symbols);
      return accept();
    } catch (ale::util::uninitializedParameterException &e) {
      set_semantic("ERROR: While computing parse-time real value: " +
                   std::string(e.what()));
      return reject();
    } catch (ale::util::wrongDimensionException &e) {
      set_semantic("ERROR: While computing parse-time real value: " +
                   std::string(e.what()));
      return reject();
    }

  } else if (match_basic<real<0>>(value)) {
    return accept();
  } else {
    return reject();
  }
}

inline bool
parser::match_basic_or_evaluated(typename index<0>::basic_type &value,
                                 basic_tag<index<0>>) {
  init();
  std::unique_ptr<value_node<index<0>>> intExpression;
  if (match_value(intExpression)) {
    if (!is_tree_constant(intExpression.get(), symbols)) {
      return reject();
    }
    try {
      value = util::evaluate_expression(intExpression.get(), symbols);
      return accept();
    } catch (ale::util::uninitializedParameterException &e) {
      set_semantic("ERROR: While computing parse-time index value:" +
                   std::string(e.what()));
      return reject();
    } catch (ale::util::wrongDimensionException &e) {
      set_semantic("ERROR: While computing parse-time index value: " +
                   std::string(e.what()));
      return reject();
    }

  } else if (match_basic<index<0>>(value)) {
    return accept();
  } else
    return reject();
}

template <typename TAtom>
bool parser::match_basic_or_evaluated(typename set<TAtom, 0>::basic_type &value,
                                 basic_tag<set<TAtom, 0>>) {
  init();
  std::unique_ptr<value_node<set<TAtom, 0>>> setExpression;
  if (match_value(setExpression)) {
    if (!is_tree_constant(setExpression.get(), symbols)) {
      return reject();
    }
	try {
      value = util::evaluate_expression(setExpression.get(), symbols);
      return accept();
    } catch (ale::util::uninitializedParameterException &e) {
      set_semantic("ERROR: While computing parse-time indicator set value:" +
                   std::string(e.what()));
      return reject();
    } catch (ale::util::wrongDimensionException &e) {
      set_semantic("ERROR: While computing parse-time indicator set value: " +
                   std::string(e.what()));
      return reject();
    }
  } else if (match_basic<set<TAtom,0>>(value)) {
    return accept();
  } else
    return reject();
}

inline bool
parser::match_basic_or_evaluated(typename boolean<0>::basic_type &value,
                                 basic_tag<boolean<0>>) {
  init();
  std::unique_ptr<value_node<boolean<0>>> boolExpression;
  if (match_value(boolExpression)) {
    if (!is_tree_constant(boolExpression.get(), symbols)) {
      return reject();
    }
    try {
      value = util::evaluate_expression(boolExpression.get(), symbols);
      return accept();
    } catch (ale::util::uninitializedParameterException &e) {
      set_semantic("ERROR: While computing parse-time boolean value:" +
                   std::string(e.what()));
      return reject();
    } catch (ale::util::wrongDimensionException &e) {
      set_semantic("ERROR: While computing parse-time boolean value: " +
                   std::string(e.what()));
      return reject();
    }

  } else if (match_basic<boolean<0>>(value)) {
    return accept();
  } else
    return reject();
}

template <typename TAtom>
bool parser::match_set(typename set<TAtom, 0>::basic_type &value) {
  init();
  if (!match(token::LBRACE)) {
    return reject();
  }
  typename TAtom::basic_type elem;
  typename set<TAtom, 0>::basic_type elements;
  if (match_basic_or_evaluated<TAtom>(elem)) {
    elements.push_back(elem);
    while (match(token::COMMA)) {
      if (!match_basic_or_evaluated<TAtom>(elem)) {
        return reject();
      }
      elements.push_back(elem);
    }
  }
  if (!match(token::RBRACE)) {
    return reject();
  }
  value = elements;
  return accept();
}

template <typename TAtom>
bool parser::match_sequence(typename set<TAtom, 0>::basic_type &) {
  return false;
}

template <>
inline bool
parser::match_sequence<index<0>>(typename set<index<0>, 0>::basic_type &value) {
  init();
  if (!match(token::LBRACE)) {
    return reject();
  }
  typename index<0>::basic_type first;

  if (!match_basic_or_evaluated<index<0>>(first)) {
    return reject();
  }
  if (!match(token::DOTS)) {
    return reject();
  }
  typename index<0>::basic_type last;

  if (!match_basic_or_evaluated<index<0>>(last)) {
    return reject();
  }

  if (!match(token::RBRACE)) {
    return reject();
  }
  value.clear();
  if (first > last) {
    // empty set
    return accept();
  }
  for (int i = first; i <= last; ++i) {
    value.push_back(i);
  }
  return accept();
}

// tag dispatch overloads for match_basic
template <typename TAtom, unsigned IDim>
bool parser::match_basic(typename tensor_type<TAtom, IDim>::basic_type &value,
                         basic_tag<tensor_type<TAtom, IDim>>) {
  return match_tensor<TAtom, IDim>(value);
}

template <typename TAtom>
bool parser::match_basic(typename tensor_type<TAtom, 1>::basic_type &value,
                         basic_tag<tensor_type<TAtom, 1>>) {
  return match_vector<TAtom>(value);
}

template <typename TAtom>
bool parser::match_basic(typename set<TAtom, 0>::basic_type &value,
                         basic_tag<set<TAtom, 0>>) {
  return match_set<TAtom>(value);
}

template <>
inline bool
parser::match_basic<index<0>>(typename set<index<0>, 0>::basic_type &value,
                              basic_tag<set<index<0>, 0>>) {
  init();
  if (match_set<index<0>>(value)) {
    return accept();
  }
  if (match_sequence<index<0>>(value)) {
    return accept();
  }

  return reject();
}

inline bool parser::match_basic(typename real<0>::basic_type &value,
                                basic_tag<real<0>>) {
  init();
  bool negative = false;
  if (match(token::MINUS)) {
    negative = true;
  }
  if (check_any(token::NUMBER, token::INTEGER)) {
    try {
      value = std::stod(current().lexeme);
      consume();
      if (negative) {
        value = -value;
      }
      return accept();
    } catch (const std::exception &e) {
      report_internal("in match_basic<real<0>>:" + (std::string)e.what(),
                      current());
    } catch (...) {
      report_internal("in match_basic<real<0>>: unknown stod error", current());
    }
  }
  return reject();
}

inline bool parser::match_basic(typename index<0>::basic_type &value,
                                basic_tag<index<0>>) {
  init();

  if (check_any(token::INTEGER)) {
    try {
      value = std::stoi(current().lexeme);
      consume();
      return accept();
    } catch (const std::exception &e) {
      report_internal("in match_basic<real<0>>:" + (std::string)e.what(),
                      current());
    } catch (...) {
      report_internal("in match_basic<real<0>>: unknown stoi error", current());
    }
  }

  return reject();
}

inline bool parser::match_basic(typename boolean<0>::basic_type &value,
                                basic_tag<boolean<0>>) {
  init();
  if (match_keyword("true")) {
    value = true;
    return accept();
  }
  if (match_keyword("false")) {
    value = false;
    return accept();
  }
  return reject();
}

// template call to tag dispatch overloads
template <typename TType>
bool parser::match_basic(typename TType::basic_type &value) {
  return match_basic(value, basic_tag<TType>{});
}

template <unsigned IDim>
bool parser::match_any_sum(std::unique_ptr<value_node<real<0>>> &result) {
  bool has_matched =
      match_internal_function<sum_node<real<IDim>>>(result, "sum") ||
      match_internal_function<sum_node<index<IDim>>>(result, "sum");

  if constexpr (IDim > 0) {
    if (has_matched) {
      return true;
    }

    return match_any_sum<IDim - 1>(result);
  }

  return has_matched;
}

template <unsigned IDim>
bool parser::match_any_product(std::unique_ptr<value_node<real<0>>> &result) {
  bool has_matched =
      match_internal_function<product_node<real<IDim>>>(result, "product") ||
      match_internal_function<product_node<index<IDim>>>(result, "product");

  if constexpr (IDim > 0) {
    if (has_matched) {
      return true;
    }

    return match_any_product<IDim - 1>(result);
  }

  return has_matched;
}

template <unsigned IDim>
bool parser::match_any_set_min(std::unique_ptr<value_node<real<0>>> &result) {
  bool has_matched =
      match_internal_function<set_min_node<real<IDim>>>(result, "min") ||
      match_internal_function<set_min_node<index<IDim>>>(result, "min");

  if constexpr (IDim > 0) {
    if (has_matched) {
      return true;
    }

    return match_any_set_min<IDim - 1>(result);
  }

  return has_matched;
}

template <unsigned IDim>
bool parser::match_any_set_max(std::unique_ptr<value_node<real<0>>> &result) {
  bool has_matched =
      match_internal_function<set_max_node<real<IDim>>>(result, "max") ||
      match_internal_function<set_max_node<index<IDim>>>(result, "max");

  if constexpr (IDim > 0) {
    if (has_matched) {
      return true;
    }

    return match_any_set_max<IDim - 1>(result);
  }

  return has_matched;
}

template <typename TType>
bool parser::match_comparison(std::unique_ptr<value_node<boolean<0>>> &result) {
  init();
  std::unique_ptr<value_node<TType>> first_child;
  if (!match_value(first_child)) {
    return reject();
  }
  if (!check_any(token::EQUAL, token::LESS, token::LEQUAL, token::GREATER,
                 token::GEQUAL)) {
    return reject();
  }
  token::token_type type = current().type;
  consume();
  std::unique_ptr<value_node<TType>> second_child;
  if (!match_value(second_child)) {
    return reject();
  }
  switch (type) {
  case token::EQUAL:
    result.reset(
        new equal_node<TType>(first_child.release(), second_child.release()));
    return accept();
  case token::LESS:
    result.reset(
        new less_node<TType>(first_child.release(), second_child.release()));
    return accept();
  case token::LEQUAL:
    result.reset(new less_equal_node<TType>(first_child.release(),
                                            second_child.release()));
    return accept();
  case token::GREATER:
    result.reset(
        new greater_node<TType>(first_child.release(), second_child.release()));
    return accept();
  case token::GEQUAL:
    result.reset(new greater_equal_node<TType>(first_child.release(),
                                               second_child.release()));
    return accept();
  default:
    return reject();
  }
}
template <typename TType>
bool parser::match_element(std::unique_ptr<value_node<boolean<0>>> &result) {
  init();
  std::unique_ptr<value_node<TType>> first_child;
  if (!match_value(
          first_child)) { // if we allow for tests of booleans in boolean sets,
                          // this here causes infinite recursion, because
                          // match_element is a potential boolean value itself
    return reject();
  }
  if (!match_keyword("in")) {
    return reject();
  }
  std::unique_ptr<value_node<set<TType, 0>>> second_child;
  if (!match_value(second_child)) {
    return reject();
  }
  result.reset(
      new element_node<TType>(first_child.release(), second_child.release()));
  return accept();
}
template <unsigned IDim>
bool parser::match_any_quantifier(
    std::unique_ptr<value_node<boolean<0>>> &result) {
  init();
  if (match_any_quantifier<IDim - 1>(result)) {
    return accept();
  }
  if (match_forall<index<IDim>>(result)) {
    return accept();
  }
  if (match_forall<real<IDim>>(result)) {
    return accept();
  }
  return reject();
}

template <>
inline bool parser::match_any_quantifier<0>(
    std::unique_ptr<value_node<boolean<0>>> &result) {
  init();
  if (match_forall<index<0>>(result)) {
    return accept();
  }
  if (match_forall<real<0>>(result)) {
    return accept();
  }
  return reject();
}

template <typename TType>
bool parser::match_forall(std::unique_ptr<value_node<boolean<0>>> &result) {
  init();
  if (!match_keyword("forall")) {
    return reject();
  }
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!available(name)) {
    set_semantic("ERROR: Symbol declared under occupied name \"" + name + "\"");
    return reject();
  }
  consume();
  if (!match_keyword("in")) {
    return reject();
  }
  std::unique_ptr<value_node<set<TType, 0>>> first_child;
  if (!match_value(first_child)) {
    return reject();
  }
  if (!match(token::COLON)) {
    return reject();
  }
  symbols.push_scope();
  symbols.define(name,
                 new parameter_symbol<TType>(name, IsPlaceholderFlag::TRUE));
  std::unique_ptr<value_node<boolean<0>>> second_child;
  if (!match_value(second_child)) {
    symbols.pop_scope();
    return reject();
  }
  result.reset(new forall_node<TType>(name, first_child.release(),
                                      second_child.release()));
  symbols.pop_scope();
  return accept();
}

template <typename TType>
bool parser::match_indicator_set(
    std::unique_ptr<value_node<set<TType, 0>>> &result) {
  init();
  if (!match(token::LBRACE)) {
    return reject();
  }
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!available(name)) {
    set_semantic("ERROR: Symbol declared under occupied name \"" + name + "\"");
    return reject();
  }
  consume();
  if (!match_keyword("in")) {
    return reject();
  }
  std::unique_ptr<value_node<set<TType, 0>>> first_child;
  if (!match_value(first_child)) {
    return reject();
  }
  if (!match(token::COLON)) {
    return reject();
  }
  symbols.push_scope();
  symbols.define(name,
                 new parameter_symbol<TType>(name, IsPlaceholderFlag::TRUE));
  std::unique_ptr<value_node<boolean<0>>> second_child;
  if (!match_value(second_child)) {
    symbols.pop_scope();
    return reject();
  }
  if (!match(token::RBRACE)) {
    symbols.pop_scope();
    return reject();
  }
  result.reset(new indicator_set_node<TType>(name, first_child.release(),
                                             second_child.release()));
  symbols.pop_scope();
  return accept();
}

template <typename TType> bool parser::match_declarator() {
  return parser::match_declarator(basic_tag<TType>{});
}

inline bool parser::match_declarator(basic_tag<base_real> tag) {
  init();
  if (match_keyword("real")) {
    return accept();
  }
  return reject();
}

inline bool parser::match_declarator(basic_tag<base_index> tag) {
  init();
  if (match_keyword("index")) {
    return accept();
  }
  return reject();
}

inline bool parser::match_declarator(basic_tag<base_boolean> tag) {
  init();
  if (match_keyword("boolean")) {
    return accept();
  }
  return reject();
}

// set{index[:]}
template <typename TElement>
inline bool parser::match_declarator(basic_tag<base_set<TElement>>) {
  init();
  if (!match_keyword("set")) {
    return reject();
  }
  if (!match(token::LBRACE)) {
    return reject();
  }
  using set_entry_type =
      typename base_set<TElement>::element_type; // e.g. real<1>
  if (!match_declarator<typename set_entry_type::atom_type>()) {
    return reject();
  }
  if (set_entry_type::dim > 0) {
    if (!match(token::LBRACK)) {
      return reject();
    }
    for (int i = 0; i < set_entry_type::dim; ++i) {
      if (i > 0 && !match(token::COMMA)) {
        return reject();
      }
      if (!match(token::COLON)) {
        return reject();
      }
    }
    if (!match(token::RBRACK)) {
      return reject();
    }
  }
  if (!match(token::RBRACE)) {
    return reject();
  }
  return accept();
}

template <typename TType> bool parser::match_definition() {
  init();
  if (!match_declarator<typename TType::atom_type>()) {
    return reject();
  }

  size_t shape[TType::dim];
  if (TType::dim > 0) {
    if (!match(token::LBRACK)) {
      return reject();
    }

    for (int i = 0; i < TType::dim; ++i) {
      if (i > 0 && !match(token::COMMA)) {
        return reject();
      }

      base_index::basic_type value;
      if (!match_basic_or_evaluated<index<0>>(value)) {
        return reject();
      }
      shape[i] = value;
    }
    if (!match(token::RBRACK)) {
      return reject();
    }
  }
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!available(name)) {
    set_semantic("ERROR: Symbol declared under occupied name \"" + name + "\"");
    return reject();
  }
  consume();
  if (!match(token::DEFINE)) {
    return reject();
  }

  if constexpr (TType::dim > 0) {
    typename TType::atom_type::basic_type scalar_init;
    if (match_basic_or_evaluated<tensor_type<typename TType::atom_type, 0>>(
            scalar_init)) {
      typename TType::basic_type value(shape, scalar_init);
      if (!match_any(token::SEMICOL, token::END)) {
        return reject();
      }
      symbols.define(name, new parameter_symbol<TType>(name, value));
      return accept();
    }
  }
  typename TType::basic_type value;
  if (!match_basic_or_evaluated<TType>(value)) {
    return reject();
  }
  for (int i = 0; i < TType::dim; ++i) {
    if (shape[i] != value.shape(i)) {
      set_semantic("ERROR: Symbol \"" + name +
                   "\" defined with different shape than declared");
      return reject();
    }
  }
  if (!match_any(token::SEMICOL, token::END)) {
    return reject();
  }
  symbols.define(name, new parameter_symbol<TType>(name, value));
  return accept();
}

template <> inline bool parser::match_definition<index<0>>() {
  init();
  if (!match_declarator<typename index<0>::atom_type>()) {
    return reject();
  }
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!available(name)) {
    set_semantic("ERROR: Symbol declared under occupied name \"" + name + "\"");
    return reject();
  }
  consume();
  if (!match(token::DEFINE)) {
    return reject();
  }
  typename index<0>::basic_type value;
  if (!match_basic_or_evaluated<index<0>>(value)) {
    return reject();
  }
  if (!match_any(token::SEMICOL, token::END)) {
    return reject();
  }
  symbols.define(name, new parameter_symbol<index<0>>(name, value));
  return accept();
}

template <> inline bool parser::match_definition<boolean<0>>() {
  init();
  if (!match_declarator<typename boolean<0>::atom_type>()) {
    return reject();
  }
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!available(name)) {
    set_semantic("ERROR: Symbol declared under occupied name \"" + name + "\"");
    return reject();
  }
  consume();
  if (!match(token::DEFINE)) {
    return reject();
  }
  typename boolean<0>::basic_type value;
  if (!match_basic_or_evaluated<boolean<0>>(value)) {
    return reject();
  }
  if (!match_any(token::SEMICOL, token::END)) {
    return reject();
  }
  symbols.define(name, new parameter_symbol<boolean<0>>(name, value));
  return accept();
}

// If possible this would be named:
// inline bool parser::match_definition<set<TType,0>>()
template <typename TType> inline bool parser::match_scalar_set_definition() {
  init();
  if (!match_keyword("set")) {
    return reject();
  }
  if (!match(token::LBRACE)) {
    return reject();
  }
  if (!match_declarator<typename TType::atom_type>()) {
    return reject();
  }
  if (TType::dim > 0) {
    if (!match(token::LBRACK)) {
      return reject();
    }
    for (int i = 0; i < TType::dim; ++i) {
      if (i > 0 && !match(token::COMMA)) {
        return reject();
      }
      if (!match(token::COLON)) {
        return reject();
      }
    }
    if (!match(token::RBRACK)) {
      return reject();
    }
  }
  if (!match(token::RBRACE)) {
    return reject();
  }
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!available(name)) {
    set_semantic("ERROR: Symbol declared under occupied name \"" + name + "\"");
    return reject();
  }
  consume();
  if (match_any(token::SEMICOL, token::END)) {
    symbols.define(name, new parameter_symbol<set<TType, 0>>(name));
    return accept();
  }
  if (!match(token::DEFINE)) {
    return reject();
  }
  typename set<TType, 0>::basic_type value;
  if (!match_basic_or_evaluated<set<TType, 0>>(value)) {
    return reject();
  }
  if (!match_any(token::SEMICOL, token::END)) {
    return reject();
  }
  symbols.define(name, new parameter_symbol<set<TType, 0>>(name, value));
  return accept();
}

template <unsigned IDim> bool parser::match_real_definition() {
  init();
  if (!match_keyword("real")) {
    return reject();
  }

  size_t shape[IDim];
  if (IDim > 0) {
    if (!match(token::LBRACK)) {
      return reject();
    }
    for (int i = 0; i < IDim; ++i) {
      if (i > 0 && !match(token::COMMA)) {
        return reject();
      }
      base_index::basic_type value;
      if (!match_basic_or_evaluated<index<0>>(value)) {
        return reject();
      }
      shape[i] = value;
    }
    if (!match(token::RBRACK)) {
      return reject();
    }
  }
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!available(name)) {
    set_semantic("ERROR: Symbol declared under occupied name \"" + name + "\"");
    return reject();
  }
  consume();
  std::string comment;
  if (!match_literal(comment)) {
    comment = "";
  }
  if (match_any(token::SEMICOL, token::END)) {
    symbols.define(name, new variable_symbol<real<IDim>>(name, shape, comment));
    return accept();
  }
  if (match(token::DEFINE)) {
    typename real<0>::basic_type scalar_init;
    if (IDim > 0 && match_basic_or_evaluated<real<0>>(scalar_init)) {
      using basic_type = typename real<0>::basic_type;
      tensor<basic_type, IDim> value(shape, scalar_init);
      if (!match_any(token::SEMICOL, token::END)) {
        return reject();
      }
      symbols.define(name, new parameter_symbol<real<IDim>>(name, value));
      return accept();
    }
    typename real<IDim>::basic_type value;
    if (!match_basic_or_evaluated<real<IDim>>(value)) {
      return reject();
    }
    for (int i = 0; i < IDim; ++i) {
      if (shape[i] != value.shape(i)) {
        set_semantic("ERROR: Symbol \"" + name +
                     "\" defined with different shape than declared");
        return reject();
      }
    }
    if (!match_any(token::SEMICOL, token::END)) {
      return reject();
    }
    symbols.define(name, new parameter_symbol<real<IDim>>(name, value));
    return accept();
  }
  if (match_keyword("in")) {
    if (!match(token::LBRACK)) {
      return reject();
    }
    typename real<IDim>::basic_type lower(shape);
    typename real<0>::basic_type scalar_lower;
    if (IDim > 0 && match_basic_or_evaluated<real<0>>(scalar_lower)) {
      using basic_type = typename real<0>::basic_type;
      lower.ref().initialize(scalar_lower);
    } else {
      if (!match_basic_or_evaluated<real<IDim>>(lower)) {
        return reject();
      }
      for (int i = 0; i < IDim; ++i) {
        if (shape[i] != lower.shape(i)) {
          set_semantic("ERROR: Symbol \"" + name +
                       "\" defined with different shape than declared");
          return reject();
        }
      }
    }
    if (!match(token::COMMA)) {
      return reject();
    }
    typename real<IDim>::basic_type upper(shape);
    typename real<0>::basic_type scalar_upper;
    if (IDim > 0 && match_basic_or_evaluated<real<0>>(scalar_upper)) {
      using basic_type = typename real<0>::basic_type;
      upper.ref().initialize(scalar_upper);
    } else {
      if (!match_basic_or_evaluated<real<IDim>>(upper)) {
        return reject();
      }
      for (int i = 0; i < IDim; ++i) {
        if (shape[i] != upper.shape(i)) {
          set_semantic("ERROR: Symbol \"" + name +
                       "\" defined with different shape than declared");
          return reject();
        }
      }
    }
    if (!match(token::RBRACK)) {
      return reject();
    }
    if (!match_literal(comment)) {
      comment = "";
    }
    if (!match_any(token::SEMICOL, token::END)) {
      return reject();
    }
    symbols.define(
        name, new variable_symbol<real<IDim>>(name, lower, upper, comment));
    return accept();
  }
  return reject();
}

template <> inline bool parser::match_real_definition<0>() {
  init();
  if (!match_declarator<typename real<0>::atom_type>()) {
    return reject();
  }
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!available(name)) {
    set_semantic("ERROR: Symbol declared under occupied name \"" + name + "\"");
    return reject();
  }
  consume();
  std::string comment;
  if (!match_literal(comment)) {
    comment = "";
  }
  if (match_any(token::SEMICOL, token::END)) {
    symbols.define(name, new variable_symbol<real<0>>(name, comment));
    return accept();
  }
  if (match(token::DEFINE)) {
    typename real<0>::basic_type value;
    if (!match_basic_or_evaluated<real<0>>(value)) {
      return reject();
    }
    if (!match_any(token::SEMICOL, token::END)) {
      return reject();
    }
    symbols.define(name, new parameter_symbol<real<0>>(name, value));
    return accept();
  }
  if (match_keyword("in")) {
    if (!match(token::LBRACK)) {
      return reject();
    }
    typename real<0>::basic_type lower;
    if (!match_basic_or_evaluated<real<0>>(lower)) {
      return reject();
    }
    if (!match(token::COMMA)) {
      return reject();
    }
    typename real<0>::basic_type upper;
    if (!match_basic_or_evaluated<real<0>>(upper)) {
      return reject();
    }
    if (!match(token::RBRACK)) {
      return reject();
    }
    match_literal(comment);
    if (!match_any(token::SEMICOL, token::END)) {
      return reject();
    }
    symbols.define(name,
                   new variable_symbol<real<0>>(name, lower, upper, comment));
    return accept();
  }
  return reject();
}

template <unsigned IDim> bool parser::match_integer_definition() {
  init();
  if (!match_keyword("integer")) {
    return reject();
  }

  size_t shape[IDim];
  if (IDim > 0) {
    if (!match(token::LBRACK)) {
      return reject();
    }
    for (int i = 0; i < IDim; ++i) {
      if (i > 0 && !match(token::COMMA)) {
        return reject();
      }
      base_index::basic_type value;
      if (!match_basic_or_evaluated<index<0>>(value)) {
        return reject();
      }
      shape[i] = value;
    }
    if (!match(token::RBRACK)) {
      return reject();
    }
  }
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!available(name)) {
    set_semantic("ERROR: Symbol declared under occupied name \"" + name + "\"");
    return reject();
  }
  consume();
  std::string comment;
  if (!match_literal(comment)) {
    comment = "";
  }
  if (match_any(token::SEMICOL, token::END)) {
    symbols.define(name,
                   new variable_symbol<real<IDim>>(name, shape, comment, true));
    return accept();
  }
  if (!match_keyword("in")) {
    return reject();
  }
  if (!match(token::LBRACK)) {
    return reject();
  }
  typename real<IDim>::basic_type lower(shape);
  typename real<0>::basic_type scalar_lower;
  if (IDim > 0 && match_basic_or_evaluated<real<0>>(scalar_lower)) {
    using basic_type = typename real<0>::basic_type;
    lower.ref().initialize(scalar_lower);
  } else {
    if (!match_basic_or_evaluated<real<IDim>>(lower)) {
      return reject();
    }
    for (int i = 0; i < IDim; ++i) {
      if (shape[i] != lower.shape(i)) {
        set_semantic("ERROR: Symbol \"" + name +
                     "\" defined with different shape than declared");
        return reject();
      }
    }
  }
  if (!match(token::COMMA)) {
    return reject();
  }
  typename real<IDim>::basic_type upper(shape);
  typename real<0>::basic_type scalar_upper;
  if (IDim > 0 && match_basic_or_evaluated<real<0>>(scalar_upper)) {
    using basic_type = typename real<0>::basic_type;
    upper.ref().initialize(scalar_upper);
  } else {
    if (!match_basic_or_evaluated<real<IDim>>(upper)) {
      return reject();
    }
    for (int i = 0; i < IDim; ++i) {
      if (shape[i] != upper.shape(i)) {
        set_semantic("ERROR: Symbol \"" + name +
                     "\" defined with different shape than declared");
        return reject();
      }
    }
  }
  if (!match(token::RBRACK)) {
    return reject();
  }
  match_literal(comment);
  if (!match_any(token::SEMICOL, token::END)) {
    return reject();
  }
  symbols.define(
      name, new variable_symbol<real<IDim>>(name, lower, upper, comment, true));
  return accept();
}

template <> inline bool parser::match_integer_definition<0>() {
  init();
  if (!match_keyword("integer")) {
    return reject();
  }
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!available(name)) {
    set_semantic("ERROR: Symbol declared under occupied name \"" + name + "\"");
    return reject();
  }
  consume();
  std::string comment;
  if (!match_literal(comment)) {
    comment = "";
  }
  if (match_any(token::SEMICOL, token::END)) {
    symbols.define(name, new variable_symbol<real<0>>(name, comment, true));
    return accept();
  }
  if (!match_keyword("in")) {
    return reject();
  }
  if (!match(token::LBRACK)) {
    return reject();
  }
  typename real<0>::basic_type lower;
  if (!match_basic_or_evaluated<real<0>>(lower)) {
    return reject();
  }
  if (!match(token::COMMA)) {
    return reject();
  }
  typename real<0>::basic_type upper;
  if (!match_basic_or_evaluated<real<0>>(upper)) {
    return reject();
  }
  if (!match(token::RBRACK)) {
    return reject();
  }
  match_literal(comment);
  if (!match_any(token::SEMICOL, token::END)) {
    return reject();
  }
  symbols.define(
      name, new variable_symbol<real<0>>(name, lower, upper, comment, true));
  return accept();
}

template <unsigned IDim> bool parser::match_binary_definition() {
  init();
  if (!match_keyword("binary")) {
    return reject();
  }

  size_t shape[IDim];
  if (IDim > 0) {

    if (!match(token::LBRACK)) {
      return reject();
    }
    for (int i = 0; i < IDim; ++i) {
      if (i > 0 && !match(token::COMMA)) {
        return reject();
      }
      base_index::basic_type value;

      if (!match_basic_or_evaluated<index<0>>(value)) {
        return reject();
      }
      shape[i] = value;
    }
    if (!match(token::RBRACK)) {
      return reject();
    }
  }
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!available(name)) {
    set_semantic("ERROR: Symbol declared under occupied name \"" + name + "\"");
    return reject();
  }
  consume();
  std::string comment;
  if (!match_literal(comment)) {
    comment = "";
  }
  if (!match_any(token::SEMICOL, token::END)) {
    return reject();
  }
  typename real<IDim>::basic_type lower(shape, 0);
  typename real<IDim>::basic_type upper(shape, 1);
  symbols.define(
      name, new variable_symbol<real<IDim>>(name, lower, upper, comment, true));
  return accept();
}

template <> inline bool parser::match_binary_definition<0>() {
  init();
  if (!match_keyword("binary")) {
    return reject();
  }
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!available(name)) {
    set_semantic("ERROR: Symbol declared under occupied name \"" + name + "\"");
    return reject();
  }
  consume();
  std::string comment;
  if (!match_literal(comment)) {
    comment = "";
  }
  if (!match_any(token::SEMICOL, token::END)) {
    return reject();
  }
  symbols.define(name, new variable_symbol<real<0>>(name, 0, 1, comment, true));
  return accept();
}

// set{index[:,:]}[3]
// set{index}
template <typename TType, unsigned IDim>
inline bool parser::match_tensor_set_definition() {
  init();

  if (match_definition<set<TType, IDim>>()) {
    return accept();
  }
  if constexpr (IDim > 1) {
    if (match_tensor_set_definition<TType, IDim - 1>()) {
      return accept();
    }
  }

  return reject();
}

template <typename TType> bool parser::match_set_definition() {

  if (match_scalar_set_definition<TType>()) {
    return true;
  }
  // tensor of sets (of potentially tensors)
  return match_tensor_set_definition<TType, LIBALE_MAX_SET_DIM>();
}

template <typename TType> bool parser::match_expr_definition() {
  init();
  if (!match_declarator<typename TType::atom_type>()) {
    return reject();
  }
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!available(name)) {
    set_semantic("ERROR: Symbol declared under occupied name \"" + name + "\"");
    return reject();
  }
  consume();
  if (!match(token::DEFINE)) {
    return reject();
  }
  std::unique_ptr<value_node<TType>> expr;
  if (!match_value(expr)) {
    return reject();
  }
  if (!match_any(token::SEMICOL, token::END)) {
    return reject();
  }
  symbols.define(name, new expression_symbol<TType>(name, expr.release()));
  std::cout << "warning: parsed expression symbol \"" << name << "\".\n"
            << "         expresssion symbols are depricated and will be "
               "removed in the next release.\n"
            << "         use a function without arguments instead, e.g., "
               "\"real foo ( ) := <your_expression_here>;\"\n";
  return accept();
}

template <typename AtomType, unsigned IDim>
void parser::define_symbol(const std::string &name, size_t dim,
                           const std::vector<size_t> &shape) {
  if (dim == IDim) {
    if constexpr (IDim == 0) {
      symbols.define(name, new parameter_symbol<tensor_type<AtomType, IDim>>(
                               name, IsPlaceholderFlag::TRUE));
    } else {
      std::array<size_t, IDim> array_shape;
      std::copy_n(shape.begin(), IDim, array_shape.begin());

      symbols.define(name, new parameter_symbol<tensor_type<AtomType, IDim>>(
                               name, array_shape, IsPlaceholderFlag::TRUE));
      return;
    }
  }
  if constexpr (IDim > 0) {
    define_symbol<AtomType, IDim - 1>(name, dim, shape);
  }
}

template <typename TType> bool parser::match_function_definition() {
  init();

  constexpr auto IDim = get_node_dimension<TType>;

  if (!match_declarator<atom_type<TType>>()) {
    return reject();
  }

  std::vector<size_t> result_shape{};
  std::vector<size_t> result_wildcards{};
  result_shape.resize(IDim);
  if (IDim > 0) {
    if (!match(token::LBRACK)) {
      return reject();
    }

    // match index/wildcard
    for (int i = 0; i < IDim; ++i) {
      base_index::basic_type value;
      if (match_basic_or_evaluated<index<0>>(value)) {
        result_shape.at(i) = value;
      } else if (match(token::COLON)) {
        result_shape.at(i) = 0;
        result_wildcards.push_back(i);
      } else {
        return reject();
      }

      if (i + 1 < IDim) {
        if (!match(token::COMMA)) {
          return reject();
        }
      }
    }

    if (!match(token::RBRACK)) {
      return reject();
    }
  }

  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!available(name)) {
    set_semantic("ERROR: Symbol declared under occupied name \"" + name + "\"");
    return reject();
  }
  consume();
  if (!match(token::LPAREN)) {
    return reject();
  }

  std::vector<std::string> arg_names;
  std::vector<size_t> arg_dims;                // order of tensors
  std::vector<std::vector<size_t>> arg_shapes; // shape of tensors
  std::vector<std::vector<size_t>> arg_wildcards;

  symbols.push_scope(); // we define several variables in the while loop
  while (true) {
    if (match(token::RPAREN)) { // no function arguments
      break;
    }
    if (!match_declarator<atom_type<TType>>()) {
      symbols.pop_scope();
      return reject();
    }
    if (!match(token::LBRACK)) { // case real arg_name
      arg_dims.push_back(0);
      arg_shapes.emplace_back();
      arg_wildcards.emplace_back();

      if (!check(token::IDENT)) {
        symbols.pop_scope();
        return reject();
      }
      std::string arg_name = current().lexeme;
      arg_names.push_back(arg_name);
      consume();

      symbols.define(arg_name,
                     new parameter_symbol<tensor_type<atom_type<TType>, 0>>(
                         arg_name, IsPlaceholderFlag::TRUE));
    } else { // case real [2,4,...] arg_name
      std::vector<size_t> shape_current;
      std::vector<size_t> wildcards_current;
      while (true) {
        // match index/wildcard
        base_index::basic_type value;
        if (match_basic_or_evaluated<index<0>>(value)) {
          shape_current.push_back(value);
        } else if (match(token::COLON)) {
          wildcards_current.push_back(shape_current.size());
          shape_current.push_back(value);
        } else {
          symbols.pop_scope();
          return reject();
        }

        if (match(token::RBRACK)) {
          break;
        }
        if (!match(token::COMMA)) {
          symbols.pop_scope();
          return reject();
        }
      }

      if (!check(token::IDENT)) {
        symbols.pop_scope();
        return reject();
      }
      std::string arg_name = current().lexeme;
      consume();

      auto arg_dim = shape_current.size();
      arg_names.push_back(arg_name);
      arg_dims.push_back(arg_dim);
      arg_shapes.push_back(shape_current);
      arg_wildcards.push_back(wildcards_current);

      if (wildcards_current.empty()) {
        define_symbol<atom_type<TType>, LIBALE_MAX_DIM>(arg_name, arg_dim,
                                                        shape_current);
      } else {
        define_symbol<atom_type<TType>, LIBALE_MAX_DIM>(arg_name, arg_dim,
                                                        {arg_dim, 0});
      }
    }
    if (match(token::RPAREN)) {
      break;
    }
    if (!match(token::COMMA)) {
      symbols.pop_scope();
      return reject();
    }
  }

  if (!match(token::DEFINE)) {
    symbols.pop_scope();
    return reject();
  }

  std::unique_ptr<value_node<TType>> expression;
  if (!match_value(expression)) {
    symbols.pop_scope();
    return reject();
  }
  symbols.pop_scope();
  if (!match_any(token::SEMICOL, token::END)) {
    return reject();
  }

  symbols.define(
      name, new function_symbol<TType>(name, arg_names, arg_dims, arg_shapes,
                                       arg_wildcards, result_shape,
                                       result_wildcards, expression.release()));
  return accept();
}

// arzi01: My understanding is that here, we convert e.g. from a real<3> to a
// vector_node<real<3>> which is a value_node<real<1>>
template <typename AtomType, unsigned IDim>
bool parser::match_vectorized_arg(
    std::unique_ptr<value_node<tensor_type<AtomType, 1>>> &result,
    size_t expected_dim) {
  init();

  if (expected_dim == IDim) {
    std::unique_ptr<value_node<tensor_type<AtomType, IDim>>> arg;
    if (!match_value(arg)) {
      return reject();
    }
    result.reset(new vector_node<tensor_type<AtomType, IDim>>(arg.release()));
    return accept();
  }

  if constexpr (IDim > 0) {
    if (match_vectorized_arg<AtomType, IDim - 1>(result, expected_dim)) {
      return accept();
    }
    return reject();
  } else {
    return reject();
  }
}

// assign for all members of a set during parse time
template <unsigned IDim> bool parser::match_forall_assignment() {
  using TType = index<0>;
  init();
  if (!match_keyword("forall")) {
    return reject();
  }
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!available(name)) {
    set_semantic("ERROR: Symbol declared under occupied name \"" + name + "\"");
    return reject();
  }
  consume();
  if (!match_keyword("in")) {
    return reject();
  }
  std::unique_ptr<value_node<set<TType, 0>>> first_child;
  if (!match_value(first_child)) {
    return reject();
  }
  if (!match(token::COLON)) {
    return reject();
  }

  // list of all set members
  auto set_members = util::evaluate_expression(first_child.get(), symbols);

  // must check assignment in case of empty set
  if (set_members.empty()) {

    while (current().type != token::SEMICOL && current().type != token::END) {

      if (current().type == token::ASSIGN) {
        set_semantic("ERROR: Empty forall assignment");
        return reject();
      }
      consume();
    }

    return reject();
  }
  // for( const TType::basic_type& set_member: set_members)
  for (auto it = set_members.begin(); it != set_members.end(); it++) {
    const TType::basic_type &set_member = *it;
    bool is_last =
        (it != set_members.end() && ++decltype(it)(it) == set_members.end());
    // match same definition multiple times
    init(); // set new jump mark {A}
    symbols.push_scope();

    symbols.define(name, new parameter_symbol<TType>(name, set_member));
    bool successfull =
        match_any_assignment<IDim>(); // will move past the definition
    if (successfull) {
      if (is_last) {
        accept(); // move to after the position and remove mark A
      } else {
        reject(); // move again to position A in string before definition
      }
    } else {
      reject(); // remove jump mark A;
      set_semantic("ERROR: forall assigment with no valid assignment");
      symbols.pop_scope();
      return reject();
    }
    symbols.pop_scope();
  }
  return accept();
}

template <typename TType> bool parser::match_assignment() {
  init();
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  parameter_symbol<TType> *sym =
      cast_parameter_symbol<TType>(symbols.resolve(name));
  if (!sym) {
    if (!symbols.resolve(name)) {
      set_semantic("ERROR: Undefined symbol \"" + name + "\"");
    } else {
      set_semantic("ERROR: Symbol \"" + name + "\" of unexpected type");
    }
    return reject();
  }
  consume();
  size_t indexes[TType::dim];
  std::vector<size_t> wildcards;
  if (!match(token::LBRACK)) {
    return reject();
  }

  for (int i = 0; i < TType::dim; ++i) {
    if (i > 0 && !match(token::COMMA)) {
      return reject();
    }
    base_index::basic_type value;
    if (match_basic_or_evaluated<index<0>>(value)) {
      indexes[i] = value - 1;

    } else {
      if (!match(token::COLON)) {
        return reject();
      }
      wildcards.push_back(i);
      indexes[i] = 0;
    }
  }
  if (!match(token::RBRACK)) {
    return reject();
  }
  if (!match(token::ASSIGN)) {
    return reject();
  }
  typename TType::atom_type::basic_type value;
  if (!match_basic_or_evaluated<tensor_type<typename TType::atom_type, 0>>(
          value)) {
    return reject();
  }
  if (!match_any(token::END, token::SEMICOL)) {
    return reject();
  }
  for (int i = 0; i < TType::dim; ++i) {
    if (indexes[i] < 0 || indexes[i] >= sym->m_value.shape(i)) {
      set_semantic("ERROR: Assignment with index out of bounds for symbol \"" +
                   name + "\"");
      return reject();
    }
  }
  if (wildcards.size() != 0) {
    size_t n = wildcards.size() - 1;
    while (indexes[wildcards[n]] < sym->m_value.shape(wildcards[n])) {
      sym->m_value[indexes] = value;
      for (int i = 0; i <= n; ++i) {
        if (++indexes[wildcards[i]] < sym->m_value.shape(wildcards[i])) {
          break;
        } else if (i != n) {
          indexes[wildcards[i]] = 0;
        }
      }
    }
  } else {
    sym->m_value[indexes] = value;
  }
  return accept();
}

template <> inline bool parser::match_assignment<real<0>>() {
  init();
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;

  parameter_symbol<real<0>> *sym =
      cast_parameter_symbol<real<0>>(symbols.resolve(name));
  if (!sym) {
    if (!symbols.resolve(name)) {
      set_semantic("ERROR: Undefined symbol \"" + name + "\"");
    } else {
      set_semantic("ERROR: Symbol \"" + name + "\" of unexpected type");
    }
    return reject();
  }
  consume();

  if (!match(token::ASSIGN)) {
    return reject();
  }
  real<0>::basic_type value;
  if (!match_basic_or_evaluated<real<0>>(value)) {
    return reject();
  }
  if (!match_any(token::END, token::SEMICOL)) {
    return reject();
  }
  sym->m_value = value;
  return accept();
}

template <> inline bool parser::match_assignment<index<0>>() {
  init();
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;

  parameter_symbol<index<0>> *sym =
      cast_parameter_symbol<index<0>>(symbols.resolve(name));
  if (!sym) {
    if (!symbols.resolve(name)) {
      set_semantic("ERROR: Undefined symbol \"" + name + "\"");
    } else {
      set_semantic("ERROR: Symbol \"" + name + "\" of unexpected type");
    }
    return reject();
  }
  consume();

  if (!match(token::ASSIGN)) {
    return reject();
  }
  index<0>::basic_type value;
  if (!match_basic_or_evaluated<index<0>>(value)) {
    return reject();
  }
  if (!match_any(token::END, token::SEMICOL)) {
    return reject();
  }
  sym->m_value = value;
  return accept();
}

template <> inline bool parser::match_assignment<boolean<0>>() {
  init();
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  parameter_symbol<boolean<0>> *sym =
      cast_parameter_symbol<boolean<0>>(symbols.resolve(name));
  if (!sym) {
    if (!symbols.resolve(name)) {
      set_semantic("ERROR: Undefined symbol \"" + name + "\"");
    } else {
      set_semantic("ERROR: Symbol \"" + name + "\" of unexpected type");
    }
    return reject();
  }
  consume();
  if (!match(token::ASSIGN)) {
    return reject();
  }
  boolean<0>::basic_type value;
  if (!match_basic_or_evaluated<boolean<0>>(value)) {
    return reject();
  }
  if (!match_any(token::END, token::SEMICOL)) {
    return reject();
  }
  sym->m_value = value;
  return accept();
}

template <unsigned IDim> bool parser::match_bound_assignment() {
  init();
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  variable_symbol<real<IDim>> *sym =
      cast_variable_symbol<real<IDim>>(symbols.resolve(name));
  if (!sym) {
    if (!symbols.resolve(name)) {
      set_semantic("ERROR: Undefined symbol \"" + name + "\"");
    } else {
      set_semantic("ERROR: Symbol \"" + name + "\" of unexpected type");
    }
    return reject();
  }
  consume();
  if (!match(token::DOT)) {
    return reject();
  }
  bool upper = false;
  if (match_keyword("ub")) {
    upper = true;
  } else if (!match_keyword("lb")) {
    return reject();
  }
  size_t indexes[IDim];
  std::vector<size_t> wildcards;
  if (!match(token::LBRACK)) {
    return reject();
  }

  for (int i = 0; i < IDim; ++i) {
    if (i > 0 && !match(token::COMMA)) {
      return reject();
    }
    base_index::basic_type value;
    if (match_basic_or_evaluated<index<0>>(value)) {
      indexes[i] = value - 1;
    } else {
      if (!match(token::COLON)) {
        return reject();
      }
      wildcards.push_back(i);
      indexes[i] = 0;
    }
  }
  if (!match(token::RBRACK)) {
    return reject();
  }
  if (!match(token::ASSIGN)) {
    return reject();
  }
  real<0>::basic_type value;
  if (!match_basic_or_evaluated<real<0>>(value)) {
    return reject();
  }
  if (!match_any(token::END, token::SEMICOL)) {
    return reject();
  }
  for (int i = 0; i < IDim; ++i) {
    if (indexes[i] < 0 || indexes[i] >= sym->shape(i)) {
      set_semantic("ERROR: Assignment with index out of bounds for symbol \"" +
                   name + "\"");
      return reject();
    }
  }
  if (wildcards.size() != 0) {
    size_t n = wildcards.size() - 1;
    while (indexes[wildcards[n]] < sym->shape(wildcards[n])) {
      if (upper) {
        sym->upper()[indexes] = value;
      } else {
        sym->lower()[indexes] = value;
      }
      for (int i = 0; i <= n; ++i) {
        if (++indexes[wildcards[i]] < sym->shape(wildcards[i])) {
          break;
        } else if (i != n) {
          indexes[wildcards[i]] = 0;
        }
      }
    }
  } else {
    if (upper) {
      sym->upper()[indexes] = value;
    } else {
      sym->lower()[indexes] = value;
    }
  }
  return accept();
}

template <> inline bool parser::match_bound_assignment<0>() {
  init();
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  variable_symbol<real<0>> *sym =
      cast_variable_symbol<real<0>>(symbols.resolve(name));
  if (!sym) {
    if (!symbols.resolve(name)) {
      set_semantic("ERROR: Undefined symbol \"" + name + "\"");
    } else {
      set_semantic("ERROR: Symbol \"" + name + "\" of unexpected type");
    }
    return reject();
  }
  consume();
  if (!match(token::DOT)) {
    return reject();
  }
  bool upper = false;
  if (match_keyword("ub")) {
    upper = true;
  } else if (!match_keyword("lb")) {
    return reject();
  }
  if (!match(token::ASSIGN)) {
    return reject();
  }
  real<0>::basic_type value;
  if (!match_basic_or_evaluated<real<0>>(value)) {
    return reject();
  }
  if (!match_any(token::END, token::SEMICOL)) {
    return reject();
  }
  if (upper) {
    sym->upper() = value;
  } else {
    sym->lower() = value;
  }
  return accept();
}

template <unsigned IDim> bool parser::match_init_assignment() {
  init();
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  variable_symbol<real<IDim>> *sym =
      cast_variable_symbol<real<IDim>>(symbols.resolve(name));
  if (!sym) {
    if (!symbols.resolve(name)) {
      set_semantic("ERROR: Undefined symbol \"" + name + "\"");
    } else {
      set_semantic("ERROR: Symbol \"" + name + "\" of unexpected type");
    }
    return reject();
  }
  consume();
  if (!match(token::DOT)) {
    return reject();
  }
  if (!match_keyword("init")) {
    return reject();
  }
  size_t indexes[IDim];
  std::vector<size_t> wildcards;
  if (!match(token::LBRACK)) {
    return reject();
  }

  for (int i = 0; i < IDim; ++i) {
    if (i > 0 && !match(token::COMMA)) {
      return reject();
    }
    base_index::basic_type value;
    if (match_basic_or_evaluated<index<0>>(value)) {
      indexes[i] = value - 1;

    } else {
      if (!match(token::COLON)) {
        return reject();
      }
      wildcards.push_back(i);
      indexes[i] = 0;
    }
  }
  if (!match(token::RBRACK)) {
    return reject();
  }
  if (!match(token::ASSIGN)) {
    return reject();
  }
  real<0>::basic_type value;
  if (!match_basic_or_evaluated<real<0>>(value)) {
    return reject();
  }
  if (!match_any(token::END, token::SEMICOL)) {
    return reject();
  }
  for (int i = 0; i < IDim; ++i) {
    if (indexes[i] < 0 || indexes[i] >= sym->shape(i)) {
      set_semantic("ERROR: Assignment with index out of bounds for symbol \"" +
                   name + "\"");
      return reject();
    }
  }
  if (wildcards.size() != 0) {
    size_t n = wildcards.size() - 1;
    while (indexes[wildcards[n]] < sym->shape(wildcards[n])) {
      sym->init()[indexes] = value;
      for (int i = 0; i <= n; ++i) {
        if (++indexes[wildcards[i]] < sym->shape(wildcards[i])) {
          break;
        } else if (i != n) {
          indexes[wildcards[i]] = 0;
        }
      }
    }
  } else {
    sym->init()[indexes] = value;
  }
  return accept();
}

template <> inline bool parser::match_init_assignment<0>() {
  init();
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  variable_symbol<real<0>> *sym =
      cast_variable_symbol<real<0>>(symbols.resolve(name));
  if (!sym) {
    if (!symbols.resolve(name)) {
      set_semantic("ERROR: Undefined symbol \"" + name + "\"");
    } else {
      set_semantic("ERROR: Symbol \"" + name + "\" of unexpected type");
    }
    return reject();
  }
  consume();
  if (!match(token::DOT)) {
    return reject();
  }
  if (!match_keyword("init")) {
    return reject();
  }
  if (!match(token::ASSIGN)) {
    return reject();
  }
  real<0>::basic_type value;
  if (!match_basic_or_evaluated<real<0>>(value)) {
    return reject();
  }
  if (!match_any(token::END, token::SEMICOL)) {
    return reject();
  }
  sym->init() = value;
  return accept();
}

template <unsigned IDim> bool parser::match_prio_assignment() {
  init();
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  variable_symbol<real<IDim>> *sym =
      cast_variable_symbol<real<IDim>>(symbols.resolve(name));
  if (!sym) {
    if (!symbols.resolve(name)) {
      set_semantic("ERROR: Undefined symbol \"" + name + "\"");
    } else {
      set_semantic("ERROR: Symbol \"" + name + "\" of unexpected type");
    }
    return reject();
  }
  consume();
  if (!match(token::DOT)) {
    return reject();
  }
  if (!match_keyword("prio")) {
    return reject();
  }
  size_t indexes[IDim];
  std::vector<size_t> wildcards;
  if (!match(token::LBRACK)) {
    return reject();
  }

  for (int i = 0; i < IDim; ++i) {
    if (i > 0 && !match(token::COMMA)) {
      return reject();
    }
    base_index::basic_type value;
    if (match_basic_or_evaluated<index<0>>(value)) {
      indexes[i] = value - 1;

    } else {
      if (!match(token::COLON)) {
        return reject();
      }
      wildcards.push_back(i);
      indexes[i] = 0;
    }
  }
  if (!match(token::RBRACK)) {
    return reject();
  }
  if (!match(token::ASSIGN)) {
    return reject();
  }
  real<0>::basic_type value;
  if (!match_basic_or_evaluated<real<0>>(value)) {
    return reject();
  }
  if (value <= 0) {
    set_semantic("ERROR: Branching priorities less than zero are not supported "
                 "(used for symbol \"" +
                 name + "\")");
    return reject();
  }
  if (!match_any(token::END, token::SEMICOL)) {
    return reject();
  }
  for (int i = 0; i < IDim; ++i) {
    if (indexes[i] < 0 || indexes[i] >= sym->shape(i)) {
      set_semantic("ERROR: Assignment with index out of bounds for symbol \"" +
                   name + "\"");
      return reject();
    }
  }
  if (wildcards.size() != 0) {
    size_t n = wildcards.size() - 1;
    while (indexes[wildcards[n]] < sym->shape(wildcards[n])) {
      sym->prio()[indexes] = value;
      for (int i = 0; i <= n; ++i) {
        if (++indexes[wildcards[i]] < sym->shape(wildcards[i])) {
          break;
        } else if (i != n) {
          indexes[wildcards[i]] = 0;
        }
      }
    }
  } else {
    sym->prio()[indexes] = value;
  }
  return accept();
}

template <> inline bool parser::match_prio_assignment<0>() {
  init();
  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  variable_symbol<real<0>> *sym =
      cast_variable_symbol<real<0>>(symbols.resolve(name));
  if (!sym) {
    if (!symbols.resolve(name)) {
      set_semantic("ERROR: Undefined symbol \"" + name + "\"");
    } else {
      set_semantic("ERROR: Symbol \"" + name + "\" of unexpected type");
    }
    return reject();
  }
  consume();
  if (!match(token::DOT)) {
    return reject();
  }
  if (!match_keyword("prio")) {
    return reject();
  }
  if (!match(token::ASSIGN)) {
    return reject();
  }
  real<0>::basic_type value;
  if (!match_basic_or_evaluated<real<0>>(value)) {
    return reject();
  }
  if (value <= 0) {
    set_semantic("ERROR: Branching priorities less than zero are not supported "
                 "(used for symbol \"" +
                 name + "\")");
    return reject();
  }
  if (!match_any(token::END, token::SEMICOL)) {
    return reject();
  }
  sym->prio() = value;
  return accept();
}

template <typename TType>
bool parser::match_tensor_node(std::unique_ptr<value_node<TType>> &result) {
  init();
  if (!match(token::LPAREN)) {
    return reject();
  }
  std::unique_ptr<value_node<entry_of<TType>>> child;
  if (!match_value(child)) {
    return reject();
  }
  std::unique_ptr<tensor_node<TType>> res(new tensor_node<TType>());
  res->add_child(child.release());
  while (!match(token::RPAREN)) {
    if (!match(token::COMMA)) {
      return reject();
    }
    if (!match_value(child)) {
      return reject();
    }
    res->add_child(child.release());
  }
  result.reset(res.release());
  return accept();
}

template <typename NodeType, typename ResultType>
bool parser::match_internal_function(
    std::unique_ptr<value_node<ResultType>> &result,
    const std::string &function_name) {
  return match_internal_function_impl<NodeType>(
      result, function_name, static_cast<NodeType *>(nullptr));
}

template <typename NodeType, typename ResultType, typename... TTypes>
bool parser::match_internal_function_impl(
    std::unique_ptr<value_node<ResultType>> &result,
    const std::string &function_name, kary_node<TTypes...> *node) {
  init();
  if (!match_keyword(function_name)) {
    return reject();
  }

  std::tuple<std::unique_ptr<value_node<TTypes>>...> children;
  if (!match(token::LPAREN)) {
    return reject();
  }

  size_t current_node = 0;
  size_t last_node = sizeof...(TTypes) - 1;
  bool all_args_matched = true;
  auto match_arg = [this, &current_node, last_node,
                    &all_args_matched](auto &&arg) {
    // if match already failed, theres no need to check any further
    if (all_args_matched) {
      // try to match next argument
      if (!match_value(arg)) {
        all_args_matched = false;
      }

      // if current_node is not the last match a comma
      if (current_node != last_node) {
        if (!match(token::COMMA)) {
          all_args_matched = false;
        }
      }

      current_node += 1;
    }
  };

  std::apply([&match_arg](auto &&...args) { (match_arg(args), ...); },
             children);

  if (!all_args_matched) {
    return reject();
  }

  if (!match(token::RPAREN)) {
    return reject();
  }

  auto children_pointers =
      tuple_for_each([](auto &&arg) { return arg.release(); }, children);
  auto new_node = std::make_from_tuple<NodeType>(children_pointers);
  result.reset(new NodeType(new_node));

  return accept();
}

template <typename NodeType, typename ResultType, typename TType>
bool parser::match_internal_function_impl(
    std::unique_ptr<value_node<ResultType>> &result,
    const std::string &function_name, nary_node<TType> *node) {
  init();
  if (!match_keyword(function_name)) {
    return reject();
  }

  if (!match(token::LPAREN)) {
    return reject();
  }

  auto parent = std::make_unique<NodeType>();
  std::unique_ptr<value_node<TType>> tmp_child;
  while (true) {
    if (!match_value(tmp_child)) {
      return reject();
    }
    parent->add_child(tmp_child.release());
    if (!match(token::COMMA)) {
      break;
    }
  }

  if (!match(token::RPAREN)) {
    return reject();
  }

  result = std::move(parent);

  return accept();
}

template <typename NodeType, typename ResultType, typename IteratorType,
          typename TType>
bool parser::match_internal_function_impl(
    std::unique_ptr<value_node<ResultType>> &result,
    const std::string &function_name,
    iterator_node<IteratorType, TType> *node) {
  init();
  if (!match_keyword(function_name)) {
    return reject();
  }

  if (!match(token::LPAREN)) {
    return reject();
  }

  if (!check(token::IDENT)) {
    return reject();
  }
  std::string name = current().lexeme;
  if (!available(name)) {
    set_semantic("ERROR: Symbol declared under occupied name \"" + name + "\"");
    return reject();
  }
  consume();
  if (!match_keyword("in")) {
    return reject();
  }

  std::unique_ptr<value_node<set<IteratorType, 0>>> first_child;
  if (!match_value(first_child)) {
    return reject();
  }

  if (!match(token::COLON)) {
    return reject();
  }

  symbols.push_scope();
  symbols.define(
      name, new parameter_symbol<IteratorType>(name, IsPlaceholderFlag::TRUE));
  std::unique_ptr<value_node<TType>> second_child;
  if (!match_value(second_child)) {
    symbols.pop_scope();
    return reject();
  }
  if (!match(token::RPAREN)) {
    symbols.pop_scope();
    return reject();
  }
  result.reset(
      new NodeType(name, first_child.release(), second_child.release()));
  symbols.pop_scope();

  return accept();
}

} // namespace ale
