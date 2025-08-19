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

#include "ubpNLopt.h"
#include "MAiNGOException.h"
#include "ubpEvaluators.h"


using namespace maingo;
using namespace ubp;


/////////////////////////////////////////////////////////////////////////
// constructor for the upper bounding solver
UbpNLopt::UbpNLopt(mc::FFGraph& DAG, const std::vector<mc::FFVar>& DAGvars, const std::vector<mc::FFVar>& DAGfunctions, const std::vector<babBase::OptimizationVariable>& variables,
                   const unsigned nineqIn, const unsigned neqIn, const unsigned nineqSquashIn, std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn, UBS_USE useIn):
    UpperBoundingSolver(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn)
{

    try {

        // Determine desired solver
        UBP_SOLVER desiredSolver;
        switch (useIn) {
            case USE_PRE:
                desiredSolver = settingsIn->UBP_solverPreprocessing;
                break;
            case USE_BAB:
                desiredSolver = settingsIn->UBP_solverBab;
                break;
            default: // GCOVR_EXCL_START
                throw MAiNGOException("  Unknown USAGE setting " + std::to_string(_intendedUse));
        } // GCOVR_EXCL_STOP

        // Initialize solver (where necessary)
        switch (desiredSolver) {
            case ubp::UBP_SOLVER_COBYLA: {
                _NLopt       = nlopt::opt(nlopt::LN_COBYLA, _nvar);    // Initialize NLOPT with solver COBYLA (only derivative-free solver that can handle equalities); set # opt vars
                _NLoptSubopt = nlopt::opt(nlopt::LN_BOBYQA, _nvar);    // Dummy, not being used! DON'T REMOVE THIS!
                break;
            }
            case ubp::UBP_SOLVER_SLSQP: {
                _NLopt       = nlopt::opt(nlopt::LD_SLSQP, _nvar);     // Initialize NLOPT with solver SLSQP (only gradient-based solver that can handle equalities); set # opt vars
                _NLoptSubopt = nlopt::opt(nlopt::LN_BOBYQA, _nvar);    // Dummy, not being used! DON'T REMOVE THIS!
                break;
            }
            case ubp::UBP_SOLVER_LBFGS: {
                _NLopt       = nlopt::opt(nlopt::AUGLAG, _nvar);      // Initialize NLOPT with AUGmented LAGrangian solver (--> converts constrained to unconstrained problem)
                _NLoptSubopt = nlopt::opt(nlopt::LD_LBFGS, _nvar);    // Set unconstrained subsolver to low-storage BFGS
                _NLopt.set_local_optimizer(_NLoptSubopt);
                break;
            }
            case ubp::UBP_SOLVER_BOBYQA: {
                _NLopt       = nlopt::opt(nlopt::AUGLAG, _nvar);       // Initialize NLOPT with AUGmented LAGrangian solver (--> converts constrained to unconstrained problem)
                _NLoptSubopt = nlopt::opt(nlopt::LN_BOBYQA, _nvar);    // Set unconstrained subsolver to BOBYQA
                _NLopt.set_local_optimizer(_NLoptSubopt);
                break;
            }
            default: { // GCOVR_EXCL_START
                throw MAiNGOException("  Unknown upper bounding solver selected for usage " + std::to_string(_intendedUse) + ": " + std::to_string(desiredSolver));
            }
        } // GCOVR_EXCL_STOP

        // Objective
        _NLopt.set_min_objective(_NLopt_get_objective, this);    // Giving pointer to current object as data since it is needed to get access to the DAG (otherwise, DAG would need to be static)

        // Inequalities
        std::vector<double> ineqTols(_nineq + _nineqSquash, _maingoSettings->deltaIneq);
        _NLopt.add_inequality_mconstraint(_NLopt_get_ineq, this, ineqTols);    // Giving pointer to current object as data since it is needed to get access to the DAG (otherwise, DAG would need to be static)

        // Equalities
        if (_neq > _nvar) {
            throw MAiNGOException("  Error iniailizing NLopt: NLopt does not support problems containing more equality constraints than variables."); // GCOVR_EXCL_LINE
        }
        std::vector<double> eqTols(_neq, _maingoSettings->deltaEq);
        _NLopt.add_equality_mconstraint(_NLopt_get_eq, this, eqTols);    // Giving pointer to current object as data since it is needed to get access to the DAG (otherwise, DAG would need to be static)

        // Variables bounds
        _NLopt.set_lower_bounds(_originalLowerBounds);
        _NLopt.set_upper_bounds(_originalUpperBounds);

        // Termination criteria
        _NLopt.set_ftol_abs(_maingoSettings->epsilonA);
        _NLopt.set_ftol_rel(_maingoSettings->epsilonR);
        _NLoptSubopt.set_ftol_abs(_maingoSettings->epsilonA);
        _NLoptSubopt.set_ftol_rel(_maingoSettings->epsilonR);

        switch (_intendedUse) {
            case USE_BAB:
                _NLopt.set_maxeval(_maingoSettings->UBP_maxStepsBab);
                _NLopt.set_maxtime(_maingoSettings->UBP_maxTimeBab);
                _NLoptSubopt.set_maxeval(_maingoSettings->UBP_maxStepsBab);
                _NLoptSubopt.set_maxtime(_maingoSettings->UBP_maxTimeBab);
                break;
            case USE_PRE:
                _NLopt.set_maxeval(_maingoSettings->UBP_maxStepsPreprocessing);
                _NLopt.set_maxtime(_maingoSettings->UBP_maxTimePreprocessing);
                _NLoptSubopt.set_maxeval(_maingoSettings->UBP_maxStepsPreprocessing);
                _NLoptSubopt.set_maxtime(_maingoSettings->UBP_maxTimePreprocessing);
                break;
            default: { // GCOVR_EXCL_START
                throw MAiNGOException("  Unknown USAGE setting " + std::to_string(_intendedUse));
            }
        } // GCOVR_EXCL_STOP
    }
    catch (const std::exception& e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error initializing NLopt.", e);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error initializing NLopt.");
    }
} // GCOVR_EXCL_STOP


