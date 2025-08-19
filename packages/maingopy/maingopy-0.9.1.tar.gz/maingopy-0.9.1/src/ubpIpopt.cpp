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


#include "ubpIpopt.h"
#include "MAiNGOException.h"

#include <iostream>


using namespace maingo;
using namespace ubp;


/////////////////////////////////////////////////////////////////////////
// constructor for the upper bounding solver
UbpIpopt::UbpIpopt(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions, const std::vector<babBase::OptimizationVariable> &variables,
                   const unsigned nineqIn, const unsigned neqIn, const unsigned nineqSquashIn, std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn, UBS_USE useIn):
    UpperBoundingSolver(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn)
{

    try {

        // Initialize IpoptProblem:
        _theIpoptProblem = new IpoptProblem(_nvar, _neq, _nineq, _nineqSquash, &_structure, constraintPropertiesIn, _DAGobj);

        // Initialize Solver objects:

        // Regular Solver
        _Ipopt = IpoptApplicationFactory();
        // Termination
        _Ipopt->Options()->SetNumericValue("tol", _maingoSettings->epsilonR);
        _Ipopt->Options()->SetNumericValue("acceptable_constr_viol_tol", std::min(_maingoSettings->deltaEq, _maingoSettings->deltaIneq));
        _Ipopt->Options()->SetNumericValue("constr_viol_tol", std::min(_maingoSettings->deltaEq, _maingoSettings->deltaIneq));
        _Ipopt->Options()->SetNumericValue("acceptable_tol", _maingoSettings->epsilonR);
        _Ipopt->Options()->SetIntegerValue("acceptable_iter", 2);
        _Ipopt->Options()->SetNumericValue("bound_relax_factor", 0);
        _Ipopt->Options()->SetStringValue("mu_strategy", "adaptive");    // Even if this is default, it seems to do something...
        _Ipopt->Options()->SetStringValue("linear_solver", "mumps");
        // We currently DO NOT set the mumps ordering settings to 5 (=METIS), since there seems to be a bug in METIS that causes crashes in some cases which we cannot handle...
        // We set the mumps ordering setting to 4 (=PORD)
        _Ipopt->Options()->SetIntegerValue("mumps_pivot_order", 4);
        // Output:
        if (_maingoSettings->UBP_verbosity == VERB_ALL) {
            _Ipopt->Options()->SetIntegerValue("print_level", 5);
        }
        else {
            _Ipopt->Options()->SetIntegerValue("print_level", 0);
        }
        _Ipopt->Options()->SetStringValue("sb", "yes");    // Suppress startup message
        _Ipopt->Options()->SetIntegerValue("file_print_level", 0);
        if (_nvar > 50) {
            // Hessian --> L-BFGS
            _Ipopt->Options()->SetStringValue("hessian_approximation", "limited-memory");
        }
        else {
            // Hessian --> own implementation
            _Ipopt->Options()->SetStringValue("hessian_approximation", "exact");
        }

        switch (_intendedUse) {
            case USE_BAB: {
                _Ipopt->Options()->SetIntegerValue("max_iter", _maingoSettings->UBP_maxStepsBab);
                _Ipopt->Options()->SetNumericValue("max_cpu_time", _maingoSettings->UBP_maxTimeBab);
                break;
            }
            case USE_PRE: {
                _Ipopt->Options()->SetIntegerValue("max_iter", _maingoSettings->UBP_maxStepsPreprocessing);
                _Ipopt->Options()->SetNumericValue("max_cpu_time", _maingoSettings->UBP_maxTimePreprocessing);
                break;
            }
            default: {
                throw "  Unknown USAGE setting " + std::to_string(_intendedUse);
            }
        }

        // Initialize
        Ipopt::ApplicationReturnStatus status = _Ipopt->Initialize();
        if (status != Ipopt::Solve_Succeeded) {
            throw MAiNGOException(" Status of Ipopt initialization: " + std::to_string(status)); // GCOVR_EXCL_LINE
        }
    }
    catch (const std::exception &e) { // GCOVR_EXCL_START
        throw MAiNGOException("  Error initializing UbpIpopt.", e);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error initializing UbpIpopt.");
    }
} // GCOVR_EXCL_STOP


/////////////////////////////////////////////////////////////////////////
// solve upper bounding problem
SUBSOLVER_RETCODE
UbpIpopt::_solve_nlp(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, double &objectiveValue, std::vector<double> &solutionPoint)
{

    try {
        // Update Ipopt problem
        _theIpoptProblem->set_bounds_and_starting_point(lowerVarBounds, upperVarBounds, solutionPoint);

        // Run optimization
        Ipopt::ApplicationReturnStatus status = _Ipopt->OptimizeTNLP(_theIpoptProblem);

        std::ostringstream outstr;
        outstr << "  Ipopt status: " << status << std::endl;
        _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);

        if (status == Ipopt::ApplicationReturnStatus::Internal_Error) {
            throw MAiNGOException("  An unknown internal error occurred within Ipopt. Please contact Ipopt mailing list."); // GCOVR_EXCL_LINE
        }
        else {
            _theIpoptProblem->get_solution(solutionPoint);
        }
    }
    catch (const std::exception &e) {

        std::ostringstream outstr;
        outstr << "  Warning: Local optimization using Ipopt failed. Continuing without a feasible point (unless initial point happens to be feasible)." << std::endl;
        outstr << "           Reason: " << e.what() << std::endl;
        _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);
    }
    catch (...) {

        std::ostringstream outstr;
        outstr << "  Warning: Local optimization using Ipopt failed. Continuing without a feasible point (unless initial point happens to be feasible)." << std::endl;
        _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);
    }

    // Check if point returned by local solver is actually feasible. If it is, the objective function value will be stored as well.
    return check_feasibility(solutionPoint, objectiveValue);
}
