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

#include "ubpClp.h"
#include "MAiNGOException.h"
#include "ubpDagObj.h"
#include "ubpLazyQuadExpr.h"
#include "ubpQuadExpr.h"
#include <limits>


using namespace maingo;
using namespace ubp;


/////////////////////////////////////////////////////////////////////////
// constructor for the upper bounding solver
UbpClp::UbpClp(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions, const std::vector<babBase::OptimizationVariable> &variables,
               const unsigned nineqIn, const unsigned neqIn, const unsigned nineqSquashIn, std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn, UBS_USE useIn):
    UpperBoundingSolver(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn)
{
    try {
        // Suppress output
        if ((_maingoSettings->LBP_verbosity <= VERB_NORMAL) || (_maingoSettings->loggingDestination == LOGGING_NONE) || (_maingoSettings->loggingDestination == LOGGING_FILE)) {
            _clp.messageHandler()->setLogLevel(0);
        }
        _clp.setPrimalTolerance(_maingoSettings->deltaEq);
        _clp.setDualTolerance(_maingoSettings->epsilonA);
        _clp.setRandomSeed(42);    // Make the behavior of CLP deterministic
    }
    catch (const std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error initializing UbpClp", e);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error initializing UbpClp.");
    }
} // GCOVR_EXCL_STOP