/////////////////////////////////////////////////////////////////////////
// solve upper bounding problem
SUBSOLVER_RETCODE
UbpNLopt::_solve_nlp(const std::vector<double>& lowerVarBounds, const std::vector<double>& upperVarBounds, double& objectiveValue, std::vector<double>& solutionPoint)
{

    // Set bounds and solve
    try {
        _NLopt.set_lower_bounds(lowerVarBounds);
        _NLopt.set_upper_bounds(upperVarBounds);
        double tmpobjectiveValue;
        nlopt::result solveStatus = _NLopt.optimize(solutionPoint, tmpobjectiveValue);
        if (_maingoSettings->UBP_verbosity >= VERB_ALL) {
            std::ostringstream outstr;
            outstr << "  Status of local optimization: " << solveStatus << std::endl;
            _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);
        }
    }
    catch (const std::exception& e) {
        if (_maingoSettings->UBP_verbosity >= VERB_ALL) {
            std::ostringstream outstr;
            outstr << "  Warning: Local optimization using NLOPT failed. Continuing without a feasible point (unless last point happens to be feasible)." << std::endl;
            outstr << "           Reason: " << e.what() << std::endl;
            _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);
        }
        if (solutionPoint.size() != _nvar) {
            return SUBSOLVER_INFEASIBLE;
        }
    }
    catch (...) {
        if (_maingoSettings->UBP_verbosity >= VERB_ALL) {
            std::ostringstream outstr;
            outstr << "  Warning: Local optimization using NLOPT failed. Continuing without a feasible point (unless last point happens to be feasible)." << std::endl;
            _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);
        }
        if (solutionPoint.size() != _nvar) {
            return SUBSOLVER_INFEASIBLE;
        }
    }

    // Check if point returned by local solver is actually feasible. If it is, the objective function value will be stored as well.
    return check_feasibility(solutionPoint, objectiveValue);
}


/////////////////////////////////////////////////////////////////////////
// wrapper for NLopt objective function
double
UbpNLopt::_NLopt_get_objective(const std::vector<double>& x, std::vector<double>& grad, void* f_data)
{
    UbpNLopt* given_this = (reinterpret_cast<UbpNLopt*>(f_data));
    if (grad.empty()) {    // Derivative-free solver
        return ubp::evaluate_objective(x.data(), x.size(), false, grad.data(), given_this->_DAGobj);
    }
    else {    // Gradient-based solver
        return ubp::evaluate_objective(x.data(), x.size(), true, grad.data(), given_this->_DAGobj);
    }
}


/////////////////////////////////////////////////////////////////////////
// wrapper for NLopt inequality constraints
void
UbpNLopt::_NLopt_get_ineq(unsigned m, double* result, unsigned n, const double* x, double* grad, void* f_data)
{
    UbpNLopt* given_this = (reinterpret_cast<UbpNLopt*>(f_data));
    if (!grad) {    // Derivative-free solver
        ubp::evaluate_inequalities(x, n, m, false, result, grad, given_this->_DAGobj);
    }
    else {    // Gradient-based solver
        ubp::evaluate_inequalities(x, n, m, true, result, grad, given_this->_DAGobj);
    }
}


/////////////////////////////////////////////////////////////////////////
// wrapper for NLopt equality constraints
void
UbpNLopt::_NLopt_get_eq(unsigned m, double* result, unsigned n, const double* x, double* grad, void* f_data)
{
    UbpNLopt* given_this = (reinterpret_cast<UbpNLopt*>(f_data));
    if (!grad) {    // Derivative-free solver
        ubp::evaluate_equalities(x, n, m, false, result, grad, given_this->_DAGobj);
    }
    else {    // Gradient-based solver
        ubp::evaluate_equalities(x, n, m, true, result, grad, given_this->_DAGobj);
    }
}