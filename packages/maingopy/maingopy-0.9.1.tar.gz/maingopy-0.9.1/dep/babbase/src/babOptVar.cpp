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

#include "babOptVar.h"
#include "babException.h"


using namespace babBase;


////////////////////////////////////////////////////////////////////////////////////////
// function for checking if bounds are really discrete for discrete variables
void
OptimizationVariable::_round_and_check_discrete_bounds()
{
    if (_variableType == enums::VT_BINARY) {
        _bounds.upper = std::min(1.0, _bounds.upper);
        _bounds.lower = std::max(0.0, _bounds.lower);
    }
    if (_variableType == enums::VT_INTEGER || _variableType == enums::VT_BINARY) {

        // Round bounds (at first: simplifies feasibility check)
        _bounds.lower = std::ceil(_bounds.lower);
        _bounds.upper = std::floor(_bounds.upper);

        // Check feasibility of range:
        // The bounds may have become inconsistent through the rounding.
        // This indicates that there were no integer values within the original bounds.
        _feasible = _bounds.are_consistent();
    }
}


////////////////////////////////////////////////////////////////////////////////////////
// constructor for OptimizationVariable without bounds
OptimizationVariable::OptimizationVariable(const unsigned branchingPriority, const std::string nameIn):
    _bounds(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
    _userSpecifiedBounds(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
    _variableType(enums::VT_CONTINUOUS), _branchingPriority(branchingPriority), _name(nameIn)
{
    throw(BranchAndBoundBaseException("  Error: User provided variable without bounds."));
}


////////////////////////////////////////////////////////////////////////////////////////
// constructor for OptimizationVariable without bounds
OptimizationVariable::OptimizationVariable(const unsigned branchingPriority):
    _bounds(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
    _userSpecifiedBounds(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
    _variableType(enums::VT_CONTINUOUS), _branchingPriority(branchingPriority), _name()
{
    throw(BranchAndBoundBaseException("  Error: User provided variable without bounds."));
}


////////////////////////////////////////////////////////////////////////////////////////
// constructor for OptimizationVariable without bounds
OptimizationVariable::OptimizationVariable(const std::string nameIn):
    _bounds(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
    _userSpecifiedBounds(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
    _variableType(enums::VT_CONTINUOUS), _branchingPriority(1), _name(nameIn)
{
    throw(BranchAndBoundBaseException("  Error: User provided variable without bounds."));
}


////////////////////////////////////////////////////////////////////////////////////////
// constructor for OptimizationVariable without bounds
OptimizationVariable::OptimizationVariable():
    _bounds(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
    _userSpecifiedBounds(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN()),
    _variableType(enums::VT_CONTINUOUS), _branchingPriority(1), _name()
{
    throw(BranchAndBoundBaseException("  Error: User provided variable without bounds."));
}


////////////////////////////////////////////////////////////////////////////////////////
// auxiliary function for variables cosntructed without bounds
void
OptimizationVariable::_infer_and_set_bounds_or_throw()
{
    switch (_variableType) {
        case enums::VT_BINARY:
            _bounds.lower = 0;
            _bounds.upper = 1;
            _feasible     = true;
            break;
        case enums::VT_INTEGER:
        case enums::VT_CONTINUOUS:
        default:
            throw(BranchAndBoundBaseException("  Error: Could not infer bounds for (non-binary) variable."));
    }
}