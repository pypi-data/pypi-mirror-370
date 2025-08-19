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

#include <iostream>

#include "util/expression_to_string.hpp"

namespace ale {

/**
 * This class has been replaced by symbol_to_string in expression_to_string.hpp
 * This class is just there to not break existing code, and should not be used
 * in new code.
 */
class [[deprecated]] symbol_printer {
public:
    [[deprecated]] static void dispatch(base_symbol *sym) {
        std::cout << symbol_to_string(sym) << std::endl;
    }
};

} // namespace ale
