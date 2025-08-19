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

#include <stdexcept>         // for invalid_argument
#include <string>            // for allocator, operator+, char_traits, string
#include "expression.hpp"    // for expression
#include "node.hpp"          // for value_node
#include "symbol_table.hpp"  // for symbol_table
#include "value.hpp"         // for owning_ref

namespace ale::util {

    struct uninitializedParameterException: public std::invalid_argument {
        uninitializedParameterException(const std::string& name) : std::invalid_argument("Parameter \"" + std::string(name) + "\" was evaluated but never initialized") {}
    };
    struct wrongDimensionException : public std::invalid_argument {
        wrongDimensionException(const std::string& ex) : std::invalid_argument(ex) {}
    };

    template <typename TType>
    owning_ref<TType> evaluate_expression(expression<TType>& expr, symbol_table& symbols);

    template <typename TType>
    owning_ref<TType> evaluate_expression(value_node<TType>* node, symbol_table& symbols);

    class [[deprecated]] evaluator {
    public:
        evaluator(symbol_table& symbols): symbols(symbols) {}

        template <typename TType>
        [[deprecated]] owning_ref<TType> dispatch(expression<TType>& expr) {
            return evaluate_expression(expr, symbols);
        }

        template <typename TType>
        [[deprecated]] owning_ref<TType> dispatch(value_node<TType>* expr) {
            return evaluate_expression(expr, symbols);
        }

    private:
        symbol_table& symbols;
    };

}  //ale