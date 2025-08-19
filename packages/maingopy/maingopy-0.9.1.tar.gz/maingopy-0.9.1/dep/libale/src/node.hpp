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

#include "config.hpp"
#include "helper.hpp"
#include "value.hpp"
#include "util/owner.hpp"

#include <list>
#include <memory>
#include <string>
#include <tuple>
#include <variant>

namespace ale {

// value node types
template <typename TType>
struct constant_node;
template <typename TType>
struct parameter_node;
template <typename TType>
struct attribute_node;
template <typename TType>
struct entry_node;
template <typename TType>
struct vector_node;
template <typename TType>
struct function_node;
template <typename TType>
struct tensor_node;
template <typename TType>
struct index_shift_node;

// generic value_node for arbitrary tensor-types
template <typename TType>
struct value_node {
    virtual ~value_node() {};
    using basic_type = typename TType::basic_type;
    using var = std::variant<constant_node<TType> *, parameter_node<TType> *,
      attribute_node<TType> *, entry_node<TType> *,
      function_node<TType> *, tensor_node<TType> *,
      index_shift_node<TType> *>;
    virtual var get_variant() = 0;
    virtual value_node<TType> *clone() = 0;
};

// pack to specialize value_node<real<1>> to also allow for vector node of
// real_types (real<1>, real<2>).
using real_vector_node_types = typename combined_pack<
  pack<constant_node<real<1>> *, parameter_node<real<1>> *,
    attribute_node<real<1>> *, entry_node<real<1>> *,
    function_node<real<1>> *, tensor_node<real<1>> *,
    index_shift_node<real<1>> *>,
  pointer_pack_from_pack<vector_node, real_types>::type>::type;

template <>
struct value_node<real<1>> {
    virtual ~value_node() {};
    using basic_type = typename real<1>::basic_type;
    using var = typename from_pack<std::variant, real_vector_node_types>::type;
    virtual var get_variant() = 0;
    virtual value_node<real<1>> *clone() = 0;
};
// pack to specialize value_node<index<1>>
using index_vector_node_types = typename combined_pack<
  pack<constant_node<index<1>> *, parameter_node<index<1>> *,
    entry_node<index<1>> *, function_node<index<1>> *,
    tensor_node<index<1>> *, index_shift_node<index<1>> *>,
  pointer_pack_from_pack<vector_node, index_types>::type>::type;

template <>
struct value_node<index<1>> {
    virtual ~value_node() {};
    using basic_type = typename index<1>::basic_type;
    using var = typename from_pack<std::variant, index_vector_node_types>::type;
    virtual var get_variant() = 0;
    virtual value_node<index<1>> *clone() = 0;
};
// pack to specialize value_node<index<1>>
using boolean_vector_node_types = typename combined_pack<
  pack<constant_node<boolean<1>> *, parameter_node<boolean<1>> *,
    entry_node<boolean<1>> *, function_node<boolean<1>> *,
    tensor_node<boolean<1>> *, index_shift_node<boolean<1>> *>,
  pointer_pack_from_pack<vector_node, boolean_types>::type>::type;

template <>
struct value_node<boolean<1>> {
    virtual ~value_node() {};
    using basic_type = typename boolean<1>::basic_type;
    using var = typename from_pack<std::variant, boolean_vector_node_types>::type;
    virtual var get_variant() = 0;
    virtual value_node<boolean<1>> *clone() = 0;
};
// value_node specializations for tensor-types to terminate upward dependency
// through entry_node
template <>
struct value_node<real<LIBALE_MAX_DIM>> {
    virtual ~value_node() {};
    using basic_type = typename real<LIBALE_MAX_DIM>::basic_type;
    using var = std::variant<constant_node<real<LIBALE_MAX_DIM>> *,
      parameter_node<real<LIBALE_MAX_DIM>> *,
      attribute_node<real<LIBALE_MAX_DIM>> *,
      function_node<real<LIBALE_MAX_DIM>> *,
      tensor_node<real<LIBALE_MAX_DIM>> *,
      index_shift_node<real<LIBALE_MAX_DIM>> *>;
    virtual var get_variant() = 0;
    virtual value_node<real<LIBALE_MAX_DIM>> *clone() = 0;
};
template <>
struct value_node<index<LIBALE_MAX_DIM>> {
    virtual ~value_node() {};
    using basic_type = typename index<LIBALE_MAX_DIM>::basic_type;
    using var = std::variant<constant_node<index<LIBALE_MAX_DIM>> *,
      parameter_node<index<LIBALE_MAX_DIM>> *,
      function_node<index<LIBALE_MAX_DIM>> *,
      tensor_node<index<LIBALE_MAX_DIM>> *,
      index_shift_node<index<LIBALE_MAX_DIM>> *>;
    virtual var get_variant() = 0;
    virtual value_node<index<LIBALE_MAX_DIM>> *clone() = 0;
};
template <>
struct value_node<boolean<LIBALE_MAX_DIM>> {
    virtual ~value_node() {};
    using basic_type = typename boolean<LIBALE_MAX_DIM>::basic_type;
    using var = std::variant<constant_node<boolean<LIBALE_MAX_DIM>> *,
      parameter_node<boolean<LIBALE_MAX_DIM>> *,
      function_node<boolean<LIBALE_MAX_DIM>> *,
      tensor_node<boolean<LIBALE_MAX_DIM>> *,
      index_shift_node<boolean<LIBALE_MAX_DIM>> *>;
    virtual var get_variant() = 0;
    virtual value_node<boolean<LIBALE_MAX_DIM>> *clone() = 0;
};

template <typename TElement>
struct value_node<set<TElement, LIBALE_MAX_SET_DIM>> {
    virtual ~value_node() {};
    using basic_type = typename set<TElement, LIBALE_MAX_SET_DIM>::basic_type;
    using var = std::variant<constant_node<set<TElement, LIBALE_MAX_SET_DIM>> *,
      parameter_node<set<TElement, LIBALE_MAX_SET_DIM>> *>;
    virtual var get_variant() = 0;
    virtual value_node<set<TElement, LIBALE_MAX_SET_DIM>> *clone() = 0;
};

// value_node specializations for tensor-types of dimension 0
struct minus_node;
struct round_node;
struct index_to_real_node;
struct real_to_index_node;
struct inverse_node;
struct addition_node;
struct multiplication_node;
struct exponentiation_node;
struct min_node;
struct max_node;
struct mid_node;
struct sqrt_node;
struct abs_node;
struct xabsx_node;
struct sin_node;
struct asin_node;
struct cos_node;
struct acos_node;
struct tan_node;
struct atan_node;
struct cosh_node;
struct sinh_node;
struct tanh_node;
struct coth_node;
struct acosh_node;
struct asinh_node;
struct atanh_node;
struct acoth_node;
struct arh_node;
struct exp_node;
struct xexpy_node;
struct xexpax_node;
struct log_node;
struct xlogx_node;
struct erf_node;
struct erfc_node;
struct norm2_node;
struct sum_div_node;
struct xlog_sum_node;
struct single_neuron_node;
struct pos_node;
struct neg_node;
struct lb_func_node;
struct ub_func_node;
struct bounding_func_node;
struct lmtd_node;
struct rlmtd_node;
struct cost_turton_node;
struct nrtl_tau_node;
struct nrtl_dtau_node;
struct nrtl_g_node;
struct nrtl_gtau_node;
struct nrtl_gdtau_node;
struct nrtl_dgtau_node;
struct antoine_psat_node;
struct ext_antoine_psat_node;
struct wagner_psat_node;
struct ik_cape_psat_node;
struct antoine_tsat_node;
struct aspen_hig_node;
struct nasa9_hig_node;
struct dippr107_hig_node;
struct dippr127_hig_node;
struct watson_dhvap_node;
struct dippr106_dhvap_node;
struct schroeder_ethanol_p_node;
struct schroeder_ethanol_rhovap_node;
struct schroeder_ethanol_rholiq_node;
struct covar_matern_1_node;
struct covar_matern_3_node;
struct covar_matern_5_node;
struct covar_sqrexp_node;
struct af_lcb_node;
struct af_ei_node;
struct af_pi_node;
struct gpdf_node;
struct regnormal_node;
struct squash_node;

template <typename TType>
struct sum_node;
template <typename TType>
struct product_node;
template <typename TType>
struct set_min_node;
template <typename TType>
struct set_max_node;

using real_node_types = typename combined_pack<
  pack<constant_node<real<0>> *, parameter_node<real<0>> *,
    attribute_node<real<0>> *, entry_node<real<0>> *, minus_node *,
    round_node *, index_to_real_node *, inverse_node *, addition_node *,
    multiplication_node *, exponentiation_node *, min_node *, max_node *,
    mid_node *, sqrt_node *, abs_node *, xabsx_node *, sin_node *,
    asin_node *, cos_node *, acos_node *, tan_node *, atan_node *,
    cosh_node *, sinh_node *, tanh_node *, coth_node *, acosh_node *,
    asinh_node *, atanh_node *, acoth_node *, arh_node *, exp_node *,
    xexpy_node *, xexpax_node *, log_node *, xlogx_node *, erf_node *,
    erfc_node *, norm2_node *, sum_div_node *, xlog_sum_node *, single_neuron_node *, pos_node *,
    neg_node *, lb_func_node *, ub_func_node *, bounding_func_node *,
    lmtd_node *, rlmtd_node *, cost_turton_node *, nrtl_tau_node *,
    nrtl_dtau_node *, nrtl_g_node *, nrtl_gtau_node *, nrtl_gdtau_node *,
    nrtl_dgtau_node *, antoine_psat_node *, ext_antoine_psat_node *,
    wagner_psat_node *, ik_cape_psat_node *, antoine_tsat_node *,
    aspen_hig_node *, nasa9_hig_node *, dippr107_hig_node *,
    dippr127_hig_node *, watson_dhvap_node *, dippr106_dhvap_node *,
    squash_node *, schroeder_ethanol_p_node *,
    schroeder_ethanol_rhovap_node *, schroeder_ethanol_rholiq_node *,
    covar_matern_1_node *, covar_matern_3_node *, covar_matern_5_node *,
    covar_sqrexp_node *, af_lcb_node *, af_ei_node *, af_pi_node *,
    gpdf_node *, regnormal_node *, function_node<real<0>> *>,
  pointer_pack_from_pack<sum_node, real_types>::type,
  pointer_pack_from_pack<sum_node, index_types>::type,
  pointer_pack_from_pack<product_node, real_types>::type,
  pointer_pack_from_pack<product_node, index_types>::type,
  pointer_pack_from_pack<set_min_node, real_types>::type,
  pointer_pack_from_pack<set_min_node, index_types>::type,
  pointer_pack_from_pack<set_max_node, real_types>::type,
  pointer_pack_from_pack<set_max_node, index_types>::type>::type;

template <>
struct value_node<real<0>> {
    virtual ~value_node() {};
    using basic_type = typename real<0>::basic_type;
    using var = typename from_pack<std::variant, real_node_types>::type;
    virtual var get_variant() = 0;
    virtual value_node<real<0>> *clone() = 0;
};

struct index_minus_node;
struct index_addition_node;
struct index_multiplication_node;

using index_node_types = pack<constant_node<index<0>> *, parameter_node<index<0>> *,
  entry_node<index<0>> *, real_to_index_node *, index_minus_node *,
  index_addition_node *, index_multiplication_node *,
  function_node<index<0>> *>;

template <>
struct value_node<index<0>> {
    virtual ~value_node() {};
    using basic_type = typename index<0>::basic_type;
    using var = typename from_pack<std::variant, index_node_types>::type;
    virtual var get_variant() = 0;
    virtual value_node<index<0>> *clone() = 0;
};

struct negation_node;
struct disjunction_node;
struct conjunction_node;
template <typename TType>
struct element_node;
template <typename TType>
struct equal_node;
template <typename TType>
struct less_node;
template <typename TType>
struct less_equal_node;
template <typename TType>
struct greater_node;
template <typename TType>
struct greater_equal_node;
template <typename TType>
struct forall_node;

using boolean_node_types = typename combined_pack<
  pack<constant_node<boolean<0>> *, parameter_node<boolean<0>> *,
    negation_node *, equal_node<real<0>> *, less_node<real<0>> *,
    less_equal_node<real<0>> *, greater_equal_node<real<0>> *,
    greater_node<real<0>> *, equal_node<index<0>> *, less_node<index<0>> *,
    less_equal_node<index<0>> *, greater_equal_node<index<0>> *,
    greater_node<index<0>> *, disjunction_node *, conjunction_node *,
    entry_node<boolean<0>> *, element_node<real<0>> *, element_node<index<0>> *,
    element_node<boolean<0>> *, function_node<boolean<0>> *>,
  pointer_pack_from_pack<forall_node, real_types>::type,
  pointer_pack_from_pack<forall_node, index_types>::type>::type;

template <>
struct value_node<boolean<0>> {
    virtual ~value_node() {};
    using basic_type = typename boolean<0>::basic_type;
    using var = typename from_pack<std::variant, boolean_node_types>::type;
    virtual var get_variant() = 0;
    virtual value_node<boolean<0>> *clone() = 0;
};

// generic value_node for set-types
template <typename TType>
struct indicator_set_node;

template <typename TType>
struct value_node<set<TType, 0>> {
    virtual ~value_node() {};
    using basic_type = typename set<TType, 0>::basic_type;
    using var = std::variant<constant_node<set<TType, 0>> *,
      parameter_node<set<TType, 0>> *, entry_node<set<TType, 0>> *,
      indicator_set_node<TType> *>;
    virtual var get_variant() = 0;
    virtual value_node<set<TType, 0>> *clone() = 0;
};

// copyable specialization of unique_ptr for storing value_node
template <typename TType>
struct value_node_ptr : public std::unique_ptr<value_node<TType>> {
    using std::unique_ptr<value_node<TType>>::unique_ptr;
    using std::unique_ptr<value_node<TType>>::reset;
    using std::unique_ptr<value_node<TType>>::release;
    using std::unique_ptr<value_node<TType>>::get;
    // copy constructor using deep copy (clone) method of value_node
    value_node_ptr(const value_node_ptr<TType> &other) :
        std::unique_ptr<value_node<TType>>() {
        reset(other ? other->clone() : nullptr);
    }
    // copy assignment using deep copy (clone) method of value_node
    value_node_ptr<TType> &operator=(const value_node_ptr<TType> &other) {
        reset(other ? other->clone() : nullptr);
        return *this;
    }
};

using value_node_ptr_types = typename combined_pack<
  ref_pack_from_pack<value_node_ptr, real_types>::type,
  ref_pack_from_pack<value_node_ptr, index_types>::type,
  ref_pack_from_pack<value_node_ptr, boolean_types>::type,
  ref_pack_from_pack<value_node_ptr, real_set_types>::type,
  ref_pack_from_pack<value_node_ptr, index_set_types>::type,
  ref_pack_from_pack<value_node_ptr, boolean_set_types>::type>::type;
using value_node_ptr_variant =
  typename from_pack<std::variant, value_node_ptr_types>::type;

using value_node_types = typename combined_pack<
  pointer_pack_from_pack<value_node, real_types>::type,
  pointer_pack_from_pack<value_node, index_types>::type,
  pointer_pack_from_pack<value_node, boolean_types>::type,
  pointer_pack_from_pack<value_node, real_set_types>::type,
  pointer_pack_from_pack<value_node, index_set_types>::type,
  pointer_pack_from_pack<value_node, boolean_set_types>::type>::type;
using value_node_variant =
  typename from_pack<std::variant, value_node_types>::type;

template <typename TNode, typename TType>
struct derived_value_node : value_node<TType> {
    using typename value_node<TType>::var;
    var get_variant() override { return static_cast<TNode *>(this); }
    // deep copy relies on TNode being copy constructable
    // this is provided by TNode using value_node_ptrs rather than unique_ptrs
    gsl::owner<value_node<TType>*> clone() override {
        return new TNode(static_cast<TNode &>(*this));
    }
};

// structural node types
struct terminal_node { };

template <typename... TTypes>
struct kary_node {
    kary_node(gsl::owner<value_node<TTypes>*>...args) :
        children(args...) {};
    template <size_t I>
    void set_child(gsl::owner<value_node<typename pick<I, TTypes...>::type>> *node) {
        std::get<I>(children).reset(node);
    }
    template <size_t I>
    value_node<typename pick<I, TTypes...>::type> *get_child() {
        return std::get<I>(children).get();
    }
    std::tuple<value_node_ptr<TTypes>...> children;
};

template <typename IteratorType, typename TType>
struct iterator_node : kary_node<set<IteratorType, 0>, TType> {
    iterator_node(const std::string &name,
      gsl::owner<value_node<set<IteratorType, 0>>*> first,
      gsl::owner<value_node<TType>*> second) :
        kary_node<set<IteratorType, 0>, TType>::kary_node(first, second),
        name(name) {};
    std::string name;
};

template <typename TType>
struct nary_node {
    void add_child(gsl::owner<value_node<TType>*> node) { children.emplace_back(node); };
    std::list<value_node_ptr<TType>> children;
};

// terminal nodes
template <typename TType>
struct constant_node : derived_value_node<constant_node<TType>, TType>,
                       terminal_node {
    constant_node() :
        value(ale::basic_type<TType>()) {};
    constant_node(const ale::basic_type<TType> &value) :
        value(value) {};
    owning_cref<TType> value; // this still copies sets -> type of cref for sets
                              // has to be changed in order to avoid that
};

template <typename TType>
struct parameter_node : derived_value_node<parameter_node<TType>, TType>,
                        terminal_node {
    parameter_node(std::string name) :
        name(name) {};
    std::string name;
};

// for respresenting var.lb or var.ub
enum class variable_attribute_type { LB,
    UB,
    INIT,
    PRIO };
template <typename TType>
struct attribute_node : derived_value_node<attribute_node<TType>, TType>,
                        terminal_node {
    attribute_node(std::string variable_name, variable_attribute_type attr) :
        variable_name(variable_name), attribute(attr) {};
    std::string variable_name;
    variable_attribute_type attribute = variable_attribute_type::INIT;
};

// unary nodes
template <typename TType>
using unary_node = kary_node<TType>;

struct round_node : derived_value_node<round_node, real<0>>,
                    unary_node<real<0>> {
    using kary_node<real<0>>::kary_node;
};
struct index_to_real_node : derived_value_node<index_to_real_node, real<0>>,
                            unary_node<index<0>> {
    using kary_node<index<0>>::kary_node;
};
struct real_to_index_node : derived_value_node<real_to_index_node, index<0>>,
                            unary_node<real<0>> {
    using kary_node<real<0>>::kary_node;
};
struct minus_node : derived_value_node<minus_node, real<0>>,
                    unary_node<real<0>> {
    using kary_node::kary_node;
};
struct inverse_node : derived_value_node<inverse_node, real<0>>,
                      unary_node<real<0>> {
    using kary_node::kary_node;
};

struct index_minus_node : derived_value_node<index_minus_node, index<0>>,
                          unary_node<index<0>> {
    using kary_node::kary_node;
};

struct negation_node : derived_value_node<negation_node, boolean<0>>,
                       unary_node<boolean<0>> {
    using kary_node::kary_node;
};

// unary helper node for function nodes =>gets real<3> and return real<1>
// (reshape) any tensor to vector (flatten)
template <typename TType>
struct vector_node
    : derived_value_node<vector_node<TType>,
        tensor_type<typename TType::atom_type, 1>>,
      unary_node<TType> {
    using kary_node<TType>::kary_node;
};

// unary function nodes
struct abs_node : derived_value_node<abs_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct xabsx_node : derived_value_node<xabsx_node, real<0>>,
                    unary_node<real<0>> {
    using kary_node::kary_node;
};
struct exp_node : derived_value_node<exp_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct log_node : derived_value_node<log_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct xlogx_node : derived_value_node<xlogx_node, real<0>>,
                    unary_node<real<0>> {
    using kary_node::kary_node;
};
struct sqrt_node : derived_value_node<sqrt_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct sin_node : derived_value_node<sin_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct asin_node : derived_value_node<asin_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct cos_node : derived_value_node<cos_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct acos_node : derived_value_node<acos_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct tan_node : derived_value_node<tan_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct atan_node : derived_value_node<atan_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct cosh_node : derived_value_node<cosh_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct sinh_node : derived_value_node<sinh_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct tanh_node : derived_value_node<tanh_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct coth_node : derived_value_node<coth_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct acosh_node : derived_value_node<acosh_node, real<0>>,
                    unary_node<real<0>> {
    using kary_node::kary_node;
};
struct asinh_node : derived_value_node<asinh_node, real<0>>,
                    unary_node<real<0>> {
    using kary_node::kary_node;
};
struct atanh_node : derived_value_node<atanh_node, real<0>>,
                    unary_node<real<0>> {
    using kary_node::kary_node;
};
struct acoth_node : derived_value_node<acoth_node, real<0>>,
                    unary_node<real<0>> {
    using kary_node::kary_node;
};
struct erf_node : derived_value_node<erf_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct erfc_node : derived_value_node<erfc_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct pos_node : derived_value_node<pos_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct neg_node : derived_value_node<neg_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};
struct schroeder_ethanol_p_node
    : derived_value_node<schroeder_ethanol_p_node, real<0>>,
      unary_node<real<0>> {
    using kary_node::kary_node;
};
struct schroeder_ethanol_rhovap_node
    : derived_value_node<schroeder_ethanol_rhovap_node, real<0>>,
      unary_node<real<0>> {
    using kary_node::kary_node;
};
struct schroeder_ethanol_rholiq_node
    : derived_value_node<schroeder_ethanol_rholiq_node, real<0>>,
      unary_node<real<0>> {
    using kary_node::kary_node;
};
struct covar_matern_1_node : derived_value_node<covar_matern_1_node, real<0>>,
                             unary_node<real<0>> {
    using kary_node::kary_node;
};
struct covar_matern_3_node : derived_value_node<covar_matern_3_node, real<0>>,
                             unary_node<real<0>> {
    using kary_node::kary_node;
};
struct covar_matern_5_node : derived_value_node<covar_matern_5_node, real<0>>,
                             unary_node<real<0>> {
    using kary_node::kary_node;
};
struct covar_sqrexp_node : derived_value_node<covar_sqrexp_node, real<0>>,
                           unary_node<real<0>> {
    using kary_node::kary_node;
};
struct gpdf_node : derived_value_node<gpdf_node, real<0>>, unary_node<real<0>> {
    using kary_node::kary_node;
};

