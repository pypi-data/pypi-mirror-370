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
#include "lbp.h"
#include "lbpClp.h"
#include "lbpInterval.h"
#include "logger.h"
#include "lbpSubinterval.h"

#ifdef HAVE_CPLEX    // If Cmake has found CPLEX this pre-processor variable is set
#include "lbpCplex.h"
#endif

#ifdef HAVE_GUROBI   // If Cmake has found CPLEX this pre-processor variable is set
#include "lbpGurobi.h"
#endif


using namespace maingo;
using namespace lbp;


/////////////////////////////////////////////////////////////////////////
// function for initializing the different lower bounding solver wrappers
std::shared_ptr<LowerBoundingSolver>
lbp::make_lbp_solver(mc::FFGraph &DAG, const std::vector<mc::FFVar> &DAGvars, const std::vector<mc::FFVar> &DAGfunctions,
                     const std::vector<babBase::OptimizationVariable> &variables, const std::vector<bool>& variableIsLinear,
                     const unsigned nineqIn, const unsigned neqIn, const unsigned nineqRelaxationOnlyIn, const unsigned neqRelaxationOnlyIn, const unsigned nineqSquashIn,
                     std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn,
                     bool printSolver)
{

    switch (settingsIn->LBP_solver) {
        case LBP_SOLVER_MAiNGO: {
            if (printSolver)
                loggerIn->print_message("      Lower bounding: MAiNGO internal solver (McCormick relaxations for objective, intervals for constraints)\n",
                                        VERB_NORMAL, BAB_VERBOSITY);
            return std::make_shared<LowerBoundingSolver>(DAG, DAGvars, DAGfunctions, variables, variableIsLinear, nineqIn, neqIn,
                                                         nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn);
        }
        case LBP_SOLVER_INTERVAL: {
            if (printSolver)
                loggerIn->print_message("      Lower bounding: Interval extensions\n", VERB_NORMAL, BAB_VERBOSITY);
            return std::make_shared<LbpInterval>(DAG, DAGvars, DAGfunctions, variables, variableIsLinear, nineqIn, neqIn,
                                                 nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn);
        }
        case LBP_SOLVER_SUBDOMAIN: {
            if (printSolver)
                loggerIn->print_message("      Lower bounding: Subinterval arithemtic\n", VERB_NORMAL, BAB_VERBOSITY);
            return std::make_shared<LbpSubinterval>(DAG, DAGvars, DAGfunctions, variables, variableIsLinear, nineqIn, neqIn,
                                                    nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn);
        }
        case LBP_SOLVER_CPLEX: {
#ifdef HAVE_CPLEX
            if (printSolver)
                loggerIn->print_message("      Lower bounding: CPLEX\n", VERB_NORMAL, BAB_VERBOSITY);
            return std::make_shared<LbpCplex>(DAG, DAGvars, DAGfunctions, variables, variableIsLinear, nineqIn, neqIn,
                                              nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn);
#else
            throw MAiNGOException("  Error in LbpFactory: Cannot use lower bounding strategy LBP_SOLVER_CPLEX: Your MAiNGO build does not contain CPLEX."); // GCOVR_EXCL_LINE
#endif
        }
        case LBP_SOLVER_GUROBI: {
#ifdef HAVE_GUROBI
            if (printSolver) {
                loggerIn->print_message("      Lower bounding: Gurobi\n", VERB_NORMAL, BAB_VERBOSITY);
            }
            return std::make_shared<LbpGurobi>(DAG, DAGvars, DAGfunctions, variables, variableIsLinear, nineqIn, neqIn,
                                              nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn);
#else
            throw MAiNGOException("  Error in LbpFactory: Cannot use lower bounding strategy LBP_SOLVER_GUROBI: Your MAiNGO build does not contain Gurobi.");    // GCOVR_EXCL_LINE
#endif
        }
        case LBP_SOLVER_CLP: {
            if (printSolver)
                loggerIn->print_message("      Lower bounding: CLP\n", VERB_NORMAL, BAB_VERBOSITY);
            return std::make_shared<LbpClp>(DAG, DAGvars, DAGfunctions, variables, variableIsLinear, nineqIn, neqIn,
                                            nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn);
        }
        default: {// GCOVR_EXCL_START
            std::ostringstream errmsg;
            errmsg << "  Error in LbpFactory: Unknown lower bounding solver: " << settingsIn->LBP_solver;
            throw MAiNGOException(errmsg.str());
        }
    } // GCOVR_EXCL_STOP
}
