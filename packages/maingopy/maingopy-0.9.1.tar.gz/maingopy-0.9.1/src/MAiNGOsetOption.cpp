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
#include "settings.h"

#include <limits>
#include <string>


using namespace maingo;


/////////////////////////////////////////////////////////////////////////
// modifies an option of MAiNGO. Returns true if successful and false if option is unknown.
// Note that in the former case, when violating a bound imposed on the value for a certain option,
// the respective bound is chosen as new value instead of the value specified in the function call
bool
MAiNGO::set_option(const std::string& option, const double value)
{

    std::ostringstream oss;    // Dummy ostringstream for more accurate output of doubles
    oss << value;
    if (option == "epsilonA") {
        if (value < 1e-9) {
            _logger->save_setting(EPSILONA, "epsilonA has to be >=1e-9, setting it to 1e-9");
            _maingoSettings->epsilonA = 1e-9;
        }
        else {
            _maingoSettings->epsilonA = value;
            _logger->save_setting(EPSILONA, option + " " + oss.str());
        }
    }
    else if (option == "epsilonR") {
        if (value < 1e-9) {
            _logger->save_setting(EPSILONR, "epsilonR has to be >=1e-9, setting it to 1e-9");
            _maingoSettings->epsilonR = 1e-9;
        }
        else {
            _maingoSettings->epsilonR = value;
            _logger->save_setting(EPSILONR, option + " " + oss.str());
        }
    }
    else if (option == "deltaIneq") {
        if (value < 1e-9) {
            _logger->save_setting(DELTAINEQ, "deltaIneq has to be >=1e-9, setting it to 1e-9");
            _maingoSettings->deltaIneq = 1e-9;
        }
        else {
            _maingoSettings->deltaIneq  = value;
            _maingoSettings->relNodeTol = std::max(1e-12, std::min(_maingoSettings->relNodeTol, std::min(value * 1e-1, _maingoSettings->deltaEq * 1e-1)));
            _logger->save_setting(DELTAINEQ, option + " " + oss.str());
        }
    }
    else if (option == "deltaEq") {
        if (value < 1e-9) {
            _logger->save_setting(DELTAEQ, "deltaEq has to be >=1e-9, setting it to 1e-9");
            _maingoSettings->deltaEq = 1e-9;
        }
        else {
            _maingoSettings->deltaEq    = value;
            _maingoSettings->relNodeTol = std::max(1e-12, std::min(_maingoSettings->relNodeTol, std::min(value * 1e-1, _maingoSettings->deltaIneq * 1e-1)));
            _logger->save_setting(DELTAEQ, option + " " + oss.str());
        }
    }
    else if (option == "relNodeTol") {
        if (value < 1e-12) {
            _logger->save_setting(RELNODETOL, "relNodeTol has to be >=1e-12, setting it to 1e-12");
            _maingoSettings->relNodeTol = 1e-12;
        }
        else {
            _maingoSettings->relNodeTol = std::max(1e-12, std::min(value, std::min(_maingoSettings->deltaIneq * 1e-1, _maingoSettings->deltaEq * 1e-1)));
            _logger->save_setting(RELNODETOL, option + " " + oss.str());
        }
    }
    else if (option == "BAB_maxNodes") {
        if (value < 0 && value != -1) {
            _logger->save_setting(BAB_MAXNODES, "BAB_maxNodes has to be >=0 or -1 (=inf), setting it to 0");
            _maingoSettings->BAB_maxNodes = 0;
        }
        else {
            if (value == -1) {
                _maingoSettings->BAB_maxNodes = std::numeric_limits<unsigned>::max();
                _logger->save_setting(BAB_MAXNODES, option + " " + oss.str());
            }
            else {
                _maingoSettings->BAB_maxNodes = (int)value;
                _logger->save_setting(BAB_MAXNODES, option + " " + oss.str());
            }
        }
    }
    else if (option == "BAB_maxIterations") {
        if (value < 0 && value != -1) {
            _logger->save_setting(BAB_MAXITERATIONS, "BAB_maxIterations has to be >=0 or -1 (=inf), setting it to 0");
            _maingoSettings->BAB_maxIterations = 0;
        }
        else {
            if (value == -1) {
                _maingoSettings->BAB_maxIterations = std::numeric_limits<unsigned>::max();
                _logger->save_setting(BAB_MAXITERATIONS, option + " " + oss.str());
            }
            else {
                _maingoSettings->BAB_maxIterations = (int)value;
                _logger->save_setting(BAB_MAXITERATIONS, option + " " + oss.str());
            }
        }
    }
    else if (option == "maxTime") {
        if (value < 0 && value != -1) {
            _logger->save_setting(MAXTIME, "maxTime has to be >= 0 or -1 (=inf), setting it to 0");
            _maingoSettings->maxTime = 0;
        }
        else {
            if (value == -1) {
                _maingoSettings->maxTime = std::numeric_limits<unsigned>::max();
                _logger->save_setting(MAXTIME, option + " " + oss.str());
            }
            else {
                _maingoSettings->maxTime = (int)value;
                _logger->save_setting(MAXTIME, option + " " + oss.str());
            }
        }
    }
    else if (option == "maxwTime") {
        if (value < 10 && value != -1) {
            _logger->save_setting(MAXWTIME, "maxwTime has to be >= 10 or -1 (=inf), setting it to 10");
            _maingoSettings->maxwTime = 10;
        }
        else {
            if (value == -1) {
                _maingoSettings->maxwTime = std::numeric_limits<unsigned>::max();
                _logger->save_setting(MAXWTIME, option + " " + oss.str());
            }
            else {
                _maingoSettings->maxwTime = (int)value;
                _logger->save_setting(MAXWTIME, option + " " + oss.str());
            }
        }
    }
    else if (option == "confirmTermination") {
        if (value != 0 && value != 1) {
            _logger->save_setting(CONFIRMTERMINATION, "confirmTermination has to be 0 or 1, setting to 0");
            _maingoSettings->confirmTermination = false;
        }
        else {
            if (value == 0) {
                _maingoSettings->confirmTermination = false;
                _logger->save_setting(CONFIRMTERMINATION, option + " 0");
            }
            else {
                _maingoSettings->confirmTermination = true;
                _logger->save_setting(CONFIRMTERMINATION, option + " 1");
            }
        }
    }
    else if (option == "terminateOnFeasiblePoint") {
        if (value != 0 && value != 1) {
            _logger->save_setting(TERMINATEONFEASIBLEPOINT, "terminateOnFeasiblePoint has to be 0 or 1, setting to 0");
            _maingoSettings->terminateOnFeasiblePoint = false;
        }
        else {
            if (value == 0) {
                _maingoSettings->terminateOnFeasiblePoint = false;
                _logger->save_setting(TERMINATEONFEASIBLEPOINT, option + " 0");
            }
            else {
                _maingoSettings->terminateOnFeasiblePoint = true;
                _logger->save_setting(TERMINATEONFEASIBLEPOINT, option + " 1");
            }
        }
    }
    else if (option == "targetLowerBound") {
        _maingoSettings->targetLowerBound = value;
        _logger->save_setting(TARGETLOWERBOUND, option + " " + oss.str());
    }
    else if (option == "targetUpperBound") {
        _maingoSettings->targetUpperBound = value;
        _logger->save_setting(TARGETUPPERBOUND, option + " " + oss.str());
    }
    else if (option == "PRE_maxLocalSearches") {
        if (value < 0) {
            _logger->save_setting(PRE_MAXLOCALSEARCHES, "PRE_maxLocalSearches has to be at least 0, setting it to 0");
            _maingoSettings->PRE_maxLocalSearches = 0;
        }
        else {
            _maingoSettings->PRE_maxLocalSearches = (int)value;
            _logger->save_setting(PRE_MAXLOCALSEARCHES, option + " " + oss.str());
        }
    }
    else if (option == "PRE_obbtMaxRounds") {
        if (value < 0) {
            _logger->save_setting(PRE_OBBTMAXROUNDS, "PRE_obbtMaxRounds has to be at least 0, setting it to 0");
            _maingoSettings->PRE_obbtMaxRounds = 0;
        }
        else {
            _maingoSettings->PRE_obbtMaxRounds = (int)value;
            _logger->save_setting(PRE_OBBTMAXROUNDS, option + " " + oss.str());
        }
    }
    else if (option == "PRE_pureMultistart") {
        if (value != 0 && value != 1) {
            _logger->save_setting(PRE_PUREMULTISTART, "PRE_pureMultistart has to be either 1 or 0, setting it to 0");
            _maingoSettings->PRE_pureMultistart = false;
        }
        else {
            if (value == 0) {
                _maingoSettings->PRE_pureMultistart = false;
                _logger->save_setting(PRE_PUREMULTISTART, option + " 0");
            }
            else {
                _maingoSettings->PRE_pureMultistart = true;
                _logger->save_setting(PRE_PUREMULTISTART, option + " 1");
            }
        }
    }
    else if (option == "BAB_nodeSelection") {
        if (value != 0 && value != 1 && value != 2) {
            _logger->save_setting(BAB_NODESELECTION, "BAB_nodeSelection has to be 0, 1 or 2, setting to 0");
            _maingoSettings->BAB_nodeSelection = babBase::enums::NS_BESTBOUND;
        }
        else {
            if ((int)value == 0) {
                _maingoSettings->BAB_nodeSelection = babBase::enums::NS_BESTBOUND;
            }
            else if ((int)value == 1) {
                _maingoSettings->BAB_nodeSelection = babBase::enums::NS_DEPTHFIRST;
            }
            else {
                _maingoSettings->BAB_nodeSelection = babBase::enums::NS_BREADTHFIRST;
            }
            _logger->save_setting(BAB_NODESELECTION, option + " " + oss.str());
        }
    }
    else if (option == "BAB_branchVariable") {
        if (value != 0 && value != 1) {
            _logger->save_setting(BAB_BRANCHVARIABLE, "BAB_branchVariable has to be 0 or 1, setting to 0");
            _maingoSettings->BAB_branchVariable = babBase::enums::BV_ABSDIAM;
        }
        else {
            if ((int)value == 0) {
                _maingoSettings->BAB_branchVariable = babBase::enums::BV_ABSDIAM;
            }
            else {
                _maingoSettings->BAB_branchVariable = babBase::enums::BV_RELDIAM;
            }
            _logger->save_setting(BAB_BRANCHVARIABLE, option + " " + oss.str());
        }
    }
    else if (option == "BAB_alwaysSolveObbt") {
        if (value != 0 && value != 1) {
            _logger->save_setting(BAB_ALWAYSSOLVEOBBT, "BAB_alwaysSolveObbt has to be 0 or 1, setting to 0");
            _maingoSettings->BAB_alwaysSolveObbt = false;
        }
        else {
            if (value == 0) {
                _maingoSettings->BAB_alwaysSolveObbt = false;
                _logger->save_setting(BAB_ALWAYSSOLVEOBBT, option + " 0");
            }
            else {
                _maingoSettings->BAB_alwaysSolveObbt = true;
                _logger->save_setting(BAB_ALWAYSSOLVEOBBT, option + " 1");
            }
        }
    }
    else if (option == "BAB_obbtDecayCoefficient") {
        if (value < 0) {
            _logger->save_setting(BAB_OBBTDECAYCOEFFICIENT, "BAB_obbtDecayCoefficient has to be at least 0 (= no depth-dependent OBBT)");
            _maingoSettings->BAB_obbtDecayCoefficient = 0;
        }
        else {
            _maingoSettings->BAB_obbtDecayCoefficient = value;
            _logger->save_setting(BAB_OBBTDECAYCOEFFICIENT, option + " " + oss.str());
        }
    }
    else if (option == "BAB_probing") {
        if (value != 0 && value != 1) {
            _logger->save_setting(BAB_PROBING, "BAB_probing has to be 0 or 1, setting to 0");
            _maingoSettings->BAB_probing = false;
        }
        else {
            if (value == 0) {
                _maingoSettings->BAB_probing = false;
                _logger->save_setting(BAB_PROBING, option + " 0");
            }
            else {
                _maingoSettings->BAB_probing = true;
                _logger->save_setting(BAB_PROBING, option + " 1");
            }
        }
    }
    else if (option == "BAB_dbbt") {
        if (value != 0 && value != 1) {
            _logger->save_setting(BAB_DBBT, "BAB_dbbt has to be 0 or 1, setting to 1");
            _maingoSettings->BAB_dbbt = true;
        }
        else {
            if (value == 0) {
                _maingoSettings->BAB_dbbt = false;
                _logger->save_setting(BAB_DBBT, option + " 0");
            }
            else {
                _maingoSettings->BAB_dbbt = true;
                _logger->save_setting(BAB_DBBT, option + " 1");
            }
        }
    }
    else if (option == "BAB_constraintPropagation") {
        if (value != 0 && value != 1) {
            _logger->save_setting(BAB_CONSTRAINTPROPAGATION, "BAB_constraintPropagation has to be 0 or 1, setting to 0");
            _maingoSettings->BAB_constraintPropagation = false;
        }
        else {
            if (value == 0) {
                _maingoSettings->BAB_constraintPropagation = false;
                _logger->save_setting(BAB_CONSTRAINTPROPAGATION, option + " 0");
            }
            else {
                _maingoSettings->BAB_constraintPropagation = true;
                _logger->save_setting(BAB_CONSTRAINTPROPAGATION, option + " 1");
            }
        }
    }
    else if (option == "LBP_solver") {
        if (value != 0 && value != 1 && value != 2 && value != 3 && value != 4 && value != 5) {
#ifdef HAVE_CPLEX
            _logger->save_setting(LBP_SOLVER, "LBP_solver has to be in {0,1,2,3,4,5}, setting it to default (CPLEX)");
            _maingoSettings->LBP_solver = lbp::LBP_SOLVER_CPLEX;
#elif HAVE_GUROBI
            _logger->save_setting(LBP_SOLVER, "LBP_solver has to be in {0,1,2,3,4,5}, setting it to default (Gurobi)");
            _maingoSettings->LBP_solver = lbp::LBP_SOLVER_GUROBI;
#else
            _logger->save_setting(LBP_SOLVER, "LBP_solver has to be in {0,1,2,3,4,5}, setting it to default (CLP)");
            _maingoSettings->LBP_solver = lbp::LBP_SOLVER_CLP;
#endif
        }
        else {
            std::string logMessage = option + " " + oss.str();
            if ((int)value == 0) {
                _maingoSettings->LBP_solver = lbp::LBP_SOLVER_MAiNGO;
            }
            else if ((int)value == 1) {
                _maingoSettings->LBP_solver = lbp::LBP_SOLVER_INTERVAL;
            }
            else if ((int)value == 2) {
#ifdef HAVE_CPLEX
                _maingoSettings->LBP_solver = lbp::LBP_SOLVER_CPLEX;
#elif HAVE_GUROBI
                logMessage                  = "Cannot use LBP_solver 2 (LBP_SOLVER_CPLEX) because your MAiNGO build does not contain CPLEX. Setting it to 4 (Gurobi)";
                _maingoSettings->LBP_solver = lbp::LBP_SOLVER_GUROBI;
#else
                logMessage                  = "Cannot use LBP_solver 2 (LBP_SOLVER_CPLEX) because your MAiNGO build does not contain CPLEX. Setting it to 3 (CLP)";
                _maingoSettings->LBP_solver = lbp::LBP_SOLVER_CLP;
#endif
            }
            else if ((int)value == 3) {
                _maingoSettings->LBP_solver = lbp::LBP_SOLVER_CLP;
            }
            else if ((int)value == 4) {
#ifdef HAVE_GUROBI
                _maingoSettings->LBP_solver = lbp::LBP_SOLVER_GUROBI;
#elif HAVE_CPLEX
                logMessage                  = "Cannot use LBP_solver 4 (LBP_SOLVER_GUROBI) because your MAiNGO build does not contain Gurobi. Setting it to 2 (CPLEX)";
                _maingoSettings->LBP_solver = lbp::LBP_SOLVER_CPLEX;
#else
                logMessage                  = "Cannot use LBP_solver 4 (LBP_SOLVER_GUROBI) because your MAiNGO build does not contain Gurobi. Setting it to 3 (CLP)";
                _maingoSettings->LBP_solver = lbp::LBP_SOLVER_CLP;
#endif
            }
            else if ((int)value == 5) {
                _maingoSettings->LBP_solver = lbp::LBP_SOLVER_SUBDOMAIN;
            }
            _logger->save_setting(LBP_SOLVER, logMessage);
        }
    }
    else if (option == "LBP_linPoints") {
        if (value != 0 && value != 1 && value != 2 && value != 3 && value != 4 && value != 5) {
            _logger->save_setting(LBP_LINPOINTS, "LBP_linPoints has to be in {0,1,2,3,4,5}, setting to 0");
            _maingoSettings->LBP_linPoints = lbp::LINP_MID;
        }
        else {
            if ((int)value == 0) {
                _maingoSettings->LBP_linPoints = lbp::LINP_MID;
            }
            else if ((int)value == 1) {
                _maingoSettings->LBP_linPoints = lbp::LINP_INCUMBENT;
            }
            else if ((int)value == 2) {
                _maingoSettings->LBP_linPoints = lbp::LINP_KELLEY;
            }
            else if ((int)value == 3) {
                _maingoSettings->LBP_linPoints = lbp::LINP_SIMPLEX;
            }
            else if ((int)value == 4) {
                _maingoSettings->LBP_linPoints = lbp::LINP_RANDOM;
            }
            else if ((int)value == 5) {
                _maingoSettings->LBP_linPoints = lbp::LINP_KELLEY_SIMPLEX;
            }
            _logger->save_setting(LBP_LINPOINTS, option + " " + oss.str());
        }
    }
    else if (option == "LBP_subgradientIntervals") {
        if (value != 0 && value != 1) {
            _logger->save_setting(LBP_SUBGRADIENTINTERVALS, "LBP_subgradientIntervals has to be 0 or 1, setting to 0");
            _maingoSettings->LBP_subgradientIntervals = false;
        }
        else {
            if (value == 0) {
                _maingoSettings->LBP_subgradientIntervals = false;
                _logger->save_setting(LBP_SUBGRADIENTINTERVALS, option + " 0");
            }
            else {
                _maingoSettings->LBP_subgradientIntervals = true;
                _logger->save_setting(LBP_SUBGRADIENTINTERVALS, option + " 1");
            }
        }
    }
    else if (option == "LBP_obbtMinImprovement") {
        if ((value < 0) || (value > 1)) {
            _logger->save_setting(LBP_OBBTMINIMPROVEMENT, "LBP_obbtMinImprovement has to be between 0 and 1, setting it to 0.5");
            _maingoSettings->LBP_obbtMinImprovement = 0.5;
        }
        else {
            _maingoSettings->LBP_obbtMinImprovement = value;
            _logger->save_setting(LBP_OBBTMINIMPROVEMENT, option + " " + oss.str());
        }
    }
    else if (option == "LBP_activateMoreScaling") {
        if ((value < 100) || (value > 100000)) {
            _logger->save_setting(LBP_OBBTMINIMPROVEMENT, "LBP_activateMoreScaling has to be between 100 and 100000, setting it to 10000");
            _maingoSettings->LBP_activateMoreScaling = 10000;
        }
        else {
            _maingoSettings->LBP_activateMoreScaling = value;
            _logger->save_setting(LBP_ACTIVATEMORESCALING, option + " " + oss.str());
        }
    }
    else if (option == "LBP_addAuxiliaryVars") {
        if (value != 0 && value != 1) {
            _logger->save_setting(LBP_ADDAUXILIARYVARS, "LBP_addAuxiliaryVars has to be 0 or 1, setting it to 0");
            _maingoSettings->LBP_addAuxiliaryVars = false;
        }
        else {
            if (value == 0) {
                _maingoSettings->LBP_addAuxiliaryVars = false;
                _logger->save_setting(LBP_ADDAUXILIARYVARS, option + " 0");
            }
            else {
                _maingoSettings->LBP_addAuxiliaryVars = true;
                _logger->save_setting(LBP_ADDAUXILIARYVARS, option + " 1");
            }
        }
    }
    else if (option == "LBP_minFactorsForAux") {
        if (value < 2) {
            _logger->save_setting(LBP_MINFACTORSFORAUX, "LBP_minFactorsForAux has to be at least 2, setting it to 2");
            _maingoSettings->LBP_minFactorsForAux = 2;
        }
        else {
            _maingoSettings->LBP_minFactorsForAux = value;
            _logger->save_setting(LBP_MINFACTORSFORAUX, option + " " + oss.str());
        }
    }
    else if (option == "LBP_maxNumberOfAddedFactors") {
        if (value < 1) {
            _logger->save_setting(LBP_MAXNUMBEROFADDEDFACTORS, "LBP_maxNumberOfAddedFactors has to be at least 1, setting it to 1");
            _maingoSettings->LBP_maxNumberOfAddedFactors = 1;
        }
        else {
            _maingoSettings->LBP_maxNumberOfAddedFactors = value;
            _logger->save_setting(LBP_MAXNUMBEROFADDEDFACTORS, option + " " + oss.str());
        }
    }
    else if (option == "MC_mvcompUse") {
        if (value != 0 && value != 1) {
            _logger->save_setting(MC_MVCOMPUSE, "MC_mvcompUse has to be 0 or 1, setting to 1");
            _maingoSettings->MC_mvcompUse = true;
        }
        else {
            if (value == 0) {
                _maingoSettings->MC_mvcompUse = false;
                _logger->save_setting(MC_MVCOMPUSE, option + " 0");
            }
            else {
                _maingoSettings->MC_mvcompUse = true;
                _logger->save_setting(MC_MVCOMPUSE, option + " 1");
            }
        }
    }
    else if (option == "MC_mvcompTol") {
        if (value < 1e-12 || value > 1e-9) {
            _logger->save_setting(MC_MVCOMPTOL, "MC_mvcompTol has to be in [1e-9,1e-12], setting it to 1e-12");
            _maingoSettings->MC_mvcompTol = 1e-12;
        }
        else {
            _maingoSettings->MC_mvcompTol = value;
            _logger->save_setting(MC_MVCOMPTOL, option + " " + oss.str());
        }
    }
    else if (option == "MC_envelTol") {
        if (value < 1e-12) {
            _logger->save_setting(MC_ENVELTOL, "MC_envelTol has to be in [1e-9,1e-12], setting it to 1e-12");
            _maingoSettings->MC_envelTol = 1e-12;
        }
        else {
            _maingoSettings->MC_envelTol = value;
            _logger->save_setting(MC_ENVELTOL, option + " " + oss.str());
        }
    }
    else if (option == "UBP_solverPreprocessing") {
        if (value != 0 && value != 1 && value != 2 && value != 3 && value != 4 && value != 5 && value != 6) {
            _logger->save_setting(UBP_SOLVERPRE, "UBP_solverPreprocessing has to be 0, 1, 2, 3, 4, 5, 6, setting to 5");
            _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_IPOPT;
        }
        else {
            std::string logMessage = option + " " + oss.str();
            if ((int)value == 0) {
                _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_EVAL;
            }
            else if ((int)value == 1) {
                _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_COBYLA;
            }
            else if ((int)value == 2) {
                _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_BOBYQA;
            }
            else if ((int)value == 3) {
                _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_LBFGS;
            }
            else if ((int)value == 4) {
                _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_SLSQP;
            }
            else if ((int)value == 5) {
                _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_IPOPT;
            }
            else if ((int)value == 6) {
#ifdef HAVE_KNITRO
                _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_KNITRO;
#else
                logMessage                               = "Cannot use UBP_solverPreprocessing 6 (UBP_SOLVER_KNITRO) because your MAiNGO build does not contain KNITRO. Setting it to 5";
                _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_IPOPT;
#endif
            }

            _logger->save_setting(UBP_SOLVERPRE, logMessage);
        }
    }
    else if (option == "UBP_maxStepsPreprocessing") {
        if (value < 1) {
            _logger->save_setting(UBP_MAXSTEPSPRE, "UBP_maxStepsPreprocessing has to be at least 1, setting to 1");
            _maingoSettings->UBP_maxStepsPreprocessing = 1;
        }
        else {
            _maingoSettings->UBP_maxStepsPreprocessing = (int)value;
            _logger->save_setting(UBP_MAXSTEPSPRE, option + " " + oss.str());
        }
    }
    else if (option == "UBP_maxTimePreprocessing") {
        if (value < 0.1) {
            _logger->save_setting(UBP_MAXTIMEPRE, "UBP_maxTimePreprocessing has to be at least 0.1, setting to 0.1");
            _maingoSettings->UBP_maxTimePreprocessing = 0.1;
        }
        else {
            _maingoSettings->UBP_maxTimePreprocessing = value;
            _logger->save_setting(UBP_MAXTIMEPRE, option + " " + oss.str());
        }
    }
    else if (option == "UBP_solverBab") {
        if (value != 0 && value != 1 && value != 2 && value != 3 && value != 4 && value != 5 && value != 6) {
            _logger->save_setting(UBP_SOLVERBAB, "UBP_solverBab has to be 0, 1, 2, 3, 4, 5, 6, setting to 4");
            _maingoSettings->UBP_solverBab = ubp::UBP_SOLVER_SLSQP;
        }
        else {
            if ((int)value == 0) {
                _maingoSettings->UBP_solverBab = ubp::UBP_SOLVER_EVAL;
            }
            else if ((int)value == 1) {
                _maingoSettings->UBP_solverBab = ubp::UBP_SOLVER_COBYLA;
            }
            else if ((int)value == 2) {
                _maingoSettings->UBP_solverBab = ubp::UBP_SOLVER_BOBYQA;
            }
            else if ((int)value == 3) {
                _maingoSettings->UBP_solverBab = ubp::UBP_SOLVER_LBFGS;
            }
            else if ((int)value == 4) {
                _maingoSettings->UBP_solverBab = ubp::UBP_SOLVER_SLSQP;
            }
            else if ((int)value == 5) {
                _maingoSettings->UBP_solverBab = ubp::UBP_SOLVER_IPOPT;
            }
            else if ((int)value == 6) {
#ifdef HAVE_KNITRO
                _maingoSettings->UBP_solverBab = ubp::UBP_SOLVER_KNITRO;
#else
                _logger->save_setting(UBP_SOLVERBAB, "Cannot use UBP_solverBab 6 (UBP_SOLVER_KNITRO) because your MAiNGO build does not contain KNITRO. Setting it to 4");
                _maingoSettings->UBP_solverBab = ubp::UBP_SOLVER_SLSQP;
#endif
            }
            _logger->save_setting(UBP_SOLVERBAB, option + " " + std::to_string(_maingoSettings->UBP_solverBab));
        }
    }
    else if (option == "UBP_maxStepsBab") {
        if (value < 1) {
            _logger->save_setting(UBP_MAXSTEPSBAB, "UBP_maxStepsBab has to be at least 1, setting to 1");
            _maingoSettings->UBP_maxStepsBab = 1;
        }
        else {
            _maingoSettings->UBP_maxStepsBab = (int)value;
            _logger->save_setting(UBP_MAXSTEPSBAB, option + " " + oss.str());
        }
    }
    else if (option == "UBP_maxTimeBab") {
        if (value < 0.1) {
            _logger->save_setting(UBP_MAXTIMEBAB, "UBP_maxTimeBab has to be at least 0.1, setting to 0.1");
            _maingoSettings->UBP_maxTimeBab = 0.1;
        }
        else {
            _maingoSettings->UBP_maxTimeBab = value;
            _logger->save_setting(UBP_MAXTIMEBAB, option + " " + oss.str());
        }
    }
    else if (option == "UBP_ignoreNodeBounds") {
        if (value != 0 && value != 1) {
            _logger->save_setting(UBP_IGNORENODEBOUNDS, "UBP_ignoreNodeBounds has to be 0 or 1, setting it to 0");
            _maingoSettings->UBP_ignoreNodeBounds = false;
        }
        else {
            if (value == 0) {
                _maingoSettings->UBP_ignoreNodeBounds = false;
                _logger->save_setting(UBP_IGNORENODEBOUNDS, option + " 0");
            }
            else {
                _maingoSettings->UBP_ignoreNodeBounds = true;
                _logger->save_setting(UBP_IGNORENODEBOUNDS, option + " 1");
            }
        }
    }
    else if (option == "EC_nPoints") {
        if (value < 2) {
            _logger->save_setting(EC_NPOINTS, "EC_nPoints has to at least 2, settings it to 2");
            _maingoSettings->EC_nPoints = 2;
        }
        else {
            _maingoSettings->EC_nPoints = (unsigned)value;
            _logger->save_setting(EC_NPOINTS, option + " " + oss.str());
        }
    }
    else if (option == "LBP_verbosity") {
        if (value != 0 && value != 1 && value != 2) {
            _logger->save_setting(LBP_VERBOSITY, "LBP_verbosity has to be 0, 1 or 2, setting to 1");
            _maingoSettings->LBP_verbosity = VERB_NORMAL;
        }
        else {
            if ((int)value == 0) {
                _maingoSettings->LBP_verbosity = VERB_NONE;
            }
            else if ((int)value == 1) {
                _maingoSettings->LBP_verbosity = VERB_NORMAL;
            }
            else {
                _maingoSettings->LBP_verbosity = VERB_ALL;
            }
            _logger->save_setting(LBP_VERBOSITY, option + " " + oss.str());
        }
    }
    else if (option == "UBP_verbosity") {
        if (value != 0 && value != 1 && value != 2) {
            _logger->save_setting(UBP_VERBOSITY, "UBP_verbosity has to be 0, 1 or 2, setting to 1");
            _maingoSettings->UBP_verbosity = VERB_NORMAL;
        }
        else {
            if ((int)value == 0) {
                _maingoSettings->UBP_verbosity = VERB_NONE;
            }
            else if ((int)value == 1) {
                _maingoSettings->UBP_verbosity = VERB_NORMAL;
            }
            else {
                _maingoSettings->UBP_verbosity = VERB_ALL;
            }
            _logger->save_setting(UBP_VERBOSITY, option + " " + oss.str());
        }
    }
    else if (option == "BAB_verbosity") {
        if (value != 0 && value != 1 && value != 2) {
            _logger->save_setting(BAB_VERBOSITY, "BAB_verbosity has to be 0, 1 or 2, setting to 1");
            _maingoSettings->BAB_verbosity = VERB_NORMAL;
        }
        else {
            if ((int)value == 0) {
                _maingoSettings->BAB_verbosity = VERB_NONE;
            }
            else if ((int)value == 1) {
                _maingoSettings->BAB_verbosity = VERB_NORMAL;
            }
            else {
                _maingoSettings->BAB_verbosity = VERB_ALL;
            }
            _logger->save_setting(BAB_VERBOSITY, option + " " + oss.str());
        }
    }
    else if (option == "BAB_printFreq") {
        if (value < 1) {
            _logger->save_setting(BAB_PRINTFREQ, "BAB_printFreq has to be at least 1, setting to 1");
            _maingoSettings->BAB_printFreq = 1;
        }
        else {
            _maingoSettings->BAB_printFreq = (int)value;
            _logger->save_setting(BAB_PRINTFREQ, option + " " + oss.str());
        }
    }
    else if (option == "BAB_logFreq") {
        if (value < 1) {
            _logger->save_setting(BAB_LOGFREQ, "BAB_logFreq has to be at least 1, setting to 1");
            _maingoSettings->BAB_logFreq = 1;
        }
        else {
            _maingoSettings->BAB_logFreq = (int)value;
            _logger->save_setting(BAB_LOGFREQ, option + " " + oss.str());
        }
    }
    else if (option == "loggingDestination") {
        if (value != 0 && value != 1 && value != 2 && value != 3) {
            _logger->save_setting(OUTSTREAMVERBOSITY, "loggingDestination has to be 0, 1, 2 or 3, setting to 3");
            _maingoSettings->loggingDestination = LOGGING_FILE_AND_STREAM;
        }
        else {
            if ((int)value == 0) {
                _maingoSettings->loggingDestination = LOGGING_NONE;
            }
            else if ((int)value == 1) {
                _maingoSettings->loggingDestination = LOGGING_OUTSTREAM;
            }
            else if ((int)value == 2) {
                _maingoSettings->loggingDestination = LOGGING_FILE;
            }
            else {
                _maingoSettings->loggingDestination = LOGGING_FILE_AND_STREAM;
            }
            _logger->save_setting(OUTSTREAMVERBOSITY, option + " " + oss.str());
        }
    }
    else if (option == "writeCsv") {
        if (value != 0 && value != 1) {
            _logger->save_setting(WRITECSV, "writeCsv has to be 0 or 1, setting to 0");
            _maingoSettings->writeCsv = false;
        }
        else {
            if (value == 0) {
                _maingoSettings->writeCsv = false;
                _logger->save_setting(WRITECSV, option + " 0");
            }
            else {
                _maingoSettings->writeCsv = true;
                _logger->save_setting(WRITECSV, option + " 1");
            }
        }
    }
    else if (option == "writeJson") {
        if (value != 0 && value != 1) {
            _logger->save_setting(WRITEJSON, "writeJson has to be 0 or 1, setting to 0");
            _maingoSettings->writeJson = false;
        }
        else {
            if (value == 0) {
                _maingoSettings->writeJson = false;
                _logger->save_setting(WRITEJSON, option + " 0");
            }
            else {
                _maingoSettings->writeJson = true;
                _logger->save_setting(WRITEJSON, option + " 1");
            }
        }
    }
    else if (option == "writeResultFile") {
        if (value != 0 && value != 1) {
            _logger->save_setting(writeResultFile, "writeResultFile has to be 0 or 1, setting to 0");
            _maingoSettings->writeResultFile = false;
        }
        else {
            if (value == 0) {
                _maingoSettings->writeResultFile = false;
                _logger->save_setting(writeResultFile, option + " 0");
            }
            else {
                _maingoSettings->writeResultFile = true;
                _logger->save_setting(writeResultFile, option + " 1");
            }
        }
    }
    else if (option == "writeToLogSec") {
        if (value < 10.) {
            _logger->save_setting(WRITETOLOGSEC, "writeToLogSec has to be at least 10, setting it to default (1800)");
            _maingoSettings->writeToLogSec = 1800;
        }
        else {
            _maingoSettings->writeToLogSec = (int)value;
            _logger->save_setting(WRITETOLOGSEC, option + " " + oss.str());
        }
    }
    else if (option == "PRE_printEveryLocalSearch") {
        if (value != 0 && value != 1) {
            _logger->save_setting(PRE_PRINTEVERYLOCALSEARCH, "PRE_printEveryLocalSearch has to be 0 or 1, setting to 0");
            _maingoSettings->PRE_printEveryLocalSearch = false;
        }
        else {
            if (value == 0) {
                _maingoSettings->PRE_printEveryLocalSearch = false;
                _logger->save_setting(PRE_PRINTEVERYLOCALSEARCH, option + " 0");
            }
            else {
                _maingoSettings->PRE_printEveryLocalSearch = true;
                _logger->save_setting(PRE_PRINTEVERYLOCALSEARCH, option + " 1");
            }
        }
    }
    else if (option == "modelWritingLanguage") {
        if (value != 0 && value != 1 && value != 2) {
            _logger->save_setting(UBP_VERBOSITY, "modelWritingLanguage has to be 0, 1, 2, setting to 1");
            _maingoSettings->modelWritingLanguage = LANG_ALE;
        }
        else {
            if ((int)value == 0) {
                _maingoSettings->modelWritingLanguage = LANG_NONE;
            }
            else if ((int)value == 1) {
                _maingoSettings->modelWritingLanguage = LANG_ALE;
            }
            else if ((int)value == 2) {
                _maingoSettings->modelWritingLanguage = LANG_GAMS;
            }
            _logger->save_setting(WRITETOOTHERLANGUAGE, option + " " + oss.str());
        }
    }
    else if (option == "growing_approach") {
#ifdef HAVE_GROWING_DATASETS
        if (value != 0 && value != 1 && value != 2) {
            _logger->save_setting(GROWING_APPROACHCHOSEN, "growing_approach has to be 0, 1, or 2, setting it to default (0)");
            _maingoSettings->growing_approach = GROW_APPR_DETERMINISTIC;
        }
        else {
            if ((int)value == 0) {
                _maingoSettings->growing_approach = GROW_APPR_DETERMINISTIC;
            }
            else if ((int)value == 1) {
                _maingoSettings->growing_approach = GROW_APPR_SSEHEURISTIC;
            }
            else if ((int)value == 2) {
                _maingoSettings->growing_approach = GROW_APPR_MSEHEURISTIC;
            }
            _logger->save_setting(GROWING_APPROACHCHOSEN, option + " " + oss.str());
        }
#else
        _logger->save_setting(GROWING_APPROACHCHOSEN, "MAiNGO is used without growing datasets: changes of growing_approach will not have an effect");
#endif    // HAVE_GROWING_DATASETS
    }
    else if (option == "growing_maxTimePostprocessing") {
#ifdef HAVE_GROWING_DATASETS
        if (_maingoSettings->growing_approach > GROW_APPR_DETERMINISTIC) {
            if (value < 0.0) {
                _logger->save_setting(GROWING_MAXTIMEPOST, "growing_maxTimePostprocessing has to be at least 0, setting it to default (60)");
                _maingoSettings->growing_maxTimePostprocessing = 60.;
            }
            else {
                _maingoSettings->growing_maxTimePostprocessing = value;
                _logger->save_setting(GROWING_MAXTIMEPOST, option + " " + oss.str());
            }
        } else if (value > 0.0) {
            _logger->save_setting(GROWING_MAXTIMEPOST, "growing_maxTimePostprocessing set to 0 since GROW_APPR_DETERMINISTIC is chosen");
            _maingoSettings->growing_maxTimePostprocessing = 0.;
        }
#else
        _logger->save_setting(GROWING_MAXTIMEPOST, "MAiNGO is used without growing datasets: changes of growing_maxTimePostprocessing will not have an effect");
#endif    // HAVE_GROWING_DATASETS
    }
    else if (option == "growing_useResampling") {
#ifdef HAVE_GROWING_DATASETS
        if (value != 0 && value != 1) {
            _logger->save_setting(GROWING_USERESAMPLING, "growing_useResampling has to be 0 or 1, setting it to default (0)");
            _maingoSettings->growing_useResampling = false;
        }
        else {
            if (value == 0) {
                _maingoSettings->growing_useResampling = false;
                _logger->save_setting(GROWING_USERESAMPLING, option + " 0");
            }
            else {
                _maingoSettings->growing_useResampling = true;
                _logger->save_setting(GROWING_USERESAMPLING, option + " 1");
            }
        }
#else
        _logger->save_setting(GROWING_USERESAMPLING, "MAiNGO is used without growing datasets: changes of growing_useResampling will not have an effect");
#endif    // HAVE_GROWING_DATASETS
    }
    else if (option == "growing_shuffleData") {
#ifdef HAVE_GROWING_DATASETS
        if (value != 0 && value != 1) {
            _logger->save_setting(GROWING_SHUFFLEDATA, "growing_shuffleData has to be 0 or 1, setting it to default (1)");
            _maingoSettings->growing_shuffleData = true;
        }
        else {
            if (value == 0) {
                _maingoSettings->growing_shuffleData = false;
                _logger->save_setting(GROWING_SHUFFLEDATA, option + " 0");
            }
            else {
                _maingoSettings->growing_shuffleData = true;
                _logger->save_setting(GROWING_SHUFFLEDATA, option + " 1");
            }
        }
#else
        _logger->save_setting(GROWING_SHUFFLEDATA, "MAiNGO is used without growing datasets: changes of growing_shuffleData will not have an effect");
#endif    // HAVE_GROWING_DATASETS
    }
    else if (option == "growing_relativeSizing") {
#ifdef HAVE_GROWING_DATASETS
        if (value != 0 && value != 1) {
            _logger->save_setting(GROWING_RELATIVESIZING, "growing_relativeSizing has to be 0 or 1, setting it to default (1)");
            _maingoSettings->growing_relativeSizing = true;
        }
        else {
            if (value == 0) {
                // Check for file first: can only use absolute sizing if the required sizes are provided
                std::ifstream sizingFile("growingDatasetsSizing.txt");
                if (sizingFile.good()) {
                    _maingoSettings->growing_relativeSizing = false;
                    _logger->save_setting(GROWING_RELATIVESIZING, option + " 0");
                }
                else {
                    _logger->save_setting(GROWING_RELATIVESIZING, "Could not find sizing file growingDatasetsSizing.txt: setting growing_relativeSizing to default (1)");
                    _maingoSettings->growing_relativeSizing = true;
                }
            }
            else {
                _maingoSettings->growing_relativeSizing = true;
                _logger->save_setting(GROWING_RELATIVESIZING, option + " 1");
            }
        }
#else
        _logger->save_setting(GROWING_RELATIVESIZING, "MAiNGO is used without growing datasets: changes of growing_relativeSizing will not have an effect");
#endif    // HAVE_GROWING_DATASETS
    }
    else if (option == "growing_initPercentage") {
#ifdef HAVE_GROWING_DATASETS
        if (value < 0. || value > 1.) {
            _logger->save_setting(GROWING_INITPERCENTAGE, "growing_initPercentage  has to be between 0 and 1, setting it to default (0.1)");
            _maingoSettings->growing_initPercentage = 0.1;
        }
        else {
            _maingoSettings->growing_initPercentage = value;
            _logger->save_setting(GROWING_INITPERCENTAGE, option + " " + oss.str());
        }
#else
        _logger->save_setting(GROWING_INITPERCENTAGE, "MAiNGO is used without growing datasets: changes of growing_initPercentage will not have an effect");
#endif    // HAVE_GROWING_DATASETS
    }
    else if (option == "growing_maxSize") {
#ifdef HAVE_GROWING_DATASETS
        if (value < 0. || value > 1.) {
            _logger->save_setting(GROWING_MAXSIZE, "growing_maxSize has to be between 0 and 1, setting it to default (0.9)");
            _maingoSettings->growing_maxSize = 0.9;
        }
        else {
            _maingoSettings->growing_maxSize = value;
            _logger->save_setting(GROWING_MAXSIZE, option + " " + oss.str());
        }
#else
        _logger->save_setting(GROWING_MAXSIZE, "MAiNGO is used without growing datasets: changes of growing_maxSize will not have an effect");
#endif    // HAVE_GROWING_DATASETS
    }
    else if (option == "growing_augmentPercentage") {
#ifdef HAVE_GROWING_DATASETS
    if (value < 0. && value > 1.) {
        _logger->save_setting(GROWING_AUGMENTPERCENTAGE, "growing_augmentPercentage has to be between 0 and 1, setting it to default (0.25)");
        _maingoSettings->growing_augmentPercentage = 0.25;
    }
    else {
        _maingoSettings->growing_augmentPercentage = value;
        _logger->save_setting(GROWING_AUGMENTPERCENTAGE, option + " " + oss.str());
    }
#else
        _logger->save_setting(GROWING_AUGMENTPERCENTAGE, "MAiNGO is used without growing datasets: changes of growing_augmentPercentage will not have an effect");
#endif    // HAVE_GROWING_DATASETS
    }
    else if (option == "growing_augmentRule") {
#ifdef HAVE_GROWING_DATASETS
    AUGMENTATION_RULE defaultRule = AUG_RULE_TOLCST;
    if ((_maingoSettings->growing_approach == GROW_APPR_MSEHEURISTIC) && (value == 1 || value == 5)) {
        _logger->save_setting(GROWING_AUGMENTRULE, "growing_augmentRule cannot use SCAL(ING) when using GROW_APPR_MSEHEURISTIC, setting it to default (8)");
        _maingoSettings->growing_augmentRule = defaultRule;
    }
    else {
        if (value != 0 && value != 1 && value != 2 && value != 3 && value != 4 && value != 5 && value != 6 && value != 7 && value != 8) {
            _logger->save_setting(GROWING_AUGMENTRULE, "growing_augmentRule has to be 0, 1, 2, 3, 4, 5, 6, 7, or 8, setting it to default (8)");
            _maingoSettings->growing_augmentRule = defaultRule;
        }
        else {
            if ((int)value == 0) {
                _maingoSettings->growing_augmentRule = AUG_RULE_CONST;
            }
            else if ((int)value == 1) {
                _maingoSettings->growing_augmentRule = AUG_RULE_SCALING;
            }
            else if ((int)value == 2) {
                _maingoSettings->growing_augmentRule = AUG_RULE_OOS;
            }
            else if ((int)value == 3) {
                _maingoSettings->growing_augmentRule = AUG_RULE_COMBI;
            }
            else if ((int)value == 4) {
                _maingoSettings->growing_augmentRule = AUG_RULE_TOL;
            }
            else if ((int)value == 5) {
                _maingoSettings->growing_augmentRule = AUG_RULE_SCALCST;
            }
            else if ((int)value == 6) {
                _maingoSettings->growing_augmentRule = AUG_RULE_OOSCST;
            }
            else if ((int)value == 7) {
                _maingoSettings->growing_augmentRule = AUG_RULE_COMBICST;
            }
            else if ((int)value == 8) {
                _maingoSettings->growing_augmentRule = AUG_RULE_TOLCST;
            }
            _logger->save_setting(GROWING_AUGMENTRULE, option + " " + oss.str());
        }
    }
#else
        _logger->save_setting(GROWING_AUGMENTRULE, "MAiNGO is used without growing datasets: changes of growing_augmentRule will not have an effect");
#endif    // HAVE_GROWING_DATASETS
    }
    else if (option == "growing_augmentFreq") {
#ifdef HAVE_GROWING_DATASETS
        if (_maingoSettings->growing_augmentRule == AUG_RULE_CONST
            || _maingoSettings->growing_augmentRule == AUG_RULE_SCALCST  || _maingoSettings->growing_augmentRule == AUG_RULE_OOSCST
            || _maingoSettings->growing_augmentRule == AUG_RULE_COMBICST || _maingoSettings->growing_augmentRule == AUG_RULE_TOLCST) {
            if (value < 1.) {
                _logger->save_setting(GROWING_AUGMENTFREQ, "growing_augmentFreq has to be at least 1, setting it to default (10)");
                _maingoSettings->growing_augmentFreq = 10;
            }
            else {
                _maingoSettings->growing_augmentFreq = (int)value;
                _logger->save_setting(GROWING_AUGMENTFREQ, option + " " + oss.str());
            }
        }
        else {
            _logger->save_setting(GROWING_AUGMENTFREQ, "CONST/CST is not used within augmentation rule: changes of growing_augmentFreq will not have an effect");
        }
#else
        _logger->save_setting(GROWING_AUGMENTFREQ, "MAiNGO is used without growing datasets: changes of growing_augmentFreq will not have an effect");
#endif    // HAVE_GROWING_DATASETS
    }
    else if (option == "growing_augmentWeight") {
#ifdef HAVE_GROWING_DATASETS
        if (_maingoSettings->growing_augmentRule == AUG_RULE_SCALING || _maingoSettings->growing_augmentRule == AUG_RULE_SCALCST) {
            if (value <= 0. || value > 1.) {
                _logger->save_setting(GROWING_AUGMENTWEIGHT, "growing_augmentWeight has to be > 0 and <= 1, setting it to default (1)");
                _maingoSettings->growing_augmentWeight = 1.;
            }
            else {
                _maingoSettings->growing_augmentWeight = value;
                _logger->save_setting(GROWING_AUGMENTWEIGHT, option + " " + oss.str());
            }
        }
        else {
            _logger->save_setting(GROWING_AUGMENTWEIGHT, "SCAL(ING) is not used within augmentation rule: changes of growing_augmentWeight will not have an effect");
        }
#else
        _logger->save_setting(GROWING_AUGMENTWEIGHT, "MAiNGO is used without growing datasets: changes of growing_augmentWeight will not have an effect");
#endif    // HAVE_GROWING_DATASETS
    }
    else if (option == "growing_augmentTol") {
#ifdef HAVE_GROWING_DATASETS
        if (_maingoSettings->growing_augmentRule == AUG_RULE_TOL || _maingoSettings->growing_augmentRule == AUG_RULE_TOLCST) {
            double minValue = std::min(_maingoSettings->epsilonA, _maingoSettings->epsilonR);
            if ( value < minValue) {
                _logger->save_setting(GROWING_AUGMENTTOL, "growing_augmentTol has to be > min(epsilonA,epsilonR), setting it to 10*min(epsilonA,epsilonR) = " + std::to_string(10 * minValue));
                _maingoSettings->growing_augmentTol = 10*minValue;
            }
            else {
                _maingoSettings->growing_augmentTol = value;
                _logger->save_setting(GROWING_AUGMENTTOL, option + " " + oss.str());
            }
        }
        else {
            _logger->save_setting(GROWING_AUGMENTTOL, "TOL is not used within augmentation rule: changes of growing_augmentTol will not have an effect");
        }
#else
        _logger->save_setting(GROWING_AUGMENTTOL, "MAiNGO is used without growing datasets: changes of growing_augmentTol will not have an effect");
#endif    // HAVE_GROWING_DATASETS
    }
    else if (option == "Num_subdomains") {
        if (value < 1) {
            _logger->save_setting(NUM_SUBDOMAINS, "Num_subdomains has to be larger than 0, setting to 1024");
            _maingoSettings->Num_subdomains = 1024;
        }
        else {
                _maingoSettings->Num_subdomains = value;
                _logger->save_setting(NUM_SUBDOMAINS, option + " " + oss.str());
            }
    }
    else if (option == "Interval_arithmetic") {
        if (value != 0 && value != 1) {
            _logger->save_setting(INTERVAL_ARITHMETIC, "Interval_arithmetic has to be 0 or 1, setting to 1");
            _maingoSettings->Interval_arithmetic = 1;
        }
        else {
                _maingoSettings->Interval_arithmetic = value;
                _logger->save_setting(INTERVAL_ARITHMETIC, option + " " + oss.str());
            }
    }
    else if (option == "Subinterval_branch_strategy") {
        if (value != 0 && value != 1) {
            _logger->save_setting(SUBINTERVAL_BRANCH_STRATEGY, "Subinterval_branch_strategy has to be 0 or 1, setting to 0");
            _maingoSettings->Subinterval_branch_strategy = 0;
        }
        else {
                _maingoSettings->Subinterval_branch_strategy = value;
                _logger->save_setting(SUBINTERVAL_BRANCH_STRATEGY, option + " " + oss.str());
            }
    }
    else if (option == "Threads_per_block") {
#ifdef CUDA_INSTALLED
        if (value < 1) {
            _logger->save_setting(THREADS_PER_BLOCK, "Threads_per_block has to be larger than 0, setting to 32");
            _maingoSettings->Threads_per_block = 32;
        }
        else {
                _maingoSettings->Threads_per_block = value;
                _logger->save_setting(THREADS_PER_BLOCK, option + " " + oss.str());
            }
#else
        _logger->save_setting(THREADS_PER_BLOCK, "CUDA is not available. Threads_per_block can not be set.");
#endif
    }
    else if (option == "Center_strategy") {
        if (value != 0 && value != 1) {
            _logger->save_setting(CENTER_STRATEGY, "Center_strategy has to be 0 or 1, setting to 0");
            _maingoSettings->Center_strategy = 0;
        }
        else {
                _maingoSettings->Center_strategy = value;
                _logger->save_setting(CENTER_STRATEGY, option + " " + oss.str());
            }
    }
    else if (option == "MIN_branching_per_dim") {
        if (value < 2) {
            _logger->save_setting(MIN_BRANCHING_PER_DIM, "MIN_branching_per_dim has to be not smaller than 2, setting to 2");
            _maingoSettings->MIN_branching_per_dim = 2;
        }
        else {
                _maingoSettings->MIN_branching_per_dim = value;
                _logger->save_setting(MIN_BRANCHING_PER_DIM, option + " " + oss.str());
            }
    }
    else if (option == "TS_useLowerBoundingSubsolvers") {
        if (value != 0 && value != 1) {
            _logger->save_setting(TS_USELBS, "TS_useLowerBoundingSubsolvers has to be 0 or 1, setting to 1");
            _maingoSettings->TS_useLowerBoundingSubsolvers = true;
        }
        else {
            if (value == 0) {
                _maingoSettings->TS_useLowerBoundingSubsolvers = false;
                _logger->save_setting(TS_USELBS, option + " 0");
            }
            else {
                _maingoSettings->TS_useLowerBoundingSubsolvers = true;
                _logger->save_setting(TS_USELBS, option + " 1");
            }
        }
    }
    else if (option == "TS_useUpperBoundingSubsolvers") {
        if (value != 0 && value != 1) {
            _logger->save_setting(TS_USEUBS, "TS_useUpperBoundingSubsolvers has to be 0 or 1, setting to 0");
            _maingoSettings->TS_useUpperBoundingSubsolvers = false;
        }
        else {
            if (value == 0) {
                _maingoSettings->TS_useUpperBoundingSubsolvers = false;
                _logger->save_setting(TS_USEUBS, option + " 0");
            }
            else {
                _maingoSettings->TS_useUpperBoundingSubsolvers = true;
                _logger->save_setting(TS_USEUBS, option + " 1");
            }
        }
    }
    else if (option == "TS_parallelOBBT") {
        if (value != 0 && value != 1) {
            _logger->save_setting(TS_POBBT, "TS_parallelOBBT has to be 0 or 1, setting to 0");
            _maingoSettings->TS_parallelOBBT = false;
        }
        else {
            if (value == 0) {
                _maingoSettings->TS_parallelOBBT = false;
                _logger->save_setting(TS_POBBT, option + " 0");
            }
            else {
                _maingoSettings->TS_parallelOBBT = true;
                _logger->save_setting(TS_POBBT, option + " 1");
            }
        }
    }
    else if (option == "TS_strongBranchingThreshold") {
        if (value < 0 || value > 1) {
            _logger->save_setting(TS_STRONGBRANCHINGTHRESHOLD, "TS_strongBranchingThreshold has to be between 0. and 1., setting to 1.");
            _maingoSettings->TS_strongBranchingThreshold = 1;
        }
        else {
            _maingoSettings->TS_strongBranchingThreshold = value;
            _logger->save_setting(TS_STRONGBRANCHINGTHRESHOLD, option + " " + oss.str());
        }
    }
    else if (option == "TS_maxBranchingPower") {
        unsigned int k_max(value);
        if (double(k_max) != value) {
            _logger->save_setting(TS_MAXBRANCHINGPOWER, "TS_maxBranchingPower has to be a positive integer, setting to 1");
            _maingoSettings->TS_maxBranchingPower = 4;
        }
        else {
            if (k_max > 14) {
                _logger->print_message("Warning, setting TS_maxBranchingPower higher than 14, more than 10000 nodes may be created for every second stage branching!", VERB_NONE, TS_MAXBRANCHINGPOWER);
            }
            _maingoSettings->TS_maxBranchingPower = k_max;
            _logger->save_setting(TS_MAXBRANCHINGPOWER, option + " " + oss.str());
        }
    }
    else {
        _logger->save_setting(UNKNOWN_SETTING, "Could not find setting " + option + ". Proceeding.");
        return false;
    }

    return true;
}