// binary nodes
template <typename TType, typename UType>
using binary_node = kary_node<TType, UType>;

template <typename TType>
struct entry_node : derived_value_node<entry_node<TType>, TType>,
                    binary_node<vector_of<TType>, index<0>> {
    using kary_node<vector_of<TType>, index<0>>::kary_node;
};
struct xexpy_node : derived_value_node<xexpy_node, real<0>>,
                    binary_node<real<0>, real<0>> {
    using kary_node::kary_node;
};
struct xexpax_node : derived_value_node<xexpax_node, real<0>>,
                     binary_node<real<0>, real<0>> {
    using kary_node::kary_node;
};
struct lmtd_node : derived_value_node<lmtd_node, real<0>>,
                   binary_node<real<0>, real<0>> {
    using kary_node::kary_node;
};
struct rlmtd_node : derived_value_node<rlmtd_node, real<0>>,
                    binary_node<real<0>, real<0>> {
    using kary_node::kary_node;
};
struct arh_node : derived_value_node<arh_node, real<0>>,
                  binary_node<real<0>, real<0>> {
    using kary_node::kary_node;
};
struct norm2_node : derived_value_node<norm2_node, real<0>>,
                    binary_node<real<0>, real<0>> {
    using kary_node::kary_node;
};
struct lb_func_node : derived_value_node<lb_func_node, real<0>>,
                      binary_node<real<0>, real<0>> {
    using kary_node::kary_node;
};
struct ub_func_node : derived_value_node<ub_func_node, real<0>>,
                      binary_node<real<0>, real<0>> {
    using kary_node::kary_node;
};

