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

#include "aleModel.h"
#include "MAiNGOevaluator.h"
#include "variableLister.h"

#include <algorithm>
#include <exception>
#include <string>


using namespace maingo;


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<OptimizationVariable>
AleModel::get_variables()
{
    return _variables;
}


//////////////////////////////////////////////////////////////////////////
// get positions
const std::unordered_map<std::string, int>&
AleModel::get_positions()
{
    return _positions;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
AleModel::get_initial_point()
{
    return _initials;
}


//////////////////////////////////////////////////////////////////////////
// evaluate the model
EvaluationContainer
AleModel::evaluate(const std::vector<Var>& optVars)
{
    EvaluationContainer result;

    MaingoEvaluator eval(_symbols, optVars, _positions);
    for (auto it = _prog.mObjective.begin(); it != _prog.mObjective.end(); ++it) {
        auto obj = eval.dispatch(*it);
        result.objective.push_back(obj, it->m_note);
    }

    for (auto it = _prog.mObjectivePerData.begin(); it != _prog.mObjectivePerData.end(); ++it) {
        auto obj = eval.dispatch(*it);
        result.objective_per_data.push_back(obj.eq, it->m_note);
    }

    for (auto it = _prog.mConstraints.begin(); it != _prog.mConstraints.end(); ++it) {
        auto cons = eval.dispatch(*it);
        result.eq.push_back(cons.eq, it->m_note);
        result.ineq.push_back(cons.ineq, it->m_note);
    }

    for (auto it = _prog.mRelaxations.begin(); it != _prog.mRelaxations.end(); ++it) {
        auto cons = eval.dispatch(*it);
        result.eqRelaxationOnly.push_back(cons.eq, it->m_note);
        result.ineqRelaxationOnly.push_back(cons.ineq, it->m_note);
    }

    for (auto it = _prog.mSquashes.begin(); it != _prog.mSquashes.end(); ++it) {
        auto cons = eval.dispatch(*it);
        if (cons.eq.size() > 0) {
            throw MAiNGOException("  Error: AleModel -- Encountered squash equality constraint. These are not allowed.");
        }
        result.ineqSquash.push_back(cons.ineq, it->m_note);
    }

    for (auto it = _prog.mOutputs.begin(); it != _prog.mOutputs.end(); ++it) {
        result.output.emplace_back(eval.dispatch(*it), it->m_note);
    }
    return result;
}


//////////////////////////////////////////////////////////////////////////
// function for making variables
void
AleModel::make_variables()
{
    _variables.clear();
    _initials.clear();
    _positions.clear();
    VariableLister varlist(_variables, _initials, _positions);
    for (auto it = _symbols.get_names().begin(); it != _symbols.get_names().end(); ++it) {
        base_symbol* sym = _symbols.resolve(*it);
        varlist.dispatch(sym);
    }
}
