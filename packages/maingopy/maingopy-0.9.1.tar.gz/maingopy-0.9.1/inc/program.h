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

// Note: need to include mpiUtilities *before* expression.hpp to avoid conflicts in preprocessor definition of BOOL (at least when using openmpi)
#include "mpiUtilities.h"

#include "expression.hpp"

#include <list>

namespace maingo {

/**
* @struct Program
* @brief Container Class for ALE expressions comprising an optimization problem
*/
struct Program {
    std::list<ale::expression<ale::real<0>>> mObjective;           /*!< Objective function expression*/
    std::list<ale::expression<ale::boolean<0>>> mObjectivePerData; /*!< Objective per data function expression for using growing datasets*/
    std::list<ale::expression<ale::boolean<0>>> mConstraints;      /*!< Constraint expressions*/
    std::list<ale::expression<ale::boolean<0>>> mRelaxations;      /*!< Relaxation-only constraint expressions*/
    std::list<ale::expression<ale::boolean<0>>> mSquashes;         /*!< Squash constraint expressions*/
    std::list<ale::expression<ale::real<0>>> mOutputs;             /*!< Additional output expressions*/
};


}    // namespace maingo