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

#include "lbp.h"
#include "MAiNGOException.h"
#include "lbpDagObj.h"
#include "pointIsWithinNodeBounds.h"
#include "instrumentor.h"
#include "version.h"

#include <fstream>
#include <iostream>

using namespace maingo;
using namespace lbp;


/////////////////////////////////////////////////////////////////////////////////////////////
// constructor for the lower bounding solver
LowerBoundingSolver::LowerBoundingSolver(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions,
                                         const std::vector<babBase::OptimizationVariable> &variables, const std::vector<bool>& variableIsLinear,
                                         const unsigned nineqIn, const unsigned neqIn, const unsigned nineqRelaxationOnlyIn,
                                         const unsigned neqRelaxationOnlyIn, const unsigned nineqSquashIn, std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn):
    _originalVariables(variables), _variableIsLinear(variableIsLinear),
    _nvar(variables.size()), _nineq(nineqIn), _neq(neqIn), _nineqRelaxationOnly(nineqRelaxationOnlyIn),
    _neqRelaxationOnly(neqRelaxationOnlyIn), _nineqSquash(nineqSquashIn), _maingoSettings(settingsIn), _logger(loggerIn), _constraintProperties(constraintPropertiesIn)
{

    _DAGobj = std::make_shared<DagObj>(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn, settingsIn, constraintPropertiesIn);

    // Depending on the linearization strategy, we have to compute different points and construct different objects
    switch (_maingoSettings->LBP_linPoints) {
        case LINP_SIMPLEX:
        case LINP_RANDOM:
        case LINP_KELLEY_SIMPLEX: {
            // Set vector McCormick options
            vMC::options.ENVEL_USE   = true;
            vMC::options.ENVEL_MAXIT = 100;
            vMC::options.ENVEL_TOL   = _maingoSettings->MC_envelTol;
            vMC::options.MVCOMP_USE  = _maingoSettings->MC_mvcompUse;
            vMC::options.MVCOMP_TOL  = _maingoSettings->MC_mvcompTol;
            // vMC::options.COMPUTE_ADDITIONAL_LINS = false;    // Currently not used
            if (_maingoSettings->LBP_subgradientIntervals) {
                vMC::options.SUB_INT_HEUR_USE = true;
                vMC::subHeur.clear();
                // We need at most as many intervals as there are factors.
                // Note that if we clear subHeur, the capacity of the interval vector in subHeur remains unchanged meaning that we don't have to reserve again.
                vMC::subHeur.reserve_size(_DAGobj->subgraph.l_op.size());
            }
            else {
                vMC::options.SUB_INT_HEUR_USE = false;
                vMC::subHeur.clear();
            }
            _DAGobj->initialize_vMcCormick();    // Additional initialization for these strategies
            _compute_and_rotate_simplex(_nvar /*dimension*/, 30.0 /*rotation angle*/, 0.725 /*sphere radius*/, _DAGobj->simplexPoints);
            _DAGobj->scaledPoints.resize(_nvar);
            _maxnParticipatingVariables = 1;
            for (size_t i = 0; i < _constraintProperties->size(); i++) {
                if ((*_constraintProperties)[i].dependency > LINEAR) {
                    _maxnParticipatingVariables = std::max(_maxnParticipatingVariables, (*_constraintProperties)[i].nparticipatingVariables);
                }
            }
            std::vector<double> lowerVarBounds(_nvar);
            std::vector<double> upperVarBounds(_nvar);
            for (unsigned int i = 0; i < _nvar; i++) {
                lowerVarBounds[i] = _originalVariables[i].get_lower_bound();
                upperVarBounds[i] = _originalVariables[i].get_upper_bound();
            }
            _choose_good_lin_points(lowerVarBounds, upperVarBounds);
            for (unsigned int i = 0; i < _nvar; i++) {
                _DAGobj->scaledPoints[i] = std::vector<double>(_DAGobj->chosenLinPoints.size(), 0.0);
                // _DAGobj->scaledPoints[i] = std::vector<double> (_nvar+2,0.0);
            }
            break;
        }
        case LINP_KELLEY:
            _maxnParticipatingVariables = 1;
            for (size_t i = 0; i < _constraintProperties->size(); i++) {
                if ((*_constraintProperties)[i].dependency > LINEAR) {
                    _maxnParticipatingVariables = std::max(_maxnParticipatingVariables, (*_constraintProperties)[i].nparticipatingVariables);
                }
            }
            break;
        case LINP_MID:
        case LINP_INCUMBENT:
        default:
            break;
    }

    // Set McCormick options
    MC::options.ENVEL_USE   = true;
    MC::options.ENVEL_MAXIT = 100;
    MC::options.ENVEL_TOL   = _maingoSettings->MC_envelTol;
    MC::options.MVCOMP_USE  = _maingoSettings->MC_mvcompUse;
    MC::options.MVCOMP_TOL  = _maingoSettings->MC_mvcompTol;
    if (_maingoSettings->LBP_subgradientIntervals) {
        MC::options.SUB_INT_HEUR_USE = true;
        MC::subHeur.clear();
        // We need at most as many intervals as there are factors.
        // Note that if we clear subHeur, the capacity of the interval vector in subHeur remains unchanged meaning that we don't have to reserve again.
        MC::subHeur.reserve_size(_DAGobj->subgraph.l_op.size());
    }
    else {
        MC::options.SUB_INT_HEUR_USE = false;
        MC::subHeur.clear();
    }
    // For vector McCormick operations we need to set some additional variables
    if (_maingoSettings->LBP_linPoints == LINP_SIMPLEX || _maingoSettings->LBP_linPoints == LINP_RANDOM) {    // In this case we use the vector McCormick class
        MC::options.SUB_INT_HEUR_USE = false;
    }

    // Set correct number of linearization points and resize own internal variables
    _nLinObj.resize(1);
    _nLinIneq.resize(_nineq);
    _nLinEq.resize(_neq);
    _nLinIneqRelaxationOnly.resize(_nineqRelaxationOnly);
    _nLinEqRelaxationOnly.resize(_neqRelaxationOnly);
    _nLinIneqSquash.resize(_nineqSquash);
    if (_maingoSettings->LBP_solver == LBP_SOLVER_MAiNGO || _maingoSettings->LBP_solver == LBP_SOLVER_INTERVAL || _maingoSettings->LBP_solver == LBP_SOLVER_SUBDOMAIN) {
        _set_number_of_linpoints(LINP_MID);
        _lowerVarBounds.resize(_nvar);
        _upperVarBounds.resize(_nvar);
    }
    else {
        _set_number_of_linpoints(_maingoSettings->LBP_linPoints);
    }

    if (_nineq + _neq + _nineqRelaxationOnly + _neqRelaxationOnly + _nineqSquash == 0) {
        _onlyBoxConstraints = true;
    }
    else {
        _onlyBoxConstraints = false;
    }

    _LPstatus = LP_UNKNOWN;

    // Set the feasibility tolerance to max(LBP_feasTol, deltaIneq, deltaEq) to achieve consistency in optimization
    _computationTol = std::max(_maingoSettings->deltaIneq, _maingoSettings->deltaEq);


    // Resize Matrix A and rhs b to appropriate sizes  ---  A*x <= b
    _matrixObj.resize(1);
    _matrixIneq.resize(_nineq);
    _matrixEq1.resize(_neq);
    _matrixEq2.resize(_neq);
    _matrixIneqRelaxationOnly.resize(_nineqRelaxationOnly);
    _matrixEqRelaxationOnly1.resize(_neqRelaxationOnly);
    _matrixEqRelaxationOnly2.resize(_neqRelaxationOnly);
    _matrixIneqSquash.resize(_nineqSquash);
    _rhsObj.resize(1);
    _rhsIneq.resize(_nineq);
    _rhsEq1.resize(_neq);
    _rhsEq2.resize(_neq);
    _rhsIneqRelaxationOnly.resize(_nineqRelaxationOnly);
    _rhsEqRelaxationOnly1.resize(_neqRelaxationOnly);
    _rhsEqRelaxationOnly2.resize(_neqRelaxationOnly);
    _rhsIneqSquash.resize(_nineqSquash);
    // Resize the matrices and right-hand sides of all constraints
    for (size_t k = 0; k < (*_constraintProperties).size(); k++) {
        unsigned i = (*_constraintProperties)[k].indexTypeNonconstant;    // In LBS, we work with non-constant functions only
        switch ((*_constraintProperties)[k].type) {
            case OBJ:
                _matrixObj[i].resize(_nLinObj[i]);
                for (unsigned int j = 0; j < _nLinObj[i]; j++) {
                    _matrixObj[i][j].resize(_nvar + 1);
                }
                _rhsObj[i].resize(_nLinObj[i]);
                break;
            case INEQ:
                _matrixIneq[i].resize(_nLinIneq[i]);
                for (unsigned int j = 0; j < _nLinIneq[i]; j++) {
                    _matrixIneq[i][j].resize(_nvar + 1);
                }
                _rhsIneq[i].resize(_nLinIneq[i]);
                break;
            case EQ:
                _matrixEq1[i].resize(_nLinEq[i]);
                _matrixEq2[i].resize(_nLinEq[i]);
                for (unsigned int j = 0; j < _nLinEq[i]; j++) {
                    _matrixEq1[i][j].resize(_nvar + 1);
                    _matrixEq2[i][j].resize(_nvar + 1);
                }
                _rhsEq1[i].resize(_nLinEq[i]);
                _rhsEq2[i].resize(_nLinEq[i]);
                break;
            case INEQ_REL_ONLY:
                _matrixIneqRelaxationOnly[i].resize(_nLinIneqRelaxationOnly[i]);
                for (unsigned int j = 0; j < _nLinIneqRelaxationOnly[i]; j++) {
                    _matrixIneqRelaxationOnly[i][j].resize(_nvar + 1);
                }
                _rhsIneqRelaxationOnly[i].resize(_nLinIneqRelaxationOnly[i]);
                break;
            case EQ_REL_ONLY:
            case AUX_EQ_REL_ONLY:
                _matrixEqRelaxationOnly1[i].resize(_nLinEqRelaxationOnly[i]);
                _matrixEqRelaxationOnly2[i].resize(_nLinEqRelaxationOnly[i]);
                for (unsigned int j = 0; j < _nLinEqRelaxationOnly[i]; j++) {
                    _matrixEqRelaxationOnly1[i][j].resize(_nvar + 1);
                    _matrixEqRelaxationOnly2[i][j].resize(_nvar + 1);
                }
                _rhsEqRelaxationOnly1[i].resize(_nLinEqRelaxationOnly[i]);
                _rhsEqRelaxationOnly2[i].resize(_nLinEqRelaxationOnly[i]);
                break;
            case INEQ_SQUASH:
                _matrixIneqSquash[i].resize(_nLinIneqSquash[i]);
                for (unsigned int j = 0; j < _nLinIneqSquash[i]; j++) {
                    _matrixIneqSquash[i][j].resize(_nvar + 1);
                }
                _rhsIneqSquash[i].resize(_nLinIneqSquash[i]);
                break;
            default:
                break;
        }
    }
    _objectiveScalingFactors.resize(1);                                   // Currently we work with only one objective
    _objectiveScalingFactors[0] = std::vector<double>(_nLinObj[0], 1);    // Need to change this if we plan to have more than one objective in future
}