template <typename TType>
struct equal_node : derived_value_node<equal_node<TType>, boolean<0>>,
                    binary_node<TType, TType> {
    using kary_node<TType, TType>::kary_node;
};
template <typename TType>
struct less_node : derived_value_node<less_node<TType>, boolean<0>>,
                   binary_node<TType, TType> {
    using kary_node<TType, TType>::kary_node;
};
template <typename TType>
struct less_equal_node : derived_value_node<less_equal_node<TType>, boolean<0>>,
                         binary_node<TType, TType> {
    using kary_node<TType, TType>::kary_node;
};
template <typename TType>
struct greater_node : derived_value_node<greater_node<TType>, boolean<0>>,
                      binary_node<TType, TType> {
    using kary_node<TType, TType>::kary_node;
};
template <typename TType>
struct greater_equal_node
    : derived_value_node<greater_equal_node<TType>, boolean<0>>,
      binary_node<TType, TType> {
    using kary_node<TType, TType>::kary_node;
};

template <typename TType>
struct element_node : derived_value_node<element_node<TType>, boolean<0>>,
                      binary_node<TType, set<TType, 0>> {
    using kary_node<TType, set<TType, 0>>::kary_node;
};

template <typename IteratorType>
struct sum_node : derived_value_node<sum_node<IteratorType>, real<0>>,
                  iterator_node<IteratorType, real<0>> {
    using iterator_node<IteratorType, real<0>>::iterator_node;
};

