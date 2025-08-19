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

#include "MAiNGOmodelEpsCon.h"
#include "MAiNGOException.h"

#include <string>


/**
*  @namespace maingo
*  @brief namespace holding all essentials of MAiNGO
*/
namespace maingo {

/////////////////////////////////////////////////////////////////////////
// evaluate function to be called by MAiNGO - invokes evaluate_user_model and converts to corresponding single-objective problem
EvaluationContainer
MAiNGOmodelEpsCon::evaluate(const std::vector<Var> &optVars)
{

    EvaluationContainer userResult = evaluate_user_model(optVars);
    if (userResult.objective.size() < 2) {
        throw MAiNGOException("  Error: Models derived from MAiNGOmodelEpsCon need at least two objectives, found " + std::to_string(userResult.objective.size()) + ".");
    }
    if (userResult.objective.size() != _epsilon.size()) {
        throw MAiNGOException("  Error in model derived from MAiNGOmodelEpsCon: size of epsilon vector does not equal number of objectives.\n  Did you use solve() instead of solve_epsilon_constraint()?");
    }
    EvaluationContainer result = userResult;
    result.objective           = userResult.objective[_objectiveIndex];
    for (size_t i = 0; i < userResult.objective.size(); i++) {
        if (i != _objectiveIndex) {
            if (!_singleObjective) {
                result.ineq.push_back(userResult.objective[i] - _epsilon[i]);
            }
        }
        result.output.emplace_back("Objective " + std::to_string(i), userResult.objective[i]);
    }

    return result;
}


}    // end namespace maingo