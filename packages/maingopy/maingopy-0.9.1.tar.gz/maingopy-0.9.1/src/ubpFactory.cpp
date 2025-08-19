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

#include "MAiNGOException.h"
#include "logger.h"
#include "ubp.h"
#include "ubpClp.h"
#include "ubpIpopt.h"
#include "ubpNLopt.h"

#ifdef HAVE_CPLEX    // If CMake has found CPLEX ,this pre-processor variable is defined
#include "ubpCplex.h"
#endif

#ifdef HAVE_GUROBI  // If CMake has found Gurobi ,this pre-processor variable is defined
#include "ubpGurobi.h"
#endif

#ifdef HAVE_KNITRO    // If CMake has found KNITRO, this pre-processor variable is defined
#include "ubpKnitro.h"
#endif


using namespace maingo;
using namespace ubp;


/////////////////////////////////////////////////////////////////////////
// Function for initializing the different upper bounding solver wrappers
std::shared_ptr<UpperBoundingSolver>
ubp::make_ubp_solver(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions,
                     const std::vector<babBase::OptimizationVariable> &variables, const unsigned nineqIn,
                     const unsigned neqIn, const unsigned nineqSquashIn, std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn,
                     std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn, UpperBoundingSolver::UBS_USE useIn,
                     bool printSolver)
{
    UBP_SOLVER desiredSolver;
    std::string useDescription;
    switch (useIn) {
        case ubp::UpperBoundingSolver::USE_PRE:
            useDescription = "Multistart";
            desiredSolver  = settingsIn->UBP_solverPreprocessing;
            break;
        case ubp::UpperBoundingSolver::USE_BAB:
            useDescription = "Upper bounding";
            desiredSolver  = settingsIn->UBP_solverBab;
            break;
        default: // GCOVR_EXCL_START
            throw MAiNGOException("  Error in UbpFactory: unknown intended use for upper bounding solver.");
    }

    switch (desiredSolver) { // GCOVR_EXCL_STOP
        case UBP_SOLVER_EVAL: {
            if (printSolver)
                loggerIn->print_message("      " + useDescription + ": Function evaluation\n", VERB_NORMAL, BAB_VERBOSITY);
            return std::make_shared<UpperBoundingSolver>(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
        }
        case UBP_SOLVER_COBYLA: {
            if (printSolver)
                loggerIn->print_message("      " + useDescription + ": COBYLA\n", VERB_NORMAL, BAB_VERBOSITY);
            return std::make_shared<UbpNLopt>(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
        }
        case UBP_SOLVER_BOBYQA: {
            if (printSolver)
                loggerIn->print_message("      " + useDescription + ": BOBYQA\n", VERB_NORMAL, BAB_VERBOSITY);
            return std::make_shared<UbpNLopt>(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
        }
        case UBP_SOLVER_LBFGS: {
            if (printSolver)
                loggerIn->print_message("      " + useDescription + ": LBFGS\n", VERB_NORMAL, BAB_VERBOSITY);
            return std::make_shared<UbpNLopt>(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
        }
        case UBP_SOLVER_SLSQP: {
            if (printSolver)
                loggerIn->print_message("      " + useDescription + ": SLSQP\n", VERB_NORMAL, BAB_VERBOSITY);
            return std::make_shared<UbpNLopt>(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
        }
        case UBP_SOLVER_IPOPT: {
            if (printSolver)
                loggerIn->print_message("      " + useDescription + ": IPOPT\n", VERB_NORMAL, BAB_VERBOSITY);
            return std::make_shared<UbpIpopt>(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
        }
        case UBP_SOLVER_KNITRO: {
#ifdef HAVE_KNITRO
            if (printSolver)
                loggerIn->print_message("      " + useDescription + ": KNITRO\n", VERB_NORMAL, BAB_VERBOSITY);
            return std::make_shared<UbpKnitro>(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
#else
            throw MAiNGOException("  Error in UbpFactory: Cannot use upper bounding strategy UBP_SOLVER_KNITRO: Your MAiNGO build does not contain KNITRO."); // GCOVR_EXCL_LINE
#endif
        }
        case UBP_SOLVER_CPLEX: {
#ifdef HAVE_CPLEX
            return std::make_shared<UbpCplex>(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
#else
            throw MAiNGOException("  Error in UbpFactory: Cannot use upper bounding strategy UBP_SOLVER_CPLEX: Your MAiNGO build does not contain CPLEX."); // GCOVR_EXCL_LINE
#endif
        }
        case UBP_SOLVER_GUROBI: {
#ifdef HAVE_GUROBI
            return std::make_shared<UbpGurobi>(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
#else
            throw(MAiNGOException("  Error in UbpFactory: Cannot use upper bounding strategy UBP_SOLVER_GUROBI: Your MAiNGO build does not contain Gurobi.")); // GCOVR_EXCL_LINE
#endif
        }
        case UBP_SOLVER_CLP: {
            return std::make_shared<UbpClp>(DAG, DAGvars, DAGfunctions, variables, nineqIn, neqIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn, useIn);
        }
        default: { // GCOVR_EXCL_START
            std::ostringstream errmsg;
            errmsg << "  Error in UbpFactory: Unknown upper bounding strategy: " << desiredSolver << std::endl;
            throw MAiNGOException("  Error in UbpFactory: Unknown upper bounding strategy: " + std::to_string(desiredSolver)); 
        }
    } // GCOVR_EXCL_STOP
}