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

#include <cstddef>
#include <functional>

namespace ale {

// parameter pack to hold a parameter list
template <typename... TTypes>
struct pack { };

// generate parameter pack from template
template <typename... TTypes>
struct pack_from_template { };

template <template <typename...> typename TTemplate, typename... TTypes>
struct pack_from_template<TTemplate<TTypes...>> {
    using type = pack<TTypes...>;
};

// combine multiple parameter packs
template <typename... TTypes>
struct combined_pack { };
// combine 3 or more parameter packs
template <typename... TTypes, typename... UTypes, typename... TRest>
struct combined_pack<pack<TTypes...>, pack<UTypes...>, TRest...> {
    using type = typename combined_pack<
      typename combined_pack<pack<TTypes...>, pack<UTypes...>>::type,
      TRest...>::type;
};
// combine 2 parameter packs
template <typename... TTypes, typename... UTypes>
struct combined_pack<pack<TTypes...>, pack<UTypes...>> {
    using type = pack<TTypes..., UTypes...>;
};
// forward single parameter pack
template <typename... TTypes>
struct combined_pack<pack<TTypes...>> {
    using type = pack<TTypes...>;
};

template <typename TType, size_t I>
struct multiplied_pack {
    using type =
      typename combined_pack<typename multiplied_pack<TType, I - 1>::type,
        pack<TType>>::type;
};

template <typename TType>
struct multiplied_pack<TType, 1> {
    using type = pack<TType>;
};

// generate template instantiation from parameter pack
template <template <typename...> typename TTemplate, typename... TTypes>
struct from_pack { };
template <template <typename...> typename TTemplate, typename... TTypes>
struct from_pack<TTemplate, pack<TTypes...>> {
    using type = TTemplate<TTypes...>;
};

template <template <typename> typename TTemplate, typename... TTypes>
struct pack_from_pack { };

// first argument is a type that depends on a template, the created pack will
// have TTemplate<TTypes1>, TTemplate<TTypes2> ..
template <template <typename> typename TTemplate, typename... TTypes>
struct pack_from_pack<TTemplate, pack<TTypes...>> {
    using type = pack<TTemplate<TTypes>...>;
};

template <template <typename> typename TTemplate, typename... TTypes>
struct pointer_pack_from_pack { };
template <template <typename> typename TTemplate, typename... TTypes>
struct pointer_pack_from_pack<TTemplate, pack<TTypes...>> {
    using type = pack<TTemplate<TTypes> *...>;
};

template <template <typename> typename TTemplate, typename... TTypes>
struct ref_pack_from_pack { };
template <template <typename> typename TTemplate, typename... TTypes>
struct ref_pack_from_pack<TTemplate, pack<TTypes...>> {
    using type = pack<std::reference_wrapper<TTemplate<TTypes>>...>;
};

// generate template instantiation from other template instantiations
template <template <typename...> typename TTemplate, typename... UTemplates>
struct from_template {
    using type =
      typename from_pack<TTemplate,
        typename combined_pack<typename pack_from_template<
          UTemplates>::type...>::type>::type;
};

// pick parameter from pack
template <size_t I, typename TType, typename... TRest>
struct pick {
    using type = typename pick<I - 1, TRest...>::type;
};

template <typename TType, typename... TRest>
struct pick<0, TType, TRest...> {
    using type = TType;
};

} // namespace ale
