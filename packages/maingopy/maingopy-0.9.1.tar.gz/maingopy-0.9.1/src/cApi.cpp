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

#include "cApi.h"
#include "MAiNGO.h"
#include "aleModel.h"

#include "programParser.h"

#include "symbol_table.hpp"

#include <iostream>
#include <memory>


/////////////////////////////////////////////
// Allows calling MAiNGO from C
extern "C" int
solve_problem_from_ale_string_with_maingo(const char* aleString, double* objectiveValue, double* solutionPoint, unsigned solutionPointLength,
                                          double* cpuSolutionTime, double* wallSolutionTime, double* upperBound, double* lowerBound,
                                          const char* resultFileName, const char* logFileName, const char* settingsFileName,
                                          const OptionPair* options, unsigned numberOptions)
{

    // Define model and MAiNGO pointers
    std::shared_ptr<maingo::AleModel> myModel;
    std::shared_ptr<maingo::MAiNGO> myMAiNGO;

    ale::symbol_table symbols;
    try {
        //convert given string to ifstream
        std::istringstream input(aleString);
        std::ofstream output;
        if (true) {


            maingo::ProgramParser par(input, symbols);
            maingo::Program prog;
            par.parse(prog);

            if (par.fail()) {
                throw std::invalid_argument("  Error: Encountered an error while parsing the problem file");
            }
            myModel  = std::make_shared<maingo::AleModel>(prog, symbols);    // define a model object implemented in ale interface
            myMAiNGO = std::make_shared<maingo::MAiNGO>(myModel);            // define a MAiNGO object with the corresponding model
        }
        else {
            throw std::invalid_argument("  Error: Could not convert given problem string");
        }
    }
    catch (std::exception& e) {

        std::cerr << std::endl
                  << "  Encountered exception:" << std::endl
                  << e.what() << std::endl;
    }

    catch (...) {

        std::cerr << std::endl
                  << "  Encountered an unknown fatal error during initialization. Terminating." << std::endl;
    }
    // Set output file names
    myMAiNGO->set_result_file_name(std::string(resultFileName));
    myMAiNGO->set_log_file_name(std::string(logFileName));
    // Read settings from file and set further options
    myMAiNGO->read_settings(std::string(settingsFileName));
    for (unsigned i = 0; i < numberOptions; i++) {
        myMAiNGO->set_option(options[i].optionName, options[i].optionValue);
    }


    // Solve the problem
    maingo::RETCODE maingoStatus;
    try {
        maingoStatus = myMAiNGO->solve();
    }
    catch (std::exception& e) {

        std::cerr << std::endl
                  << e.what() << std::endl;

        return (-1);
    }
    catch (...) {

        std::cerr << std::endl
                  << "  Encountered an unknown fatal error during solution. Terminating." << std::endl;
        return (-1);
    }

    // Get solution info
    if ((maingoStatus == maingo::GLOBALLY_OPTIMAL) || (maingoStatus == maingo::FEASIBLE_POINT)) {
        *objectiveValue            = myMAiNGO->get_objective_value();
        unsigned numberOfVariables = myMAiNGO->get_solution_point().size();
        if (solutionPointLength >= numberOfVariables) {
            for (size_t i = 0; i < numberOfVariables; i++) {
                solutionPoint[i] = myMAiNGO->get_solution_point()[i];
            }
        }
    }


    *cpuSolutionTime  = myMAiNGO->get_cpu_solution_time();
    *wallSolutionTime = myMAiNGO->get_wallclock_solution_time();
    *upperBound       = myMAiNGO->get_final_abs_gap() + myMAiNGO->get_final_LBD();
    *lowerBound       = myMAiNGO->get_final_LBD();

    return maingoStatus;
}