template <typename IteratorType>
struct product_node : derived_value_node<product_node<IteratorType>, real<0>>,
                      iterator_node<IteratorType, real<0>> {
    using iterator_node<IteratorType, real<0>>::iterator_node;
};

template <typename IteratorType>
struct set_min_node : derived_value_node<set_min_node<IteratorType>, real<0>>,
                      iterator_node<IteratorType, real<0>> {
    using iterator_node<IteratorType, real<0>>::iterator_node;
};

template <typename IteratorType>
struct set_max_node : derived_value_node<set_max_node<IteratorType>, real<0>>,
                      iterator_node<IteratorType, real<0>> {
    using iterator_node<IteratorType, real<0>>::iterator_node;
};

template <typename IteratorType>
struct forall_node : derived_value_node<forall_node<IteratorType>, boolean<0>>,
                     iterator_node<IteratorType, boolean<0>> {
    using iterator_node<IteratorType, boolean<0>>::iterator_node;
};

template <typename IteratorType>
struct indicator_set_node : derived_value_node<indicator_set_node<IteratorType>,
                              set<IteratorType, 0>>,
                            iterator_node<IteratorType, boolean<0>> {
    using iterator_node<IteratorType, boolean<0>>::iterator_node;
};

// ternary nodes
template <typename TType, typename UType, typename VType>
using ternary_node = kary_node<TType, UType, VType>;

