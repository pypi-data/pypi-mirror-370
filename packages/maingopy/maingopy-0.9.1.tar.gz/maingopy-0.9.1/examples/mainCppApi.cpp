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
#include "instrumentor.h"
#include "mpiUtilities.h"

#include "01_BasicExample/problem.h"

// #include "02_FlowsheetPowerCycle/problemCaseStudy2LCOE.h"

// #include "03_Biobjective/problemEpsCon.h"

/**
 * The following examples require that the CMake flag MAiNGO_build_melon is set to true.
 * Note that the MeLOn toolbox is not compatible with Intel compilers due to missing C++17 features.
 */
// #include "04_ArtificalNeuralNetwork/problemReducedSpace.h"
// #include "04_ArtificalNeuralNetwork/problemFullSpace.h"

// #include "05_GaussianProcess/problemGpReducedSpace.h"
// #include "05_GaussianProcess/problemGpFullspace.h"
// #include "05_GaussianProcess/problemGpFullspacePrediction.h"
// #include "05_GaussianProcess/problemGpFullspaceVariance.h"

// #include "06_BayesianOptimization/problemBayesianOptimizationReducedSpace.h"
// #include "06_BayesianOptimization/problemBayesianOptimizationFullspace.h"

// #include "09_MultifidelityGaussianProcess/problemMulfilGpReducedSpace.h"

/**
 * The following example requires that the CMake flag MAiNGO_use_growing_datasets is set to true.
 */
// #include "07_GrowingDatasets/problem_growingDatasets_simple.h"

// #include "08_TwoStage/CHP_sizing.h"

#include <memory>


/**
 * @brief Main function managing MAiNGO for standalone use
 *
 * Retrieves settings and calls the branch-and-bound solver
 */
int
main(int argc, char *argv[])
{
    PROFILE_SESSION("MAiNGOcpp");
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

    // Define model and MAiNGO objects
    std::shared_ptr<Model> myModel;
    std::unique_ptr<maingo::MAiNGO> myMAiNGO;
    try {
        myModel  = std::make_shared<Model>();                                       // Define a model object implemented in problem.h
        myMAiNGO = std::unique_ptr<maingo::MAiNGO>(new maingo::MAiNGO(myModel));    // Define a MAiNGO object with the corresponding model
    }
    catch (std::exception &e) {
        MAiNGO_IF_BAB_MANAGER
            std::cerr
                << std::endl
                << e.what() << std::endl;
        MAiNGO_END_IF
        MAiNGO_MPI_FINALIZE return (-1);
    }
    catch (...) {
        MAiNGO_IF_BAB_MANAGER
            std::cerr
                << std::endl
                << "  Encountered an unknown fatal error during initialization. Terminating." << std::endl;
        MAiNGO_END_IF
        MAiNGO_MPI_FINALIZE return (-1);
    }

    // Read settings from file
    if (argc >= 2) {
        if (argc > 2) {
            std::cout << "  Warning: Accept only the settings file name as input. Ignoring additional command line arguments." << std::endl
                      << std::endl;
        }
        const std::string settingsFileName = argv[1];
        myMAiNGO->read_settings(settingsFileName); // Attempt to read from a settings file with the given name in the current working directory
    } else {
        myMAiNGO->read_settings(); // Attempt to read from a settings file with the default name (MAiNGOSettings.txt) in the current working directory
    }
    // myMAiNGO->set_log_file_name("my_log_file.log");                                 // Set name of log file; default name is maingo.log
    // myMAiNGO->set_iterations_csv_file_name("my_csv_iterations_file.csv");           // Set names of csv iteration files; default name is iterations.csv
    // myMAiNGO->set_solution_and_statistics_csv_file_name("my_csv_general_file.csv"); // Set names of csv with general information on solution and statistics; default name is statisticsAndSolution.csv
    // myMAiNGO->set_json_file_name("my_json_file.json");                              // Set names of json file with solution and statistics; default name is statisticsAndSolution.json

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
        // Use this function instead of solve() for solving bi-objective problems using the epsilon-constraint method (don't forget to include the example problem in problemEpsCon.h):
        // maingoStatus = myMAiNGO->solve_epsilon_constraint();
    }
    catch (std::exception &e) {
        MAiNGO_IF_BAB_MANAGER
            std::cerr
                << std::endl
                << e.what() << std::endl;
        MAiNGO_END_IF
        MAiNGO_MPI_FINALIZE return (-1);
    }
    catch (...) {
        MAiNGO_IF_BAB_MANAGER
            std::cerr
                << std::endl
                << "  Encountered an unknown fatal error during solution. Terminating." << std::endl;
        MAiNGO_END_IF
        MAiNGO_MPI_FINALIZE return (-1);
    }

    MAiNGO_MPI_FINALIZE return 0;
}