/////////////////////////////////////////////////////////////////////////////////////////////
// sets the correct number of linearization points depending on the LBP_linpoints setting
void
LowerBoundingSolver::_set_number_of_linpoints(const unsigned int LBP_linPoints)
{
    // Determine number of linearization points
    for (size_t i = 0; i < _constraintProperties->size(); i++) {
        unsigned index      = (*_constraintProperties)[i].indexTypeNonconstant;    // Correct index of the given constraint type
        unsigned numberLins = 1;
        switch (LBP_linPoints) {
            case LINP_MID:
            case LINP_INCUMBENT:    //  0. Midpoint // 1. Incumbent if in node, else mid
            {
                switch ((*_constraintProperties)[i].type) {
                    case OBJ:
                        _nLinObj[index] = 1;
                        break;
                    case INEQ:
                        _nLinIneq[index] = 1;
                        break;
                    case EQ:
                        _nLinEq[index] = 1;
                        break;
                    case INEQ_REL_ONLY:
                        _nLinIneqRelaxationOnly[index] = 1;
                        break;
                    case EQ_REL_ONLY:
                    case AUX_EQ_REL_ONLY:
                        _nLinEqRelaxationOnly[index] = 1;
                        break;
                    case INEQ_SQUASH:
                        _nLinIneqSquash[index] = 1;
                        break;
                    default:
                        break;
                }
                break;
            }
            case LINP_KELLEY:    // 2. Linearization points are computed via an adapted version of Kelley's algorithm
            {
                if ((*_constraintProperties)[i].dependency > LINEAR) {
                    numberLins = std::max((unsigned)1, _maxnParticipatingVariables);
                }
                switch ((*_constraintProperties)[i].type) {
                    case OBJ:
                        _nLinObj[index]          = numberLins;
                        _DAGobj->objRowFilled    = std::vector<bool>(numberLins, false);
                        _DAGobj->objRowFilled[0] = true;    // Midpoint is used always
                        break;
                    case INEQ:
                        _nLinIneq[index] = numberLins;
                        break;
                    case EQ:
                        _nLinEq[index] = numberLins;
                        break;
                    case INEQ_REL_ONLY:
                        _nLinIneqRelaxationOnly[index] = numberLins;
                        break;
                    case EQ_REL_ONLY:
                    case AUX_EQ_REL_ONLY:
                        _nLinEqRelaxationOnly[index] = numberLins;
                        break;
                    case INEQ_SQUASH:
                        _nLinIneqSquash[index] = numberLins;
                        break;
                    default:
                        break;
                }

                break;
            }
            case LINP_SIMPLEX:
            case LINP_RANDOM:    // 3. First, a simplex is computed and its vertices are scaled to domain determining points
            {                    // 4. Random points are generated
                // If function is not linear, we need at most _nvar+2 linearization points (the final number has is determined in _choose_good_lin_points()), else we need only 1 linearization point
                if ((*_constraintProperties)[i].dependency > LINEAR) {
                    numberLins = _DAGobj->chosenLinPoints.size();
                }
                if (_maingoSettings->LBP_subgradientIntervals) {
                    vMC::subHeur.resize_vectors(_DAGobj->chosenLinPoints.size());    // Resize the underlying vector for subgradient heuristic
                }
                switch ((*_constraintProperties)[i].type) {
                    case OBJ:
                        _nLinObj[index] = numberLins;
                        break;
                    case INEQ:
                        _nLinIneq[index] = numberLins;
                        break;
                    case EQ:
                        _nLinEq[index] = numberLins;
                        break;
                    case INEQ_REL_ONLY:
                        _nLinIneqRelaxationOnly[index] = numberLins;
                        break;
                    case EQ_REL_ONLY:
                    case AUX_EQ_REL_ONLY:
                        _nLinEqRelaxationOnly[index] = numberLins;
                        break;
                    case INEQ_SQUASH:
                        _nLinIneqSquash[index] = numberLins;
                        break;
                    default:
                        break;
                }
                //vMC::additionalLins.initialize(_DAGobj->chosenLinPoints.size(), _nvar, /*midIndex*/0, _DAGobj->subgraphNonlinear.l_op.size(), vMC::additionalLins.COMPOSITION_BEST_POINT);
                break;
            }
            case LINP_KELLEY_SIMPLEX:    // 5. First, a simplex is computed and its vertices are scaled to domain determining linearization points, then Kelley's algorithm is applied
            {
                // If function is not linear, we need at most chosenLinPoints.size() + 3 points
                if ((*_constraintProperties)[i].dependency > LINEAR) {
                    numberLins = _DAGobj->chosenLinPoints.size() + 3;
                }
                if (_maingoSettings->LBP_subgradientIntervals) {
                    vMC::subHeur.resize_vectors(_DAGobj->chosenLinPoints.size());    // Resize the underlying vector for subgradient heuristic
                }
                switch ((*_constraintProperties)[i].type) {
                    case OBJ:
                        _nLinObj[index]       = numberLins;
                        _DAGobj->objRowFilled = std::vector<bool>(numberLins, false);
                        if ((*_constraintProperties)[i].dependency > LINEAR) {
                            std::fill(_DAGobj->objRowFilled.begin(), _DAGobj->objRowFilled.begin() + _DAGobj->chosenLinPoints.size(), true);    // Simplex points are always used
                        }
                        else {
                            _DAGobj->objRowFilled[0] = true;
                        }
                        break;
                    case INEQ:
                        _nLinIneq[index] = numberLins;
                        break;
                    case EQ:
                        _nLinEq[index] = numberLins;
                        break;
                    case INEQ_REL_ONLY:
                        _nLinIneqRelaxationOnly[index] = numberLins;
                        break;
                    case EQ_REL_ONLY:
                    case AUX_EQ_REL_ONLY:
                        _nLinEqRelaxationOnly[index] = numberLins;
                        break;
                    case INEQ_SQUASH:
                        _nLinIneqSquash[index] = numberLins;
                        break;
                    default:
                        break;
                }
                //vMC::additionalLins.initialize(_DAGobj->chosenLinPoints.size(), _nvar, /*midIndex*/0, _DAGobj->subgraphNonlinear.l_op.size(), vMC::additionalLins.COMPOSITION_BEST_POINT);
                break;
            }
            default: { // GCOVR_EXCL_START
                throw MAiNGOException("  Error initializing LowerBoundingSolver: Unknown linearization point for LBP.");
            } 
        }   // GCOVR_EXCL_STOP // End of switch(LBP_linPoints)
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// solve lower bounding problem by affine relaxation
SUBSOLVER_RETCODE
LowerBoundingSolver::solve_LBP(const babBase::BabNode &currentNode, double &lowerBound, std::vector<double> &solution, LbpDualInfo &dualInfo)
{
    PROFILE_FUNCTION()

    // Update the LP for the current node (i.e., modify bounds and update coefficients and RHS)
    LINEARIZATION_RETCODE linStatus;
    try {
        PROFILE_SCOPE("LBP_update_LP")
        linStatus = _update_LP(currentNode);
    }
    catch (std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error while modifying the lower bounding LP for LBP.", e, currentNode);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error while modifying the lower bounding LP for LBP.", currentNode);
    }
// GCOVR_EXCL_STOP
    // Solve problem and check return status
    if (linStatus == LINEARIZATION_UNKNOWN) {
        // Only need to solve the problem if it was not solved during linearization
        PROFILE_SCOPE("LBP_solve_LP")
		_LPstatus = _solve_LP(currentNode);
    }
    else {
        _LPstatus = _get_LP_status();
    }

    if (_LPstatus == LP_INFEASIBLE) {

        _logger->print_message("  LBP status: Infeasible", VERB_ALL, LBP_VERBOSITY);

#ifdef MAiNGO_DEBUG_MODE
        if (_contains_incumbent(currentNode)) {
            const bool reallyInfeasible = _check_if_LP_really_infeasible();
            if (reallyInfeasible) {
#ifdef LP__WRITE_CHECK_FILES
                _write_LP_to_file("solve_LBP_infeas_with_incumbent_in_node");
#endif
                std::ostringstream outstr;
                outstr << "  Warning: Node with id " << currentNode.get_ID() << " declared infeasible by LBP although it contains the incumbent. Proceeding with parent LBD..." << std::endl;
                _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
            }
            else {
                _logger->print_message("  Found node to not actually be infeasible. Problem seems to be difficult numerically. Proceeding with parent LBD...", VERB_ALL, LBP_VERBOSITY);
            }
            return SUBSOLVER_FEASIBLE;
        }
#endif

#ifdef LP__OPTIMALITY_CHECK
        if (_maingoSettings->LBP_solver == lbp::LBP_SOLVER_CLP) {    // For CLP, we need this additional check to avoid weird behavior for some problems
            bool reallyInfeasible = _check_if_LP_really_infeasible();
            if (!reallyInfeasible)
                _logger->print_message("  Found node to not actually be infeasible. Problem seems to be numerically difficult. Using interval bounds instead.", VERB_ALL, LBP_VERBOSITY);
            return _fallback_to_intervals(lowerBound);
        }
        return _check_infeasibility(currentNode);
#endif
    }
    else if (_LPstatus == LP_UNKNOWN) {
#ifdef LP__WRITE_CHECK_FILES
        _write_LP_to_file("solve_LBP_unknown_status_code");
#endif
        _logger->print_message("  Warning: LP solver returned unknown status code. Using interval bounds instead.\n", VERB_NORMAL, LBP_VERBOSITY);
        return _fallback_to_intervals(lowerBound);
    }

    _logger->print_message("  LBP status: Optimal", VERB_ALL, LBP_VERBOSITY);


    // Process solution: solution point (If we got here, the LP solver declared that an optimal solution was found)
    double etaVal = 0;
    try {
        _get_solution_point(solution, etaVal);
    }
    catch (std::exception &e) {
        std::ostringstream outstr;
        outstr << "  Warning: Variables at solution of LBP could not be obtained by LP solver: " << e.what() << std::endl;
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
        // Return empty solution instead
        solution.clear();
        return SUBSOLVER_FEASIBLE;
    }
    // Ok, successfully obtained solution point
    _logger->print_vector(_nvar, solution, "  LBP solution point: ", VERB_ALL, LBP_VERBOSITY);

#ifdef LP__OPTIMALITY_CHECK
    // Feasibility check
    if (_check_feasibility(solution) == SUBSOLVER_INFEASIBLE) {
        solution.clear();
        return SUBSOLVER_FEASIBLE;
    }
#endif

    // Process solution: optimal solution value
    double newLBD = _get_objective_value();
    if (!(newLBD >= (-_maingoSettings->infinity))) {    // Note that all comparisons return false if one operand is NAN
        std::ostringstream outstr;
        outstr << "  Warning: Objective obtained from LP solver in LBP is out of bounds (" << newLBD << ") although the LP solver solution status is optimal. Keeping parent LBD." << std::endl;
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
        return SUBSOLVER_FEASIBLE;
    }

    // If the lower bound becomes too low, CPLEX returns -1e19 as lowest value, we need to catch that to properly proceed
    if (newLBD <= -1e19 && _maingoSettings->LBP_solver == LBP_SOLVER_CPLEX) {
        // Not providing multipliers
        dualInfo.multipliers.clear();
        // Simply fallback to intervals
        return _fallback_to_intervals(lowerBound);
    }
    // Process solution: multipliers for DBBT
    try {
        _get_multipliers(dualInfo.multipliers);
    }
    catch (std::exception &e) {
        // This is okay, not providing multipliers
        std::ostringstream outstr;
        outstr << "  No multipliers obtained from LP solver: " << e.what() << std::endl;
        _logger->print_message(outstr.str(), VERB_ALL, LBP_VERBOSITY);

        dualInfo.multipliers.clear();
        return SUBSOLVER_FEASIBLE;
    }
#ifdef LP__OPTIMALITY_CHECK
    // Optimality check through strong duality
    if (_check_optimality(currentNode, newLBD, solution, etaVal, dualInfo.multipliers) == SUBSOLVER_INFEASIBLE) {
        solution.clear();
        dualInfo.multipliers.clear();
        // In this case just use intervals to check feasibility and obtain a lower bound
        return _fallback_to_intervals(lowerBound);
    }
#endif

    lowerBound            = std::max(newLBD, _DAGobj->validIntervalLowerBound);    // In case the interval bound is better, use that one
    dualInfo.lpLowerBound = newLBD;                                                // Here, we need the actual lower bound from the LP, since this is the one we need for DBBT

    std::ostringstream outstr;
    outstr << "  LBD: " << lowerBound << std::endl;
    _logger->print_message(outstr.str(), VERB_ALL, LBP_VERBOSITY);


    return SUBSOLVER_FEASIBLE;
}


#ifdef HAVE_GROWING_DATASETS
/////////////////////////////////////////////////////////////////////////////////////////////
// evaluate lower bounding problem based on affine relaxations at a given point
void
LowerBoundingSolver::evaluate_LBP(const babBase::BabNode& currentNode, const std::vector<double>& evaluationPoint, double& resultValue)
{
    // Update the LP for the current node (i.e., modify bounds and update coefficients and RHS)
    // Simplest approach: always use midpoint linearization
    lbp::LINP tempLinPoints = _maingoSettings->LBP_linPoints;
    _maingoSettings->LBP_linPoints = LINP_MID;

    LINEARIZATION_RETCODE linStatus;
    try {
        linStatus = _update_LP(currentNode);
    }
    catch (std::exception& e) {
        throw MAiNGOException("  Error while modifying the lower bounding LP for LBP.", e, currentNode);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error while modifying the lower bounding LP for LBP.", currentNode);
    }

    if (linStatus == LINEARIZATION_INFEASIBLE) {
        std::ostringstream errmsg;
        errmsg << "  Error in LowerBoundingSolver - evaluation of LBP: LBP based on LINP_MID is reported to be infeasible. " << std::endl;
        throw MAiNGOException(errmsg.str());
    }
    // Reset linearization point strategy to previous setting
    _maingoSettings->LBP_linPoints = tempLinPoints;

    // Evaluate objective of LBP
    if (!evaluationPoint.empty()) {
        // LBP with 1 linearization point and single objective (cf. _print_LP(...)):
        // min_x  eta
        // s.t.   sum_j _matrixObj[0][0][j]* x_j - _objectiveScalingFactors[0][0]*eta <= _rhsObj[0][0]
        //        other constraints
        resultValue = -_rhsObj[0][0];
        for (unsigned j = 0; j < _nvar; j++) {
            resultValue = resultValue + _matrixObj[0][0][j] * evaluationPoint[j];
        }
        resultValue = resultValue / _objectiveScalingFactors[0][0];

        // Check for NaN
        if (resultValue != resultValue) {
            resultValue = -_maingoSettings->infinity;
        }

        resultValue = std::max(resultValue, _DAGobj->validIntervalLowerBound);    // As for solve_LBP: In case the interval bound is better, use that one

        // Check if evaluationPoint is feasible
        if (_check_feasibility(evaluationPoint) == SUBSOLVER_INFEASIBLE) {
            std::ostringstream outstr;
            outstr << "  Warning: Evaluated LBP in node with id " << currentNode.get_ID() << " is infeasible at the given point." << std::endl;
            _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
        }
    }
    else {
        _fallback_to_intervals(resultValue);
    }
}
#endif    // HAVE_GROWING_DATASETS


/////////////////////////////////////////////////////////////////////////////////////////////
// solve LP for optimization-based range reduction
TIGHTENING_RETCODE
LowerBoundingSolver::solve_OBBT(babBase::BabNode &currentNode, const double currentUBD, const OBBT reductionType, const bool includeLinearVars)
{
    PROFILE_FUNCTION()

    if ((reductionType == OBBT_FEAS) && _onlyBoxConstraints) {
        return TIGHTENING_UNCHANGED;
    }

    std::vector<double> lowerVarBounds(currentNode.get_lower_bounds()), upperVarBounds(currentNode.get_upper_bounds());
    std::vector<double> originalWidth(_nvar);
    for (size_t i = 0; i < _nvar; ++i) {
        originalWidth[i] = upperVarBounds[i] - lowerVarBounds[i];
    }
    bool nodeChanged = false;
    // Update the LP for the current node (i.e., modify bounds and update coefficients and RHS)
    LINEARIZATION_RETCODE linStatus;
    try {
        PROFILE_SCOPE("OBBT_update_LP")
        linStatus = _update_LP(currentNode);
    }
    catch (std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error while modifying the lower bounding LP for OBBT.", e, currentNode);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error while modifying the lower bounding LP for OBBT.", currentNode);
    }
// GCOVR_EXCL_STOP
    bool foundInfeasible = false;
    if (linStatus == LINEARIZATION_INFEASIBLE) {
        _logger->print_message("  OBBT linearization status: Infeasible", VERB_ALL, LBP_VERBOSITY);

#ifdef MAiNGO_DEBUG_MODE
        if (_contains_incumbent(currentNode)) {
            const bool reallyInfeasible = _check_if_LP_really_infeasible();
            if (reallyInfeasible) {
#ifdef LP__WRITE_CHECK_FILES
                _write_LP_to_file("solve_OBBT_infeas_at_linearization_with_incumbent_in_node");
#endif
                if (currentNode.get_ID() == 0) {
                    return TIGHTENING_INFEASIBLE;    // For the root node, we immediately want to report this false infeasibility claim since we want to completeley disable OBBT based on this information.
                }
                std::ostringstream outstr;
                outstr << "  Warning: Node with id " << currentNode.get_ID() << " declared infeasible by linearization technique in OBBT although it contains the incumbent. Skipping OBBT..." << std::endl;
                _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
            }
            else {
                _logger->print_message("  Found node to not actually be infeasible. Problem seems to be difficult numerically. Skipping OBBT...", VERB_ALL, LBP_VERBOSITY);
            }
            return TIGHTENING_UNCHANGED;
        }
#endif  // MAiNGO_DEBUG_MODE

        foundInfeasible = true;
#ifdef LP__OPTIMALITY_CHECK
        if (_check_infeasibility(currentNode) == SUBSOLVER_FEASIBLE) {
            foundInfeasible = false;
        }
#endif
    }

    // Only do OBBT if the LP was not found to be infeasible during the linearization
    if (!foundInfeasible) {
        // Prepare OBBT
        std::list<unsigned> toTreatMax, toTreatMin;
        std::vector<double> lastPoint(_nvar);
        for (unsigned ivar = 0; ivar < _nvar; ivar++) {    // Note that we also treat auxiliaries (if any are added)
            if (!_variableIsLinear[ivar] || includeLinearVars) {
                toTreatMax.push_back(ivar);
                toTreatMin.push_back(ivar);
            }
            lastPoint[ivar] = 0.5 * (lowerVarBounds[ivar] + upperVarBounds[ivar]);
        }
        // Modify treatment of objective function
        switch (reductionType) {
            case OBBT_FEAS:    // Feasibility-based only
            {
                // Objective function is not needed in this case --> "deactivate" objective linearizations
                _deactivate_objective_function_for_OBBT();
                break;
            }
            case OBBT_FEASOPT:    // including both feasibility and optimality
            {
                // Modify objective: remove eta and establish proper ubd
                _modify_LP_for_feasopt_OBBT(currentUBD, toTreatMax, toTreatMin);
                break;
            }
            default: { // GCOVR_EXCL_START
                std::ostringstream errmsg;
                errmsg << "  Unknown OBBT range reduction type: " << reductionType;
                throw MAiNGOException(errmsg.str(), currentNode);
            }
        } // GCOVR_EXCL_STOP

        // Loop over variable bounds until all variable bounds have either been treated by OBBT or filtered
        unsigned OBBTcnt  = 0;
        bool foundRelFeas = false;
        while ((toTreatMax.size() + toTreatMin.size()) > 0) {
			PROFILE_SCOPE("OBBT_loop")

            OBBTcnt++;
            // Select next candidate lower bound
            std::list<unsigned>::iterator tmpIt = toTreatMin.begin(), nextMinIt = toTreatMin.begin();
            double smallestDistanceMin = _maingoSettings->infinity;
            if (foundRelFeas == true) {
                // Get minimum difference between last point and one lower variable bound, and use last point for trivial filtering (cf. Gleixner et al., J. Global Optim 67 (2017) 731)
                while (tmpIt != toTreatMin.end()) {
                    double tmpDistance = (lastPoint[*tmpIt] - lowerVarBounds[*tmpIt]);
                    double diameter    = upperVarBounds[*tmpIt] - lowerVarBounds[*tmpIt];
                    if ((diameter < _computationTol) || (tmpDistance <= diameter * _maingoSettings->LBP_obbtMinImprovement)) {
                        tmpIt = toTreatMin.erase(tmpIt);
                    }
                    else {
                        if (tmpDistance < smallestDistanceMin) {
                            smallestDistanceMin = tmpDistance;
                            nextMinIt           = tmpIt;
                        }
                        tmpIt++;
                    }
                }
            }
            else {
                // If no feasible (in relaxation) point was found, no need to search for the closest bound (first lower bound will be considered, if one exists)
                if (!toTreatMin.empty()) {
                    smallestDistanceMin = 0;    // If there are still lower bounds to be treated, these get priority
                }
            }

            // Select next candidate upper bound
            std::list<unsigned>::iterator nextMaxIt = toTreatMax.begin();
            tmpIt                                   = toTreatMax.begin();
            double smallestDistanceMax              = _maingoSettings->infinity;
            if (foundRelFeas == true) {
                // Get minimum difference between last point and one upper variable bound and use last point for trivial filtering (cf. Gleixner et al., J. Global Optim 67 (2017) 731)
                while (tmpIt != toTreatMax.end()) {
                    double tmpDistance = (upperVarBounds[*tmpIt] - lastPoint[*tmpIt]);
                    double diameter    = upperVarBounds[*tmpIt] - lowerVarBounds[*tmpIt];
                    if ((diameter < _computationTol) || (tmpDistance <= diameter * _maingoSettings->LBP_obbtMinImprovement)) {
                        tmpIt = toTreatMax.erase(tmpIt);
                    }
                    else {
                        if (tmpDistance < smallestDistanceMax) {
                            smallestDistanceMax = tmpDistance;
                            nextMaxIt           = tmpIt;
                        }
                        tmpIt++;
                    }
                }
            }
            else {
                // If no feasible (in relaxation) point was found, no need to search for the closest bound (first upper bound will be considered, if one exists)
                if (!toTreatMax.empty()) {
                    smallestDistanceMax = 0.5;    // If there are still upper bounds to be treated, these should be considered (smallestDistanceMax<infinity), but lower bounds get priority (just to ensure reproducibility)
                }
            }

            // If the last variables left just got erased, there is nothing left to do:
            if ((smallestDistanceMax >= _maingoSettings->infinity) && (smallestDistanceMin >= _maingoSettings->infinity)) {
                break;
            }

            // Depending on which one is better (max or min), prepare OBBT
            unsigned iVar;                            // Index of the variable to be modified
            std::vector<double> *boundVector;         // Pointer to the bound vector to be modified
            std::vector<double> *otherBoundVector;    // Pointer to the bound vector that is not to be modified in the current run
            int optimizationSense;                    // 1: minimize, -1: maximize
            if (smallestDistanceMin <= smallestDistanceMax) {
                iVar = *nextMinIt;
                toTreatMin.erase(nextMinIt);
                boundVector       = &lowerVarBounds;
                otherBoundVector  = &upperVarBounds;
                optimizationSense = 1;    // 1 = minimize
            }
            else {
                iVar = *nextMaxIt;
                toTreatMax.erase(nextMaxIt);
                boundVector       = &upperVarBounds;
                otherBoundVector  = &lowerVarBounds;
                optimizationSense = -1;    // -1 = maximize
            }

            // Conduct OBBT: solve LP and update bound
            _set_optimization_sense_of_variable(iVar, optimizationSense);    // Depending on whether we want to change upper or lower bound, use +1 or -1 as coefficient
			{
                PROFILE_SCOPE("OBBT_solve_LP")
                _LPstatus = _solve_LP(currentNode);
            }
            if (_LPstatus == LP_INFEASIBLE) {
                _logger->print_message("  OBBT tightening LP status: Infeasible", VERB_ALL, LBP_VERBOSITY);

#ifdef MAiNGO_DEBUG_MODE
                if (_contains_incumbent(currentNode)) {
                    const bool reallyInfeasible = _check_if_LP_really_infeasible();
                    if (reallyInfeasible) {
  #ifdef LP__WRITE_CHECK_FILES
                        _write_LP_to_file("solve_OBBT_infeas_with_incumbent_in_node");
  #endif
                        if (currentNode.get_ID() == 0) {
                            _restore_LP_coefficients_after_OBBT();
                            return TIGHTENING_INFEASIBLE;    // For the root node, we immediately want to report this false infeasibility claim since we want to completeley disable OBBT based on this information.
                        }
                        std::ostringstream outstr;
                        outstr << "  Warning: Node with id " << currentNode.get_ID() << " declared infeasible by OBBT although it contains the incumbent. Skipping OBBT..." << std::endl;
                        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                        break;
                    }
                    else {
                        std::ostringstream outstr;
                        outstr << "  Warning: Node with id " << currentNode.get_ID() << " is numerically sensitive in OBBT for bound " << iVar << " with sense " << optimizationSense << ". Skipping this bound..." << std::endl;
                        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                        _set_optimization_sense_of_variable(iVar, 0);
                        continue;
                    }
                }
#endif  // MAiNGO_DEBUG_MODE
                foundInfeasible = true;
#ifdef LP__OPTIMALITY_CHECK
                if (_check_infeasibility(currentNode) == SUBSOLVER_FEASIBLE) {
                    foundInfeasible = false;
                    break;
                }
#endif
                _logger->print_message("  OBBT status: " + std::to_string(_LPstatus), VERB_ALL, LBP_VERBOSITY);

                break;
            }    // end of if(_LPstatus == LP_INFEASIBLE)
            else if (_LPstatus != LP_OPTIMAL) {
                std::ostringstream outstr;
                outstr << "  Warning: No optimal solution found in OBBT. Status: " << _LPstatus << ". Skipping OBBT..." << std::endl;
                _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                break;
            }
            else {

                // Process solution: solution point to be used as "last point" in the next round
                std::vector<double> tmpPoint(_nvar);
                double dummy = 0;
                try {
                    _get_solution_point(tmpPoint, dummy);
                }
                catch (std::exception &e) {
                    std::ostringstream outstr;
                    outstr << "  Warning: Variables at solution of OBBT could be not obtained by LP solver: " << e.what() << std::endl;
                    _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                    _set_optimization_sense_of_variable(iVar, 0);
                    continue;
                }
#ifdef LP__OPTIMALITY_CHECK
                if (_check_feasibility(tmpPoint) == SUBSOLVER_INFEASIBLE) {
                    _set_optimization_sense_of_variable(iVar, 0);
                    continue;
                }
#endif
                foundRelFeas = true;
                lastPoint    = tmpPoint;

                // Make sure the new bound makes sense and does not violate variable bounds
                double objectiveValue = _get_objective_value();

                if (!(objectiveValue >= (-_maingoSettings->infinity))) {    // Note that all comparisons return false if one operand is NaN
                    std::ostringstream outstr;
                    outstr << "  Warning: Objective obtained from LP solver in OBBT is out of bounds (" << objectiveValue << ") although LP solution status is optimal. Skipping this bound." << std::endl;
                    _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                    _set_optimization_sense_of_variable(iVar, 0);
                    continue;
                }

                double newBound = optimizationSense * objectiveValue;    // Again depending on whether we want to change upper or lower bound, need to account for sign

#ifdef MAiNGO_DEBUG_MODE
                if (_contains_incumbent(currentNode)) {
                    if (optimizationSense > 0) {    // Lower bound
                        if (iVar < _incumbent.size()) {
                            if (_incumbent[iVar] < newBound) {
                                // We only need to tell the user something if we are not within computational tolerances, meaning that something really went wrong
                                if (!mc::isequal(_incumbent[iVar], newBound, _computationTol, _computationTol)) {
#ifdef LP__WRITE_CHECK_FILES
                                    _write_LP_to_file("solve_OBBT_bound_infeas_with_incumbent_in_node");
#endif
                                    std::ostringstream outstr;
                                    outstr << "  Warning: Node #" << currentNode.get_ID() << " contains the incumbent and OBBT computed a lower bound for variable " << iVar << " which cuts off the incumbent. " << std::endl
                                           << "           Correcting this bound and skipping OBBT... " << std::endl;
                                    _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                                }
                                // We skip the bound, even if the bound is within computational tolerances
                                break;
                            }
                        }
                    }
                    else {    // Upper bound
                        if (iVar < _incumbent.size()) {
                            if (_incumbent[iVar] > newBound) {
                                // We only need to tell the user something if we are not within computational tolerances, meaning that something really went wrong
                                if (!mc::isequal(_incumbent[iVar], newBound, _computationTol, _computationTol)) {
                                    std::ostringstream outstr;
                                    outstr << "  Warning: Node #" << currentNode.get_ID() << " contains the incumbent and OBBT computed an upper bound for variable " << iVar << " which cuts off the incumbent. " << std::endl
                                           << "           Correcting this bound and skipping OBBT... " << std::endl;
                                    _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                                }
                                // We skip the bound, even if the bound is within computational tolerances
                                break;
                            }
                        }
                    }
                }
#endif  // MAiNGO_DEBUG_MODE

                double remainingWidth = optimizationSense * (*otherBoundVector)[iVar] - optimizationSense * newBound;
                if (remainingWidth < -_computationTol) {
                    if (_originalVariables[iVar].get_variable_type() >= babBase::enums::VT_BINARY /* this includes VT_INTEGER */) {
                        // The problem is found to be infeasible, since, e.g., lb of variable 1 was tightened to 3.2 and was then set to 4. Later on ub of variable 1 is tightened to 3.6 and thus set to 3,
                        // meaning that this node is infeasible
                        // This could be extended to saving the old lb value 3.2 and checking if it does not cross the new ub value 3.6
                        _restore_LP_coefficients_after_OBBT();
                        return TIGHTENING_INFEASIBLE;
                    }
                    // We only need to tell the user something if we are not within computational tolerances, meaning that something really went wrong
                    if (!mc::isequal(optimizationSense * newBound, optimizationSense * (*otherBoundVector)[iVar], _computationTol, _computationTol)) {
                        std::ostringstream outstr;
                        outstr << "  Warning: Bounds crossover for variable " << iVar << " during OBBT with optimizationSense " << optimizationSense << ":" << std::endl;
                        if (optimizationSense > 0) {
                            outstr << std::setprecision(16) << "  Lower Bound = " << newBound << " > " << std::setprecision(16) << (*otherBoundVector)[iVar] << " = Upper Bound. Skipping this bound." << std::endl;
                        }
                        else {
                            outstr << std::setprecision(16) << "  Upper Bound = " << newBound << " < " << std::setprecision(16) << (*otherBoundVector)[iVar] << " = Lower Bound. Skipping this bound." << std::endl;
                        }
                        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                    }
                    _set_optimization_sense_of_variable(iVar, 0);
                    continue;
                }
                else {

                    // Update bound
                    if (remainingWidth < _computationTol) {
                        // Can't surely set bounds equal, there is the possibility that we make the LP infeasible although it isn't !
                        // (*boundVector)[iVar] = (*otherBoundVector)[iVar];
                    }
                    else {
                        switch (_originalVariables[iVar].get_variable_type()) {
                            case babBase::enums::VT_CONTINUOUS:
                                // Only update bounds if difference is larger than tolerance
                                if (!mc::isequal((*boundVector)[iVar], newBound, _computationTol, _computationTol)) {
                                    nodeChanged          = true;
                                    (*boundVector)[iVar] = newBound;
                                }
                                break;
                            case babBase::enums::VT_BINARY:
                                // Round bounds to ensure binary values
                                if (optimizationSense > 0) {    // Lower bound
                                    if (!mc::isequal(newBound, 0, _computationTol, _computationTol)) {
                                        nodeChanged          = true;
                                        (*boundVector)[iVar] = 1;
                                    }
                                    // Integer bounds crossing => node is infeasible
                                    if ((*boundVector)[iVar] > upperVarBounds[iVar]) {
                                        _restore_LP_coefficients_after_OBBT();
                                        return TIGHTENING_INFEASIBLE;
                                    }
                                }
                                else {    // Upper bound
                                    if (!mc::isequal(newBound, 1, _computationTol, _computationTol)) {
                                        nodeChanged          = true;
                                        (*boundVector)[iVar] = 0;
                                    }
                                    // Integer bounds crossing => node is infeasible
                                    if ((*boundVector)[iVar] < lowerVarBounds[iVar]) {
                                        _restore_LP_coefficients_after_OBBT();
                                        return TIGHTENING_INFEASIBLE;
                                    }
                                }
                                break;
                            case babBase::enums::VT_INTEGER:
                                // Round bounds to ensure integer values
                                if (optimizationSense > 0) {    // Lower bound
                                    if (!mc::isequal(newBound, std::floor(newBound), _computationTol, _computationTol)) {
                                        newBound = std::ceil(newBound);
                                    }
                                    else {
                                        newBound = std::floor(newBound);
                                    }
                                    if (!mc::isequal((*boundVector)[iVar], newBound, _computationTol, _computationTol)) {
                                        nodeChanged          = true;
                                        (*boundVector)[iVar] = newBound;
                                    }
                                    // Integer bounds crossing => node is infeasible
                                    if ((*boundVector)[iVar] > upperVarBounds[iVar]) {
                                        _restore_LP_coefficients_after_OBBT();
                                        return TIGHTENING_INFEASIBLE;
                                    }
                                }
                                else {    // Upper bound
                                    if (!mc::isequal(newBound, std::ceil(newBound), _computationTol, _computationTol)) {
                                        newBound = std::floor(newBound);
                                    }
                                    else {
                                        newBound = std::ceil(newBound);
                                    }
                                    if (!mc::isequal((*boundVector)[iVar], newBound, _computationTol, _computationTol)) {
                                        nodeChanged          = true;
                                        (*boundVector)[iVar] = newBound;
                                    }
                                    // Integer bounds crossing => node is infeasible
                                    if ((*boundVector)[iVar] < lowerVarBounds[iVar]) {
                                        _restore_LP_coefficients_after_OBBT();
                                        return TIGHTENING_INFEASIBLE;
                                    }
                                }
                                break;
                            default: // GCOVR_EXCL_START
                                throw MAiNGOException("  Error while solving OBBT: Unknown variable type.");
                                break;
                        }
                    } // GCOVR_EXCL_STOP
                }
                // Restore objective coefficient
                _set_optimization_sense_of_variable(iVar, 0);
            }
        }    // End of OBBT while loop
    }        // End of if(!foundInfeasible)

    // Restore proper objective function and restore LP solver options
    _restore_LP_coefficients_after_OBBT();

    // Return appropriate return code and possibly update currentNode with new bounds
    if (foundInfeasible) {
        return TIGHTENING_INFEASIBLE;
    }
    else {
        if (!nodeChanged) {
            return TIGHTENING_UNCHANGED;
        }
        else {
            currentNode = babBase::BabNode(currentNode, lowerVarBounds, upperVarBounds);
            return TIGHTENING_CHANGED;
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// propagate intervals in reverse order to possibly tighten variable bounds
TIGHTENING_RETCODE
LowerBoundingSolver::do_constraint_propagation(babBase::BabNode &currentNode, const double currentUBD, const unsigned pass)
{
    PROFILE_FUNCTION()

    if ((currentUBD >= _maingoSettings->infinity) && _onlyBoxConstraints) {
        return TIGHTENING_UNCHANGED;
    }


    // Set lower and upper bounds for intervals
    for (unsigned int i = 0; i < _nvar; i++) {
        _DAGobj->currentIntervals[i] = I(currentNode.get_lower_bounds()[i], currentNode.get_upper_bounds()[i]);
    }
    for (size_t i = 0; i < _constraintProperties->size(); i++) {
        switch ((*_constraintProperties)[i].type) {
            case OBJ:
                _DAGobj->constraintIntervals[i] = I(-_maingoSettings->infinity, currentUBD + std::min(_maingoSettings->epsilonA, std::fabs(currentUBD) * _maingoSettings->epsilonR));    // Add tolerance to avoid pathological cases, e.g, [x,x]
                break;
            case INEQ:
            case INEQ_REL_ONLY:
                _DAGobj->constraintIntervals[i] = I(-_maingoSettings->infinity, _maingoSettings->deltaIneq);
                break;
            case EQ:
            case EQ_REL_ONLY:
            case AUX_EQ_REL_ONLY:
                _DAGobj->constraintIntervals[i] = I(-_maingoSettings->deltaEq, _maingoSettings->deltaEq);
                break;
            case INEQ_SQUASH:
                _DAGobj->constraintIntervals[i] = I(-_maingoSettings->infinity, 0);    // No tolerance allowed for squash inequalities
                break;
            default:
                break;
        }
    }

    // Flag describing the status of constraint propagation <0 means that the problem is infeasible, 0 means that no bound tightening was possible, >0 means that tightening was possible
    // 0.001 stands for a minimum improvement of 0.1%
    unsigned int maxpass = pass;
    int flag             = _DAGobj->DAG.reval(_DAGobj->subgraph, _DAGobj->intervalArray, _DAGobj->functions.size(), _DAGobj->functions.data(),
                                              _DAGobj->constraintIntervals.data(), _nvar, _DAGobj->vars.data(), _DAGobj->currentIntervals.data(), maxpass, 0.001);

    // The node has been found to be infeasible
    std::vector<double> lowerVarBounds(currentNode.get_lower_bounds());
    std::vector<double> upperVarBounds(currentNode.get_upper_bounds());
    bool nodeChanged = false;
    if (flag > 0) {    // We can tighten bounds
        for (unsigned int i = 0; i < _nvar; i++) {
            if (mc::Op<I>::l(_DAGobj->currentIntervals[i]) > mc::Op<I>::u(_DAGobj->currentIntervals[i])) {
                std::ostringstream outstr;
                outstr << "  Warning: Something went wrong in constraint propagation. Skipping constraint propagation...";
                _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                break;
            }
            double newLowerBound = mc::Op<I>::l(_DAGobj->currentIntervals[i]);
            double newUpperBound = mc::Op<I>::u(_DAGobj->currentIntervals[i]);


#ifdef MAiNGO_DEBUG_MODE
            if (_contains_incumbent(currentNode)) {
                if (i < _incumbent.size()) {
                    if (_incumbent[i] < newLowerBound && !mc::isequal(_incumbent[i], newLowerBound, _computationTol, _computationTol) || _incumbent[i] > newUpperBound && !mc::isequal(_incumbent[i], newUpperBound, _computationTol, _computationTol)) {
                        std::ostringstream outstr;
                        outstr << "  Warning: Node #" << currentNode.get_ID() << " contains the incumbent and constraint propagation computed a bound for variable " << i << " which cuts off the incumbent. " << std::endl;
                        outstr << "           Correcting this bound and skipping constraint propagation... " << std::endl;
                        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                        break;
                    }
                }
            }
#endif

            switch (_originalVariables[i].get_variable_type()) {
                case babBase::enums::VT_CONTINUOUS:
                    // Only update bounds if difference is larger than tolerance
                    if (!mc::isequal(newLowerBound, lowerVarBounds[i], _computationTol, _computationTol)) {
                        nodeChanged       = true;
                        lowerVarBounds[i] = newLowerBound;
                    }
                    if (!mc::isequal(newUpperBound, upperVarBounds[i], _computationTol, _computationTol)) {
                        nodeChanged       = true;
                        upperVarBounds[i] = newUpperBound;
                    }
                    break;
                case babBase::enums::VT_BINARY:
                    // Round bounds to ensure binary values
                    if (!mc::isequal(newLowerBound, 0, _computationTol, _computationTol) && lowerVarBounds[i] != 1) {
                        nodeChanged       = true;
                        lowerVarBounds[i] = 1;
                    }
                    if (!mc::isequal(newUpperBound, 1, _computationTol, _computationTol) && upperVarBounds[i] != 0) {
                        nodeChanged       = true;
                        upperVarBounds[i] = 0;
                    }
                    // Integer bounds crossing => node is infeasible
                    if (lowerVarBounds[i] > upperVarBounds[i]) {
                        return TIGHTENING_INFEASIBLE;
                    }
                    break;
                case babBase::enums::VT_INTEGER:
                    // Round bounds to ensure integer values
                    if (!mc::isequal(newLowerBound, std::floor(newLowerBound), _computationTol, _computationTol)) {
                        if (lowerVarBounds[i] != std::ceil(newLowerBound)) {
                            nodeChanged       = true;
                            lowerVarBounds[i] = std::ceil(newLowerBound);
                        }
                    }
                    else {
                        if (lowerVarBounds[i] != std::floor(newLowerBound)) {
                            nodeChanged       = true;
                            lowerVarBounds[i] = std::floor(newLowerBound);
                        }
                    }
                    if (!mc::isequal(newUpperBound, std::ceil(newUpperBound), _computationTol, _computationTol)) {
                        if (upperVarBounds[i] != std::floor(newUpperBound)) {
                            nodeChanged       = true;
                            upperVarBounds[i] = std::floor(newUpperBound);
                        }
                    }
                    else {
                        if (upperVarBounds[i] != std::ceil(newUpperBound)) {
                            nodeChanged       = true;
                            upperVarBounds[i] = std::ceil(newUpperBound);
                        }
                    }
                    // Integer bounds crossing => node is infeasible
                    if (lowerVarBounds[i] > upperVarBounds[i]) {
                        return TIGHTENING_INFEASIBLE;
                    }
                    break;
                default: // GCOVR_EXCL_START
                    std::ostringstream errmsg;
                    errmsg << "  Error while solving constraint propagation: Unknown variable type " << _originalVariables[i].get_variable_type() << std::endl;
                    throw MAiNGOException(errmsg.str());
                    break;
            }
        } // GCOVR_EXCL_STOP
    }
    else if (flag < 0) {    // Problem is found to be infeasible
        if (flag < -(int)maxpass) {
            return TIGHTENING_UNCHANGED;    // Means that an error occured and we cannot make a statement
        }


#ifdef MAiNGO_DEBUG_MODE
        if (_contains_incumbent(currentNode)) {
            if (currentNode.get_ID() == 0) {
                return TIGHTENING_INFEASIBLE;
            }
            std::ostringstream outstr;
            outstr << "  Warning: Constraint propagation declared node #" << currentNode.get_ID() << " as infeasible although it holds the incumbent. Skipping constraint propagation..." << std::endl;
            _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);

            return TIGHTENING_UNCHANGED;
        }
#endif

        return TIGHTENING_INFEASIBLE;
    }
    // Otherwise we get 0 meaning that constraint propagation did not provide any improvement

    if (!nodeChanged) {
        return TIGHTENING_UNCHANGED;
    }
    else {
        currentNode = babBase::BabNode(currentNode, lowerVarBounds, upperVarBounds);
        return TIGHTENING_CHANGED;
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// conduct duality-based bound tightening (DBBT) and probing
TIGHTENING_RETCODE
LowerBoundingSolver::do_dbbt_and_probing(babBase::BabNode &currentNode, const std::vector<double> &lbpSolutionPoint, const LbpDualInfo &dualInfo, const double currentUBD)
{

    // Ok, we have multipliers, go ahead
    std::vector<double> newLowerBounds(currentNode.get_lower_bounds());
    std::vector<double> newUpperBounds(currentNode.get_upper_bounds());
    bool changedBounds = false;
    for (unsigned iVar = 0; iVar < _nvar; iVar++) {

        // -----------------------------------
        // 5a DBBT
        // -----------------------------------
        if (lbpSolutionPoint[iVar] == newUpperBounds[iVar]) {

            if (_maingoSettings->BAB_dbbt) {
                if (dualInfo.multipliers[iVar] < 0) {
                    const double ptmp = newUpperBounds[iVar] + (currentUBD - dualInfo.lpLowerBound) / dualInfo.multipliers[iVar];
                    if (ptmp > newLowerBounds[iVar]) {
                        newLowerBounds[iVar] = ptmp;
                        if (_originalVariables[iVar].get_variable_type() > babBase::enums::VT_CONTINUOUS) {
                            if (!mc::isequal(newLowerBounds[iVar], std::floor(newLowerBounds[iVar]), _computationTol, _computationTol)) {
                                newLowerBounds[iVar] = std::ceil(newLowerBounds[iVar]);
                            }
                            else {
                                newLowerBounds[iVar] = std::floor(newLowerBounds[iVar]);
                            }
                        }
                        changedBounds = true;
                    }
                    // Sanity check:
                    if (newLowerBounds[iVar] > newUpperBounds[iVar]) {
                        std::ostringstream errmsg; // GCOVR_EXCL_START
                        errmsg << "  Error in LowerBoundingSolver - DBBT - 1: while setting new lower bound during DBBT for variable " << iVar << ": lower bound became larger than upper bound: " << std::endl;
                        errmsg << "  " << newLowerBounds[iVar] << " > " << newUpperBounds[iVar];
                        throw MAiNGOException(errmsg.str());
                    }
                } // GCOVR_EXCL_STOP
            }
        }
        else if (lbpSolutionPoint[iVar] == newLowerBounds[iVar]) {

            if (_maingoSettings->BAB_dbbt) {
                if (dualInfo.multipliers[iVar] > 0) {
                    const double ptmp = newLowerBounds[iVar] + (currentUBD - dualInfo.lpLowerBound) / dualInfo.multipliers[iVar];
                    if (ptmp < newUpperBounds[iVar]) {
                        newUpperBounds[iVar] = ptmp;
                        if (_originalVariables[iVar].get_variable_type() > babBase::enums::VT_CONTINUOUS) {
                            if (!mc::isequal(newUpperBounds[iVar], std::ceil(newUpperBounds[iVar]), _computationTol, _computationTol)) {
                                newUpperBounds[iVar] = std::floor(newUpperBounds[iVar]);
                            }
                            else {
                                newUpperBounds[iVar] = std::ceil(newUpperBounds[iVar]);
                            }
                        }
                        changedBounds = true;
                    }
                    // Sanity check:
                    if (newLowerBounds[iVar] > newUpperBounds[iVar]) {
                        std::ostringstream errmsg; // GCOVR_EXCL_START
                        errmsg << "  Error in LowerBoundingSolver - DBBT - 2: while setting new upper bound during DBBT for variable " << iVar << ": lower bound became larger than upper bound: " << std::endl;
                        errmsg << "  " << newLowerBounds[iVar] << " > " << newUpperBounds[iVar];
                        throw MAiNGOException(errmsg.str());
                    }
                } // GCOVR_EXCL_STOP
            }
        }
        else {

            // -----------------------------------
            // 5b Probing
            // -----------------------------------
            if (_maingoSettings->BAB_probing) {
                // Lower bound:
                LbpDualInfo probingDualInfo;
                // Declare a tmp node to work on
                babBase::BabNode tmpNode(currentNode, newLowerBounds, newUpperBounds);
                SUBSOLVER_RETCODE probingStatus = _solve_probing_LBP(tmpNode, probingDualInfo, iVar, true);
                if ((probingStatus == SUBSOLVER_FEASIBLE) && (probingDualInfo.multipliers.size() == _nvar)) {
                    if (probingDualInfo.multipliers[iVar] < 0) {
                        const double ptmp = newLowerBounds[iVar] - (probingDualInfo.lpLowerBound - currentUBD) / probingDualInfo.multipliers[iVar];
                        if (ptmp > newLowerBounds[iVar]) {
                            newLowerBounds[iVar] = ptmp;
                            if (_originalVariables[iVar].get_variable_type() > babBase::enums::VT_CONTINUOUS) {
                                newLowerBounds[iVar] = std::ceil(newLowerBounds[iVar]);
                            }
                            if (newLowerBounds[iVar] > newUpperBounds[iVar]) {
                                return TIGHTENING_INFEASIBLE;
                            }
                            changedBounds = true;
                        }
                        // Update the bound of the tmp node
                        tmpNode.set_lower_bound(iVar, newLowerBounds[iVar]);
                    }
                }
                // Upper bound:
                probingStatus = _solve_probing_LBP(tmpNode, probingDualInfo, iVar, false);
                if ((probingStatus == SUBSOLVER_FEASIBLE) && (probingDualInfo.multipliers.size() == _nvar)) {
                    if (probingDualInfo.multipliers[iVar] > 0) {
                        const double ptmp = newUpperBounds[iVar] - (probingDualInfo.lpLowerBound - currentUBD) / probingDualInfo.multipliers[iVar];
                        if (ptmp < newUpperBounds[iVar]) {
                            newUpperBounds[iVar] = ptmp;
                            if (_originalVariables[iVar].get_variable_type() > babBase::enums::VT_CONTINUOUS) {
                                newUpperBounds[iVar] = std::floor(newUpperBounds[iVar]);
                            }
                            if (newUpperBounds[iVar] < newLowerBounds[iVar]) {
                                return TIGHTENING_INFEASIBLE;
                            }
                            changedBounds = true;
                        }
                    }
                    // Update the bound of the tmp node
                    tmpNode.set_upper_bound(iVar, newUpperBounds[iVar]);
                }
            }
        }
    }    // end of for loop over variables

    if (changedBounds) {
        currentNode = babBase::BabNode(currentNode, newLowerBounds, newUpperBounds);
        return TIGHTENING_CHANGED;
    }
    else {
        return TIGHTENING_UNCHANGED;
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// update incumbent, needed for some heuristics
void
LowerBoundingSolver::update_incumbent_LBP(const std::vector<double> &incumbentBAB)
{
    _incumbent = incumbentBAB;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function called by the B&B in preprocessing in order to check the need for specific options, currently for subgradient intervals & CPLEX no large values
void
LowerBoundingSolver::activate_more_scaling()
{

    // Not needed in the default solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// solve lower bounding problem by affine relaxation for probing heuristic
SUBSOLVER_RETCODE
LowerBoundingSolver::_solve_probing_LBP(babBase::BabNode &currentNode, LbpDualInfo &dualInfo,
                                        const unsigned int iVar, const bool fixToLowerBound)
{

    // Update the LP for the current node (i.e., modify bounds and update coefficients and RHS)
    try {
        PROFILE_SCOPE("probing_update_LP")
        _update_LP(currentNode);
    }
    catch (std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error while modifying the lower bounding LP for probing.", e, currentNode);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error while modifying the lower bounding LP for probing.", currentNode);
    }
// GCOVR_EXCL_STOP
    // Fix variable
    _fix_variable(iVar, fixToLowerBound);
    // Solve problem and check return status
    {
        PROFILE_SCOPE("probing_solve_LP")
	    _LPstatus = _solve_LP(currentNode);
    }

    // If LP solver says the problem is infeasible, it's ok, since probing is just a heuristic
    if (_LPstatus == LP_INFEASIBLE) {
        _logger->print_message("  Probing LBP status: Infeasible", VERB_ALL, LBP_VERBOSITY);

        return SUBSOLVER_INFEASIBLE;
    }    // end of if(_LPstatus == LP_INFEASIBLE)
    else if (_LPstatus == LP_UNKNOWN) {
        _logger->print_message("  Warning: LP solver returned unknown status code. Proceeding with parent LBD.\n", VERB_NORMAL, LBP_VERBOSITY);
#ifdef LP__WRITE_CHECK_FILES
        _write_LP_to_file("solve_probing_LBP_unknown_status_code");
#endif
        return SUBSOLVER_INFEASIBLE;
    }

    _logger->print_message("  Probing LBP status: Optimal", VERB_ALL, LBP_VERBOSITY);


    // Process solution: solution point (If we got here, the LP solver declared that an optimal solution was found)
    double etaVal = 0;
    std::vector<double> solution;
    try {
        _get_solution_point(solution, etaVal);
    }
    catch (std::exception &e) {
        std::ostringstream outstr;
        outstr << "  Warning: Variables at solution of Probing LBP could be not obtained by LP solver: " << e.what() << std::endl;
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
        // Return empty solution instead
        solution.clear();
        return SUBSOLVER_INFEASIBLE;
    }
    // Ok, successfully obtained solution point
    _logger->print_vector(_nvar, solution, "  Probing LBP solution point: ", VERB_ALL, LBP_VERBOSITY);

#ifdef LP__OPTIMALITY_CHECK
    // Feasibility check
    if (_check_feasibility(solution) == SUBSOLVER_INFEASIBLE) {
        solution.clear();
        dualInfo.multipliers.clear();
        return SUBSOLVER_INFEASIBLE;
    }
#endif

    // Process solution: optimal solution value
    double newLBD = _get_objective_value();
    if (!(newLBD >= (-_maingoSettings->infinity))) {    // Note that all comparisons return false if one operand is NAN
        std::ostringstream outstr;
        outstr << "  Warning: Objective obtained from LP solver in Probing LBP is out of bounds (" << newLBD << ") although the LP solver solution status is optimal. Keeping parent LBD." << std::endl;
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
        return SUBSOLVER_INFEASIBLE;
    }

    // If the lower bound becomes too low, CPLEX returns -1e19 as lowest value, we need to catch that to properly proceed
    if (newLBD <= -1e19 && _maingoSettings->LBP_solver == LBP_SOLVER_CPLEX) {
        // Not providing multipliers
        dualInfo.multipliers.clear();
        // Simply fallback to intervals
        return SUBSOLVER_INFEASIBLE;
    }
    // Process solution: multipliers for probing
    try {
        _get_multipliers(dualInfo.multipliers);
    }
    catch (std::exception &e) {
        // This is okay, not providing multipliers
        std::ostringstream outstr;
        outstr << "  No multipliers obtained from LP solver for probing: " << e.what() << std::endl;
        _logger->print_message(outstr.str(), VERB_ALL, LBP_VERBOSITY);

        dualInfo.multipliers.clear();
        return SUBSOLVER_INFEASIBLE;
    }

#ifdef LP__OPTIMALITY_CHECK
    double oldBound;
    if (fixToLowerBound) {
        oldBound = currentNode.get_upper_bounds()[iVar];
        currentNode.set_upper_bound(iVar, currentNode.get_lower_bounds()[iVar]);
    }
    else {
        oldBound = currentNode.get_lower_bounds()[iVar];
        currentNode.set_lower_bound(iVar, currentNode.get_upper_bounds()[iVar]);
    }
    // Optimality check through strong duality
    SUBSOLVER_RETCODE status = _check_optimality(currentNode, newLBD, solution, etaVal, dualInfo.multipliers);
    // Restore bounds
    if (fixToLowerBound) {
        currentNode.set_upper_bound(iVar, oldBound);
    }
    else {
        currentNode.set_lower_bound(iVar, oldBound);
    }
    if (status == SUBSOLVER_INFEASIBLE) {
        solution.clear();
        dualInfo.multipliers.clear();
        // In this case just restore the bound and return infeasible
        return SUBSOLVER_INFEASIBLE;
    }
#endif

    dualInfo.lpLowerBound = newLBD;
    std::ostringstream outstr;
    outstr << "  Probing LBD: " << dualInfo.lpLowerBound << std::endl;
    _logger->print_message(outstr.str(), VERB_ALL, LBP_VERBOSITY);


    return SUBSOLVER_FEASIBLE;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// constructs the desired linearization point and calls the function for updating linearizations and modifying the coefficients of the optimization problem
LINEARIZATION_RETCODE
LowerBoundingSolver::_update_LP(const babBase::BabNode &currentNode)
{
    // Set bounds for current node
    std::vector<double> lowerVarBounds(currentNode.get_lower_bounds());
    std::vector<double> upperVarBounds(currentNode.get_upper_bounds());

    _set_variable_bounds(lowerVarBounds, upperVarBounds);
    // Reset the status of computed improved intervals
    _DAGobj->intervals_already_computed = false;

    // Construct linearization points and call function for updating the corresponding linearizations within the optimization problem
    switch (_maingoSettings->LBP_linPoints) {
        case LINP_MID:    //  0. Midpoint
        {
            MC::subHeur.clear();
            return _linearize_model_at_midpoint(lowerVarBounds, upperVarBounds);
            break;
        }
        case LINP_INCUMBENT:    // 1. Incumbent values if in node, else mid
        {
            MC::subHeur.clear();
            return _linearize_model_at_incumbent_or_at_midpoint(lowerVarBounds, upperVarBounds);
            break;
        }
        case LINP_KELLEY:    // 2. Linearization points are computed via an adapted version of Kelley's algorithm
        {
            MC::subHeur.clear();
            return _linearization_points_Kelley(currentNode);
            break;
        }
        case LINP_SIMPLEX:    // 3. Linearization points are given by a previously computed n+1 simplex
        {
            vMC::subHeur.clear();
            return _linearization_points_Simplex(lowerVarBounds, upperVarBounds);
            break;
        }
        case LINP_RANDOM:    // 4. Linearization points are random
        {
            vMC::subHeur.clear();
            return _linearization_points_random(lowerVarBounds, upperVarBounds);
            break;
        }
        case LINP_KELLEY_SIMPLEX:    // 5. Linearization points are first determined by simplex and then Kelley's algorithm is applied
        {
            vMC::subHeur.clear();
            MC::subHeur.clear();
            return _linearization_points_Kelley_Simplex(currentNode);
            break;
        }
        default: { // GCOVR_EXCL_START
            throw MAiNGOException("  Error while updating LP: Unknown linearization strategy.");
            break;
        }
    } // GCOVR_EXCL_STOP
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for setting the bounds of variables
void
LowerBoundingSolver::_set_variable_bounds(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds)
{
    for (unsigned i = 0; i < _nvar; i++) {
        _lowerVarBounds[i] = lowerVarBounds[i];
        _upperVarBounds[i] = upperVarBounds[i];
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// conduct equilibration (scaling with the 1-norm) for an LP row
double
LowerBoundingSolver::_equilibrate_and_relax(std::vector<double> &coefficients, double &rhs, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds)
{

    // Compute 1-norm of row coefficient vector
    double oneNorm(0.);
    double nnonZeros = 0.;
    for (unsigned i = 0; i < coefficients.size(); ++i) {
        oneNorm += std::fabs(coefficients[i]);
        if (coefficients[i] != 0.) {
            nnonZeros++;
        }
    }

    double factor = nnonZeros / oneNorm;    // Arithmetic mean  = number of non zeros / std::fabs(a_ij)

    if (oneNorm >= _computationTol) {

        // Scale by this 1-norm
        for (unsigned i = 0; i < coefficients.size(); ++i) {
            coefficients[i] = coefficients[i] * factor;
        }
        rhs = rhs * factor;

        return factor;
    }
    else {
        return 1.0;
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an objective of the linear program
void
LowerBoundingSolver::_update_LP_obj(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iObj)
{

    if (_maingoSettings->LBP_solver != LBP_SOLVER_MAiNGO) {
        std::ostringstream outstr;
        outstr << "  You need to define function _update_LP_obj in the derived lower bounding solver " << _maingoSettings->LBP_solver << " !";
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
    }

    // Not needed in the default solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an inequality of the linear program
void
LowerBoundingSolver::_update_LP_ineq(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneq)
{

    if (_maingoSettings->LBP_solver != LBP_SOLVER_MAiNGO) {
        std::ostringstream outstr;
        outstr << "  You need to define function _update_LP_ineq in the derived lower bounding solver " << _maingoSettings->LBP_solver << " !";
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
    }

    // Not needed in the default solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an equality of the linear program
void
LowerBoundingSolver::_update_LP_eq(const MC &resultRelaxationCv, const MC &resultRelaxationCc, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iEq)
{

    if (_maingoSettings->LBP_solver != LBP_SOLVER_MAiNGO) {
        std::ostringstream outstr;
        outstr << "  You need to define function _update_LP_eq in the derived lower bounding solver " << _maingoSettings->LBP_solver << " !";
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
    }

    // Not needed in the default solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates a relaxation only inequality of the linear program
void
LowerBoundingSolver::_update_LP_ineqRelaxationOnly(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneqRelaxationOnly)
{

    if (_maingoSettings->LBP_solver != LBP_SOLVER_MAiNGO) {
        std::ostringstream outstr;
        outstr << "  You need to define function _update_LP_ineqRelaxationOnly in the derived lower bounding solver " << _maingoSettings->LBP_solver << " !";
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
    }

    // Not needed in the default solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an equality of the linear program
void
LowerBoundingSolver::_update_LP_eqRelaxationOnly(const MC &resultRelaxationCv, const MC &resultRelaxationCc, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iEqRelaxationOnly)
{

    if (_maingoSettings->LBP_solver != LBP_SOLVER_MAiNGO) {
        std::ostringstream outstr;
        outstr << "  You need to define function _update_LP_eqRelaxationOnly in the derived lower bounding solver " << _maingoSettings->LBP_solver << " !";
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
    }

    // Not needed in the default solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an inequality of the linear program
void
LowerBoundingSolver::_update_LP_ineq_squash(const MC &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin, unsigned const &iIneqSquash)
{

    if (_maingoSettings->LBP_solver != LBP_SOLVER_MAiNGO) {
        std::ostringstream outstr;
        outstr << "  You need to define function _update_LP_ineq_squash in the derived lower bounding solver " << _maingoSettings->LBP_solver << " !";
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
    }

    // Not needed in the default solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates the whole problem by inserting the linearizations
void
LowerBoundingSolver::_update_whole_LP_at_linpoint(const std::vector<MC> &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iLin)
{
    PROFILE_FUNCTION()

    // The function simply calls the methods for updating specific functions
    // Note that all functions are linearized at the same point
    for (size_t i = 0; i < _constraintProperties->size(); i++) {
        unsigned indexNonconstant     = (*_constraintProperties)[i].indexNonconstant;
        unsigned indexTypeNonconstant = (*_constraintProperties)[i].indexTypeNonconstant;
        switch ((*_constraintProperties)[i].type) {
            case OBJ:
                if (iLin < _nLinObj[indexTypeNonconstant]) {
                    _update_LP_obj(resultRelaxation[indexNonconstant], linearizationPoint, lowerVarBounds, upperVarBounds, iLin, indexTypeNonconstant);
                    _DAGobj->validIntervalLowerBound = resultRelaxation[indexNonconstant].l();
                }
                break;
            case INEQ:
                if (iLin < _nLinIneq[indexTypeNonconstant]) {
                    _update_LP_ineq(resultRelaxation[indexNonconstant], linearizationPoint, lowerVarBounds, upperVarBounds, iLin, indexTypeNonconstant);
                }
                break;
            case EQ:
                if (iLin < _nLinEq[indexTypeNonconstant]) {
                    _update_LP_eq(resultRelaxation[indexNonconstant], resultRelaxation[indexNonconstant], linearizationPoint, lowerVarBounds, upperVarBounds, iLin, indexTypeNonconstant);
                }
                break;
            case INEQ_REL_ONLY:
                if (iLin < _nLinIneqRelaxationOnly[indexTypeNonconstant]) {
                    _update_LP_ineqRelaxationOnly(resultRelaxation[indexNonconstant], linearizationPoint, lowerVarBounds, upperVarBounds, iLin, indexTypeNonconstant);
                }
                break;
            case EQ_REL_ONLY:
            case AUX_EQ_REL_ONLY:
                if (iLin < _nLinEqRelaxationOnly[indexTypeNonconstant]) {
                    _update_LP_eqRelaxationOnly(resultRelaxation[indexNonconstant], resultRelaxation[indexNonconstant],
                                                linearizationPoint, lowerVarBounds, upperVarBounds, iLin, indexTypeNonconstant);
                }
                break;
            case INEQ_SQUASH:
                if (iLin < _nLinIneqSquash[indexTypeNonconstant]) {
                    _update_LP_ineq_squash(resultRelaxation[indexNonconstant], linearizationPoint, lowerVarBounds, upperVarBounds, iLin, indexTypeNonconstant);
                }
                break;
            default:
                break;
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an objective of the linear program
void
LowerBoundingSolver::_update_LP_obj(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iObj)
{

    if (_maingoSettings->LBP_solver != LBP_SOLVER_MAiNGO) {
        std::ostringstream outstr;
        outstr << "  You need to define function _update_LP_obj for vector McCormick in the derived lower bounding solver " << _maingoSettings->LBP_solver << " !";
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
    }

    // Not needed in the default solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an inequality of the linear program
void
LowerBoundingSolver::_update_LP_ineq(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iIneq)
{

    if (_maingoSettings->LBP_solver != LBP_SOLVER_MAiNGO) {
        std::ostringstream outstr;
        outstr << "  You need to define function _update_LP_ineq for vector McCormick in the derived lower bounding solver " << _maingoSettings->LBP_solver << " !";
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
    }

    // Not needed in the default solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an equality of the linear program
void
LowerBoundingSolver::_update_LP_eq(const vMC &resultRelaxationCvVMC, const vMC &resultRelaxationCcVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iEq)
{

    if (_maingoSettings->LBP_solver != LBP_SOLVER_MAiNGO) {
        std::ostringstream outstr;
        outstr << "  You need to define function _update_LP_eq for vector McCormick in the derived lower bounding solver " << _maingoSettings->LBP_solver << " !";
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
    }

    // Not needed in the default solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates a relaxation only inequality of the linear program
void
LowerBoundingSolver::_update_LP_ineqRelaxationOnly(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iIneqRelaxationOnly)
{

    if (_maingoSettings->LBP_solver != LBP_SOLVER_MAiNGO) {
        std::ostringstream outstr;
        outstr << "  You need to define function _update_LP_ineqRelaxationOnly for vector McCormick in the derived lower bounding solver " << _maingoSettings->LBP_solver << " !";
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
    }

    // Not needed in the default solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an equality of the linear program
void
LowerBoundingSolver::_update_LP_eqRelaxationOnly(const vMC &resultRelaxationCvVMC, const vMC &resultRelaxationCcVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iEqRelaxationOnly)
{

    if (_maingoSettings->LBP_solver != LBP_SOLVER_MAiNGO) {
        std::ostringstream outstr;
        outstr << "  You need to define function _update_LP_eqRelaxationOnly for vectpr McCormick in the derived lower bounding solver " << _maingoSettings->LBP_solver << " !";
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
    }

    // Not needed in the default solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an inequality of the linear program
void
LowerBoundingSolver::_update_LP_ineq_squash(const vMC &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, unsigned const &iIneqSquash)
{

    if (_maingoSettings->LBP_solver != LBP_SOLVER_MAiNGO) {
        std::ostringstream outstr;
        outstr << "  You need to define function _update_LP_ineq_squash for vector McCormick in the derived lower bounding solver " << _maingoSettings->LBP_solver << " !";
        _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
    }

    // Not needed in the default solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates the whole problem by inserting the linearizations
void
LowerBoundingSolver::_update_whole_LP_at_vector_linpoints(const std::vector<vMC> &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoints, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds)
{
    // The function simply calls the methods for updating specific functions
    for (size_t i = 0; i < _constraintProperties->size(); i++) {
        unsigned indexNonconstant     = (*_constraintProperties)[i].indexNonconstant;
        unsigned indexTypeNonconstant = (*_constraintProperties)[i].indexTypeNonconstant;
        switch ((*_constraintProperties)[i].type) {
            case OBJ:
                _update_LP_obj(resultRelaxationVMC[indexNonconstant], linearizationPoints, lowerVarBounds, upperVarBounds, indexTypeNonconstant);
                _DAGobj->validIntervalLowerBound = resultRelaxationVMC[indexNonconstant].l();
                break;
            case INEQ:
                _update_LP_ineq(resultRelaxationVMC[indexNonconstant], linearizationPoints, lowerVarBounds, upperVarBounds, indexTypeNonconstant);
                break;
            case EQ:
                _update_LP_eq(resultRelaxationVMC[indexNonconstant], resultRelaxationVMC[indexNonconstant], linearizationPoints, lowerVarBounds, upperVarBounds, indexTypeNonconstant);
                break;
            case INEQ_REL_ONLY:
                _update_LP_ineqRelaxationOnly(resultRelaxationVMC[indexNonconstant], linearizationPoints, lowerVarBounds, upperVarBounds, indexTypeNonconstant);
                break;
            case EQ_REL_ONLY:
            case AUX_EQ_REL_ONLY:
                _update_LP_eqRelaxationOnly(resultRelaxationVMC[indexNonconstant], resultRelaxationVMC[indexNonconstant],
                                            linearizationPoints, lowerVarBounds, upperVarBounds, indexTypeNonconstant);
                break;
            case INEQ_SQUASH:
                _update_LP_ineq_squash(resultRelaxationVMC[indexNonconstant], linearizationPoints, lowerVarBounds, upperVarBounds, indexTypeNonconstant);
                break;
            default:
                break;
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for solving the currently constructed linear program, also internally sets the _solutionPoint, _multipliers, and the _LPstatus
LP_RETCODE
LowerBoundingSolver::_solve_LP(const babBase::BabNode &currentNode)
{
    _solutionPoint.clear();
    _multipliers.clear();
    for (size_t i = 0; i < (*_constraintProperties).size(); i++) {
        double constraintValueL = _DAGobj->resultRelaxation[i].l();    // Interval lower bound
        double constraintValueU = _DAGobj->resultRelaxation[i].u();    // Interval upper bound
        switch ((*_constraintProperties)[i].type) {
            case INEQ:
            case INEQ_REL_ONLY:
                if (constraintValueL > _maingoSettings->deltaIneq) {
                    _LPstatus = LP_INFEASIBLE;
                    return _LPstatus;
                }
                break;
            case EQ:
            case EQ_REL_ONLY:
            case AUX_EQ_REL_ONLY:
                if (constraintValueL > _maingoSettings->deltaEq || constraintValueU < -_maingoSettings->deltaEq) {
                    _LPstatus = LP_INFEASIBLE;
                    return _LPstatus;
                }
                break;
            case INEQ_SQUASH:
                if (constraintValueL > 0) {
                    _LPstatus = LP_INFEASIBLE;
                    return _LPstatus;
                }
                break;
            case OBJ:
            default:
                break;
        }
    }
    // Minimize the convex relaxation of the objective function and save solution point and multipliers
    _objectiveValue = _DAGobj->resultRelaxation[0].cv();

    _solutionPoint.resize(_nvar);
    _multipliers.resize(_nvar);
    for (unsigned int i = 0; i < _nvar; i++) {
        // Check the sign of the subgradients to go in the correct direction on the linearization
        if (_DAGobj->resultRelaxation[0].cvsub(i) == 0) {
            // Nothing to add
            _solutionPoint[i] = (_lowerVarBounds[i] + _upperVarBounds[i]) / 2.;
        }
        else if (_DAGobj->resultRelaxation[0].cvsub(i) > 0.) {
            _objectiveValue   = _objectiveValue + _DAGobj->resultRelaxation[0].cvsub(i) * (_lowerVarBounds[i] - (_lowerVarBounds[i] + _upperVarBounds[i]) / 2.);
            _solutionPoint[i] = _lowerVarBounds[i];
        }
        else {
            _objectiveValue   = _objectiveValue + _DAGobj->resultRelaxation[0].cvsub(i) * (_upperVarBounds[i] - (_lowerVarBounds[i] + _upperVarBounds[i]) / 2.);
            _solutionPoint[i] = _upperVarBounds[i];
        }
        _multipliers[i] = _DAGobj->resultRelaxation[0].cvsub(i);
    }    // end of for i

    _DAGobj->validIntervalLowerBound = _DAGobj->resultRelaxation[0].l();

    _LPstatus = LP_OPTIMAL;
	return _LPstatus;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function returning the current status of solved linear program
LP_RETCODE
LowerBoundingSolver::_get_LP_status()
{
    return _LPstatus;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function setting the solution point and value of the eta variable to the solution point of the lastly solved LP
void
LowerBoundingSolver::_get_solution_point(std::vector<double> &solution, double &etaVal)
{
    solution = _solutionPoint;
    etaVal   = 0;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function returning the objective value of lastly solved LP
double
LowerBoundingSolver::_get_objective_value()
{
    double objVal = _get_objective_value_solver();
    return objVal;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function returning the objective value of lastly solved LP
double
LowerBoundingSolver::_get_objective_value_solver()
{
    return _objectiveValue;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function setting the multipliers
void
LowerBoundingSolver::_get_multipliers(std::vector<double> &multipliers)
{
    multipliers = _multipliers;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for restoring coefficients and options for the LP after OBBT
void
LowerBoundingSolver::_restore_LP_coefficients_after_OBBT()
{
    // Not needed in the MAiNGO solver, since OBBT is not performed
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for deactivating the objective for feasibility OBBT
void
LowerBoundingSolver::_deactivate_objective_function_for_OBBT()
{
    // Not needed in the MAiNGO solver, since OBBT is not performed
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for modifying the LP for feasibility-optimality OBBT
void
LowerBoundingSolver::_modify_LP_for_feasopt_OBBT(const double &currentUBD, std::list<unsigned> &toTreatMax, std::list<unsigned> &toTreatMin)
{
    // Not needed in the MAiNGO solver, since OBBT is not performed
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for setting the optimization sense of variable iVar
void
LowerBoundingSolver::_set_optimization_sense_of_variable(const unsigned &iVar, const int &optimizationSense)
{
    // Not needed in the MAiNGO solver, since OBBT is not performed
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for fixing the optimization variable iVar
void
LowerBoundingSolver::_fix_variable(const unsigned &iVar, const bool fixToLowerBound)
{
    if (fixToLowerBound) {
        _upperVarBounds[iVar] = _lowerVarBounds[iVar];
    }
    else {
        _lowerVarBounds[iVar] = _upperVarBounds[iVar];
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for checking whether the current linear program is really infeasible
bool
LowerBoundingSolver::_check_if_LP_really_infeasible()
{

    // If we have to check this in the MAiNGO default solver, something went really wrong
    return true;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// check need for options in preprocessing
void
LowerBoundingSolver::preprocessor_check_options(const babBase::BabNode &rootNode)
{

    // Set bounds for root node
    std::vector<double> lowerVarBounds(rootNode.get_lower_bounds());
    std::vector<double> upperVarBounds(rootNode.get_upper_bounds());
    std::vector<double> linearizationPoint;

    for (unsigned int i = 0; i < _nvar; i++) {
        linearizationPoint.push_back(0.5 * (lowerVarBounds[i] + upperVarBounds[i]));
    }

    try {
        // Set relNodeTol
        _maingoSettings->relNodeTol = std::min(_maingoSettings->deltaIneq, std::min(_maingoSettings->deltaEq, _maingoSettings->relNodeTol));

        // Currently the evaluation is used only to possibly detect interval and McCormick exceptions
        for (unsigned int i = 0; i < _nvar; i++) {
            _DAGobj->McPoint[i] = MC(I(lowerVarBounds[i], upperVarBounds[i]), linearizationPoint[i]);
            _DAGobj->McPoint[i].sub(_nvar, i);
        }

        if (_maingoSettings->LBP_subgradientIntervals) {
            // Compute improved relaxations at mid point
            bool oldSetting                 = MC::options.SUB_INT_HEUR_USE;
            MC::options.SUB_INT_HEUR_USE    = true;
            MC::subHeur.originalLowerBounds = &lowerVarBounds;
            MC::subHeur.originalUpperBounds = &upperVarBounds;
            MC::subHeur.referencePoint      = &linearizationPoint;

            _DAGobj->DAG.eval(_DAGobj->subgraph, _DAGobj->MCarray, _DAGobj->functions.size(), _DAGobj->functions.data(), _DAGobj->resultRelaxation.data(), _nvar, _DAGobj->vars.data(), _DAGobj->McPoint.data());
            MC::options.SUB_INT_HEUR_USE        = oldSetting;
            MC::subHeur.usePrecomputedIntervals = false;
            MC::subHeur.reset_iterator();
        }
        else {
            _DAGobj->DAG.eval(_DAGobj->subgraph, _DAGobj->MCarray, _DAGobj->functions.size(), _DAGobj->functions.data(), _DAGobj->resultRelaxation.data(), _nvar, _DAGobj->vars.data(), _DAGobj->McPoint.data());
        }

        if (_maingoSettings->LBP_addAuxiliaryVars && !_maingoSettings->BAB_constraintPropagation) {
            _logger->print_message("        The option BAB_constraintPropagation has to be 1 when using option LBP_addAuxiliaryVars. Setting it to 1.\n", VERB_NORMAL, LBP_VERBOSITY);
            _maingoSettings->BAB_constraintPropagation = true;
        }

        // Check whether the options can be applied with respect to the used solver
        _turn_off_specific_options();
    }
    catch (const filib::interval_io_exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException(std::string("  (Preprocessor) Error in interval extensions: ") + e.what());
    }
    catch (const MC::Exceptions &e) {
        throw MAiNGOException(std::string("  (Preprocessor) Error in evaluation of McCormick relaxations: ") + e.what());
    }
    catch (const std::exception &e) {
        throw MAiNGOException("  (Preprocessor) Error in evaluation of relaxed model equations. ", e);
    }
    catch (...) {
        throw MAiNGOException("  (Preprocessor) Unknown error in evaluation of relaxed model equations. ");
    }
} // GCOVR_EXCL_STOP


#ifdef HAVE_GROWING_DATASETS
/////////////////////////////////////////////////////////////////////////
// passes index of new dataset to DagObj routine
void
LowerBoundingSolver::change_growing_objective(const int indexDataset)
{
    _DAGobj->change_growing_objective(indexDataset);
}


/////////////////////////////////////////////////////////////////////////
// calling respective DagObj routine
void
LowerBoundingSolver::change_growing_objective_for_resampling()
{
    _DAGobj->change_growing_objective_for_resampling();
}


/////////////////////////////////////////////////////////////////////////
// passes dataset and position of first data point to DagObj routine
void
LowerBoundingSolver::pass_data_position_to_solver(const std::shared_ptr<std::vector<unsigned int>> datasetsIn, const unsigned int indexFirstDataIn)
{
    _DAGobj->datasets       = datasetsIn;
    _DAGobj->indexFirstData = indexFirstDataIn;
}


/////////////////////////////////////////////////////////////////////////
// passes resampled initial dataset to DagObj routine
void
LowerBoundingSolver::pass_resampled_dataset_to_solver(const std::shared_ptr<std::set<unsigned int>> datasetIn)
{
    _DAGobj->datasetResampled = datasetIn;
}


/////////////////////////////////////////////////////////////////////////
// passes flag indicating whether to use mean squared error as the objective function to respective DagObj routine
void
LowerBoundingSolver::pass_use_mse_to_solver(const bool useMseIn)
{
    _DAGobj->useMse = useMseIn;
}
#endif    //HAVE_GROWING_DATASETS


/////////////////////////////////////////////////////////////////////////////////////////////
// check need for options in preprocessing
void
LowerBoundingSolver::_turn_off_specific_options()
{

    if (_maingoSettings->LBP_solver != LBP_SOLVER_MAiNGO) {
        _logger->print_message("        Warning: Function for turning off specific options not implemented. Not changing any settings. Proceeding...\n", VERB_NORMAL, LBP_VERBOSITY);
    }
    else {
        if (_maingoSettings->LBP_linPoints != LINP_MID) {
            _logger->print_message("        The option LBP_linPoints has to be  0 when using the default MAiNGO solver (LBP_solver = 0). Setting it to 0.\n", VERB_NORMAL, LBP_VERBOSITY);
            _maingoSettings->LBP_linPoints = LINP_MID;    // Note that this already has been used in the constructor!
        }
        if (_maingoSettings->PRE_obbtMaxRounds > 0) {
            _logger->print_message("        The option PRE_obbtMaxRounds has to be 0 when using the default MAiNGO solver (LBP_solver = 0). Setting it to 0.\n", VERB_NORMAL, LBP_VERBOSITY);
            _maingoSettings->PRE_obbtMaxRounds = 0;
        }
        if (_maingoSettings->BAB_alwaysSolveObbt) {
            _logger->print_message("        The option BAB_alwaysSolveObbt has to be 0 when using the default MAiNGO solver (LBP_solver = 0). Setting it to 0.\n", VERB_NORMAL, LBP_VERBOSITY);
            _maingoSettings->BAB_alwaysSolveObbt = false;
        }
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// fallback to rigorous interval checks
SUBSOLVER_RETCODE
LowerBoundingSolver::_fallback_to_intervals(double &newLBD)
{
    // Next, check feasibility
    switch (_maingoSettings->LBP_linPoints) {
        case LINP_MID:
        case LINP_INCUMBENT:
        case LINP_KELLEY: {
            for (size_t i = 0; i < (*_constraintProperties).size(); i++) {

                double constraintValueL = _DAGobj->resultRelaxation[i].l();    // Interval lower bound
                double constraintValueU = _DAGobj->resultRelaxation[i].u();    // Interval upper bound

                switch ((*_constraintProperties)[i].type) {
                    case INEQ:
                    case INEQ_REL_ONLY:
                        if (constraintValueL > _maingoSettings->deltaIneq) {
                            return SUBSOLVER_INFEASIBLE;
                        }
                        break;
                    case EQ:
                    case EQ_REL_ONLY:
                    case AUX_EQ_REL_ONLY:
                        if (constraintValueL > _maingoSettings->deltaEq || constraintValueU < -_maingoSettings->deltaEq) {
                            return SUBSOLVER_INFEASIBLE;
                        }
                        break;
                    case INEQ_SQUASH:
                        if (constraintValueL > 0) {
                            return SUBSOLVER_INFEASIBLE;
                        }
                        break;
                    case OBJ:
                    default:
                        break;
                }
            }
            // The objective value is the interval lower bound of the objective
            newLBD = _DAGobj->resultRelaxation[0].l();
            break;
        }
        case LINP_SIMPLEX:
        case LINP_RANDOM:
        case LINP_KELLEY_SIMPLEX: {

            for (size_t i = 0; i < (*_constraintProperties).size(); i++) {
                double constraintValueL;    // Interval lower bound
                double constraintValueU;
                if ((*_constraintProperties)[i].dependency > LINEAR) {
                    constraintValueL = _DAGobj->resultRelaxationVMCNonlinear[(*_constraintProperties)[i].indexNonlinear].l();
                    constraintValueU = _DAGobj->resultRelaxationVMCNonlinear[(*_constraintProperties)[i].indexNonlinear].u();
                }
                else {
                    constraintValueL = _DAGobj->resultRelaxationLinear[(*_constraintProperties)[i].indexLinear].l();
                    constraintValueU = _DAGobj->resultRelaxationLinear[(*_constraintProperties)[i].indexLinear].u();
                }
                switch ((*_constraintProperties)[i].type) {
                    case INEQ:
                    case INEQ_REL_ONLY:
                        if (constraintValueL > _maingoSettings->deltaIneq) {
                            return SUBSOLVER_INFEASIBLE;
                        }
                        break;
                    case EQ:
                    case EQ_REL_ONLY:
                    case AUX_EQ_REL_ONLY:
                        if (constraintValueL > _maingoSettings->deltaEq || constraintValueU < -_maingoSettings->deltaEq) {
                            return SUBSOLVER_INFEASIBLE;
                        }
                        break;
                    case INEQ_SQUASH:
                        if (constraintValueL > 0) {
                            return SUBSOLVER_INFEASIBLE;
                        }
                        break;
                    case OBJ:
                    default:
                        break;
                }
            }
            if ((*_constraintProperties)[0].dependency > LINEAR) {
                // The objective value is the interval lower bound of the objective
                newLBD = _DAGobj->resultRelaxationVMCNonlinear[0].l();
            }
            else {
                newLBD = _DAGobj->resultRelaxationLinear[0].l();
            }
            break;
        }
    }
    if (newLBD != newLBD) {
        newLBD = -_maingoSettings->infinity;
    }
    return SUBSOLVER_FEASIBLE;
}


#ifdef LP__OPTIMALITY_CHECK
/////////////////////////////////////////////////////////////////////////////////////////////
// infeasibility check
SUBSOLVER_RETCODE
LowerBoundingSolver::_check_infeasibility(const babBase::BabNode &currentNode)
{
    // We don't have a check in the MAiNGO solver
    return SUBSOLVER_INFEASIBLE;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// feasibility check
SUBSOLVER_RETCODE
LowerBoundingSolver::_check_feasibility(const std::vector<double> &solution)
{
    // We don't have a check in the MAiNGO solver
    return SUBSOLVER_FEASIBLE;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// optimality check
SUBSOLVER_RETCODE
LowerBoundingSolver::_check_optimality(const babBase::BabNode &currentNode, const double newLBD, const std::vector<double> &solution, const double etaVal, const std::vector<double> &multipliers)
{
    // We don't have a check in the MAiNGO solver
    return SUBSOLVER_FEASIBLE;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// print current LP
void
LowerBoundingSolver::_print_LP(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds)
{

    std::ostringstream outstr;
    outstr << "  min eta" << std::endl;
    outstr << "  constraints:" << std::setprecision(16) << std::endl;
    for (unsigned int i = 0; i < 1; i++) {
        for (unsigned int k = 0; k < _nLinObj[i]; k++) {
            for (unsigned int j = 0; j < _nvar; j++) {
                outstr << _matrixObj[i][k][j] << "*x" << j << " ";
            }
            outstr << -(_objectiveScalingFactors[i][k]) << "*eta";
            outstr << "  <= " << _rhsObj[i][k] << std::endl;
        }
    }
    if (_nineq > 0) {
        outstr << "  inequalities:" << std::endl;
    }
    for (unsigned int i = 0; i < _nineq; i++) {
        for (unsigned int k = 0; k < _nLinIneq[i]; k++) {
            for (unsigned int j = 0; j < _nvar; j++) {
                outstr << _matrixIneq[i][k][j] << "*x" << j << " ";
            }
            outstr << "  <= " << _rhsIneq[i][k] << std::endl;
        }
    }
    if (_neq > 0) {
        outstr << "  equalities (convex):" << std::endl;
    }
    for (unsigned int i = 0; i < _neq; i++) {
        for (unsigned int k = 0; k < _nLinEq[i]; k++) {
            for (unsigned int j = 0; j < _nvar; j++) {
                outstr << _matrixEq1[i][k][j] << "*x" << j << " ";
            }
            outstr << "  <= " << _rhsEq1[i][k] << std::endl;
        }
    }
    if (_neq > 0) {
        outstr << "  equalities (concave):" << std::endl;
    }
    for (unsigned int i = 0; i < _neq; i++) {
        for (unsigned int k = 0; k < _nLinEq[i]; k++) {
            for (unsigned int j = 0; j < _nvar; j++) {
                outstr << _matrixEq2[i][k][j] << "*x" << j << " ";
            }
            outstr << "  <= " << _rhsEq2[i][k] << std::endl;
        }
    }
    if (_nineqRelaxationOnly > 0) {
        outstr << "  relaxation only inequalities:" << std::endl;
    }
    for (unsigned int i = 0; i < _nineqRelaxationOnly; i++) {
        for (unsigned int k = 0; k < _nLinIneqRelaxationOnly[i]; k++) {
            for (unsigned int j = 0; j < _nvar; j++) {
                outstr << _matrixIneqRelaxationOnly[i][k][j] << "*x" << j << " ";
            }
            outstr << "  <= " << _rhsIneqRelaxationOnly[i][k] << std::endl;
        }
    }
    if (_neqRelaxationOnly > 0) {
        outstr << "  relaxation only equalities (convex):" << std::endl;
    }
    for (unsigned int i = 0; i < _neqRelaxationOnly; i++) {
        for (unsigned int k = 0; k < _nLinEqRelaxationOnly[i]; k++) {
            for (unsigned int j = 0; j < _nvar; j++) {
                outstr << _matrixEqRelaxationOnly1[i][k][j] << "*x" << j << " ";
            }
            outstr << "  <= " << _rhsEqRelaxationOnly1[i][k] << std::endl;
        }
    }
    if (_neqRelaxationOnly > 0) {
        outstr << "  relaxation only equalities (concave):" << std::endl;
    }
    for (unsigned int i = 0; i < _neqRelaxationOnly; i++) {
        for (unsigned int k = 0; k < _nLinEqRelaxationOnly[i]; k++) {
            for (unsigned int j = 0; j < _nvar; j++) {
                outstr << _matrixEqRelaxationOnly2[i][k][j] << "*x" << j << " ";
            }
            outstr << "  <= " << _rhsEqRelaxationOnly2[i][k] << std::endl;
        }
    }
    if (_nineqSquash > 0) {
        outstr << "  squash inequalities:" << std::endl;
    }
    for (unsigned int i = 0; i < _nineqSquash; i++) {
        for (unsigned int k = 0; k < _nLinIneqSquash[i]; k++) {
            for (unsigned int j = 0; j < _nvar; j++) {
                outstr << _matrixIneqSquash[i][k][j] << "*x" << j << " ";
            }
            outstr << "  <= " << _rhsIneqSquash[i][k] << std::endl;
        }
    }
    for (unsigned i = 0; i < _nvar; i++) {
        outstr << "  x(" << i << "): " << lowerVarBounds[i] << " : " << upperVarBounds[i] << std::endl;
    }

    _logger->print_message(outstr.str(), VERB_NONE, LBP_VERBOSITY);
}
#endif

#ifdef LP__WRITE_CHECK_FILES
/////////////////////////////////////////////////////////////////////////////////////////////
// write current LP to file
void
LowerBoundingSolver::_write_LP_to_file(const std::string &fileName)
{

    std::string str;
    if (fileName.empty()) {
        str = "MAiNGO_LP_WRITE_CHECK_FILES.lp";
    }
    else {
        str = fileName + ".lp";
    }

    std::ofstream lpFile(str);

    lpFile << "\\ This file was generated by MAiNGO " << get_version() << "\n\n";

    lpFile << "Minimize\n";
    // Print objective
    lpFile << std::setprecision(16) << _DAGobj->resultRelaxation[0].cv();
    for (unsigned int i = 0; i < _nvar; i++) {
        // Check the sign of the subgradients to go in the correct direction on the linearization
        if (mc::isequal(std::fabs(_DAGobj->resultRelaxation[0].cvsub(i)), 0., MC::options.MVCOMP_TOL, MC::options.MVCOMP_TOL)) {
            lpFile << " + 0 x" << i + 1;
        }
        else {
            lpFile << " + " << std::setprecision(16) << _DAGobj->resultRelaxation[0].cvsub(i) << " x" << i + 1 << " - " << std::setprecision(16) << _DAGobj->resultRelaxation[0].cvsub(i) * (_lowerVarBounds[i] + _upperVarBounds[i]) / 2.0;
        }
    }
    lpFile << "\n Subject To \n";

    // Inequalities
    for (unsigned int i = 1; i < 1 + _nineq; i++) {
        lpFile << "ineq" << i << ": " << std::setprecision(16) << _DAGobj->resultRelaxation[i].l() << " <= " << _maingoSettings->deltaIneq << "\n";
    }
    // Equalities
    for (unsigned int i = 1 + _nineq; i < 1 + _nineq + _neq; i++) {
        lpFile << "eqcv" << i << ": " << std::setprecision(16) << _DAGobj->resultRelaxation[i].l() << " <= " << _maingoSettings->deltaEq << "\n";
        lpFile << "eqcc" << i << ": " << std::setprecision(16) << -_DAGobj->resultRelaxation[i].u() << " <= " << _maingoSettings->deltaEq << "\n";
    }
    // Relaxation only inequalities
    for (unsigned int i = 1 + _nineq + _neq; i < 1 + _nineq + _neq + _nineqRelaxationOnly; i++) {
        lpFile << "ineqRelOnly" << i << ": " << std::setprecision(16) << _DAGobj->resultRelaxation[i].l() << " <= " << _maingoSettings->deltaIneq << "\n";
    }
    // Relaxation only equalities
    for (unsigned int i = 1 + _nineq + _neq + _nineqRelaxationOnly; i < 1 + _nineq + _neq + _nineqRelaxationOnly + _neqRelaxationOnly; i++) {
        lpFile << "eqcvRelOnly" << i << ": " << std::setprecision(16) << _DAGobj->resultRelaxation[i].l() << " <= " << _maingoSettings->deltaEq << "\n";
        lpFile << "eqccRelOnly" << i << ": " << std::setprecision(16) << -_DAGobj->resultRelaxation[i].u() << " <= " << _maingoSettings->deltaEq << "\n";
    }
    // Squash inequalities
    for (unsigned int i = 1 + _nineq + _neq + _nineqRelaxationOnly + _neqRelaxationOnly; i < 1 + _nineq + _neq + _nineqRelaxationOnly + _neqRelaxationOnly + _nineqSquash; i++) {
        lpFile << "ineqSquash" << i << ": " << std::setprecision(16) << _DAGobj->resultRelaxation[i].l() << " <= " << 0 << "\n";
    }
    lpFile << "Bounds\n";

    // Write bounds
    for (unsigned i = 0; i < _nvar; i++) {
        lpFile << std::setprecision(16) << _lowerVarBounds[i] << " <= x" << i + 1 << " <= " << std::setprecision(16) << _upperVarBounds[i] << "\n";
    }
    lpFile << "End\n";
    lpFile.close();
}
#endif


/////////////////////////////////////////////////////////////////////////////////////////////
// check if a branch-and-bound node contains the incumbent (if any)
bool
LowerBoundingSolver::_contains_incumbent(const babBase::BabNode &node)
{
    _logger->print_message("  Checking if node contains incumbent.", VERB_ALL, LBP_VERBOSITY);

    if (_incumbent.empty()) {
        _logger->print_message("  No incumbent available.", VERB_ALL, LBP_VERBOSITY);
        return false;
    }
    else if (point_is_within_node_bounds(_incumbent, node)) {
        _logger->print_message("  Node contains incumbent.", VERB_ALL, LBP_VERBOSITY);
        return true;
    }
    else {
        _logger->print_message("  Node does not contain incumbent.", VERB_ALL, LBP_VERBOSITY);
        return false;
    }
}
