/**********************************************************************************
 * Copyright (c) 2021 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#pragma once


extern "C" {


/**
  * @brief Struct used for communication options to MAiNGO via the C-API
  **/
struct OptionPair {
    const char* optionName; /*!< The name of the option to be changed*/
    double optionValue;     /*!< The value this option is to be set to*/
};

/**
  * @brief Main function with C-API for calling MAiNGO for passing the problem by string
  *
  * Parses the string, calls the branch-and-bound solver and returns the result.
  *
  * @param[in] aleString is a valid string containing the problem definition in ALE syntax
  * @param[out] objectiveValue is an allocated pointer that is used to receive the objective value [allocated outside]
  * @param[out] solutionPoint is the solution of the optimization [allocated outside]
  * @param[in ] solutionPointLength is the allocated size of the solutionPoint array, must be greater than or equal to the number of optimization variables
  * @param[out] cpuSolutionTime is the cpu time needed to solve the problem [allocated outside]
  * @param[out] wallSolutionTime is the wall time needed to solve the problem [allocated outside]
  * @param[out] upperBound is the upper bound of the objective function [allocated outside]
  * @param[out] lowerBound is the lower bound of the objective function [allocated outside]
  * @param[in]  resultFileName is the name of the file that results are saved into
  * @param[in]  logFileName is the name of the file that logs are saved into
  * @param[in]  settingsFileName is the name of the file that logs are saved into
  * @param[in]  options are pairs of C-string and double values for options that are forwarded to MAiNGO
  * @param[in]  numberOptions is the length of the array passed in options
  * @return     returns either an integer corresponding to the MAiNGO return code in case of success, or -1 in case an unhandled exception occurred
  **/

int solve_problem_from_ale_string_with_maingo(const char* aleString, double* objectiveValue, double* solutionPoint, unsigned solutionPointLength, double* cpuSolutionTime, double* wallSolutionTime, double* upperBound, double* lowerBound, const char* resultFileName, const char* logFileName, const char* settingsFileName, const OptionPair* options, unsigned numberOptions);
}