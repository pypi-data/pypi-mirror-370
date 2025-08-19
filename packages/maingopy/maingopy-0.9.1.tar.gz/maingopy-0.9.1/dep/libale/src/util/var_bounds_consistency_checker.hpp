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

#include <stdexcept>                // for invalid_argument
#include <string>                   // for allocator, operator+, char_traits, string
#include "expression.hpp"           // for expression
#include "node.hpp"                 // for value_node
#include "symbol_table.hpp"         // for symbol_table
#include "util/visitor_utils.hpp"   // for serialize_indexes
namespace ale::util {

class variable_bounds_consistency_checker {
public:
    variable_bounds_consistency_checker(symbol_table& symbols) :
        m_symbols(symbols) {};

    // base_symbol dispatch
    std::vector<std::string> dispatch(base_symbol* sym) {
        std::visit(*this, sym->get_base_variant());
        return m_result;
    }

    template <typename TType>
    void operator()(value_symbol<TType>* sym) {
        std::visit(*this, sym->get_value_variant());
    }

    // symbol visits
    template <typename TType>
    void operator()(parameter_symbol<TType>* sym) {
        // skipped
    }

    template <unsigned IDim>
    void operator()(parameter_symbol<real<IDim>>* sym) {
        // skipped
    }

    void operator()(parameter_symbol<real<0>>* sym) {
        // skipped
    }

    template <unsigned IDim>
    void operator()(variable_symbol<real<IDim>>* sym) {
        for(int i = 0; i < IDim; ++i) {
            if(sym->shape(i) == 0) {
                return;
            }
        }
        size_t indexes[IDim];
        for(int i = 0; i < IDim; ++i) {
            indexes[i] = 0;
        }

        while(indexes[0] < sym->shape(0)) {
            if(sym->lower()[indexes] > sym->upper()[indexes]) {
                m_result.push_back(sym->m_name + "[" + ale::helper::serialize_indexes<IDim>(indexes, ',') + "](lb, ub) = (" + std::to_string(sym->lower()[indexes]) + " , " + std::to_string(sym->upper()[indexes]) + ')');
            }
            for(int i = IDim - 1; i >= 0; --i) {
                if(++indexes[i] < sym->shape(i)) {
                    break;
                } else if(i != 0) {
                    indexes[i] = 0;
                }
            }
        }
    }

    void operator()(variable_symbol<real<0>>* sym) {
        if(sym->lower() > sym->upper()) {
            m_result.push_back(sym->m_name + "(lb, ub) = (" + std::to_string(sym->lower()) + " , " + std::to_string(sym->upper()) + ')');
        }
    }

    template <typename TType>
    void operator()(function_symbol<TType>* sym) {
        // skipped
    }

private:
    symbol_table& m_symbols;
    std::vector<std::string> m_result;
};

} // namespace ale::util