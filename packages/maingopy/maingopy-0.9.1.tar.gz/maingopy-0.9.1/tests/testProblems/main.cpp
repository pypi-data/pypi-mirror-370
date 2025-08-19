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

#include "mpiUtilities.h"


#include "problem_Henry_RS_IdealGasFlash.h"
#include "problem_LP.h"
#include "problem_LP_random.h"
#include "problem_LP_mod.h"
#include "problem_LP_IN_RO.h"
#include "problem_MILP.h"
#include "problem_NRTL_RS_Flash.h"
#include "problem_OME_RS_IdealGasFlash.h"
#include "problem_QP.h"
#include "problem_bin1.h"
#include "problem_case1_lcoe.h"
#include "problem_case2_lcoe.h"
#include "problem_case3_wnet.h"
#include "problem_ex8_1_3.h"
#include "problem_growingDatasets_AVM.h"
#include "problem_growingDatasets_simple.h"
#include "problem_int1.h"
#include "problem_nonsmooth.h"
#include "problem_sudoku.h"
#include "problem_unusedVars.h"
#include "problem_relaxOnly.h"
#include "problem_chance.h"
#include "problem_wallfix.h"
#include "problem_Squash.h"
#include "problem_st_e27.h"
#include "problem_1d.h"
#include "problem_nonlinearCons.h"
#include "problem_CHP_sizing_Ns1.h"
#include "problem_twoStageIP.h"
#include "problem_SubdomainLowerBounding.h"

#include "MAiNGO.h"
#include "getTime.h"

#ifdef HAVE_MAiNGO_PARSER
#include "aleModel.h"
#include "programParser.h"
#include "symbol_table.hpp"
#endif

#include <iostream>
#include <memory>
#include <string>


#if defined(HAVE_CPLEX) || defined(HAVE_GUROBI)
#define HAVE_QP_SOLVER 1
#define HAVE_MILP_SOLVER 1
#endif


bool
print_testResults(std::shared_ptr<maingo::MAiNGO> theMAiNGO, maingo::RETCODE maingoStatus, const double correctObjectiveValue, const double epsilonA, const double epsilonR, double &CPUofAllProcesses)
{
    bool correctA = true;
    bool correctR = true;

#ifdef HAVE_MAiNGO_MPI
    int _rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &_rank);
#endif

    MAiNGO_IF_BAB_MANAGER
        CPUofAllProcesses += theMAiNGO->get_cpu_solution_time();
        if (maingoStatus != maingo::RETCODE::GLOBALLY_OPTIMAL) {
            std::cout << "ERROR - model did not converge globally. Return code: " << maingoStatus << std::endl;
            correctA = false;
            correctR = false;
        }
        else {
            if (std::fabs(theMAiNGO->get_objective_value() - correctObjectiveValue) > epsilonA) {
                correctA = false;
            }
            if ((std::fabs(theMAiNGO->get_objective_value() - correctObjectiveValue)) > epsilonR * std::fabs(theMAiNGO->get_objective_value())) {
                correctR = false;
            }
            if (correctA || correctR) {
                std::cout << "OK  "
                          << " Time needed: " << std::setw(7) << std::right << theMAiNGO->get_cpu_solution_time() << "s";
                std::cout << " Time needed (wallclock): " << std::setw(7) << std::right << theMAiNGO->get_wallclock_solution_time() << "s";
                std::cout << std::endl;
            }
            else {
                if (!correctA) {
                    std::cout << "ERROR - incorrect objective value (absolute tolerance): " << theMAiNGO->get_objective_value() << " instead of " << correctObjectiveValue << std::endl;
                }
                else if (!correctR) {
                    std::cout << "ERROR - incorrect objective value (relative tolerance): " << theMAiNGO->get_objective_value() << " instead of " << correctObjectiveValue << std::endl;
                }
            }
        }
    MAiNGO_END_IF
    return (correctA || correctR);
}

bool
run_test(std::shared_ptr<maingo::MAiNGO> theMAiNGO, const std::string &name, const double correctObjectiveValue, const double epsilonA, const double epsilonR, double &CPUofAllProcesses,
         bool testAle = false, bool useMinMax = true, bool useTrig = true, bool ignoreBoundingFuncs = false, bool useRelOnly = true)
{

#ifdef HAVE_MAiNGO_MPI
    int _rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &_rank);
