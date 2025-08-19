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
// function returning the value of a desired option
double
MAiNGO::get_option(const std::string& option) const
{
    if (option == "epsilonA") {
        return _maingoSettings->epsilonA;
    }
    else if (option == "epsilonR") {
        return _maingoSettings->epsilonR;
    }
    else if (option == "deltaIneq") {
        return _maingoSettings->deltaIneq;
    }
    else if (option == "deltaEq") {
        return _maingoSettings->deltaEq;
    }
    else if (option == "relNodeTol") {
        return _maingoSettings->relNodeTol;
    }
    else if (option == "BAB_maxNodes") {
        return _maingoSettings->BAB_maxNodes;
    }
    else if (option == "BAB_maxIterations") {
        return _maingoSettings->BAB_maxIterations;
    }
    else if (option == "maxTime") {
        return _maingoSettings->maxTime;
    }
    else if (option == "confirmTermination") {
        return _maingoSettings->confirmTermination;
    }
    else if (option == "terminateOnFeasiblePoint") {
        return _maingoSettings->terminateOnFeasiblePoint;
    }
    else if (option == "targetLowerBound") {
        return _maingoSettings->targetLowerBound;
    }
    else if (option == "targetUpperBound") {
        return _maingoSettings->targetUpperBound;
    }
    else if (option == "PRE_maxLocalSearches") {
        return _maingoSettings->PRE_maxLocalSearches;
    }
    else if (option == "PRE_obbtMaxRounds") {
        return _maingoSettings->PRE_obbtMaxRounds;
    }
    else if (option == "PRE_pureMultistart") {
        return _maingoSettings->PRE_pureMultistart;
    }
    else if (option == "BAB_nodeSelection") {
        return _maingoSettings->BAB_nodeSelection;
    }
    else if (option == "BAB_branchVariable") {
        return _maingoSettings->BAB_branchVariable;
    }
    else if (option == "BAB_alwaysSolveObbt") {
        return _maingoSettings->BAB_alwaysSolveObbt;
    }
    else if (option == "BAB_obbtDecayCoefficient") {
        return _maingoSettings->BAB_obbtDecayCoefficient;
    }
    else if (option == "BAB_probing") {
        return _maingoSettings->BAB_probing;
    }
    else if (option == "BAB_dbbt") {
        return _maingoSettings->BAB_dbbt;
    }
    else if (option == "BAB_constraintPropagation") {
        return _maingoSettings->BAB_constraintPropagation;
    }
    else if (option == "LBP_solver") {
        return _maingoSettings->LBP_solver;
    }
    else if (option == "Num_subdomains") {
        return _maingoSettings->Num_subdomains;
    }
    else if (option == "Interval_arithmetic") {
        return _maingoSettings->Interval_arithmetic;
    }
    else if (option == "Subinterval_branch_strategy") {
        return _maingoSettings->Subinterval_branch_strategy;
    }
    else if (option == "Center_strategy") {
        return _maingoSettings->Center_strategy;
    }
    else if (option == "MIN_branching_per_dim") {
        return _maingoSettings->MIN_branching_per_dim;
    }
    else if (option == "Threads_per_block") {
        return _maingoSettings->Threads_per_block;
    }
    else if (option == "LBP_linPoints") {
        return _maingoSettings->LBP_linPoints;
    }
    else if (option == "LBP_subgradientIntervals") {
        return _maingoSettings->LBP_subgradientIntervals;
    }
    else if (option == "LBP_obbtMinImprovement") {
        return _maingoSettings->LBP_obbtMinImprovement;
    }
    else if (option == "LBP_activateMoreScaling") {
        return _maingoSettings->LBP_activateMoreScaling;
    }
    else if (option == "LBP_addAuxiliaryVars") {
        return _maingoSettings->LBP_addAuxiliaryVars;
    }
    else if (option == "LBP_minFactorsForAux") {
        return _maingoSettings->LBP_minFactorsForAux;
    }
    else if (option == "LBP_maxNumberOfAddedFactors") {
        return _maingoSettings->LBP_maxNumberOfAddedFactors;
    }
    else if (option == "MC_mvcompUse") {
        return _maingoSettings->MC_mvcompUse;
    }
    else if (option == "MC_mvcompTol") {
        return _maingoSettings->MC_mvcompTol;
    }
    else if (option == "MC_envelTol") {
        return _maingoSettings->MC_envelTol;
    }
    else if (option == "UBP_solverPreprocessing") {
        return _maingoSettings->UBP_solverPreprocessing;
    }
    else if (option == "UBP_maxStepsPreprocessing") {
        return _maingoSettings->UBP_maxStepsPreprocessing;
    }
    else if (option == "UBP_maxTimePreprocessing") {
        return _maingoSettings->UBP_maxTimePreprocessing;
    }
    else if (option == "UBP_solverBab") {
        return _maingoSettings->UBP_solverBab;
    }
    else if (option == "UBP_maxStepsBab") {
        return _maingoSettings->UBP_maxStepsBab;
    }
    else if (option == "UBP_maxTimeBab") {
        return _maingoSettings->UBP_maxTimeBab;
    }
    else if (option == "UBP_ignoreNodeBounds") {
        return _maingoSettings->UBP_ignoreNodeBounds;
    }
    else if (option == "EC_nPoints") {
        return _maingoSettings->EC_nPoints;
    }
    else if (option == "LBP_verbosity") {
        return _maingoSettings->LBP_verbosity;
    }
    else if (option == "UBP_verbosity") {
        return _maingoSettings->UBP_verbosity;
    }
    else if (option == "BAB_verbosity") {
        return _maingoSettings->BAB_verbosity;
    }
    else if (option == "BAB_printFreq") {
        return _maingoSettings->BAB_printFreq;
    }
    else if (option == "BAB_logFreq") {
        return _maingoSettings->BAB_logFreq;
    }
    else if (option == "loggingDestination") {
        return _maingoSettings->loggingDestination;
    }
    else if (option == "writeCsv") {
        return _maingoSettings->writeCsv;
    }
    else if (option == "writeJson") {
        return _maingoSettings->writeJson;
    }
    else if (option == "writeResultFile") {
        return _maingoSettings->writeResultFile;
    }
    else if (option == "writeToLogSec") {
        return _maingoSettings->writeToLogSec;
    }
    else if (option == "PRE_printEveryLocalSearch") {
        return _maingoSettings->PRE_printEveryLocalSearch;
    }
    else if (option == "modelWritingLanguage") {
        return _maingoSettings->modelWritingLanguage;
    }
    else if (option == "growing_approach") {
        return _maingoSettings->growing_approach;
    }
    else if (option == "growing_maxTimePostprocessing") {
        return _maingoSettings->growing_maxTimePostprocessing;
    }
    else if (option == "growing_useResampling") {
        return _maingoSettings->growing_useResampling;
    }
    else if (option == "growing_shuffleData") {
        return _maingoSettings->growing_shuffleData;
    }
    else if (option == "growing_relativeSizing") {
        return _maingoSettings->growing_relativeSizing;
    }
    else if (option == "growing_initPercentage") {
        return _maingoSettings->growing_initPercentage;
    }
    else if (option == "growing_augmentPercentage") {
        return _maingoSettings->growing_augmentPercentage;
    }
    else if (option == "growing_maxSize") {
        return _maingoSettings->growing_maxSize;
    }
    else if (option == "growing_augmentRule") {
        return _maingoSettings->growing_augmentRule;
    }
    else if (option == "growing_augmentFreq") {
        return _maingoSettings->growing_augmentFreq;
    }
    else if (option == "growing_augmentWeight") {
        return _maingoSettings->growing_augmentWeight;
    }
    else if (option == "growing_augmentTol") {
        return _maingoSettings->growing_augmentTol;
    }
    throw MAiNGOException("Error getting option: unknown option " + option + ".");
}