/**********************************************************************************
 * Copyright (c) 2019-2023 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#include "MAiNGOException.h"
#include "instrumentor.h"
#include "lbp.h"
#include "lbpDagObj.h"
#include "pointIsWithinNodeBounds.h"

#include <algorithm>

using namespace maingo;
using namespace lbp;


/////////////////////////////////////////////////////////////////////////
// linearizes each function of the model at the middle point of the underlying box
LINEARIZATION_RETCODE
LowerBoundingSolver::_linearize_model_at_midpoint(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds)
{
    PROFILE_FUNCTION()

    std::vector<double> linearizationPoint;
    for (unsigned int i = 0; i < _nvar; i++) {
        linearizationPoint.push_back(0.5 * (lowerVarBounds[i] + upperVarBounds[i]));
    }

    _linearize_functions_at_linpoint(_DAGobj->resultRelaxation, linearizationPoint, lowerVarBounds, upperVarBounds, _DAGobj->subgraph, _DAGobj->functions);

    _update_whole_LP_at_linpoint(_DAGobj->resultRelaxation, linearizationPoint, lowerVarBounds, upperVarBounds, 0);
    // The LP will be solved in solve_LBP/solve_OBBT
    return LINEARIZATION_UNKNOWN;
}


/////////////////////////////////////////////////////////////////////////
// linearizes each function of the model at the incumbent, if the incumbent is not in the node, linearize at mid point of the underlying box
LINEARIZATION_RETCODE
LowerBoundingSolver::_linearize_model_at_incumbent_or_at_midpoint(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds)
{
    PROFILE_FUNCTION()

    _logger->print_message("  Checking if node contains incumbent.", VERB_ALL, LBP_VERBOSITY);
    if (!_incumbent.empty() && point_is_within_node_bounds(_incumbent, lowerVarBounds, upperVarBounds)) {
        _logger->print_message("  Node contains incumbent, linearizing there.", VERB_ALL, LBP_VERBOSITY);

        _linearize_functions_at_linpoint(_DAGobj->resultRelaxation, _incumbent, lowerVarBounds, upperVarBounds, _DAGobj->subgraph, _DAGobj->functions);

        _update_whole_LP_at_linpoint(_DAGobj->resultRelaxation, _incumbent, lowerVarBounds, upperVarBounds, 0);
        // The LP will be solved in solve_LBP/solve_OBBT
        return LINEARIZATION_UNKNOWN;
    }
    else {
        _logger->print_message("  Node does not contain incumbent, linearizing at midpoint.", VERB_ALL, LBP_VERBOSITY);
        return _linearize_model_at_midpoint(lowerVarBounds, upperVarBounds);
    }
}


/////////////////////////////////////////////////////////////////////////
// call the proper function for linearization of the relaxation of the objective function and the constraints
void
LowerBoundingSolver::_linearize_functions_at_linpoint(std::vector<MC> &resultRelaxation, const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds,
                                                      mc::FFSubgraph &subgraph, std::vector<mc::FFVar> &functions)
{
    PROFILE_FUNCTION()

    for (unsigned int i = 0; i < _nvar; i++) {
        _DAGobj->McPoint[i] = MC(I(lowerVarBounds[i], upperVarBounds[i]), linearizationPoint[i]);
        _DAGobj->McPoint[i].sub(_nvar, i);
    }

    try {
        PROFILE_SCOPE("DAG evaluation for _linearize_functions_at_linpoint")
        
        // Use the DAG interval subgradient heuristic if specified in settings
        if (!_DAGobj->intervals_already_computed && _maingoSettings->LBP_subgradientIntervals) {
            // Set required pointers
            MC::subHeur.originalLowerBounds     = &lowerVarBounds;
            MC::subHeur.originalUpperBounds     = &upperVarBounds;
            MC::subHeur.referencePoint          = &linearizationPoint;
            _DAGobj->intervals_already_computed = true;
            _DAGobj->DAG.eval(subgraph, _DAGobj->MCarray, functions.size(), functions.data(), resultRelaxation.data(), _nvar, _DAGobj->vars.data(), _DAGobj->McPoint.data());
            // Note that we HAVE TO set the bool AFTER the first computation of relaxations. It is set to false via clear() in _update_LP
            MC::subHeur.usePrecomputedIntervals = true;
        }
        else {
            _DAGobj->DAG.eval(subgraph, _DAGobj->MCarray, functions.size(), functions.data(), resultRelaxation.data(), _nvar, _DAGobj->vars.data(), _DAGobj->McPoint.data());
        }
    }
    catch (const filib::interval_io_exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException(std::string("  Error in interval extensions: ") + e.what());
    }
    catch (const MC::Exceptions &e) {
        throw MAiNGOException(std::string("  Error in evaluation of McCormick relaxations: ") + e.what());
    }
    catch (const vMC::Exceptions &e) {
        throw MAiNGOException(std::string("  Error in evaluation of vMcCormick relaxations: ") + e.what());
    }
    catch (const std::exception &e) {
        throw MAiNGOException("  Error in evaluation of relaxed model equations.", e);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error in evaluation of relaxed model equations.");
    }
    // GCOVR_EXCL_STOP
    if (_maingoSettings->LBP_subgradientIntervals) {
        // Reset interval iterator to enable the computation of the next linearization point with the use of precomputed intervals
        MC::subHeur.reset_iterator();
    }
}


/////////////////////////////////////////////////////////////////////////
// call the proper function for linearization of the relaxation of the objective function and the constraints
void
LowerBoundingSolver::_linearize_functions_at_preset_vector_linpoint(std::vector<vMC> &resultRelaxationVMC, const std::vector<std::vector<double>> &linearizationPoints, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds,
                                                                    mc::FFSubgraph &subgraph, std::vector<mc::FFVar> &functions)
{
    PROFILE_FUNCTION()

    try {
        // Use the DAG interval subgradient heuristic if specified in settings
        if (!_DAGobj->intervals_already_computed && _maingoSettings->LBP_subgradientIntervals) {
            // Set required pointers
            vMC::subHeur.originalLowerBounds = &lowerVarBounds;
            vMC::subHeur.originalUpperBounds = &upperVarBounds;
            vMC::subHeur.referencePoints     = &linearizationPoints;
            //vMC::additionalLins.set_points(&linearizationPoints, &lowerVarBounds, &upperVarBounds);
            _DAGobj->intervals_already_computed = true;
            _DAGobj->DAG.eval(subgraph, _DAGobj->vMCarray, functions.size(), functions.data(), resultRelaxationVMC.data(), _nvar, _DAGobj->vars.data(), _DAGobj->vMcPoint.data());
            // Note that we HAVE TO set the bool AFTER the first computation of relaxations
            vMC::subHeur.usePrecomputedIntervals = true;
        }
        else {
            _DAGobj->DAG.eval(subgraph, _DAGobj->vMCarray, functions.size(), functions.data(), resultRelaxationVMC.data(), _nvar, _DAGobj->vars.data(), _DAGobj->vMcPoint.data());
        }
    }
    catch (const filib::interval_io_exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException(std::string("  Error in interval extensions: ") + e.what());
    }
    catch (const MC::Exceptions &e) {
        throw MAiNGOException(std::string("  Error in evaluation of McCormick relaxations: ") + e.what());
    }
    catch (const vMC::Exceptions &e) {
        throw MAiNGOException(std::string("  Error in evaluation of vMcCormick relaxations: ") + e.what());
    }
    catch (const std::exception &e) {
        throw MAiNGOException("  Error in evaluation of relaxed model equations. ", e);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error in evaluation of relaxed model equations. ");
    }
    // GCOVR_EXCL_STOP
    if (_maingoSettings->LBP_subgradientIntervals) {
        // Reset interval iterator to enable the computation of the next linearization point with the use of precomputed intervals
        vMC::subHeur.reset_iterator();
    }
}


/////////////////////////////////////////////////////////////////////////
// function for computing linearization points with the use of an adapted version of Kelley's algorithm
LINEARIZATION_RETCODE
LowerBoundingSolver::_linearization_points_Kelley(const babBase::BabNode &currentNode)
{
    PROFILE_FUNCTION()

    // First, compute initial point as mid point
    std::vector<double> linearizationPoint(_nvar);
    std::vector<double> lowerVarBounds(currentNode.get_lower_bounds());
    std::vector<double> upperVarBounds(currentNode.get_upper_bounds());
    std::fill(_DAGobj->objRowFilled.begin() + 1, _DAGobj->objRowFilled.end(), false);

    for (unsigned int i = 0; i < _nvar; i++) {
        linearizationPoint[i] = 0.5 * (lowerVarBounds[i] + upperVarBounds[i]);
    }
    // Reset LP
    _reset_LP(linearizationPoint, lowerVarBounds, upperVarBounds);
    // Compute improved intervals and relaxations
    _linearize_functions_at_linpoint(_DAGobj->resultRelaxation, linearizationPoint, lowerVarBounds, upperVarBounds, _DAGobj->subgraph, _DAGobj->functions);
    // Insert first linearization point
    _update_whole_LP_at_linpoint(_DAGobj->resultRelaxation, linearizationPoint, lowerVarBounds, upperVarBounds, 0);

    // IloAlgorithm::Status cplexStatus;
    double oldSolutionValue = -_maingoSettings->infinity;
    double newSolutionValue = -_maingoSettings->infinity;
    for (unsigned iLin = 1; iLin < _maxnParticipatingVariables; iLin++) {
        _LPstatus = _solve_LP(currentNode);
        if (_LPstatus == LP_INFEASIBLE) {
            return LINEARIZATION_INFEASIBLE;
            break;
        }
        else if (_LPstatus != LP_OPTIMAL) {
#ifdef LP__WRITE_CHECK_FILES
            _write_LP_to_file("Kelley_not_optimal_or_infeas");
#endif
            break;
        }
        else {
            // Otherwise get the solution value
            newSolutionValue = _get_objective_value();
            double dummyEta  = 0;
            try {
                _get_solution_point(linearizationPoint, dummyEta);
                for (unsigned i = 0; i < _nvar; i++) {
                    linearizationPoint[i] = std::max(std::min(linearizationPoint[i], upperVarBounds[i]), lowerVarBounds[i]);
                }
            }
            catch (std::exception &e) {
                std::ostringstream outstr;
                outstr << "  Warning: Variables at solution of auxiliary LP in Kelley's algorithm could be not obtained by LP solver:" << e.what() << std::endl;
                _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                // Return empty solution instead
                break;
            }
            // We want at least 1% improvement
            if ((newSolutionValue - oldSolutionValue) < 0.01 * std::fabs(newSolutionValue) || (newSolutionValue - oldSolutionValue) < _maingoSettings->epsilonA * 1e1) {
                // In this case, the LBP is already solved within the linearization method
                return LINEARIZATION_OPTIMAL;
            }

            _linearize_functions_at_linpoint(_DAGobj->resultRelaxation, linearizationPoint, lowerVarBounds, upperVarBounds, _DAGobj->subgraph, _DAGobj->functions);
            _update_whole_LP_at_linpoint(_DAGobj->resultRelaxation, linearizationPoint, lowerVarBounds, upperVarBounds, iLin);
            oldSolutionValue            = newSolutionValue;
            _DAGobj->objRowFilled[iLin] = true;
        }
    }
    // If this point is reached, the final LP was not solved, since one additional row was added so it has to be solved in solve_LBP/solve_OBBT
    return LINEARIZATION_UNKNOWN;
}


/////////////////////////////////////////////////////////////////////////
// function for resetting the whole LP, meaning it sets all rhs to 1e19 and coefficients to 0. Eta coefficients are -1
void
LowerBoundingSolver::_reset_LP(const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds)
{

    // Objective
    for (size_t i = 0; i < _constraintProperties->size(); i++) {
        unsigned index = (*_constraintProperties)[i].indexTypeNonconstant;
        switch ((*_constraintProperties)[i].type) {
            case OBJ:
                for (unsigned iLin = 0; iLin < _nLinObj[index]; iLin++) {
                    _update_LP_obj(_DAGobj->infinityMC, linearizationPoint, lowerVarBounds, upperVarBounds, iLin, index);
                }
                break;
            case INEQ:
                for (unsigned iLin = 0; iLin < _nLinIneq[index]; iLin++) {
                    _update_LP_ineq(_DAGobj->infinityMC, linearizationPoint, lowerVarBounds, upperVarBounds, iLin, index);
                }
                break;
            case EQ:
                for (unsigned iLin = 0; iLin < _nLinEq[index]; iLin++) {
                    _update_LP_eq(_DAGobj->infinityMC, _DAGobj->infinityMC, linearizationPoint, lowerVarBounds, upperVarBounds, iLin, index);
                }
                break;
            case INEQ_REL_ONLY:
                for (unsigned iLin = 0; iLin < _nLinIneqRelaxationOnly[index]; iLin++) {
                    _update_LP_ineqRelaxationOnly(_DAGobj->infinityMC, linearizationPoint, lowerVarBounds, upperVarBounds, iLin, index);
                }
                break;
            case EQ_REL_ONLY:
            case AUX_EQ_REL_ONLY:
                for (unsigned iLin = 0; iLin < _nLinEqRelaxationOnly[index]; iLin++) {
                    _update_LP_eqRelaxationOnly(_DAGobj->infinityMC, _DAGobj->infinityMC, linearizationPoint, lowerVarBounds, upperVarBounds, iLin, index);
                }
                break;
            case INEQ_SQUASH:
                for (unsigned iLin = 0; iLin < _nLinIneqSquash[index]; iLin++) {
                    _update_LP_ineq_squash(_DAGobj->infinityMC, linearizationPoint, lowerVarBounds, upperVarBounds, iLin, index);
                }
                break;
            default:
                break;
        }
    }
}


/////////////////////////////////////////////////////////////////////////
// compute dim+1 simplex on [-1,1] with vertices lying on the dim-dimensional ball with radius sphereRadius and rotate this simplex by angleIn then also add mid point
void
LowerBoundingSolver::_compute_and_rotate_simplex(const unsigned int dim, const double angleIn, const double sphereRadius, std::vector<std::vector<double>> &simplexPoints)
{
    // Points are written row-wise meaning simplexPoints[0] is first coordinate, simplexPoints[1] is second etc.
    simplexPoints.resize(dim);
    for (unsigned int i = 0; i < simplexPoints.size(); i++) {
        simplexPoints[i] = std::vector<double>(dim + 2, 0);
        // First point is always midpoint of [-1,1]
        simplexPoints[i][0] = 0.0;
    }

    // For 1D problems, we use 3 points
    if (dim == 1) {
        simplexPoints[0][1] = 0.66;
        simplexPoints[0][2] = -0.66;
    }
    else {
        // Fill first row
        simplexPoints[0][1] = sphereRadius;
        for (unsigned int i = 2; i < simplexPoints[0].size(); i++) {
            simplexPoints[0][i] = -sphereRadius / dim;
        }
        // Fill all other rows
        for (unsigned int i = 1; i < simplexPoints.size(); i++) {
            // Fill column entry
            double val = 0;
            for (unsigned int j = 0; j < i; j++) {
                val += std::pow(simplexPoints[j][i + 1], 2);
            }
            simplexPoints[i][i + 1] = std::sqrt(std::pow(sphereRadius, 2) - val);
            // Fill row
            for (unsigned int j = i + 2; j < simplexPoints[i].size(); j++) {
                simplexPoints[i][j] = -simplexPoints[i][i + 1] / (dim - i);
            }
        }
    }

    // Compute doubles once
    double angle1 = angleIn * M_PI / 180.0;
    double angle2 = (180.0 + angleIn) * M_PI / 180.0;
    double sinD1  = std::sin(angle1);
    double cosD1  = std::cos(angle1);
    double sinD2  = std::sin(angle2);
    double cosD2  = std::cos(angle2);
    std::vector<double> tmpRow1(simplexPoints[0].size() - 1, 0.0);
    std::vector<double> tmpRow2(simplexPoints[0].size() - 1, 0.0);

    unsigned int skipIndex = 0;    // Avoid doing too many rotation of the matrix, since it results in high computational times if number of variables is large
    if (dim >= 100) {
        if (dim >= 1000) {
            skipIndex = (unsigned)dim / 100 * (unsigned)dim / 1000;
        }
        else {
            skipIndex = (unsigned)dim / 100;
        }
    }

    // Rotate the Simplex by a given angle
    for (unsigned int k = 0; k < simplexPoints.size() - 1; k++) {    // We do roughly ((dimension-1)^2+(dimension-1))/4 rotations (if skipIndex is = 0)
        for (unsigned int i = k + 1; i < simplexPoints.size(); i += 1 + skipIndex) {
            for (unsigned int j = 1; j < simplexPoints[0].size(); j++) {    // We need to go through all columns
                // Save temporary results
                if (i % 2) {    // We rotate in two different directions
                    tmpRow1[j - 1] = simplexPoints[k][j] * cosD1 + simplexPoints[i][j] * sinD1;
                    tmpRow2[j - 1] = simplexPoints[k][j] * (-sinD1) + simplexPoints[i][j] * cosD1;
                }
                else {
                    tmpRow1[j - 1] = simplexPoints[k][j] * cosD2 + simplexPoints[i][j] * sinD2;
                    tmpRow2[j - 1] = simplexPoints[k][j] * (-sinD2) + simplexPoints[i][j] * cosD2;
                }
            }
            for (unsigned int j = 1; j < simplexPoints[0].size(); j++) {    // We need to go through all columns
                simplexPoints[k][j] = std::fabs(tmpRow1[j - 1]) < 1e-9 ? 0 : tmpRow1[j - 1];
                simplexPoints[i][j] = std::fabs(tmpRow2[j - 1]) < 1e-9 ? 0 : tmpRow2[j - 1];
            }
        }
    }
}


/////////////////////////////////////////////////////////////////////////
// linearizes each function of the model at precomputed points, the precomputed points are vertices of a n+1 simplex
LINEARIZATION_RETCODE
LowerBoundingSolver::_linearization_points_Simplex(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds)
{

    std::vector<double> linearizationPoint(_nvar);    // This is the reference point for the subgradient heuristic, we choose it always as mid point, it also equals the first simplexPoints entry
    for (unsigned int i = 0; i < _nvar; i++) {
        double diam           = upperVarBounds[i] - lowerVarBounds[i];
        linearizationPoint[i] = 0.5 * (lowerVarBounds[i] + upperVarBounds[i]);
        // Scale simplex points to node lower and upper bounds
        for (unsigned int j = 0; j < _DAGobj->scaledPoints[i].size(); j++) {
            _DAGobj->scaledPoints[i][j] = (_DAGobj->simplexPoints[i][_DAGobj->chosenLinPoints[j]] + 1.0) / 2.0 * diam + lowerVarBounds[i];
        }
        _DAGobj->vMcPoint[i] = vMC(I(lowerVarBounds[i], upperVarBounds[i]), _DAGobj->scaledPoints[i]);
        _DAGobj->vMcPoint[i].sub(_nvar, i);    // Set subgradient dimension
    }

    // Compute vector McCormick relaxations of nonlinear functions
    _linearize_functions_at_preset_vector_linpoint(_DAGobj->resultRelaxationVMCNonlinear, _DAGobj->scaledPoints,
                                                   lowerVarBounds, upperVarBounds, _DAGobj->subgraphNonlinear, _DAGobj->functionsNonlinear);

    // Compute McCormick relaxations of linear functions
    bool oldSetting                           = _maingoSettings->LBP_subgradientIntervals;
    _maingoSettings->LBP_subgradientIntervals = false;    // Turn it off for linear functions
    _linearize_functions_at_linpoint(_DAGobj->resultRelaxationLinear, linearizationPoint,
                                     lowerVarBounds, upperVarBounds, _DAGobj->subgraphLinear, _DAGobj->functionsLinear);
    _maingoSettings->LBP_subgradientIntervals = oldSetting;

    _update_LP_nonlinear_linear(_DAGobj->resultRelaxationVMCNonlinear, _DAGobj->resultRelaxationLinear, linearizationPoint, _DAGobj->scaledPoints, lowerVarBounds, upperVarBounds);

    return LINEARIZATION_UNKNOWN;
}


/////////////////////////////////////////////////////////////////////////
// linearizes each function of the model at precomputed points, the precomputed points are vertices of a n+1 simplex
LINEARIZATION_RETCODE
LowerBoundingSolver::_linearization_points_random(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds)
{

    std::srand(39);
    std::vector<double> linearizationPoint(_nvar);    // This is the reference point for the subgradient heuristic, we choose it always as mid point, it also equals the first simplexPoints entry
    for (unsigned int i = 0; i < _nvar; i++) {
        double diam                 = upperVarBounds[i] - lowerVarBounds[i];
        linearizationPoint[i]       = 0.5 * (lowerVarBounds[i] + upperVarBounds[i]);
        _DAGobj->scaledPoints[i][0] = linearizationPoint[i];
        // Scale simplex points to node lower and upper bounds
        for (unsigned int j = 1; j < _DAGobj->scaledPoints[i].size(); j++) {
            double tmpRand              = std::rand() / ((double)RAND_MAX + 1);
            _DAGobj->scaledPoints[i][j] = lowerVarBounds[i] + tmpRand * (upperVarBounds[i] - lowerVarBounds[i]);
            ;
        }
        _DAGobj->vMcPoint[i] = vMC(I(lowerVarBounds[i], upperVarBounds[i]), _DAGobj->scaledPoints[i]);
        _DAGobj->vMcPoint[i].sub(_nvar, i);    // Set subgradient dimension
    }

    // Compute vector McCormick relaxations of nonlinear functions
    _linearize_functions_at_preset_vector_linpoint(_DAGobj->resultRelaxationVMCNonlinear, _DAGobj->scaledPoints,
                                                   lowerVarBounds, upperVarBounds, _DAGobj->subgraphNonlinear, _DAGobj->functionsNonlinear);

    // Compute McCormick relaxations of linear functions
    bool oldSetting                           = _maingoSettings->LBP_subgradientIntervals;
    _maingoSettings->LBP_subgradientIntervals = false;    // Turn it off for linear functions
    _linearize_functions_at_linpoint(_DAGobj->resultRelaxationLinear, linearizationPoint,
                                     lowerVarBounds, upperVarBounds, _DAGobj->subgraphLinear, _DAGobj->functionsLinear);
    _maingoSettings->LBP_subgradientIntervals = oldSetting;

    _update_LP_nonlinear_linear(_DAGobj->resultRelaxationVMCNonlinear, _DAGobj->resultRelaxationLinear, linearizationPoint, _DAGobj->scaledPoints, lowerVarBounds, upperVarBounds);

    return LINEARIZATION_UNKNOWN;
}


/////////////////////////////////////////////////////////////////////////
// function for computing linearization points with the use of an adapted version of Kelley's algorithm
LINEARIZATION_RETCODE
LowerBoundingSolver::_linearization_points_Kelley_Simplex(const babBase::BabNode &currentNode)
{

    // First, compute initial point as mid point
    std::vector<double> linearizationPoint(_nvar);
    std::vector<double> lowerVarBounds(currentNode.get_lower_bounds());
    std::vector<double> upperVarBounds(currentNode.get_upper_bounds());
    if ((*_constraintProperties)[0].dependency > LINEAR) {
        std::fill(_DAGobj->objRowFilled.begin() + _DAGobj->chosenLinPoints.size(), _DAGobj->objRowFilled.end(), false);
    }

    for (unsigned int i = 0; i < _nvar; i++) {
        linearizationPoint[i] = 0.5 * (lowerVarBounds[i] + upperVarBounds[i]);
    }
    // Reset LP
    _reset_LP(linearizationPoint, lowerVarBounds, upperVarBounds);
    // Compute improved intervals and relaxations
    bool oldSetting              = MC::options.SUB_INT_HEUR_USE;
    MC::options.SUB_INT_HEUR_USE = false;    // Has to be turned off for Simplex
    _differentNumberOfLins       = true;

    _linearization_points_Simplex(lowerVarBounds, upperVarBounds);

    MC::options.SUB_INT_HEUR_USE        = oldSetting;
    MC::subHeur.intervals               = vMC::subHeur.intervals;
    _DAGobj->intervals_already_computed = true;
    MC::subHeur.usePrecomputedIntervals = true;
    MC::subHeur.reset_iterator();
    // IloAlgorithm::Status cplexStatus;
    double oldSolutionValue = -_maingoSettings->infinity;
    double newSolutionValue = -_maingoSettings->infinity;
    for (unsigned iLin = 0; iLin < 3; iLin++) {    // At most 3 additional points
        _solve_LP(currentNode);

        _LPstatus = _get_LP_status();
        if (_LPstatus == LP_INFEASIBLE) {
            return LINEARIZATION_INFEASIBLE;
            break;
        }
        else if (_LPstatus != LP_OPTIMAL) {
#ifdef LP__WRITE_CHECK_FILES
            _write_LP_to_file("Kelley_Simplex_not_optimal_or_infeas");
#endif
            break;
        }
        else {
            // Otherwise get the solution value
            newSolutionValue = _get_objective_value();
            double dummyEta  = 0;
            try {
                _get_solution_point(linearizationPoint, dummyEta);
                for (unsigned i = 0; i < _nvar; i++) {
                    linearizationPoint[i] = std::max(std::min(linearizationPoint[i], upperVarBounds[i]), lowerVarBounds[i]);
                }
            }
            catch (std::exception &e) {
                std::ostringstream outstr;
                outstr << "  Warning: Variables at solution of auxiliary LP in Kelley's algorithm (with Simplex starting points) could be not obtained by LP solver:" << e.what() << std::endl;
                _logger->print_message(outstr.str(), VERB_NORMAL, LBP_VERBOSITY);
                // Return empty solution instead
                break;
            }
            // We want at least 1% improvement
            if ((newSolutionValue - oldSolutionValue) < 0.01 * std::fabs(newSolutionValue) || (newSolutionValue - oldSolutionValue) < _maingoSettings->epsilonA * 1e1) {
                // In this case, the LBP is already solved within the linearization method
                return LINEARIZATION_OPTIMAL;
            }

            _linearize_functions_at_linpoint(_DAGobj->resultRelaxationNonlinear, linearizationPoint, lowerVarBounds, upperVarBounds, _DAGobj->subgraphNonlinear, _DAGobj->functionsNonlinear);
            _update_LP_nonlinear(_DAGobj->resultRelaxationNonlinear, linearizationPoint, lowerVarBounds, upperVarBounds, iLin + _DAGobj->chosenLinPoints.size());
            oldSolutionValue = newSolutionValue;
            if ((*_constraintProperties)[0].dependency > LINEAR) {
                _DAGobj->objRowFilled[iLin + _DAGobj->chosenLinPoints.size()] = true;
            }
        }
    }
    // If this point is reached, the final LP was not solved, since one additional row was added so it has to be solved in solve_LBP/solve_OBBT
    return LINEARIZATION_UNKNOWN;
}


/////////////////////////////////////////////////////////////////////////
// updates the underlying LP with the separation of nonlinear and linear functions
void
LowerBoundingSolver::_update_LP_nonlinear_linear(const std::vector<vMC> &resultRelaxationVMCNonlinear, const std::vector<MC> &resultRelaxationLinear,
                                                 const std::vector<double> &linearizationPoint, const std::vector<std::vector<double>> &scaledPoints,
                                                 const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds)
{

    for (size_t i = 0; i < _constraintProperties->size(); i++) {
        unsigned indexType = (*_constraintProperties)[i].indexTypeNonconstant;
        switch ((*_constraintProperties)[i].dependency) {
            case LINEAR: {
                unsigned indexLinear = (*_constraintProperties)[i].indexLinear;
                switch ((*_constraintProperties)[i].type) {
                    case OBJ:
                        _update_LP_obj(resultRelaxationLinear[indexLinear], linearizationPoint, lowerVarBounds, upperVarBounds, 0, indexType);
                        _DAGobj->validIntervalLowerBound = resultRelaxationLinear[indexLinear].l();
                        break;
                    case INEQ:
                        _update_LP_ineq(resultRelaxationLinear[indexLinear], linearizationPoint, lowerVarBounds, upperVarBounds, 0, indexType);
                        break;
                    case EQ:
                        _update_LP_eq(resultRelaxationLinear[indexLinear], resultRelaxationLinear[indexLinear], linearizationPoint, lowerVarBounds, upperVarBounds, 0, indexType);
                        break;
                    case INEQ_REL_ONLY:
                        _update_LP_ineqRelaxationOnly(resultRelaxationLinear[indexLinear], linearizationPoint, lowerVarBounds, upperVarBounds, 0, indexType);
                        break;
                    case EQ_REL_ONLY:
                    case AUX_EQ_REL_ONLY:
                        _update_LP_eqRelaxationOnly(resultRelaxationLinear[indexLinear], resultRelaxationLinear[indexLinear],
                                                    linearizationPoint, lowerVarBounds, upperVarBounds, 0, indexType);
                        break;
                    case INEQ_SQUASH:
                        _update_LP_ineq_squash(resultRelaxationLinear[indexLinear], linearizationPoint, lowerVarBounds, upperVarBounds, 0, indexType);
                        break;
                    default:
                        break;
                }
                break;
            }
            case BILINEAR:
            case QUADRATIC:
            case POLYNOMIAL:
            case RATIONAL:
            case NONLINEAR: {
                unsigned indexNonlinear = (*_constraintProperties)[i].indexNonlinear;
                switch ((*_constraintProperties)[i].type) {
                    case OBJ:
                        _update_LP_obj(resultRelaxationVMCNonlinear[indexNonlinear], scaledPoints, lowerVarBounds, upperVarBounds, indexType);
                        _DAGobj->validIntervalLowerBound = resultRelaxationVMCNonlinear[indexNonlinear].l();
                        break;
                    case INEQ:
                        _update_LP_ineq(resultRelaxationVMCNonlinear[indexNonlinear], scaledPoints, lowerVarBounds, upperVarBounds, indexType);
                        break;
                    case EQ:
                        _update_LP_eq(resultRelaxationVMCNonlinear[indexNonlinear], resultRelaxationVMCNonlinear[indexNonlinear], scaledPoints,
                                      lowerVarBounds, upperVarBounds, indexType);
                        break;
                    case INEQ_REL_ONLY:
                        _update_LP_ineqRelaxationOnly(resultRelaxationVMCNonlinear[indexNonlinear], scaledPoints, lowerVarBounds, upperVarBounds, indexType);
                        break;
                    case EQ_REL_ONLY:
                    case AUX_EQ_REL_ONLY:
                        _update_LP_eqRelaxationOnly(resultRelaxationVMCNonlinear[indexNonlinear], resultRelaxationVMCNonlinear[indexNonlinear],
                                                    scaledPoints, lowerVarBounds, upperVarBounds, indexType);
                        break;
                    case INEQ_SQUASH:
                        _update_LP_ineq_squash(resultRelaxationVMCNonlinear[indexNonlinear], scaledPoints, lowerVarBounds, upperVarBounds, indexType);
                        break;
                    default:
                        break;
                }
                break;
            }
            default:
                break;
        }    // End of switch( dependency )
    }
}

/////////////////////////////////////////////////////////////////////////
// updates the underlying LP
void
LowerBoundingSolver::_update_LP_nonlinear(const std::vector<MC> &resultRelaxationNonlinear,
                                          const std::vector<double> &linearizationPoint, const std::vector<double> &lowerVarBounds,
                                          const std::vector<double> &upperVarBounds, const unsigned iLin)
{

    for (size_t i = 0; i < _constraintProperties->size(); i++) {
        unsigned indexType = (*_constraintProperties)[i].indexTypeNonconstant;
        switch ((*_constraintProperties)[i].dependency) {
            case LINEAR: {
                break;
            }
            case BILINEAR:
            case QUADRATIC:
            case POLYNOMIAL:
            case RATIONAL:
            case NONLINEAR: {
                unsigned indexNonlinear = (*_constraintProperties)[i].indexNonlinear;
                switch ((*_constraintProperties)[i].type) {
                    case OBJ:
                        _update_LP_obj(resultRelaxationNonlinear[indexNonlinear], linearizationPoint, lowerVarBounds, upperVarBounds, iLin, indexType);
                        break;
                    case INEQ:
                        _update_LP_ineq(resultRelaxationNonlinear[indexNonlinear], linearizationPoint, lowerVarBounds, upperVarBounds, iLin, indexType);
                        break;
                    case EQ:
                        _update_LP_eq(resultRelaxationNonlinear[indexNonlinear], resultRelaxationNonlinear[indexNonlinear], linearizationPoint,
                                      lowerVarBounds, upperVarBounds, iLin, indexType);
                        break;
                    case INEQ_REL_ONLY:
                        _update_LP_ineqRelaxationOnly(resultRelaxationNonlinear[indexNonlinear], linearizationPoint, lowerVarBounds, upperVarBounds, iLin, indexType);
                        break;
                    case EQ_REL_ONLY:
                    case AUX_EQ_REL_ONLY:
                        _update_LP_eqRelaxationOnly(resultRelaxationNonlinear[indexNonlinear], resultRelaxationNonlinear[indexNonlinear],
                                                    linearizationPoint, lowerVarBounds, upperVarBounds, iLin, indexType);
                        break;
                    case INEQ_SQUASH:
                        _update_LP_ineq_squash(resultRelaxationNonlinear[indexNonlinear], linearizationPoint, lowerVarBounds, upperVarBounds, iLin, indexType);
                        break;
                    default:
                        break;
                }
                break;
            }
            default:
                break;
        }    // End of switch( dependency )
    }
}

/////////////////////////////////////////////////////////////////////////
// Heuristical determination of good linearization points
void
LowerBoundingSolver::_choose_good_lin_points(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, bool firstTime)
{


    if (_maingoSettings->LBP_subgradientIntervals) {
        unsigned npts = _nvar + 2;
        vMC::subHeur.resize_vectors(npts);    // Resize the underlying vector for subgradient heuristic
        // vMC::additionalLins.initialize(npts, _nvar, /*midIndex*/ 0, _DAGobj->subgraphNonlinear.l_op.size());
        for (unsigned int i = 0; i < _nvar; i++) {
            _DAGobj->scaledPoints[i] = std::vector<double>(npts, 0.0);
            // _DAGobj->scaledPoints[i] = std::vector<double> (_nvar+2,0.0);
        }

        std::vector<double> linearizationPoint(_nvar);    // This is the reference point for the subgradient heuristic, we choose it always as mid point, it also equals the first simplexPoints entry
        for (unsigned int i = 0; i < _nvar; i++) {
            double diam           = upperVarBounds[i] - lowerVarBounds[i];
            linearizationPoint[i] = 0.5 * (lowerVarBounds[i] + upperVarBounds[i]);
            // Scale simplex points to node lower and upper bounds
            for (unsigned int j = 0; j < npts; j++) {
                _DAGobj->scaledPoints[i][j] = (_DAGobj->simplexPoints[i][j] + 1.0) / 2.0 * diam + lowerVarBounds[i];
            }
            _DAGobj->vMcPoint[i] = vMC(I(lowerVarBounds[i], upperVarBounds[i]), _DAGobj->scaledPoints[i]);
            _DAGobj->vMcPoint[i].sub(_nvar, i);    // Set subgradient dimension
        }

        vMC::options.COMPUTE_POINT_RANKING = true;
        if (!firstTime) {
            vMC::subHeur.clear();
            _DAGobj->intervals_already_computed  = false;
            vMC::subHeur.usePrecomputedIntervals = false;
        }
        // Compute vector McCormick relaxations of nonlinear functions
        _linearize_functions_at_preset_vector_linpoint(_DAGobj->resultRelaxationVMCNonlinear, _DAGobj->scaledPoints,
                                                       lowerVarBounds, upperVarBounds, _DAGobj->subgraphNonlinear, _DAGobj->functionsNonlinear);


        unsigned maxNumberLins = _maxnParticipatingVariables;

        _DAGobj->chosenLinPoints.clear();
        _DAGobj->chosenLinPoints.push_back(0);    // We always take the midpoint
        std::vector<unsigned> usedPoints = {0};

        unsigned int defaultIndex = 1;    // used in cases where all points are equally good/bad
        for (unsigned int i = 1; i < maxNumberLins; i++) {
            double maxScore        = 0;
            unsigned maxScoreIndex = defaultIndex;
            for (size_t j = 0; j < vMC::subHeur.subHeurRanking.size(); j++) {
                if (maxScore < vMC::subHeur.subHeurRanking[j]) {
                    bool used = false;
                    for (size_t k = 0; k < usedPoints.size(); k++) {
                        if (usedPoints[k] == j) {
                            used = true;
                            break;
                        }
                    }
                    if (!used) {
                        maxScore      = vMC::subHeur.subHeurRanking[j];
                        maxScoreIndex = j;
                    }
                }
            }
            _DAGobj->chosenLinPoints.push_back(maxScoreIndex);
            usedPoints.push_back(maxScoreIndex);
            defaultIndex++;
        }
        vMC::options.COMPUTE_POINT_RANKING = false;
    }
    else {
        // Default version
        _DAGobj->chosenLinPoints.clear();
        unsigned numberLins = std::ceil((_maxnParticipatingVariables + 2) / 2.0);
        unsigned n          = std::floor((_nvar + 2.0) / (double)numberLins);
        for (unsigned int i = 0; i < numberLins; i++) {
            _DAGobj->chosenLinPoints.push_back(n * i);    // This is every n-th point from scaledPoints, we always take 0, since it is the mid point
        }
    }
}