#endif

    std::cout << std::left << std::setw(65) << name << ": ";
    maingo::RETCODE solverStatus; 
    solverStatus = theMAiNGO->solve();
    const maingo::RETCODE maingoStatus = solverStatus;
    MAiNGO_MPI_BARRIER const bool default_success = print_testResults(theMAiNGO, maingoStatus, correctObjectiveValue, epsilonA, epsilonR, CPUofAllProcesses);
    

#ifdef HAVE_MAiNGO_PARSER
    MAiNGO_IF_BAB_MANAGER
        theMAiNGO->write_model_to_file_in_other_language(maingo::WRITING_LANGUAGE::LANG_ALE, name + ".txt", "", useMinMax, useTrig, ignoreBoundingFuncs, useRelOnly);
    MAiNGO_END_IF
    MAiNGO_MPI_BARRIER
        std::shared_ptr<maingo::AleModel>
            myModel;
    std::ifstream input(name + ".txt");
    ale::symbol_table symbols;

    try {
        maingo::ProgramParser par(input, symbols);
        maingo::Program prog;
        par.parse(prog);
        if (par.fail()) {
            throw std::invalid_argument("Encountered an error while parsing the problem file.");
        }
        myModel = std::make_shared<maingo::AleModel>(prog, symbols);
    }
    catch (std::exception &e) {
        MAiNGO_IF_BAB_MANAGER
            std::cout << std::left << std::setw(65) << name + " (parsed)"
                      << ": ERROR - " << e.what() << std::endl;
        MAiNGO_END_IF
        MAiNGO_MPI_FINALIZE return false;
    }
    catch (...) {
        MAiNGO_IF_BAB_MANAGER
            std::cout << std::left << std::setw(65) << name + " (parsed)"
                      << ": ERROR - Encountered an unknown fatal error." << std::endl;
        MAiNGO_END_IF
        MAiNGO_MPI_FINALIZE return false;
    }

    theMAiNGO->set_model(myModel);
    std::cout << std::left << std::setw(65) << name + " (parsed)"
              << ": ";
    const maingo::RETCODE parsed_maingoStatus = theMAiNGO->solve();
    const bool parsed_success                 = print_testResults(theMAiNGO, parsed_maingoStatus, correctObjectiveValue, epsilonA, epsilonR, CPUofAllProcesses);
    return (default_success && parsed_success);
#else
    return default_success;
#endif
}


/**
 * @brief Main function for testing MAiNGO on given instances
 *
 * Sets options and calls the branch-and-bound solver
 */
