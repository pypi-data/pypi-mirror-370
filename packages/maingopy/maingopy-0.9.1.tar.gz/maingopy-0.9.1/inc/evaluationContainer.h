/**********************************************************************************
 * Copyright (c) 2019 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#pragma once

#include "modelFunction.h"
#include "outputVariable.h"

#include "ffunc.hpp"

#include <vector>


namespace maingo {


/**
    * @struct EvaluationContainer
    * @brief Struct for storing the values returned by model evaluation at the given point "var"
    *
    * This struct is used as return type for the evaluate function to be implemented by the user.
    * The vectors ineqRelaxationOnly and eqRelaxationOnly can be used to supply constraints that are not part of the actual problem, but can serve to tighten relaxations.
    * This concept has been taken from Sahinidis & Tawarmalani, J. Global Optim. 32 (2005) 259.
    */
struct EvaluationContainer {
    ModelFunction objective;            /*!< value of objective function f(var) */
    ModelFunction objective_per_data;   /*!< vector of values of objective function f(var) per data point used in MAiNGO with growing datasets (empty otherwise)*/
    ModelFunction ineq;                 /*!< vector of residuals of inequality constraints g(var) */
    ModelFunction eq;                   /*!< vector of residuals of equality constraints h(var) */
    ModelFunction ineqRelaxationOnly;   /*!< vector of residuals of inequality constraints to be used only in the relaxed problem */
    ModelFunction eqRelaxationOnly;     /*!< vector of residuals of equality constraints to be used only in the relaxed problem */
    ModelFunction ineqSquash;           /*!< vector of residuals of inequality constraints to be added when using the squash_node function */
    std::vector<OutputVariable> output; /*!< vector of additional output variables (should only be computed and returned if calling evaluate with ADDITIONAL_OUTPUT) */

    /**
        * @brief Clears all information, note that currently objective has not to be cleared, since it is overwritten
        */
    void clear()
    {
        objective.clear();
        objective_per_data.clear();
        ineq.clear();
        eq.clear();
        ineqRelaxationOnly.clear();
        eqRelaxationOnly.clear();
        ineqSquash.clear();
        output.clear();
    }
};

}    // end namespace maingo