struct mid_node : derived_value_node<mid_node, real<0>>,
                  ternary_node<real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};
struct bounding_func_node : derived_value_node<bounding_func_node, real<0>>,
                            ternary_node<real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};
struct squash_node : derived_value_node<squash_node, real<0>>,
                     ternary_node<real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};
struct regnormal_node : derived_value_node<regnormal_node, real<0>>,
                        ternary_node<real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};
struct af_lcb_node : derived_value_node<af_lcb_node, real<0>>,
                     ternary_node<real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};
struct af_ei_node : derived_value_node<af_ei_node, real<0>>,
                    ternary_node<real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};
struct af_pi_node : derived_value_node<af_pi_node, real<0>>,
                    ternary_node<real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};

// quaternary nodes
template <typename TType, typename UType, typename VType, typename WType>
using quaternary_node = kary_node<TType, UType, VType, WType>;

struct cost_turton_node : derived_value_node<cost_turton_node, real<0>>,
                          quaternary_node<real<0>, real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};
struct nrtl_dtau_node : derived_value_node<nrtl_dtau_node, real<0>>,
                        quaternary_node<real<0>, real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};
struct antoine_psat_node : derived_value_node<antoine_psat_node, real<0>>,
                           quaternary_node<real<0>, real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};
struct antoine_tsat_node : derived_value_node<antoine_tsat_node, real<0>>,
                           quaternary_node<real<0>, real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};

