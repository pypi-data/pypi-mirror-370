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

#include "evaluationContainer.h"
#include "usingAdditionalIntrinsicFunctions.h"

#include "babOptVar.h"
#include "babUtils.h"

#include "ffunc.hpp"
#include "functionWrapper.h"

#include <vector>


/**
*	@namespace maingo
*	@brief namespace holding all essentials of MAiNGO
*/
namespace maingo {

using OptimizationVariable = babBase::OptimizationVariable; /*!< Redefine for easier usage */
using Bounds               = babBase::Bounds;               /*!< Redefine for easier usage */
using VT                   = babBase::enums::VT;            /*!< Redefine for easier usage */
constexpr VT VT_CONTINUOUS = babBase::enums::VT_CONTINUOUS; /*!< Redefine for easier usage */
constexpr VT VT_BINARY     = babBase::enums::VT_BINARY;     /*!< Redefine for easier usage */
constexpr VT VT_INTEGER    = babBase::enums::VT_INTEGER;    /*!< Redefine for easier usage */

/**
* @class MAiNGOmodel
* @brief This class is the base class for models to be solved by MAiNGO
*
* This class is used to derive a Model class in problem.h, where the user can implement their actual model.
*/
class MAiNGOmodel {

  public:
    using Var = mc::FFVar; /*!< Redefine for easier usage */

    /**
		* @brief Destructor
		*/
    virtual ~MAiNGOmodel() {}

    /**
		* @brief Virtual function which has to be implemented by the user in order to enable evaluation of the model
		*
		* @param[in] optVars is a vector holding the optimization variables
		*/
    virtual EvaluationContainer evaluate(const std::vector<Var> &optVars) = 0;

    /**
		* @brief Virtual function which has to be implemented by the user in order to enable getting data on optimization variables
		*/
    virtual std::vector<OptimizationVariable> get_variables() = 0;

    /**
		* @brief Virtual function which has to be implemented by the user in order to enable getting data on the initial point
		*/
    virtual std::vector<double> get_initial_point() { return std::vector<double>(); }  // GCOVR_EXCL_START

  private: // GCOVR_EXCL_STOP
};


}    // namespace maingo