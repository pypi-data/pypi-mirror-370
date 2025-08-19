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

#include "MAiNGO.h"
#include "MAiNGOException.h"


using namespace maingo;


////////////////////////////////////////////////////////////////////////////////////////
// function returning the objective and all constraints at solution point
std::vector<double>
MAiNGO::evaluate_model_at_solution_point()
{
    // Problem has to be solved
    if (_solutionPoint.empty()) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: Error querying model outputs in get_model_at_solution_point. MAiNGO status: " << _maingoStatus;
        throw MAiNGOException(errmsg.str());
    }

    std::vector<double> evaluationResult;
    bool feasibleDummy;    // Solution point is always feasible
    std::tie(evaluationResult, feasibleDummy) = _evaluate_model_at_point(_solutionPoint);
    return evaluationResult;
}


////////////////////////////////////////////////////////////////////////////////////////
// function returning the additional model outputs at the solution point
std::vector<std::pair<std::string, double>>
MAiNGO::evaluate_additional_outputs_at_solution_point()
{
    // Return variable additional model outputs
    if (_solutionPoint.empty()) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: Error querying additional model outputs in get_additional_outputs_at_solution_point. MAiNGO status: " << _maingoStatus;
        throw MAiNGOException(errmsg.str());
    }

    if ((!_solutionPoint.empty()) && (_noutputVariables > 0 || _nconstantOutputVariables > 0) && (_constantConstraintsFeasible)) {
        return _evaluate_additional_outputs_at_point(_solutionPoint);
    }
    else {
        return std::vector<std::pair<std::string, double>>();
    }
}


////////////////////////////////////////////////////////////////////////////////////////
// function returning the objective and all constraints at a user specified point
std::pair<std::vector<double>, bool>
MAiNGO::evaluate_model_at_point(const std::vector<double> &point)
{
    if (!_modelSpecified) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: Error in get_model_at_point. Model has not been set yet.";
        throw MAiNGOException(errmsg.str());
    }

    // DAG has to be constructed
    if (!_DAGconstructed) {
        _construct_DAG();
    }

    if (point.size() != _nvarOriginal) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: The dimension of the point in function get_model_at_point does not match the dimensions of the set MAiNGO model.";
        throw MAiNGOException(errmsg.str());
    }

    // Match each DAG variable to a double variable and skip removed variables
    // Evaluate DAG at point
    std::vector<double> pointUsed;
    bool removedVariablesFeasible = true;
    for (unsigned int i = 0; i < _nvarOriginal; i++) {
        if (!_removedVariables[i]) {
            pointUsed.push_back(point[i]);
        }
        else {
            if ((point[i] > _originalVariables[i].get_upper_bound()) || (point[i] < _originalVariables[i].get_lower_bound())) {
                removedVariablesFeasible = false;
            }
            babBase::enums::VT varType(_originalVariables[i].get_variable_type());
            if ((varType == babBase::enums::VT_BINARY) && (point[i] != 0) && (point[i] != 1)) {
                removedVariablesFeasible = false;
            }
            else if (varType == babBase::enums::VT_INTEGER) {
                if (point[i] != std::round(point[i])) {
                    removedVariablesFeasible = false;
                }
            }
        }
    }

    std::pair<std::vector<double>, bool> result = _evaluate_model_at_point(pointUsed);
    result.second                               = result.second && removedVariablesFeasible;
    return result;
}


////////////////////////////////////////////////////////////////////////////////////////
// function returning the additional model outputs at a user specified point
std::vector<std::pair<std::string, double>>
MAiNGO::evaluate_additional_outputs_at_point(const std::vector<double> &point)
{
    if (!_modelSpecified) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: Error in get_additional_output_at_point. Model has not been set yet.";
        throw MAiNGOException(errmsg.str());
    }

    if (!_DAGconstructed) {
        _construct_DAG();
    }

    if (point.size() != _nvarOriginal) {
        std::ostringstream errmsg;
        errmsg << "  MAiNGO: The dimension of the point in function get_additional_output_at_point does not match the dimensions of the set MAiNGO model.";
        throw MAiNGOException(errmsg.str());
    }

    // Match each DAG variable to a double variable and skip removed variables
    // Evaluate DAG at point
    std::vector<double> pointUsed;
    for (unsigned int i = 0; i < _nvarOriginal; i++) {
        if (!_removedVariables[i]) {
            pointUsed.push_back(point[i]);
        }
    }

    return _evaluate_additional_outputs_at_point(pointUsed);
}


