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

#include "symbol.hpp"

#include <iostream>
#include <sstream>

namespace ale {

enum SymbolType {
    parameter_real,
    parameter_index,
    parameter_boolean,
    parameter_set_real,
    parameter_set_index,
    parameter_set_boolean,
    variable_real,
    variable_integral,
    expression_real,
    expression_index,
    expression_boolean,
    function_real,
    function_index,
    function_boolean
};

class symbol_typer {
    // the following example code returns the enum SymbolType
    // of the symbol named "my_symbol_name"
    // ale::symbol_typer my_symbol_typer;
    // ale::SymbolType =
    //     my_symbol_typer.getSymbolType(my_symbols.resolve("my_symbol_name"));

public:
    SymbolType getSymbolType(base_symbol *sym) {
        return std::visit(*this, sym->get_base_variant());
    }

    template <typename TType>
    SymbolType operator()(value_symbol<TType> *sym) {
        return std::visit(*this, sym->get_value_variant());
    }

    template <unsigned IDim>
    SymbolType operator()(parameter_symbol<real<IDim>> *sym) {
        return parameter_real;
    }

    template <unsigned IDim>
    SymbolType operator()(parameter_symbol<index<IDim>> *sym) {
        return parameter_index;
    }

    template <unsigned IDim>
    SymbolType operator()(parameter_symbol<boolean<IDim>> *sym) {
        return parameter_boolean;
    }

    template <unsigned IDim, unsigned IDim_>
    SymbolType
    operator()(parameter_symbol<
      tensor_type<base_set<tensor_type<base_real, IDim>>, IDim_>> *sym) {
        return parameter_set_real;
    }

    template <unsigned IDim, unsigned IDim_>
    SymbolType operator()(
      parameter_symbol<
        tensor_type<base_set<tensor_type<base_index, IDim>>, IDim_>> *sym) {
        return parameter_set_index;
    }

    template <unsigned IDim, unsigned IDim_>
    SymbolType operator()(
      parameter_symbol<
        tensor_type<base_set<tensor_type<base_boolean, IDim>>, IDim_>> *sym) {
        return parameter_set_boolean;
    }

    template <unsigned IDim>
    SymbolType operator()(variable_symbol<real<IDim>> *sym) {
        if(sym->integral()) {
            return variable_integral;
        }
        return variable_real;
    }

    template <unsigned IDim>
    SymbolType operator()(expression_symbol<real<IDim>> *sym) {
        return expression_real;
    }

    template <unsigned IDim>
    SymbolType operator()(expression_symbol<boolean<IDim>> *sym) {
        return expression_boolean;
    }

    template <unsigned IDim>
    SymbolType operator()(expression_symbol<index<IDim>> *sym) {
        return expression_index;
    }

    template <unsigned IDim>
    SymbolType operator()(function_symbol<real<IDim>> *sym) {
        return function_real;
    }

    template <unsigned IDim>
    SymbolType operator()(function_symbol<index<IDim>> *sym) {
        return function_index;
    }

    template <unsigned IDim>
    SymbolType operator()(function_symbol<boolean<IDim>> *sym) {
        return function_boolean;
    }
};

} // namespace ale