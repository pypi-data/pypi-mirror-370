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

#ifdef HAVE_KNITRO

#include "ubpKnitro.h"
#include "MAiNGOException.h"


using namespace maingo;
using namespace ubp;


/////////////////////////////////////////////////////////////////////////
// constructor for the upper bounding solver
UbpKnitro::UbpKnitro(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions, const std::vector<babBase::OptimizationVariable> &variables,
                     const unsigned nineqIn, const unsigned neqIn, const unsigned nineqSquashIn, std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn, UBS_USE useIn):
    UpperBoundingSolver(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn),
    _theKnitroProblem(new KnitroProblem(_nvar, _neq, _nineq, _nineqSquash, variables, &_structure, constraintPropertiesIn, _DAGobj)),
    _Knitro(_theKnitroProblem, /*KN_GRADOPT_FORWARD*/ KN_GRADOPT_EXACT, /*KN_HESSOPT_BFGS*/ KN_HESSOPT_EXACT)
{

    try {

        // Termination
        _Knitro.setParam("feastol", std::min(_maingoSettings->deltaIneq, _maingoSettings->deltaEq));
        _Knitro.setParam("feastol_abs", std::min(_maingoSettings->deltaIneq, _maingoSettings->deltaEq));
        _Knitro.setParam("opttol", _maingoSettings->epsilonR);
        _Knitro.setParam("opttol_abs", _maingoSettings->epsilonA);
        _Knitro.setParam("mip_integral_gap_abs", std::min(_maingoSettings->deltaIneq, _maingoSettings->deltaEq));
        _Knitro.setParam("mip_integral_gap_rel", std::min(_maingoSettings->deltaIneq, _maingoSettings->deltaEq));
        _Knitro.setParam("presolve", 1);
        _Knitro.setParam("presolve_tol", 1e-6);

        // Output:
        if (_maingoSettings->UBP_verbosity < VERB_ALL) {
            _Knitro.setParam("outlev", 0);     // Suppress output
            _Knitro.setParam("outmode", 0);    // Suppress file writing
        }
        if (_maingoSettings->UBP_verbosity == VERB_ALL) {
            _Knitro.setParam("outlev", 3);     // Allow output
            _Knitro.setParam("outmode", 0);    // Suppress file writing
        }

        switch (_intendedUse) {
            case USE_BAB: {
                _Knitro.setParam("maxit", (int)_maingoSettings->UBP_maxStepsBab);
                _Knitro.setParam("mip_heuristic_maxit", 1);
                _Knitro.setParam("mip_strong_maxit", 0);
                _Knitro.setParam("mip_maxnodes", 1);
                _Knitro.setParam("mip_maxsolves", 1);
                _Knitro.setParam("mip_terminate", 1);
                _Knitro.setParam("maxtime_cpu", _maingoSettings->UBP_maxTimeBab);
                break;
            }
            case USE_PRE: {
                _Knitro.setParam("maxit", (int)_maingoSettings->UBP_maxStepsPreprocessing);
                _Knitro.setParam("mip_heuristic_maxit", (int)_maingoSettings->UBP_maxStepsPreprocessing);
                _Knitro.setParam("mip_strong_maxit", (int)_maingoSettings->UBP_maxStepsPreprocessing);
                _Knitro.setParam("mip_maxnodes", (int)_maingoSettings->UBP_maxStepsPreprocessing);
                _Knitro.setParam("mip_maxsolves", (int)_maingoSettings->UBP_maxStepsPreprocessing);
                _Knitro.setParam("maxtime_cpu", _maingoSettings->UBP_maxTimePreprocessing);
                break;
            }
            default: {
                std::ostringstream errmsg;
                errmsg << "  Unknown USAGE setting " << _intendedUse << std::endl;
                throw MAiNGOException(errmsg.str());
            }
        }
    }
    catch (const std::exception &e) {
        throw MAiNGOException("  Error initializing UbpKnitro.", e);
    }
    catch (...) {
        throw MAiNGOException("  Unknown error initializing UbpKnitro.");
    }
}


/////////////////////////////////////////////////////////////////////////
// solve upper bounding problem
SUBSOLVER_RETCODE
UbpKnitro::_solve_nlp(const std::vector<double> &lowerVarBounds, const std::vector<double> &upperVarBounds, double &objectiveValue, std::vector<double> &solutionPoint)
{


    try {
        // Update Knitro problem
        _Knitro.restart(solutionPoint, std::vector<double>());    // Set initial point
        _Knitro.chgVarBnds(lowerVarBounds, upperVarBounds);

        // Run optimization
        _solverStatus = _Knitro.solve();
        if (_maingoSettings->UBP_verbosity >= VERB_ALL) {
            std::ostringstream outstr;
            outstr << "Knitro status: " << _solverStatus << std::endl;
            _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);
        }
        if (_solverStatus <= -500) {
            throw MAiNGOException("  An unknown internal error occurred within Knitro. Please contact Knitro mailing list.");
        }
        else if (_solverStatus <= -200) {
            // Infeasible point
        }
        else {
            for (unsigned int i = 0; i < _nvar; i++) {
                solutionPoint[i] = _Knitro.getXValues(i);
            }
        }
    }
    catch (const std::exception &e) {
        if (_maingoSettings->UBP_verbosity >= VERB_ALL) {
            std::ostringstream outstr;
            outstr << "  Warning: Local optimization using Knitro failed. Continuing without a feasible point (unless initial point happens to be feasible)." << std::endl;
            outstr << "           Reason: " << e.what() << std::endl;
            _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);
        }
    }
    catch (...) {
        if (_maingoSettings->UBP_verbosity >= VERB_ALL) {
            std::ostringstream outstr;
            outstr << "  Warning: Local optimization using Knitro failed. Continuing without a feasible point (unless initial point happens to be feasible)." << std::endl;
            _logger->print_message(outstr.str(), VERB_ALL, UBP_VERBOSITY);
        }
    }

    // Check if point returned by local solver is actually feasible. If it is, the objective function value will be stored as well.
    return check_feasibility(solutionPoint, objectiveValue);
}

#endif