// quinary nodes
template <typename TType, typename UType, typename VType, typename WType,
  typename XType>
using quinary_node = kary_node<TType, UType, VType, WType, XType>;

struct nrtl_tau_node
    : derived_value_node<nrtl_tau_node, real<0>>,
      quinary_node<real<0>, real<0>, real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};

// senary nodes
template <typename TType, typename UType, typename VType, typename WType,
  typename XType, typename YType>
using senary_node = kary_node<TType, UType, VType, WType, XType, YType>;

struct nrtl_g_node
    : derived_value_node<nrtl_g_node, real<0>>,
      senary_node<real<0>, real<0>, real<0>, real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};
struct nrtl_gtau_node
    : derived_value_node<nrtl_gtau_node, real<0>>,
      senary_node<real<0>, real<0>, real<0>, real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};
struct nrtl_gdtau_node
    : derived_value_node<nrtl_gdtau_node, real<0>>,
      senary_node<real<0>, real<0>, real<0>, real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};
struct nrtl_dgtau_node
    : derived_value_node<nrtl_dgtau_node, real<0>>,
      senary_node<real<0>, real<0>, real<0>, real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};
struct watson_dhvap_node
    : derived_value_node<watson_dhvap_node, real<0>>,
      senary_node<real<0>, real<0>, real<0>, real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};

