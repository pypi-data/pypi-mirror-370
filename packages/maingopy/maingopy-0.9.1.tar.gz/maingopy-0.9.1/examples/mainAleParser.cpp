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
#include "aleModel.h"
#include "mpiUtilities.h"
#include "programParser.h"

#include "symbol_table.hpp"

#include <memory>

/**
 * @brief Main function managing MAiNGO for standalone use
 *
 * Retrieves settings and calls the branch-and-bound solver
 */
int
main(int argc, char *argv[])
{

#ifdef HAVE_MAiNGO_MPI
    // Initialize MPI and corresponding variable
    MPI_Init(&argc, &argv);
    int _rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &_rank);
    // Mute cout for workers to avoid multiple outputs
    std::ostringstream mutestream;
    std::streambuf *coutBuf = std::cout.rdbuf();
    std::streambuf *cerrBuf = std::cerr.rdbuf();
    MAiNGO_IF_BAB_WORKER
        std::cout.rdbuf(mutestream.rdbuf());
        std::cerr.rdbuf(mutestream.rdbuf());
    MAiNGO_END_IF
#endif

    // Define model and MAiNGO pointers
    std::shared_ptr<maingo::AleModel> myModel;
    std::shared_ptr<maingo::MAiNGO> myMAiNGO;

    ale::symbol_table symbols;
    try {
        std::string problemFile = "problem.txt";
        if (argc >= 2) {
            problemFile = argv[1];
        }
        std::cout << "Reading problem from file " << problemFile << ".\n";
        std::ifstream input(problemFile);
        if (input.is_open()) {
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
            throw std::invalid_argument("  Error: Could not open problem file " + problemFile);
        }
        input.close();
    }
    catch (std::exception &e) {
        MAiNGO_IF_BAB_MANAGER
            std::cerr << std::endl
                      << "  Encountered exception:" << std::endl
                      << e.what() << std::endl;
        MAiNGO_END_IF
        MAiNGO_MPI_FINALIZE return (-1);
    }
    catch (...) {
        MAiNGO_IF_BAB_MANAGER
            std::cerr << std::endl
                      << "  Encountered an unknown fatal error during initialization. Terminating." << std::endl;
        MAiNGO_END_IF
        MAiNGO_MPI_FINALIZE return (-1);
    }

    // Read settings from file
    if (argc >= 3) {
        if (argc > 3) {
            std::cout << "  Warning: Accept only the problem and settings file names as input. Ignoring additional command line arguments." << std::endl
                      << std::endl;
        }
        const std::string settingsFileName = argv[2];
        myMAiNGO->read_settings(settingsFileName); // Attempt to read from a settings file with the given name in the current working directory
    } else {
        myMAiNGO->read_settings(); // Attempt to read from a settings file with the default name (MAiNGOSettings.txt) in the current working directory
    }
    // myMAiNGO->set_log_file_name("my_log_file.log");                                 // Set name of log file; default name is maingo.log
    // myMAiNGO->set_iterations_csv_file_name("my_csv_iterations_file.csv");           // Set names of csv iteration files; default name is iterations.csv
    // myMAiNGO->set_solution_and_statistics_csv_file_name("my_csv_general_file.csv"); // Set names of csv with general information on solution and statistics; default name is statisticsAndSolution.csv
    // myMAiNGO->set_json_file_name("my_json_file.json");                              // Set names of json file with solution and statistics; default name is statisticsAndSolution.json

    // Print MANGO and copyright
    // myMAiNGO->print_MAiNGO(std::cout);

#ifdef HAVE_MAiNGO_MPI
    // Turn on output again
    std::cout.rdbuf(coutBuf);
    std::cerr.rdbuf(cerrBuf);
#endif

    // Solve the problem
    maingo::RETCODE maingoStatus;
    try {
        // Optional: Write current model to file in a given modeling language (currently GAMS or ALE).
        // Alternativey, this is also done by solve() when using the MAiNGO Setting writeToOtherLanguage, although with less possibility for customization of the output.
        MAiNGO_IF_BAB_MANAGER
            // myMAiNGO->write_model_to_file_in_other_language(maingo::WRITING_LANGUAGE::LANG_ALE,"my_problem_file_MAiNGO.txt","dummySolverName(onlyUsedWhenWritingGAMS)",/*useMinMax*/true,/*useTrig*/true,/*ignoreBoundingFuncs*/true,/*useRelOnly*/false);
        MAiNGO_END_IF
        maingoStatus = myMAiNGO->solve();
    }
    catch (std::exception &e) {
        MAiNGO_IF_BAB_MANAGER
            std::cerr << std::endl
                      << e.what() << std::endl;
        MAiNGO_END_IF
        MAiNGO_MPI_FINALIZE return (-1);
    }
    catch (...) {
        MAiNGO_IF_BAB_MANAGER
            std::cerr << std::endl
                      << "  Encountered an unknown fatal error during solution. Terminating." << std::endl;
        MAiNGO_END_IF
        MAiNGO_MPI_FINALIZE return (-1);
    }

    MAiNGO_MPI_FINALIZE return 0;
}