/////////////////////////////////////////////////////////////////////////
// solve the underlying problem
SUBSOLVER_RETCODE
UbpClp::_solve_nlp(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, double &objectiveValue, std::vector<double> &solutionPoint)
{

    try {
        // First evaluate DAG in UbpQuadExpr arithmetic to obtain the coefficients of the LP
        std::vector<UbpQuadExpr> coefficients(_nvar);
        for (unsigned i = 0; i < _nvar; i++) {
            coefficients[i] = UbpQuadExpr(_nvar, i);
        }
        std::vector<UbpQuadExpr> resultCoefficients(_DAGobj->functions.size());
        std::vector<UbpQuadExpr> dummyCoefficients(_DAGobj->subgraph.l_op.size());
        _DAGobj->DAG.eval(_DAGobj->subgraph, dummyCoefficients, _DAGobj->functions.size(), _DAGobj->functions.data(), resultCoefficients.data(), _nvar, _DAGobj->vars.data(), coefficients.data());

        // Get number of constraints by going through the model
        _numrows = 0;
        for (size_t i = 0; i < _constraintProperties->size(); i++) {
            switch ((*_constraintProperties)[i].type) {
                case OBJ:
                    // The objective is handled in a separate object, not a regular row
                    break;
                case INEQ:
                    _numrows += 1;
                    break;
                case EQ:
                    _numrows += 1;
                    break;
                case INEQ_SQUASH:
                    _numrows += 1;
                    break;
                case INEQ_REL_ONLY:
                case EQ_REL_ONLY:
                case AUX_EQ_REL_ONLY:
                default:
                    break;    // We don't use relaxation only constraint in upper bounding
            }
        }

        // Initialize lower and upper row bounds
        _lowerRowBounds = std::vector<double>(_numrows, -std::numeric_limits<double>::max());
        _upperRowBounds = std::vector<double>(_numrows, 0.);

        // Initialize lower and upper bounds on variables
        _lowerVarBounds.resize(_nvar);
        _upperVarBounds.resize(_nvar);
        for (unsigned i = 0; i < _nvar; i++) {
            _lowerVarBounds[i] = _originalVariables[i].get_lower_bound();
            _upperVarBounds[i] = _originalVariables[i].get_upper_bound();
        }

        // coefficients in objective function
        _objectiveCoeffs   = std::vector<double>(_nvar, 0.);
        _objectiveConstant = 0;

        // auxiliary structure needed to input LP in sparse matrix format
        // note that the assignMatrix method of ConPackedMatrix deletes all arrays we must not delete them ourselves...!!
        int *start               = new int[_nvar + 1];
        int *index               = new int[_numrows * _nvar];
        double *constraintCoeffs = new double[_numrows * _nvar];
        int *dummy               = NULL;
        for (unsigned i = 0; i < _numrows * _nvar; i++) {
            constraintCoeffs[i] = 0;
        }

        // Add coefficients and right-hand sides to the model
        size_t irow = 0;
        for (size_t i = 0; i < _constraintProperties->size(); i++) {
            const size_t index       = (*_constraintProperties)[i].indexNonconstantUBP;
            QuadExpr evaluatedResult = resultCoefficients[index].assemble_quadratic_expression_matrix_wise(_nvar);
            switch ((*_constraintProperties)[i].type) {
                case OBJ:
                    _objectiveConstant = evaluatedResult.linearPart.constant();
                    for (size_t k = 0; k < _nvar; k++) {
                        _objectiveCoeffs[k] = evaluatedResult.linearPart.get_value(k);
                    }
                    break;
                case INEQ:
                    _upperRowBounds[irow] = -evaluatedResult.linearPart.constant();
                    for (size_t k = 0; k < _nvar; k++) {
                        constraintCoeffs[k * _numrows + irow] = evaluatedResult.linearPart.get_value(k);
                    }
                    irow++;
                    break;
                case EQ:
                    _lowerRowBounds[irow] = -evaluatedResult.linearPart.constant();
                    _upperRowBounds[irow] = -evaluatedResult.linearPart.constant();
                    for (size_t k = 0; k < _nvar; k++) {
                        constraintCoeffs[k * _numrows + irow] = evaluatedResult.linearPart.get_value(k);
                    }
                    irow++;
                    break;
                case INEQ_SQUASH:
                    _upperRowBounds[irow] = -evaluatedResult.linearPart.constant();
                    for (size_t k = 0; k < _nvar; k++) {
                        constraintCoeffs[k * _numrows + irow] = evaluatedResult.linearPart.get_value(k);
                    }
                    irow++;
                    break;
                case INEQ_REL_ONLY:
                case EQ_REL_ONLY:
                case AUX_EQ_REL_ONLY:
                default:
                    break;    // We don't use relaxation only constraint in upper bounding
            }
        }

        // Sparse matrix - column major - format
        size_t count = 0;
        for (size_t i = 0; i < _nvar; i++) {
            for (size_t j = 0; j < _numrows; j++) {
                index[count] = j;
                count++;
            }
        }
        for (size_t i = 0; i <= _nvar; i++) {
            start[i] = i * _numrows;
        }

        // Initialize CLP objects
        _matrix.assignMatrix(true, _numrows, _nvar, _nvar * _numrows, constraintCoeffs, index, start, dummy);
        _clp.loadProblem(_matrix, _lowerVarBounds.data(), _upperVarBounds.data(), _objectiveCoeffs.data(), _lowerRowBounds.data(), _upperRowBounds.data());

        // Set direction to minimize (also default)
        _clp.setOptimizationDirection(1);

        // Solve problem using dual simplex
        _clp.dual();
    }
    catch (std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error while solving the UBP with CLP.", e);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error while solving UBP with CLP.");
    }
    // GCOVR_EXCL_STOP
    // Get CLP status
    const int clpStatus = _clp.status();
    if ((clpStatus == 1) || (clpStatus == 2)) {
        return SUBSOLVER_INFEASIBLE;
    }
    if (_maingoSettings->LBP_verbosity >= VERB_ALL) {
        std::ostringstream outstr;
        outstr << "  UBP status: " << clpStatus << std::endl;
        _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);
    }

    // Get objective value
    objectiveValue = _clp.objectiveValue() + _objectiveConstant;

    // Process solution: solution point
    double *columnPrimal;
    try {
        columnPrimal = _clp.primalColumnSolution();
    }
    catch (std::exception &e) {
        std::ostringstream outstr;
        outstr << "  Warning: Variables at solution of UBP could not be extracted from CLP:" << e.what() << std::endl;
        _logger->print_message(outstr.str(), VERB_NORMAL, UBP_VERBOSITY);
        // Return empty solution instead
        solutionPoint.clear();
        return SUBSOLVER_FEASIBLE;
    }
    // Ok, successfully obtained solution point
    solutionPoint.clear();
    for (unsigned int i = 0; i < _nvar; i++) {
        solutionPoint.push_back(columnPrimal[i]);
    }
    std::ostringstream outstr;
    outstr << "  UBP solution point: " << std::endl;
    for (unsigned int i = 0; i < _nvar; i++) {
        outstr << "   x(" << i << "): " << solutionPoint[i] << std::endl;
    }
    _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);

    return SUBSOLVER_FEASIBLE;
}