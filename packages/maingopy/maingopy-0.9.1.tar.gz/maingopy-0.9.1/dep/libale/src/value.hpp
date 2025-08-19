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
#include "tensor.hpp"

#include <list>
#include <vector>

namespace ale {

struct base_real {
    using basic_type = double;
    using ref_type = basic_type &;
    using cref_type = basic_type;
};

struct base_index {
    using basic_type = int;
    using ref_type = basic_type &;
    using cref_type = basic_type;
};

struct base_boolean {
    using basic_type = bool;
    using ref_type = basic_type &;
    using cref_type = basic_type;
};

template <typename TElement>
struct base_set {
    template <typename UType>
    using container_type = std::list<UType>;
    using element_type = TElement;
    using basic_type = container_type<typename element_type::basic_type>;
    using ref_type = basic_type &;
    using cref_type = const basic_type &;
};

template <typename TAtom, unsigned IDim>
struct tensor_type {
    using basic_type = tensor<typename TAtom::basic_type, IDim>;
    using ref_type = tensor_ref<typename TAtom::basic_type, IDim>;
    using cref_type = tensor_cref<typename TAtom::basic_type, IDim>;
    using atom_type = TAtom;
    static const unsigned dim = IDim;
};

template <typename TAtom>
struct tensor_type<TAtom, 0> {
    using basic_type = typename TAtom::basic_type;
    using ref_type = typename TAtom::ref_type;
    using cref_type = typename TAtom::cref_type;
    using atom_type = TAtom;
    static const unsigned dim = 0;
};

template <typename TType>
using vector_of = tensor_type<typename TType::atom_type, TType::dim + 1>;

template <typename TType>
using entry_of = tensor_type<typename TType::atom_type, TType::dim - 1>;

template <unsigned IDim>
using real = tensor_type<base_real, IDim>;

template <unsigned IDim>
using index = tensor_type<base_index, IDim>;

template <unsigned IDim>
using boolean = tensor_type<base_boolean, IDim>;

template <typename TAtom, unsigned IDim>
struct tensor_pack {
    using type =
      typename combined_pack<typename tensor_pack<TAtom, IDim - 1>::type,
        pack<tensor_type<TAtom, IDim>>>::type;
};

template <typename TAtom>
struct tensor_pack<TAtom, 0> {
    using type = pack<tensor_type<TAtom, 0>>;
};

using real_types = typename tensor_pack<base_real, LIBALE_MAX_DIM>::type;
using index_types = typename tensor_pack<base_index, LIBALE_MAX_DIM>::type;
using boolean_types = typename tensor_pack<base_boolean, LIBALE_MAX_DIM>::type;

template <typename TElement, unsigned IDim>
using set = tensor_type<base_set<TElement>, IDim>;

// IDim = (outer) set dimension
// JDim = (inner) element dimension
// Returns all tensors (IDim) of sets of tensors (0 .. JDim)
template <typename TAtom, unsigned IDim, unsigned JDim>
struct element_pack {
    using type =
      typename combined_pack<typename element_pack<TAtom, IDim, JDim - 1>::type,
        pack<set<tensor_type<TAtom, JDim>, IDim>>>::type;
};

template <typename TAtom, unsigned IDim>
struct element_pack<TAtom, IDim, 0> {
    using type = pack<set<tensor_type<TAtom, 0>, IDim>>;
};

template <typename TAtom, unsigned IDim, unsigned JDim>
struct set_pack {
    using type = typename combined_pack<
      typename set_pack<TAtom, IDim - 1, JDim>::type,
      typename element_pack<TAtom, IDim, JDim>::type>::type;
};

template <typename TAtom, unsigned JDim>
struct set_pack<TAtom, 0, JDim> {
    using type = typename element_pack<TAtom, 0, JDim>::type;
};

using real_set_types =
  typename set_pack<base_real, LIBALE_MAX_SET_DIM, LIBALE_MAX_DIM>::type;
using index_set_types =
  typename set_pack<base_index, LIBALE_MAX_SET_DIM, LIBALE_MAX_DIM>::type;
using boolean_set_types =
  typename set_pack<base_boolean, LIBALE_MAX_SET_DIM, LIBALE_MAX_DIM>::type;

/**
 * Returns the dimension of the node
 */
template <typename TType>
constexpr unsigned get_node_dimension = TType::dim;

/**
 * Returns if the node is a real node
 */
template <typename TType>
constexpr bool is_real_node = std::is_same_v<typename TType::atom_type, base_real>;

/**
 * Returns if the node is an index node
 */
template <typename TType>
constexpr bool is_index_node = std::is_same_v<typename TType::atom_type, base_index>;

/**
 * Returns if the node is a boolean node
 */
template <typename TType>
constexpr bool is_boolean_node = std::is_same_v<typename TType::atom_type, base_boolean>;

/**
 * Returns if the node is a set node
 */
template <typename TType>
constexpr bool is_set_node = false;

template <typename TElement, unsigned IDim>
inline constexpr bool is_set_node<set<TElement, IDim>> = true;

/**
 * Returns the type of the value stored in value_node<TType>.
 * ie basic_type<real<0>> -> double
 *    basic_type<real<1>> -> tensor<real<1>>
 *    basic_type<set<real<0>, 0>> -> list<double>
 *    basic_type<set<real<1>, 0>> -> list<tensor<1>>
 */
template <typename TType>
using basic_type = typename TType::basic_type;

/**
 * Returns the reference type of the value stored in value_node<TType>.
 * ie ref_type<real<0>> -> double&
 *    ref_type<real<1>> -> tensor_ref<real<1>>
 *    ref_type<set<real<0>, 0>> -> list<double>&
 *    ref_type<set<real<1>, 0>> -> list<tensor<1>>&
 */
template <typename TType>
using ref_type = typename TType::ref_type;

/**
 * Returns the constant reference type of the value stored in value_node<TType>.
 * ie cref_type<real<0>> -> double
 *    cref_type<real<1>> -> tensor_cref<real<1>>
 *    cref_type<set<real<0>, 0>> -> const list<double>&
 *    cref_type<set<real<1>, 0>> -> const list<tensor<1>>&
 */
template <typename TType>
using cref_type = typename TType::cref_type;

/**
 * Returns the abstracted type of numbers that are stored in value_node<TType>.
 * ie atom_type<real<0>> -> base_real
 *    atom_type<real<1>> -> base_real
 *    atom_type<set<real<0>, 0>> -> base_real
 *    atom_type<set<real<1>, 0>> -> base_real
 */
template <typename TType>
using atom_type = typename TType::atom_type;

/**
 * Returns the actual type of numbers that are stored in value_node<TType>
 * ie base_type<real<0>> -> double
 *    base_type<real<1>> -> double
 *    base_type<set<real<0>, 0>> -> double
 *    base_type<set<real<1>, 1>> -> double
 *
 * TODO: this might need to be renamed
 */
template <typename TType>
using base_type = basic_type<atom_type<TType>>;

template <typename TType>
using element_type = typename atom_type<TType>::element_type;

/**
 * Returns ref_type but with all (cpp-)references removed.
 *
 * ie owning_ref<real<0>> -> double
 *    owning_ref<real<1>> -> tensor_ref<real<1>>
 *    owning_ref<set<real<0>, 0>> -> list<double>
 *    owning_ref<set<real<1>, 0>> -> list<tensor<1>>
 */
template <typename TType>
using owning_ref = std::remove_reference_t<ref_type<TType>>;

/**
 * Returns cref_type but with all (cpp-)references removed.
 *
 * ie owning_cref<real<0>> -> double
 *    owning_cref<real<1>> -> tensor_cref<real<1>>
 *    owning_cref<set<real<0>, 0>> -> list<double>
 *    owning_cref<set<real<1>, 0>> -> list<tensor<1>>
 */
template <typename TType>
using owning_cref = std::remove_reference_t<cref_type<TType>>;

} // namespace ale