////////////////////////////////////////////////////////////////////////////////////////
// function returning the additional model outputs at a user specified point
std::vector<std::pair<std::string, double>>
MAiNGO::_evaluate_additional_outputs_at_point(const std::vector<double> &pointUsed)
{
    // Match each DAG variable to a double variable
    // Evaluate DAG to compute outputs
    std::vector<double> outputRes(_DAGoutputFunctions.size());
    try {
        _DAG.eval(_DAGoutputFunctions.size(), _DAGoutputFunctions.data(), outputRes.data(), _nvar, _DAGvars.data(), pointUsed.data());
    }
    catch (std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  MAiNGO: Error while evaluating additional user outputs.", e);
    }
    catch (...) {
        throw MAiNGOException("  MAiNGO: Unknown error while evaluating additional user outputs.");
    }
    // GCOVR_EXCL_STOP
    
    // Get additional output, don't forget the constant ones
    std::vector<std::pair<std::string, double>> additionalModelOutputs(_noutputVariables + _nconstantOutputVariables);
    // Non-constant outputs first
    for (size_t i = 0; i < _noutputVariables; i++) {
        additionalModelOutputs[(*_nonconstantOutputs)[i].indexOriginal] = std::make_pair((*_nonconstantOutputs)[i].name, outputRes[(*_nonconstantOutputs)[i].indexNonconstant]);
    }
    // Constant outputs second
    for (size_t i = 0; i < _nconstantOutputVariables; i++) {
        additionalModelOutputs[(*_constantOutputs)[i].indexOriginal] = std::make_pair((*_constantOutputs)[i].name, (*_constantOutputs)[i].constantValue);
    }

    return additionalModelOutputs;
}


////////////////////////////////////////////////////////////////////////////////////////
// function returning the objective and all constraints at a user specified point
std::pair<std::vector<double>, bool>
MAiNGO::_evaluate_model_at_point(const std::vector<double> &pointUsed)
{

    std::vector<double> result(_DAGfunctions.size());
    _DAG.eval(_DAGfunctions.size(), _DAGfunctions.data(), result.data(), _nvar, _DAGvars.data(), pointUsed.data());

    bool isFeasible = true;
    // First check feasibility w.r.t. variable bounds & integrality
    for (unsigned int i = 0; i < _nvar; i++) {
        if ((pointUsed[i] > _variables[i].get_upper_bound()) || (pointUsed[i] < _variables[i].get_lower_bound())) {
            isFeasible = false;
        }
        babBase::enums::VT varType(_variables[i].get_variable_type());
        if ((varType == babBase::enums::VT_BINARY) && (pointUsed[i] != 0) && (pointUsed[i] != 1)) {
            isFeasible = false;
        }
        else if (varType == babBase::enums::VT_INTEGER) {
            if (pointUsed[i] != std::round(pointUsed[i])) {
                isFeasible = false;
            }
        }
    }

    // Don't forget the constant functions
    std::vector<double> evaluationResult(1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly + _neqRelaxationOnly + _nconstantEqRelOnly + _nineqSquash + _nconstantIneqSquash);
    evaluationResult[0] = result[0];    // Objective first
    // Non-constant constraints first
    unsigned offset = _nauxiliaryRelOnlyEqs;    // Don't count auxiliary equalities
    for (size_t i = 0; i < _nonconstantConstraints->size() - offset; i++) {
        double value = result[(*_nonconstantConstraints)[i].indexNonconstant];
        switch ((*_nonconstantConstraints)[i].type) {
            case INEQ:
            case INEQ_REL_ONLY: {
                if (value > _maingoSettings->deltaIneq) {
                    isFeasible = false;
                }
                break;
            }
            case EQ:
            case EQ_REL_ONLY: {
                if (std::fabs(value) > _maingoSettings->deltaEq) {
                    isFeasible = false;
                }
                break;
            }
            case INEQ_SQUASH: {
                if (value > 0) {
                    isFeasible = false;
                }
                break;
            }
            default:
                break;
        }
        evaluationResult[(*_nonconstantConstraints)[i].indexOriginal] = value;
    }
    // Constant constraints second
    for (size_t i = 0; i < _constantConstraints->size(); i++) {
        double value = (*_constantConstraints)[i].constantValue;
        switch ((*_constantConstraints)[i].type) {
            case INEQ:
            case INEQ_REL_ONLY: {
                if (value > _maingoSettings->deltaIneq) {
                    isFeasible = false;
                }
                break;
            }
            case EQ:
            case EQ_REL_ONLY: {
                if (std::fabs(value) > _maingoSettings->deltaEq) {
                    isFeasible = false;
                }
                break;
            }
            case INEQ_SQUASH: {
                if (value > 0) {
                    isFeasible = false;
                }
                break;
            }
            default:
                break;
        }
        evaluationResult[(*_constantConstraints)[i].indexOriginal] = value;
    }

    return std::make_pair(evaluationResult, isFeasible);
}