// septenenary nodes
template <typename TType, typename UType, typename VType, typename WType,
  typename XType, typename YType, typename ZType>
using septenary_node = kary_node<TType, UType, VType, WType, XType, YType, ZType>;

struct wagner_psat_node : derived_value_node<wagner_psat_node, real<0>>,
                          septenary_node<real<0>, real<0>, real<0>, real<0>,
                            real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};
struct dippr107_hig_node : derived_value_node<dippr107_hig_node, real<0>>,
                           septenary_node<real<0>, real<0>, real<0>, real<0>,
                             real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};
struct dippr106_dhvap_node : derived_value_node<dippr106_dhvap_node, real<0>>,
                             septenary_node<real<0>, real<0>, real<0>, real<0>,
                               real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};

// octonary nodes
template <typename TType, typename UType, typename VType, typename WType,
  typename XType, typename YType, typename ZType, typename AType>
using octonary_node = kary_node<TType, UType, VType, WType, XType, YType, ZType, AType>;

struct ext_antoine_psat_node
    : derived_value_node<ext_antoine_psat_node, real<0>>,
      octonary_node<real<0>, real<0>, real<0>, real<0>, real<0>, real<0>,
        real<0>, real<0>> {
    using kary_node::kary_node;
};
struct aspen_hig_node : derived_value_node<aspen_hig_node, real<0>>,
                        octonary_node<real<0>, real<0>, real<0>, real<0>,
                          real<0>, real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};