int
main(int argc, char *argv[])
{

#ifdef HAVE_MAiNGO_MPI
    // Initialize MPI stuff
    MPI_Init(&argc, &argv);
    int _rank;
    int nProcs;
    MPI_Comm_rank(MPI_COMM_WORLD, &_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nProcs);
#endif
    int exceptionCounter = 0;
    // Define model and MAiNGO objects
    std::shared_ptr<Model_bin1> myModel_bin1;
    std::shared_ptr<Model_int1> myModel_int1;
    std::shared_ptr<Model_nonsmooth> myModel_nonsmooth;
    std::shared_ptr<Model_case1_lcoe> myModel_case1_lcoe;
    std::shared_ptr<Model_case2_lcoe> myModel_case2_lcoe;
    std::shared_ptr<Model_case3_wnet> myModel_case3_wnet;
    std::shared_ptr<Model_ex8_1_3> myModel_ex8_1_3;
    std::shared_ptr<Model_Henry_RS_IdealGasFlash> myModel_Henry_RS_IdealGasFlash;
    std::shared_ptr<Model_NRTL_RS_Flash> myModel_NRTL_RS_Flash;
    std::shared_ptr<Model_OME_RS_IdealGasFlash> myModel_OME_RS_IdealGasFlash;
    std::shared_ptr<Model_unusedVars> myModel_unusedVars;
    std::shared_ptr<Model_LP> myModel_LP;
    std::shared_ptr<Model_LP_IN_RO> myModel_LP_IN_RO;
    std::shared_ptr<Model_LP_mod> myModel_LP_mod;
    std::shared_ptr<Model_LP_random> myModel_LP_random;
    std::shared_ptr<Model_QP> myModel_QP;
    std::shared_ptr<Model_MILP> myModel_MILP;
    std::shared_ptr<Model_MILP_sudoku> myModel_MILP_sudoku;
    std::shared_ptr<Model_growing_simple> myModel_growing_simple;
    std::shared_ptr<Model_growing_AVM> myModel_growing_AVM;
    std::shared_ptr<Model_relaxOnly> myModel_relaxOnly;
    std::shared_ptr<Model_chance> myModel_chance;
    std::shared_ptr<Model_wallfix> myModel_wallfix;
    std::shared_ptr<Model_Squash> myModel_Squash;
    std::shared_ptr<Model_st_e27> myModel_st_e27;
    std::shared_ptr<Model_1d> myModel_1d;
    std::shared_ptr<Model_nonlinearCons> myModel_nonlinearCons;
    std::shared_ptr<CHP_sizing_problem> myModel_CHP_sizing;
    std::shared_ptr<TwoStageIP_problem> myModel_twoStageIP;
    std::shared_ptr<Model_SubdomainLB> myModel_SubdomainLB;

    std::shared_ptr<maingo::MAiNGO> myMAiNGO;
    try {
        myModel_bin1                   = std::make_shared<Model_bin1>();
        myModel_int1                   = std::make_shared<Model_int1>();
        myModel_nonsmooth              = std::make_shared<Model_nonsmooth>();
        myModel_case1_lcoe             = std::make_shared<Model_case1_lcoe>();
        myModel_case2_lcoe             = std::make_shared<Model_case2_lcoe>();
        myModel_case3_wnet             = std::make_shared<Model_case3_wnet>();
        myModel_ex8_1_3                = std::make_shared<Model_ex8_1_3>();
        myModel_Henry_RS_IdealGasFlash = std::make_shared<Model_Henry_RS_IdealGasFlash>();
        myModel_NRTL_RS_Flash          = std::make_shared<Model_NRTL_RS_Flash>();
        myModel_OME_RS_IdealGasFlash   = std::make_shared<Model_OME_RS_IdealGasFlash>();
        myModel_unusedVars             = std::make_shared<Model_unusedVars>();
        myModel_LP                     = std::make_shared<Model_LP>();
        myModel_LP_random              = std::make_shared<Model_LP_random>(50, 1);
        myModel_LP_IN_RO               = std::make_shared<Model_LP_IN_RO>();
        myModel_LP_mod                 = std::make_shared<Model_LP_mod>();
        myModel_MILP                   = std::make_shared<Model_MILP>();
        myModel_QP                     = std::make_shared<Model_QP>();
        myModel_MILP_sudoku            = std::make_shared<Model_MILP_sudoku>();
        myModel_relaxOnly              = std::make_shared<Model_relaxOnly>();
        myModel_chance                 = std::make_shared<Model_chance>();
        myModel_wallfix                = std::make_shared<Model_wallfix>();
        myModel_Squash                 = std::make_shared<Model_Squash>();
        myModel_st_e27                 = std::make_shared<Model_st_e27>();
        myModel_1d                     = std::make_shared<Model_1d>();
        myModel_nonlinearCons          = std::make_shared<Model_nonlinearCons>();
        myModel_growing_simple         = std::make_shared<Model_growing_simple>();    // Define a model object implemented in problem_growingDatasets_simple.h
        myModel_growing_AVM            = std::make_shared<Model_growing_AVM>();       // Define a model object implemented in problem_growingDatasets_AVM.h
        myModel_CHP_sizing             = std::make_shared<CHP_sizing_problem>();
        myModel_twoStageIP             = std::make_shared<TwoStageIP_problem>();
        myModel_SubdomainLB            = std::make_shared<Model_SubdomainLB>();
        // Start with problem_bin1 and initialize MAiNGO object
        myMAiNGO = std::shared_ptr<maingo::MAiNGO>(new maingo::MAiNGO(myModel_bin1));
    }
    catch (std::exception &e) {
        exceptionCounter++;
        MAiNGO_IF_BAB_MANAGER
            std::cerr << std::endl
                      << e.what() << std::endl;
        MAiNGO_END_IF
        MAiNGO_MPI_FINALIZE return -1;
    }
    catch (...) {
        exceptionCounter++;
        MAiNGO_IF_BAB_MANAGER
            std::cerr << std::endl
                      << "Encountered an unknown fatal error during initialization. Terminating." << std::endl;
        MAiNGO_END_IF
        MAiNGO_MPI_FINALIZE return -1;
    }

#ifdef HAVE_MAiNGO_MPI
    // Mute cout for workers
    std::ostringstream mutestream;
    std::streambuf *coutBuf = std::cout.rdbuf();
    MAiNGO_IF_BAB_WORKER
        std::cout.rdbuf(mutestream.rdbuf());    // Note that all workers would return "ERROR - model did not converge globally."
        MAiNGO_ELSE
            std::cout
                << std::endl
                << "Running testproblems with " << nProcs << " processes (1 manager and " << nProcs - 1 << " workers)." << std::endl;
        MAiNGO_END_IF
#endif

        std::cout
            << std::endl
            << "Setting tolerances and other options." << std::endl;
        const double epsilonA = 1e-4;
        const double epsilonR = 1e-4;
        myMAiNGO->set_option("epsilonA", epsilonA);
        myMAiNGO->set_option("epsilonR", epsilonR);
        myMAiNGO->set_option("deltaIneq", 1e-6);
        myMAiNGO->set_option("deltaEq", 1e-6);
        myMAiNGO->set_option("LBP_solver", maingo::lbp::LBP_SOLVER_CPLEX);
        std::cout << "Disabling all output." << std::endl;
        myMAiNGO->set_option("loggingDestination", maingo::LOGGING_NONE);
        myMAiNGO->set_option("growing_augmentRule", 0);
        myMAiNGO->set_option("growing_augmentFreq", 1);
        std::cout << std::endl;

        double CPUofAllProcesses = 0;
        const double startCPU    = maingo::get_cpu_time();
        const double startWall   = maingo::get_wall_time();


        // Solve the problems
        try {

            // Problem bin 1
            // The model is already set
            if (!(run_test(myMAiNGO, "Problem_bin1", 1, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem int 1
            myMAiNGO->set_model(myModel_int1);
            if (!(run_test(myMAiNGO, "Problem_int1", -0.869297426825, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem nonsmooth
            myMAiNGO->set_model(myModel_nonsmooth);
            if (!(run_test(myMAiNGO, "Problem_nonsmooth", 0, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem case 1 lcoe
            myMAiNGO->set_model(myModel_case1_lcoe);
            if (!(run_test(myMAiNGO, "Problem_case1_lcoe", 50.2488287676, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem case 2 lcoe
            myMAiNGO->set_model(myModel_case2_lcoe);
            if (!(run_test(myMAiNGO, "Problem_case2_lcoe", 48.946254947, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem case 3 wnet
            myMAiNGO->set_model(myModel_case3_wnet);
            if (!(run_test(myMAiNGO, "Problem_case3_wnet", -39349.2554447061, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem ex8 1 3
            myMAiNGO->set_model(myModel_ex8_1_3);
            if (!(run_test(myMAiNGO, "Problem_ex8_1_3", 3, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem Henry RS Ideal Gas Flash
            myMAiNGO->set_model(myModel_Henry_RS_IdealGasFlash);
            if (!(run_test(myMAiNGO, "Problem_Henry_RS_IdealGasFlash", -0.931661985716, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem NRTL RS Flash
            myMAiNGO->set_model(myModel_NRTL_RS_Flash);
            if (!(run_test(myMAiNGO, "Problem_NRTL_RS_Flash", 1064.34, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem OME RS Ideal Gas Flash
            myMAiNGO->set_model(myModel_OME_RS_IdealGasFlash);
            if (!(run_test(myMAiNGO, "Problem_OME_RS_IdealGasFlash", -0.385131174192, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem unused variables
            myMAiNGO->set_model(myModel_unusedVars);
            if (!(run_test(myMAiNGO, "Problem_unusedVars", 4.355812920567349, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem LP
            myMAiNGO->set_model(myModel_LP);
            if (!(run_test(myMAiNGO, "Problem_LP", 153.675, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem LP random
            myMAiNGO->set_model(myModel_LP_random);
            if (!(run_test(myMAiNGO, "Problem_LP_random", -2, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem MILP
            myMAiNGO->set_model(myModel_MILP);
            if (!(run_test(myMAiNGO, "Problem_MILP", -2, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem with only relaxation constraints
            myMAiNGO->set_model(myModel_relaxOnly);
            if (!(run_test(myMAiNGO, "Problem_relaxOnly", 4.35581, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem LP with additional constant contraints
            myMAiNGO->set_model(myModel_LP_mod);
            if (!(run_test(myMAiNGO, "Problem_LP_mod", 153.675, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

	         // Problem with Squashing inequalities
            myMAiNGO->set_model(myModel_Squash);
            if (!(run_test(myMAiNGO, "Problem_Squash", -2.30259, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem wallfix
            myMAiNGO->set_model(myModel_wallfix);
            if (!(run_test(myMAiNGO, "Problem_wallfix", 1, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

	        // Problem LP_IN_RO (LP with relaxation only inequalities)
            myMAiNGO->set_model(myModel_LP_IN_RO);
            if (!(run_test(myMAiNGO, "Problem_LP_IN_RO", 0, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // two-stage integer programming problem
            myMAiNGO->set_model(myModel_twoStageIP);
            if (!(run_test(myMAiNGO, "Problem_twoStageIP", -57, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem CHP Sizing (two-stage NLP)
            myMAiNGO->set_model(myModel_CHP_sizing);
            if (!(run_test(myMAiNGO, "Problem_CHP_sizing", 1.287948603324161, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem chance, LinStrat: KELLEY_SIMPLEX; LBP_SubgradientIntervals:FALSE, probing:TRUE
            myMAiNGO->set_option("BAB_probing", 1); 
            myMAiNGO->set_option("LBP_subgradientIntervals", 0);  
	        myMAiNGO->set_option("LBP_linPoints", maingo::lbp::LINP_KELLEY_SIMPLEX);
	        myMAiNGO->set_model(myModel_chance);
	        if (!(run_test(myMAiNGO, "Problem_chance_LINP_KELLEY_SIMPLEX_probing", 29.894 , epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }
            myMAiNGO->set_option("BAB_probing", 0); 
	        myMAiNGO->set_option("LBP_subgradientIntervals", 1); 

	        // Problem nonlinear Constraints, LinStrat: KELLEY_SIMPLEX        
            myMAiNGO->set_model(myModel_nonlinearCons);
            if (!(run_test(myMAiNGO, "Problem_nonlinearCons_LINP_KELLEY_SIMPLEX", -2.30259, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            } 
	
            // Problem chance, LinStrats: RANDOM
	        myMAiNGO->set_option("LBP_linPoints", maingo::lbp::LINP_RANDOM);
	        myMAiNGO->set_model(myModel_chance);
            if (!(run_test(myMAiNGO, "Problem_chance_LINP_RANDOM", 29.894, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem 1d, LinStrats: SIMPLEX
	        myMAiNGO->set_model(myModel_1d);
	        if (!(run_test(myMAiNGO, "Problem_1d_LINP_SIMPLEX", 0, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem RelaxOnly constraints, LinStrats: SIMPLEX
            myMAiNGO->set_model(myModel_relaxOnly);
            if (!(run_test(myMAiNGO, "Problem_relaxOnly_LINP_SIMPLEX", 4.35581, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem squash, LinStrats: SIMPLEX, subgradientIntervals:False           
		    myMAiNGO->set_model(myModel_Squash);
            if (!(run_test(myMAiNGO, "Problem_Squash_LINP_SIMPLEX", -2.30259, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            myMAiNGO->set_option("LBP_solver", maingo::lbp::LBP_SOLVER_CLP);
            // Problem RelaxOnly constraints, LinStrats: SIMPLEX
            myMAiNGO->set_model(myModel_relaxOnly);
            if (!(run_test(myMAiNGO, "Problem_relaxOnly_LBP_CLP_LINP_SIMPLEX", 4.35581, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            myMAiNGO->set_option("UBP_solverPreprocessing", maingo::ubp::UBP_SOLVER_EVAL);
            myMAiNGO->set_option("UBP_solverBab", maingo::ubp::UBP_SOLVER_EVAL);

            // Problem wallfix, Pre_printeveryLocalsearch: True, UBP_verbosity: ALL, UBP: EVAL, LBP: CLP
            myMAiNGO->set_option("UBP_verbosity", 2);
            myMAiNGO->set_option("PRE_printEveryLocalSearch", 1);   
            myMAiNGO->set_option("LBP_subgradientIntervals", 0);
            myMAiNGO->set_model(myModel_wallfix);
            if (!(run_test(myMAiNGO, "Problem_wallfix_UBP_EVAL_pinteverylocalSearch", 1, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }
            myMAiNGO->set_option("UBP_verbosity", 0);
            myMAiNGO->set_option("PRE_printEveryLocalSearch", 0);

            // Problem ex8_1_3, UBP Solver: Eval, LBP Solver: CLP, LinStrat: Incumbent
            myMAiNGO->set_option("LBP_linPoints", maingo::lbp::LINP_INCUMBENT);
	        myMAiNGO->set_model(myModel_ex8_1_3);
	        if (!(run_test(myMAiNGO, "Problem_ex8_1_3_UBP_EVAL_LBP_CLP_LINP_INCUMENT", 3, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            //Problem relxation only constraints, UBP: COBYLA, LBP: CLP, LinStrat: Kelley
            myMAiNGO->set_option("UBP_solverPreprocessing", maingo::ubp::UBP_SOLVER_COBYLA);
            myMAiNGO->set_option("UBP_solverBab", maingo::ubp::UBP_SOLVER_COBYLA);
	        myMAiNGO->set_option("LBP_linPoints", maingo::lbp::LINP_KELLEY);
            myMAiNGO->set_model(myModel_relaxOnly);
            if (!(run_test(myMAiNGO, "Problem_relaxOnly_UBP_COBYLA_LBP_CLP_LINP_KELLEY", 4.35581, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

	        myMAiNGO->set_model(myModel_chance);
            if (!(run_test(myMAiNGO, "Problem_chance_LBP_CLP_LINP_KELLEY", 29.894, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }
 
	        // Problem wallfix, ignoreNodeBounds: True, UBP: COBYLA, LBP: CLP, LinStrat: Kelley 
            myMAiNGO->set_option("UBP_ignoreNodeBounds", 1);
            myMAiNGO->set_model(myModel_wallfix);
            if (!(run_test(myMAiNGO, "Problem_wallfix_ignoreNodeBounds", 1, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }
            myMAiNGO->set_option("UBP_ignoreNodeBounds", 0);

            // Problem LP with constant constraints, Bab_probing:True, UBP: COBYLA, LBP: CLP, LinStrat: Kelley
            myMAiNGO->set_option("BAB_probing", 1); 
            myMAiNGO->set_model(myModel_LP_mod);
            if (!(run_test(myMAiNGO, "Problem_LP_mod_UBP_COBLYA_LBP_CLP_probing", 153.675, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }
            myMAiNGO->set_option("BAB_probing", 0); 

            //Problem Squash, UBP: LBFGS, LBP: CLP, LinStrat: Kelley
            myMAiNGO->set_option("UBP_solverPreprocessing", maingo::ubp::UBP_SOLVER_LBFGS);
            myMAiNGO->set_option("UBP_solverBab", maingo::ubp::UBP_SOLVER_LBFGS);
            myMAiNGO->set_model(myModel_Squash);
            if (!(run_test(myMAiNGO, "Problem_Squash_UBP_LBFGS_LBP_CLP_LINP_KELLEY", -2.30259, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            //Problem ste27, UBP: SLSQP , LBP:CLP; LinSTrat: Kelley
            myMAiNGO->set_option("UBP_solverPreprocessing", maingo::ubp::UBP_SOLVER_SLSQP);
            myMAiNGO->set_option("UBP_solverBab", maingo::ubp::UBP_SOLVER_SLSQP);
            myMAiNGO->set_model(myModel_st_e27);
            if (!(run_test(myMAiNGO, "Problem_st_e27_UBP_SLSQP_LBP_CLP", 2, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }
            
	        // Problem Squash, UBP: BOBYQA, LBP: MAiNGO, LinStrat: SIMPLEX, LBP_subgradientIntervals: FALSE
            myMAiNGO->set_option("LBP_solver", maingo::lbp::LBP_SOLVER_MAiNGO);
            myMAiNGO->set_option("UBP_solverPreprocessing", maingo::ubp::UBP_SOLVER_BOBYQA);
            myMAiNGO->set_option("UBP_solverBab", maingo::ubp::UBP_SOLVER_BOBYQA);
	        myMAiNGO->set_option("LBP_linPoints", maingo::lbp::LINP_SIMPLEX);
            myMAiNGO->set_option("LBP_subgradientIntervals", 0);   
            myMAiNGO->set_model(myModel_Squash);
            if (!(run_test(myMAiNGO, "Problem_Squash_UBP_BOBYQA_LBP_MAiNGO", -2.30259, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }
            myMAiNGO->set_option("LBP_subgradientIntervals", 1);   

	        // Problem with relaxation only constraints, UBP: IPOPT, LBP: MAiNGO, LinStrat: SIMPLEX
            myMAiNGO->set_option("UBP_solverPreprocessing", maingo::ubp::UBP_SOLVER_IPOPT);
            myMAiNGO->set_option("UBP_solverBab", maingo::ubp::UBP_SOLVER_IPOPT);
            myMAiNGO->set_model(myModel_relaxOnly);
            if (!(run_test(myMAiNGO, "Problem_relaxOnly_UBP_IPOPT_LBP_MAiNGO", 4.35581, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }
            
            //Problem chance, UBP: IPOPT, LBP: MAiNGO, LinStrat: SIMPLEX, BAB_probing: TRUE
            myMAiNGO->set_option("BAB_probing", 1);
            myMAiNGO->set_model(myModel_chance);
	        if (!(run_test(myMAiNGO, "Problem_chance_LINP_SIMPLEX_probing", 29.894 , epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }
            myMAiNGO->set_option("BAB_probing", 0);
       
	        // Problem chance, UBP: IPOPT, LBP: INTERVAL, LinStrat: KELLEY, LBP_subgradientIntervals: FALSE, BAB_probing: TRUE
            myMAiNGO->set_option("LBP_solver", maingo::lbp::LBP_SOLVER_INTERVAL);
	        myMAiNGO->set_option("LBP_subgradientIntervals", 0);  
            myMAiNGO->set_option("LBP_linPoints", 2);
            myMAiNGO->set_option("BAB_probing", 1); 
            myMAiNGO->set_model(myModel_chance);
            if (!(run_test(myMAiNGO, "Problem_chance_LBP_INTERVAL_probing",  29.894, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }
	        myMAiNGO->set_option("LBP_subgradientIntervals", 1);   
            myMAiNGO->set_option("BAB_probing", 0); 

	        // Problem with relaxation only constraints, UBP: IPOPT, LBP: INTERVAL, LinStrat: LINP_RANDOM
            myMAiNGO->set_model(myModel_relaxOnly);
            if (!(run_test(myMAiNGO, "Problem_relaxOnly_UBP_IPOPT_LBP_INTERVAL_LINP_RANDOM", 4.35581, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

	        // Problem LP with constant constraints, UBP: IPOPT, LBP: INTERVAL, LinStrat: LINP_RANDOM
            myMAiNGO->set_model(myModel_LP_mod);
            if (!(run_test(myMAiNGO, "Problem_LP_mod_UBP_IPOPT_LBP_INTEVAL_LINP_RANDOM", 153.675, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

	        // Problem Squash, UBP: IPOPT, LBP: INTERVAL, LinStrat: LINP_RANDOM
            myMAiNGO->set_model(myModel_Squash);
            if (!(run_test(myMAiNGO, "Problem_Squash_UBP_IPOPT_LBP_INTEVAL_LINP_RANDOM", -2.30259, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

	        myMAiNGO->set_option("LBP_linPoints", maingo::lbp::LINP_MID);
         
            // Setting growing dataset options even though we run without having growing datasets
            myMAiNGO->set_model(myModel_LP);
            myMAiNGO->set_option("growing_approach", -1);
            myMAiNGO->set_option("growing_maxTimePostprocessing", -1);
            myMAiNGO->set_option("growing_useResampling", -1);
            myMAiNGO->set_option("growing_shuffleData", -1);
            myMAiNGO->set_option("growing_relativeSizing", -1);
            myMAiNGO->set_option("growing_initPercentage", -1);
            myMAiNGO->set_option("growing_augmentPercentage", -1);
            myMAiNGO->set_option("growing_maxSize", -1);
            myMAiNGO->set_option("growing_augmentRule", -1);
            myMAiNGO->set_option("growing_augmentFreq", -1);
            myMAiNGO->set_option("growing_augmentWeight", -1);
            myMAiNGO->set_option("growing_augmentTol", -1);
            if (!(run_test(myMAiNGO, "Problem_LP", 153.675, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

#ifdef HAVE_MILP_SOLVER
            // Problem MILP Sudoku - only run if dedicated MILP solver available, takes too long otherwise
            myMAiNGO->set_model(myModel_MILP_sudoku);
            if (!(run_test(myMAiNGO, "Problem_MILP_sudoku", 5, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }
#else
        std::cout << "Skipping Problem_MILP_sudoku to save time - no dedicated MILP solver available." << std::endl;
#endif

#ifdef HAVE_QP_SOLVER
            // Problem QP (extremly sparse) - only run if dedicated QP solver available, takes too long otherwise
            myMAiNGO->set_model(myModel_QP);
            if (!(run_test(myMAiNGO, "Problem_QP", 11.25, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }
#else
        std::cout << "Skipping Problem_QP to save time - no dedicated QP solver available." << std::endl;
#endif

            // Problem growing datasets - simple
            myMAiNGO->set_model(myModel_growing_simple);
            if (!(run_test(myMAiNGO, "Problem_growing_simple", 0.5066, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }

            // Problem growing datasets - AVM
            myMAiNGO->set_model(myModel_growing_AVM);
            myMAiNGO->set_option("LBP_addAuxiliaryVars", 1);
            if (!(run_test(myMAiNGO, "Problem_growing_AVM", 0.5066, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            }           

            // For further test cases reset AVM:
            myMAiNGO->set_option("LBP_addAuxiliaryVars", 0);
            
            // Problem SubdomainLB - LBD: Subdomain Lower Bounding Solver
            myMAiNGO->set_model(myModel_SubdomainLB);
            myMAiNGO->set_option("LBP_solver", maingo::lbp::LBP_SOLVER_SUBDOMAIN);
            myMAiNGO->set_option("Num_subdomains", 256);
            myMAiNGO->set_option("Interval_arithmetic", 1);
            myMAiNGO->set_option("Subinterval_branch_strategy", 0);
            myMAiNGO->set_option("Center_strategy", 0); 
            if (!(run_test(myMAiNGO, "Problem_Subdomain_LowerBounding", -6.5511, epsilonA, epsilonR, CPUofAllProcesses))) {
                exceptionCounter++;
            } 
            // Reset lower bounding solver
            myMAiNGO->set_option("LBP_solver", maingo::lbp::LBP_SOLVER_CPLEX);
        }
        catch (std::exception &e) {
            exceptionCounter++;
            MAiNGO_IF_BAB_MANAGER
                std::cerr << std::endl
                          << e.what() << std::endl;
            MAiNGO_END_IF
            MAiNGO_MPI_FINALIZE return -1;
        }
        catch (...) {
            exceptionCounter++;
            MAiNGO_IF_BAB_MANAGER
                std::cerr << std::endl
                          << "Encountered an unknown fatal error during solution. Terminating." << std::endl;
            MAiNGO_END_IF
            MAiNGO_MPI_FINALIZE return -1;
        }

        if (exceptionCounter > 0) {
            throw std::exception();
            return -1;
        }

        std::cout << "Done." << std::endl
                  << std::endl;

        const double endCPU              = maingo::get_cpu_time();
        const double endWall             = maingo::get_wall_time();
        const unsigned int cpuAllMinutes = std::floor(CPUofAllProcesses / 60.);
        const unsigned int cpuMinutes    = std::floor((endCPU - startCPU) / 60.);
        const unsigned int wallMinutes   = std::floor((endWall - startWall) / 60.);
#ifdef HAVE_MAiNGO_MPI
        std::cout << "Total CPU time:  " << CPUofAllProcesses << " s = " << cpuAllMinutes << " m " << (CPUofAllProcesses) - (cpuAllMinutes * 60.) << "s." << std::endl;
#else
        std::cout << "Total CPU time:  " << endCPU - startCPU << " s = " << cpuMinutes << " m " << (endCPU - startCPU) - (cpuMinutes * 60.) << "s." << std::endl;
#endif
        std::cout << "Total wall-clock time: " << endWall - startWall << " s = " << wallMinutes << " m " << (endWall - startWall) - (wallMinutes * 60.) << "s." << std::endl
                  << std::endl;

#ifdef HAVE_MAiNGO_MPI
        std::cout.rdbuf(coutBuf);
#endif

        MAiNGO_MPI_FINALIZE return 0;
}