// novenary nodes
template <typename TType, typename UType, typename VType, typename WType,
  typename XType, typename YType, typename ZType, typename AType,
  typename BType>
using novenary_node = kary_node<TType, UType, VType, WType, XType, YType, ZType, AType, BType>;

struct nasa9_hig_node
    : derived_value_node<nasa9_hig_node, real<0>>,
      novenary_node<real<0>, real<0>, real<0>, real<0>, real<0>, real<0>,
        real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};
struct dippr127_hig_node
    : derived_value_node<dippr127_hig_node, real<0>>,
      novenary_node<real<0>, real<0>, real<0>, real<0>, real<0>, real<0>,
        real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};

// undenary nodes
template <typename TType, typename UType, typename VType, typename WType,
  typename XType, typename YType, typename ZType, typename AType,
  typename BType, typename CType, typename DType>
using undenary_node = kary_node<TType, UType, VType, WType, XType, YType, ZType,
  AType, BType, CType, DType>;

struct ik_cape_psat_node
    : derived_value_node<ik_cape_psat_node, real<0>>,
      undenary_node<real<0>, real<0>, real<0>, real<0>, real<0>, real<0>,
        real<0>, real<0>, real<0>, real<0>, real<0>> {
    using kary_node::kary_node;
};

// nary nodes
struct addition_node : derived_value_node<addition_node, real<0>>,
                       nary_node<real<0>> { };
struct multiplication_node : derived_value_node<multiplication_node, real<0>>,
                             nary_node<real<0>> { };
struct exponentiation_node : derived_value_node<exponentiation_node, real<0>>,
                             nary_node<real<0>> { };
struct min_node : derived_value_node<min_node, real<0>>, nary_node<real<0>> { };
struct max_node : derived_value_node<max_node, real<0>>, nary_node<real<0>> { };

struct index_addition_node : derived_value_node<index_addition_node, index<0>>,
                             nary_node<index<0>> { };
struct index_multiplication_node
    : derived_value_node<index_multiplication_node, index<0>>,
      nary_node<index<0>> { };

struct disjunction_node : derived_value_node<disjunction_node, boolean<0>>,
                          nary_node<boolean<0>> { };
struct conjunction_node : derived_value_node<conjunction_node, boolean<0>>,
                          nary_node<boolean<0>> { };

struct sum_div_node : derived_value_node<sum_div_node, real<0>>,
                      nary_node<real<0>> { };
struct xlog_sum_node : derived_value_node<xlog_sum_node, real<0>>,
                       nary_node<real<0>> { };
struct single_neuron_node : derived_value_node<single_neuron_node, real<0>>,
                      nary_node<real<0>> { };

// only accepts vectors as arguments (argument tensors need to be flattened with
// vetcor node>
template <typename TType>
struct function_node : derived_value_node<function_node<TType>, TType>,
                       nary_node<tensor_type<typename TType::atom_type, 1>> {
    function_node(const std::string &name) :
        name(name) { }
    std::string name;
};

// create a vector from scalars (or a tensor<i> from tensor<i-1>'s)
template <typename TType>
struct tensor_node : derived_value_node<tensor_node<TType>, TType>,
                     nary_node<entry_of<TType>> { };

// implements the following for tensors:
// out[i,j,k]=in[k,i,j] \forall k,j,i
template <typename TType>
struct index_shift_node : derived_value_node<index_shift_node<TType>, TType>,
                          unary_node<TType> {
    using kary_node<TType>::kary_node;
};

} // namespace ale
