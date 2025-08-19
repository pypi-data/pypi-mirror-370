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
#include "MAiNGOmodelEpsCon.h"
#include "bab.h"
#include "getTime.h"
#include "intervalLibrary.h"
#include "lbp.h"
#include "lbpTwoStage.h"
#include "mpiUtilities.h"
#include "readData.h"
#include "ubp.h"
#include "ubpTwoStage.h"

#include <cassert>


using namespace maingo;


/////////////////////////////////////////////////////////////////////////
// constructor that does not require a model (model can be set later)
MAiNGO::MAiNGO()
{
#ifdef HAVE_MAiNGO_MPI
    // Set MPI variables
    MPI_Comm_rank(MPI_COMM_WORLD, &_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &_nProcs);
    if (_nProcs < 2) {
        throw MAiNGOException("  Error initializing MAiNGO: The parallel version of MAiNGO requires at least 2 MPI processes.");
    }
#endif
    _modelSpecified     = false;
    _DAGconstructed     = false;
}


/////////////////////////////////////////////////////////////////////////
// constructor that requires a model
MAiNGO::MAiNGO(std::shared_ptr<MAiNGOmodel> myModel) : MAiNGO()
{
    set_model(myModel);
}


/////////////////////////////////////////////////////////////////////////
// solve function which actually solves the problem
RETCODE
MAiNGO::solve()
{

    if (!_modelSpecified) {
        throw MAiNGOException("  Error trying to solve problem: Model has not been set successfully.");
    }

    // ---------------------------------------------------------------------------------
    // 0: Prepare
    // ---------------------------------------------------------------------------------
    MAiNGO_IF_BAB_MANAGER
        // Start timing and print header
        _preprocessTime        = get_cpu_time();
        _preprocessTimeWallClock = get_wall_time();
        _logger->clear();
        _logger->create_log_file();
        _print_MAiNGO_header();
#ifdef HAVE_MAiNGO_MPI
        _logger->print_message("\n  You are using the parallel MAiNGO version. This run uses " + std::to_string(_nProcs) + " processes ( 1 manager and " + std::to_string(_nProcs - 1) + " workers ).\n",
                               VERB_NORMAL, BAB_VERBOSITY);
#endif
    MAiNGO_END_IF
    MAiNGO_MPI_BARRIER


        // ---------------------------------------------------------------------------------
        // 1: Preliminaries: inform about changed settings and write model to file in other language
        // ---------------------------------------------------------------------------------
        _maingoOriginalSettings = *_maingoSettings;    // Save original settings
    MAiNGO_IF_BAB_MANAGER
        _logger->print_settings(VERB_NORMAL, BAB_VERBOSITY);

        // Write MAiNGO model to other language if desired
        if (_maingoSettings->modelWritingLanguage != LANG_NONE) {
            _inMAiNGOsolve = true;
            write_model_to_file_in_other_language(_maingoSettings->modelWritingLanguage);
            _inMAiNGOsolve     = false;
            double tmpTimeCPU  = get_cpu_time() - _preprocessTime;
            double tmpTimeWall = get_wall_time() - _preprocessTimeWallClock;
            std::string str;
            switch (_maingoSettings->modelWritingLanguage) {
                case LANG_GAMS:
                    str = ".gms";
                    break;
                default:
                    str = ".txt";
                    break;
            }
            std::ostringstream outstr;
            outstr << "  Writing to file \"MAiNGO_written_model" + str + "\" took:\n";
            outstr << "  CPU time:         " << std::fixed << std::setprecision(3) << tmpTimeCPU << " seconds.\n";
            outstr << "  Wall-clock time:  " << std::fixed << std::setprecision(3) << tmpTimeWall << " seconds.\n";
            _logger->print_message(outstr.str(), VERB_NORMAL, BAB_VERBOSITY);
            // Reset times, since we don't want to add the file writing to the final MAiNGO solution time
            _preprocessTime          = get_cpu_time();
            _preprocessTimeWallClock = get_wall_time();
        }
    MAiNGO_END_IF
    MAiNGO_MPI_BARRIER

    // ---------------------------------------------------------------------------------
    // 2: Construct DAG, possibly remove unused variables, and check constant constraints
    // ---------------------------------------------------------------------------------
    try {
        _construct_DAG();
    }
    catch (const std::exception& e) {
        MAiNGO_IF_BAB_MANAGER
            std::ostringstream errmsg;
            errmsg << e.what() << "\n  Encountered a fatal error during DAG construction.";
            _write_files_error(errmsg.str());
            throw MAiNGOException("  Encountered a fatal error during DAG construction.", e);
            MAiNGO_ELSE
                throw;
            MAiNGO_END_IF
    }
    catch (...) {   // GCOVR_EXCL_START
        MAiNGO_IF_BAB_MANAGER
            _write_files_error("  Encountered an unknown fatal error during DAG construction.");
            throw MAiNGOException("  Encountered an unknown fatal error during DAG construction.");
            MAiNGO_ELSE
                throw;
            MAiNGO_END_IF
    }
    // GCOVR_EXCL_STOP

    MAiNGO_IF_BAB_MANAGER
        _print_info_about_initial_point();
    MAiNGO_END_IF

    // ---------------------------------------------------------------------------------
    // 3: Determine structure, set constraint properties, and invoke internal solution routine
    // ---------------------------------------------------------------------------------
    _analyze_and_solve_problem();


    // ---------------------------------------------------------------------------------
    // 4: Final Output
    // ---------------------------------------------------------------------------------
    MAiNGO_IF_BAB_MANAGER
        // Timing for output
        _outputTime = get_cpu_time();
        _outputTimeWallClock = get_wall_time();

        // Print problem statistics, solution, additional output & CPU time.
        _print_statistics();
        _print_solution();
        _print_additional_output();
        _print_time();
#ifdef HAVE_GROWING_DATASETS
        if ((_maingoSettings->growing_approach > GROW_APPR_DETERMINISTIC)
            && (_maingoSettings->growing_maxTimePostprocessing > 0)) {
            _print_statistics_postprocessing();
        }
#endif    // HAVE_GROWING_DATASETS


        // Write files
        _write_files();

        // Restore settings
        *_maingoSettings = _maingoOriginalSettings;
    MAiNGO_END_IF


    return _maingoStatus;
}


/////////////////////////////////////////////////////////////////////////
// solve function for multi-objective problems using the epsilon-constraint method
RETCODE
MAiNGO::solve_epsilon_constraint()
{

    if (!_modelSpecified) {
        throw MAiNGOException("  Error trying to solve problem: Model has not been set successfully.");
    }

    // ---------------------------------------------------------------------------------
    // 0: Prepare
    // ---------------------------------------------------------------------------------
    double cpuTimeEpsCon, wallTimeEpsCon;
    MAiNGO_IF_BAB_MANAGER
        // Start timing and print header
        cpuTimeEpsCon  = 0.;    // We compute the CPU time by suming over all runs
        wallTimeEpsCon = get_wall_time();
        _logger->clear();
        _logger->create_log_file();
        _logger->create_iterations_csv_file(_maingoSettings->writeCsv);
        _print_MAiNGO_header();
#ifdef HAVE_MAiNGO_MPI
        _logger->print_message("\n  You are using the parallel MAiNGO version. This run uses " + std::to_string(_nProcs) + " processes ( 1 manager and " + std::to_string(_nProcs - 1) + " workers ).\n",
                               VERB_NORMAL, BAB_VERBOSITY);
#endif
    MAiNGO_END_IF
    MAiNGO_MPI_BARRIER


        // ---------------------------------------------------------------------------------
        // 1: Inform the user about changed Settings
        // ---------------------------------------------------------------------------------
        _maingoOriginalSettings = *_maingoSettings;    // Save original settings
    MAiNGO_IF_BAB_MANAGER
        _logger->print_settings(VERB_NORMAL, BAB_VERBOSITY);
        // Don't write MAiNGO model to other language, even if desired
        if (_maingoSettings->modelWritingLanguage != LANG_NONE) {
            _logger->print_message("  Warning: Not writing to other language when solving multi-objective problem.", VERB_NORMAL, BAB_VERBOSITY);
        }
    MAiNGO_END_IF
    MAiNGO_MPI_BARRIER

        // ---------------------------------------------------------------------------------
        // 2: Get information on model
        // ---------------------------------------------------------------------------------
        std::shared_ptr<MAiNGOmodelEpsCon>
            epsConModel = std::dynamic_pointer_cast<MAiNGOmodelEpsCon>(_myFFVARmodel);
    if (!epsConModel) {
        MAiNGO_IF_BAB_MANAGER
            throw MAiNGOException("  Error in epsilon-constraint method: model needs to be derived from MAiNGOmodelEpsCon.");
            MAiNGO_ELSE
                throw;
            MAiNGO_END_IF
    }
    EvaluationContainer userResult;
    try {
        userResult = epsConModel->evaluate_user_model(std::vector<mc::FFVar>(_nvarOriginal));
    }
    catch (const std::exception& e) {
        MAiNGO_IF_BAB_MANAGER
            std::ostringstream errmsg;
            errmsg << e.what() << "\n  Encountered a fatal error while evaluating model in epsilon constraint method.";
            _write_files_error(errmsg.str());
            throw MAiNGOException("  Encountered a fatal error while evaluating model in epsilon constraint method.", e);
            MAiNGO_ELSE
                throw;
            MAiNGO_END_IF
    }
    catch (...) {   // GCOVR_EXCL_START
        MAiNGO_IF_BAB_MANAGER
            _write_files_error("  Encountered an unknown fatal error while evaluating model in epsilon constraint method.");
            throw MAiNGOException("  Encountered an unknown fatal error while evaluating model in epsilon constraint method.");
            MAiNGO_ELSE
                throw;
            MAiNGO_END_IF
    }
    //GCOVR_EXCL_STOP

    size_t nObj = userResult.objective.size();
    if (nObj != 2) {
        MAiNGO_IF_BAB_MANAGER
            throw MAiNGOException("  Error in epsilon-constraint method: currently only supporting exactly two objectives.");
            MAiNGO_ELSE
                throw;
            MAiNGO_END_IF
    }
    std::vector<double> epsilon(nObj, _maingoSettings->infinity);


    // ---------------------------------------------------------------------------------
    // 2: Solve single-objective problems first
    // ---------------------------------------------------------------------------------
    epsConModel->set_epsilon(epsilon);
    std::vector<std::vector<double>> optimalObjectives;
    std::vector<std::vector<double>> solutionPoints;
    RETCODE status;
    for (size_t iObj = 0; iObj < nObj; iObj++) {
        // First, minimize objective iObj without additional constraints
        epsConModel->set_single_objective(true);
        MAiNGO_IF_BAB_MANAGER
            // Reset timing for this run and give intermediate output
            _preprocessTime          = get_cpu_time();
            _preprocessTimeWallClock = get_wall_time();
            _print_message(std::string("*** Solving single-objective problem for objective " + std::to_string(iObj) + ". ***"));
        MAiNGO_END_IF
        epsConModel->set_objective_index(iObj);
        try {
            _construct_DAG();
        }
        catch (const std::exception& e) {   //GCOVR_EXCL_START
            MAiNGO_IF_BAB_MANAGER
                std::ostringstream errmsg;
                errmsg << e.what() << "\n  Encountered a fatal error during DAG construction.";
                _write_files_error(errmsg.str());
                throw MAiNGOException("  Encountered a fatal error during DAG construction.", e);
                MAiNGO_ELSE
                    throw;
                MAiNGO_END_IF
        }
        catch (...) {
            MAiNGO_IF_BAB_MANAGER
                _write_files_error("  Encountered an unknown fatal error during DAG construction.");
                throw MAiNGOException("  Encountered an unknown fatal error during DAG construction.");
                MAiNGO_ELSE
                    throw;
                MAiNGO_END_IF
        }
        //GCOVR_EXCL_STOP

        status = _analyze_and_solve_problem();
        MAiNGO_IF_BAB_MANAGER
            // Print problem statistics, solution, additional output & CPU time.
            _outputTime = get_cpu_time();
            _outputTimeWallClock = get_wall_time();
            _print_statistics();
            _print_solution();
            _print_additional_output();
            _print_time();
            if (status == INFEASIBLE) {
                if (iObj != 0) {
                    _print_message(std::string("*** Error in epsilon-constraint: false infeasibility claim ***")); // GCOVR_EXCL_LINE
                }
                else {
                    _print_message(std::string("*** Problem is infeasible. Stopping epsilon-constraint method. ***"));
                }
#ifdef HAVE_MAiNGO_MPI
                BCAST_TAG bcastTag = BCAST_EXCEPTION;
                MPI_Bcast(&bcastTag, 1, MPI_INT, 0, MPI_COMM_WORLD);
#endif
                break;
            }
            std::vector<double> tmpObjectives(nObj);
            std::vector<std::pair<std::string, double>> tmpOutput = evaluate_additional_outputs_at_solution_point();
            for (size_t jObj = 0; jObj < nObj; jObj++) {
                tmpObjectives[jObj] = tmpOutput[tmpOutput.size() - nObj + jObj].second;
            }
            optimalObjectives.push_back(tmpObjectives);
            cpuTimeEpsCon += get_cpu_solution_time();
#ifdef HAVE_MAiNGO_MPI
            BCAST_TAG bcastTag = BCAST_EVERYTHING_FINE;
            MPI_Bcast(&bcastTag, 1, MPI_INT, 0, MPI_COMM_WORLD);
            MAiNGO_ELSE    // Workers just wait for a broadcast
                // Check whether an exception was raised
                BCAST_TAG tag;
                MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
                if (tag == BCAST_EXCEPTION) {
                    throw MAiNGOMpiException("  Worker " + std::to_string(_rank) + " received message about an exception during epsilon-constraint method.", MAiNGOMpiException::ORIGIN_OTHER);
                }
#endif
            MAiNGO_END_IF
            *_maingoSettings = _maingoOriginalSettings;

            // Next, minimize the other objective s.t. iObj stays the same
            MAiNGO_IF_BAB_MANAGER
                // Reset timing for this run and give intermediate output
                _preprocessTime          = get_cpu_time();
                _preprocessTimeWallClock = get_wall_time();
                _print_message(std::string("*** Solving complementary problem to single-objective problem for objective " + std::to_string(iObj) + ". ***"));
            MAiNGO_END_IF
            // Get correct epsilon
            epsConModel->set_single_objective(false);
            double tmpOptimalObjective;
            MAiNGO_IF_BAB_MANAGER
                tmpOptimalObjective = optimalObjectives[iObj][iObj];
            MAiNGO_END_IF
#ifdef HAVE_MAiNGO_MPI
            MPI_Bcast(&tmpOptimalObjective, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
#endif
            epsilon[iObj] = tmpOptimalObjective;
            epsConModel->set_epsilon(epsilon);
            unsigned otherObj = (iObj == 0) ? 1 : 0;    // Works only for bi-objective
            epsConModel->set_objective_index(otherObj);
            try {
                _construct_DAG();
            }
            catch (const std::exception& e) {   // GCOVR_EXCL_START
                MAiNGO_IF_BAB_MANAGER
                    std::ostringstream errmsg;
                    errmsg << e.what() << "\n  Encountered a fatal error during DAG construction.";
                    _write_files_error(errmsg.str());
                    throw MAiNGOException("  Encountered a fatal error during DAG construction.", e);
                    MAiNGO_ELSE
                        throw;
                    MAiNGO_END_IF
            }
            catch (...) {
                MAiNGO_IF_BAB_MANAGER
                    _write_files_error("  Encountered an unknown fatal error during DAG construction.");
                    throw MAiNGOException("  Encountered an unknown fatal error during DAG construction.");
                    MAiNGO_ELSE
                        throw;
                    MAiNGO_END_IF
            }
            // GCOVR_EXCL_STOP

            status = _analyze_and_solve_problem();
            MAiNGO_IF_BAB_MANAGER
                // Print problem statistics, solution, additional output & CPU time.
                _outputTime = get_cpu_time();
                _outputTimeWallClock = get_wall_time();
                _print_statistics();
                _print_solution();
                _print_additional_output();
                _print_time();
                if (status == INFEASIBLE) {
                    _print_message(std::string("*** Error in epsilon-constraint: false infeasibility claim ***"));  // GCOVR_EXCL_LINE
#ifdef HAVE_MAiNGO_MPI
                    BCAST_TAG bcastTag = BCAST_EXCEPTION;
                    MPI_Bcast(&bcastTag, 1, MPI_INT, 0, MPI_COMM_WORLD);
#endif
                    break;  // GCOVR_EXCL_LINE
                }
                std::vector<std::pair<std::string, double>> tmpOutput2 = evaluate_additional_outputs_at_solution_point();
                for (size_t jObj = 0; jObj < nObj; jObj++) {
                    optimalObjectives[iObj][jObj] = tmpOutput2[tmpOutput2.size() - nObj + jObj].second;
                }
                solutionPoints.push_back(get_solution_point());
                cpuTimeEpsCon += get_cpu_solution_time();
#ifdef HAVE_MAiNGO_MPI
                BCAST_TAG bcastTag = BCAST_EVERYTHING_FINE;
                MPI_Bcast(&bcastTag, 1, MPI_INT, 0, MPI_COMM_WORLD);
                MAiNGO_ELSE    // Workers just wait for a broadcast
                    // Check whether an exception was raised
                    BCAST_TAG tag;
                    MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
                    if (tag == BCAST_EXCEPTION) {
                        throw MAiNGOMpiException("  Worker " + std::to_string(_rank) + " received message about an exception during epsilon-constraint method.", MAiNGOMpiException::ORIGIN_OTHER);
                    }
#endif
                MAiNGO_END_IF
                *_maingoSettings = _maingoOriginalSettings;
    }
    MAiNGO_MPI_BARRIER

        if (status != INFEASIBLE)
    {
        // ---------------------------------------------------------------------------------
        // 3: Solve problems with epsilon-constraint
        // ---------------------------------------------------------------------------------
#ifdef HAVE_MAiNGO_MPI
        MAiNGO_IF_BAB_MANAGER
            for (size_t i = 0; i < nObj; i++) {
                MPI_Bcast(optimalObjectives[i].data(), nObj, MPI_DOUBLE, 0, MPI_COMM_WORLD);
            }
            MAiNGO_ELSE
                optimalObjectives.resize(nObj);
                for (size_t i = 0; i < nObj; i++) {
                    optimalObjectives[i].resize(nObj);
                    MPI_Bcast(optimalObjectives[i].data(), nObj, MPI_DOUBLE, 0, MPI_COMM_WORLD);
                }
            MAiNGO_END_IF
#endif
            epsConModel->set_single_objective(false);
            epsConModel->set_objective_index(0);
            const size_t nPoints = _maingoSettings->EC_nPoints;
            for (size_t iEps = 1; iEps < nPoints - 1; iEps++) {
                MAiNGO_IF_BAB_MANAGER
                    // Reset timing for this run and give intermediate output
                    _preprocessTime          = get_cpu_time();
                    _preprocessTimeWallClock = get_wall_time();
                    _print_message(std::string("*** Solving epsilon-constraint problem number " + std::to_string(iEps) + ". ***"));
                MAiNGO_END_IF
                for (size_t iObj = 0; iObj < nObj; iObj++) {
                    if (iObj != 0) {
                        epsilon[iObj] = optimalObjectives[iObj][iObj] + iEps * (optimalObjectives[0][iObj] - optimalObjectives[iObj][iObj]) / (nPoints - 1);
                    }
                }
                epsConModel->set_epsilon(epsilon);
                try {
                    _construct_DAG();
                }
                catch (const std::exception& e) {   // GCOVR_EXCL_START
                    MAiNGO_IF_BAB_MANAGER
                        std::ostringstream errmsg;
                        errmsg << e.what() << "\n  Encountered a fatal error during DAG construction.";
                        _write_files_error(errmsg.str());
                        throw MAiNGOException("  Encountered a fatal error during DAG construction.", e);
                        MAiNGO_ELSE
                            throw;
                        MAiNGO_END_IF
                }
                catch (...) {
                    MAiNGO_IF_BAB_MANAGER
                        _write_files_error("  Encountered an unknown fatal error during DAG construction.");
                        throw MAiNGOException("  Encountered an unknown fatal error during DAG construction.");
                        MAiNGO_ELSE
                            throw;
                        MAiNGO_END_IF
                }
                // GCOVR_EXCL_STOP

                status = _analyze_and_solve_problem();
                MAiNGO_IF_BAB_MANAGER
                    // Print problem statistics, solution, additional output & CPU time.
                    _outputTime = get_cpu_time();
                    _outputTimeWallClock = get_wall_time();
                    _print_statistics();
                    _print_solution();
                    _print_additional_output();
                    _print_time();
                    if (status == INFEASIBLE) {
                        _print_message(std::string("*** Error in epsilon-constraint: false infeasibility claim ***"));    //GCOVR_EXCL_LINE
#ifdef HAVE_MAiNGO_MPI
                        BCAST_TAG bcastTag = BCAST_EXCEPTION;
                        MPI_Bcast(&bcastTag, 1, MPI_INT, 0, MPI_COMM_WORLD);
#endif
                        break;  //GCOVR_EXCL_LINE
                    }
                    std::vector<double> tmpObjectives(nObj);
                    std::vector<std::pair<std::string, double>> tmpOutput = evaluate_additional_outputs_at_solution_point();
                    for (size_t jObj = 0; jObj < nObj; jObj++) {
                        tmpObjectives[jObj] = tmpOutput[tmpOutput.size() - nObj + jObj].second;
                    }
                    optimalObjectives.push_back(tmpObjectives);
                    solutionPoints.push_back(get_solution_point());
                    cpuTimeEpsCon += get_cpu_solution_time();
#ifdef HAVE_MAiNGO_MPI
                    BCAST_TAG bcastTag = BCAST_EVERYTHING_FINE;
                    MPI_Bcast(&bcastTag, 1, MPI_INT, 0, MPI_COMM_WORLD);
                    MAiNGO_ELSE    // Workers just wait for a broadcast
                        // Check whether an exception was raised
                        BCAST_TAG tag;
                        MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
                        if (tag == BCAST_EXCEPTION) {
                            throw MAiNGOMpiException("  Worker " + std::to_string(_rank) + " received message about an exception during epsilon-constraint method.", MAiNGOMpiException::ORIGIN_OTHER);
                        }
#endif
                    MAiNGO_END_IF
                    *_maingoSettings = _maingoOriginalSettings;
            }
    }

    // ---------------------------------------------------------------------------------
    // 4: Final Output
    // ---------------------------------------------------------------------------------
    MAiNGO_IF_BAB_MANAGER
        // Restore settings
        *_maingoSettings = _maingoOriginalSettings;
        // Write files
        _write_files();
        _write_epsilon_constraint_result(optimalObjectives, solutionPoints);
        // Print time (slight abuse of regular time variables...)
        _logger->print_message("\n  Overall time for epsilon constraint method:", VERB_NORMAL, BAB_VERBOSITY);
        _preprocessTime          = 0.;
        _preprocessTimeWallClock = 0.;
        _babTime                 = cpuTimeEpsCon;
        _babTimeWallClock        = wallTimeEpsCon;
        _outputTime              = get_cpu_time();
        _outputTimeWallClock     = get_wall_time();
        _print_time();
    MAiNGO_END_IF

    return _maingoStatus;
}


/////////////////////////////////////////////////////////////////////////
// recognize structure, set constraint properties, and invoke solution routine
RETCODE
MAiNGO::_analyze_and_solve_problem()
{
    assert(_nobj == 1);

    // Proceed only if the problem is not already found to be infeasible because of constant, infeasible constraints (e.g., 2<=1; this is checked in _construct_DAG()) or inconsistent variable bounds (e.g., x in [0,-1]; this is checked in set_model)
    if (_constantConstraintsFeasible && _infeasibleVariables.empty()) {

        // ----------------------------------------------------------------------------------------------------
        // 3: Structure recognition (LP, MIP, QP, NLP, MINLP) and constraint properties (Linear, convex, etc.)
        // ----------------------------------------------------------------------------------------------------
        // A bit dirty, but a simple way to get a handle on the special features of TwoStageModel
        // Needs to be here because it is needed in _set_constraint_and_variable_properties to avoid setting branching prios to zero for two-stage (MI)LPs
        _myTwoStageFFVARmodel = std::dynamic_pointer_cast<maingo::TwoStageModel>(_myFFVARmodel);

        try {
            _recognize_structure();
            _set_constraint_and_variable_properties();
            MAiNGO_MPI_BARRIER
        }
        catch (const std::exception& e) {   // GCOVR_EXCL_START
            MAiNGO_IF_BAB_MANAGER
                std::ostringstream errmsg;
                errmsg << e.what() << "\n  Encountered a fatal error during structure recognition.";
                _write_files_error(errmsg.str());
                throw MAiNGOException("  Encountered a fatal error during structure recognition.", e);
            MAiNGO_ELSE
                throw;
            MAiNGO_END_IF
        }
        catch (...) {
            MAiNGO_IF_BAB_MANAGER
                _write_files_error("  Encountered an unknown fatal error during structure recognition.");
                throw MAiNGOException("  Encountered an unknown fatal error during structure recognition.");
            MAiNGO_ELSE
                throw;
            MAiNGO_END_IF
        }
        // GCOVR_EXCL_STOP

        // ---------------------------------------------------------------------------------
        // 4: Solve the problem
        // ---------------------------------------------------------------------------------
        if (_myTwoStageFFVARmodel){
            if (_maingoSettings->TS_useLowerBoundingSubsolvers || _maingoSettings->TS_useUpperBoundingSubsolvers) {
#ifdef _OPENMP
                omp_set_dynamic(0);    // Explicitly disable dynamic teams
                omp_set_num_threads(std::min((unsigned int)omp_get_max_threads(), _myTwoStageFFVARmodel->Ns));
                MAiNGO_IF_BAB_MANAGER
                    _logger->print_message("\nUsing OpenMP with up to " + std::to_string(omp_get_max_threads()) + " threads!\n", VERB_NORMAL, BAB_VERBOSITY);
                MAiNGO_END_IF
#endif
                return _solve_MINLP();
            }
        }

        switch (_problemStructure) {
#ifdef HAVE_CPLEX    // If we have CPLEX, we can use it directly for problems of type LP, MIP, QP, or MIQP
            case LP:
                MAiNGO_IF_BAB_MANAGER
                    _logger->print_message("\n  Recognized the problem to be a linear program.\n", VERB_NORMAL, BAB_VERBOSITY);
#ifdef HAVE_GROWING_DATASETS
                    _logger->print_message("\n  Growing datasets will not be used.\n", VERB_NORMAL, BAB_VERBOSITY);
#endif    //HAVE_GROWING_DATASETS
                MAiNGO_END_IF
                return _solve_MIQP();
                break;
            case MIP:
                MAiNGO_IF_BAB_MANAGER
                    _logger->print_message("\n  Recognized the problem to be a mixed-integer linear program.\n", VERB_NORMAL, BAB_VERBOSITY);
#ifdef HAVE_GROWING_DATASETS
                    _logger->print_message("\n  Growing datasets will not be used.\n", VERB_NORMAL, BAB_VERBOSITY);
#endif    //HAVE_GROWING_DATASETS
                MAiNGO_END_IF
                return _solve_MIQP();
                break;
            case QP:
                MAiNGO_IF_BAB_MANAGER
                    _logger->print_message("\n  Recognized the problem to be a quadratic program.\n", VERB_NORMAL, BAB_VERBOSITY);
#ifdef HAVE_GROWING_DATASETS
                    _logger->print_message("\n  Growing datasets will not be used.\n", VERB_NORMAL, BAB_VERBOSITY);
#endif    //HAVE_GROWING_DATASETS
                MAiNGO_END_IF
                return _solve_MIQP();
                break;
            case MIQP:
                MAiNGO_IF_BAB_MANAGER
                    _logger->print_message("\n  Recognized the problem to be a mixed-integer quadratic program.\n", VERB_NORMAL, BAB_VERBOSITY);
#ifdef HAVE_GROWING_DATASETS
                    _logger->print_message("\n  Growing datasets will not be used.\n", VERB_NORMAL, BAB_VERBOSITY);
#endif    //HAVE_GROWING_DATASETS
                MAiNGO_END_IF
                return _solve_MIQP();
                break;
#elif HAVE_GUROBI   // If we have Gurobi, we can use it directly for problems of type LP, MIP, QP, or MIQP
            case LP:
                MAiNGO_IF_BAB_MANAGER
                    _logger->print_message("\n  Recognized the problem to be a linear program.\n", VERB_NORMAL, BAB_VERBOSITY);
#ifdef HAVE_GROWING_DATASETS
                    _logger->print_message("\n  Growing datasets will not be used.\n", VERB_NORMAL, BAB_VERBOSITY);
#endif    //HAVE_GROWING_DATASETS
                MAiNGO_END_IF
                    return _solve_MIQP();
                break;
            case MIP:
                MAiNGO_IF_BAB_MANAGER
                    _logger->print_message("\n  Recognized the problem to be a mixed-integer linear program.\n", VERB_NORMAL, BAB_VERBOSITY);
#ifdef HAVE_GROWING_DATASETS
                    _logger->print_message("\n  Growing datasets will not be used.\n", VERB_NORMAL, BAB_VERBOSITY);
#endif    //HAVE_GROWING_DATASETS
                MAiNGO_END_IF
                    return _solve_MIQP();
                break;
            case QP:
                MAiNGO_IF_BAB_MANAGER
                    _logger->print_message("\n  Recognized the problem to be a quadratic program.\n", VERB_NORMAL, BAB_VERBOSITY);
#ifdef HAVE_GROWING_DATASETS
                    _logger->print_message("\n  Growing datasets will not be used.\n", VERB_NORMAL, BAB_VERBOSITY);
#endif    //HAVE_GROWING_DATASETS
                MAiNGO_END_IF
                    return _solve_MIQP();
                break;
            case MIQP:
                MAiNGO_IF_BAB_MANAGER
                    _logger->print_message("\n  Recognized the problem to be a mixed-integer quadratic program.\n", VERB_NORMAL, BAB_VERBOSITY);
#ifdef HAVE_GROWING_DATASETS
                    _logger->print_message("\n  Growing datasets will not be used.\n", VERB_NORMAL, BAB_VERBOSITY);
#endif    //HAVE_GROWING_DATASETS
                MAiNGO_END_IF
                    return _solve_MIQP();
                break;
#else    // If we have neither CPLEX nor Gurobi, we only pass LPs to CLP and solve all other problems as general MINLP
            case LP:
                MAiNGO_IF_BAB_MANAGER
                    _logger->print_message("\n  Recognized the problem to be a linear program.\n", VERB_NORMAL, BAB_VERBOSITY);
#ifdef HAVE_GROWING_DATASETS
                    _logger->print_message("\n  Growing datasets will not be used.\n", VERB_NORMAL, BAB_VERBOSITY);
#endif    //HAVE_GROWING_DATASETS
                MAiNGO_END_IF
                return _solve_MIQP();
                break;
            case QP:
                MAiNGO_IF_BAB_MANAGER
                    _logger->print_message("\n  Recognized the problem to be a quadratic program, but no dedicated QP solver is available.\n  Solving it as an NLP.\n", VERB_NORMAL, BAB_VERBOSITY);
                MAiNGO_END_IF
                _problemStructure = NLP;
                return _solve_MINLP();
            case MIP:
                MAiNGO_IF_BAB_MANAGER
                    _logger->print_message("\n  Recognized the problem to be a mixed-integer linear program, but no dedicated MILP solver is available.\n  Solving it as an MINLP.\n", VERB_NORMAL, BAB_VERBOSITY);
                MAiNGO_END_IF
                _problemStructure = MINLP;
                return _solve_MINLP();
            case MIQP:
                MAiNGO_IF_BAB_MANAGER
                    _logger->print_message("\n  Recognized the problem to be a mixed-integer quadratic program, but no dedicated MIQP solver is available.\n  Solving it as an MINLP.\n", VERB_NORMAL, BAB_VERBOSITY);
                MAiNGO_END_IF
                _problemStructure = MINLP;
                return _solve_MINLP();
#endif
            case NLP:
            case DNLP:
            case MINLP:
            default:
                return _solve_MINLP();
                break;
        }
    }
    else {
        _set_constraint_and_variable_properties();
        _initialize_solve();    // Needed to properly clear everything
        _preprocessTime = get_cpu_time() - _preprocessTime;

        MAiNGO_IF_BAB_MANAGER
            _maingoStatus = INFEASIBLE;
        MAiNGO_END_IF
    }

    return _maingoStatus;
}


////////////////////////////////////////////////////////////////////////
// solve function for MIPs
RETCODE
MAiNGO::_solve_MIQP()
{
    assert(_nobj == 1);

    MAiNGO_IF_BAB_MANAGER
        try {

            // ---------------------------------------------------------------------------------
            // 1: Pre-processing
            // ---------------------------------------------------------------------------------

            // 1a: Initialize  & start timing
            std::string aboutSolver;
#ifdef HAVE_CPLEX
            switch (_maingoSettings->LBP_solver) {
                case lbp::LBP_SOLVER_MAiNGO: {
                    aboutSolver                              = "    MAiNGO solver is not available as (mixed-integer) linear/quadratic solver. Calling CPLEX.\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_CPLEX;
                    break;
                }
                case lbp::LBP_SOLVER_INTERVAL: {
                    aboutSolver                              = "    Interval solver is not available as (mixed-integer) linear/quadratic solver. Calling CPLEX.\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_CPLEX;
                    break;
                }
                case lbp::LBP_SOLVER_CPLEX: {
                    aboutSolver                              = "    Calling CPLEX.\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_CPLEX;
                    break;
                }
                case lbp::LBP_SOLVER_GUROBI: {
#ifdef HAVE_GUROBI
                    aboutSolver                              = "    Calling Gurobi.\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_GUROBI;
#else
                    aboutSolver                              = "    Gurobi is not available on your machine. Calling CPLEX.\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_CPLEX;
#endif
                    break;
                }
                case lbp::LBP_SOLVER_CLP: {
                    if (_problemStructure > LP) {
                        aboutSolver                              = "    CLP is not available as (mixed-integer) linear/quadratic solver. Calling CPLEX.\n";
                        _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_CPLEX;
                    }
                    else {
                        aboutSolver                              = "    Calling CLP.\n";
                        _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_CLP;
                    }
                    break;
                }
                case lbp::LBP_SOLVER_SUBDOMAIN: {
                    aboutSolver                              = "    Subdomain solver is not available as (mixed-integer) linear/quadratic solver. Calling CPLEX.\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_CPLEX;
                    break;
                }
                default:    // GCOVR_EXCL_LINE
                    throw MAiNGOException("    Error in _solve_MIQP: Unknown lower bounding solver: " + std::to_string(_maingoSettings->LBP_solver));   // GCOVR_EXCL_LINE
            }
#elif HAVE_GUROBI
            switch (_maingoSettings->LBP_solver) {
                case lbp::LBP_SOLVER_MAiNGO: {
                    aboutSolver                              = "    MAiNGO solver is not available as (mixed-integer) linear/quadratic solver. Calling Gurobi.\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_GUROBI;
                    break;
                }
                case lbp::LBP_SOLVER_INTERVAL: {
                    aboutSolver                              = "    Interval solver is not available as (mixed-integer) linear/quadratic solver. Calling Gurobi\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_GUROBI;
                    break;
                }
                case lbp::LBP_SOLVER_CPLEX: {
                    aboutSolver                              = "    CPLEX is not available on your machine. Calling Gurobi.\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_GUROBI;
                    break;
                }
                case lbp::LBP_SOLVER_GUROBI: {
                    aboutSolver                              = "    Calling Gurobi.\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_GUROBI;
                    break;
                }
                case lbp::LBP_SOLVER_CLP: {
                    if (_problemStructure > LP) {
                        aboutSolver                              = "    CLP is not available as (mixed-integer) linear/quadratic solver. Calling Gurobi.\n";
                        _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_GUROBI;
                    }
                    else {
                        aboutSolver                              = "    Calling CLP.\n";
                        _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_CLP;
                    }
                    break;
                }
                case lbp::LBP_SOLVER_SUBDOMAIN: {
                    aboutSolver                              = "    Subdomain solver is not available as (mixed-integer) linear/quadratic solver. Calling Gurobi.\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_GUROBI;
                    break;
                }
                default:    // GCOVR_EXCL_LINE
                    throw MAiNGOException("    Error in _solve_MIQP: Unknown lower bounding solver: " + std::to_string(_maingoSettings->LBP_solver));   // GCOVR_EXCL_LINE
            }
#else
            // It is not possible to reach this point with a problem which is not an LP due to switch(_problemStructure) in _analyze_and_solve_problem()
            switch (_maingoSettings->LBP_solver) {
                case lbp::LBP_SOLVER_MAiNGO: {
                    aboutSolver                              = "    MAiNGO solver is not available as a linear solver. Calling CLP.\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_CLP;
                    break;
                }
                case lbp::LBP_SOLVER_INTERVAL: {
                    aboutSolver                              = "    Interval solver is not available as a linear solver. Calling CLP.\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_CLP;
                    break;
                }
                case lbp::LBP_SOLVER_CPLEX: {
                    aboutSolver                              = "    CPLEX is not available on your machine. Calling CLP.\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_CLP;
                    break;
                }
                case lbp::LBP_SOLVER_GUROBI: {
                    aboutSolver                              = "    Gurobi is not available on your machine. Calling CLP.\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_CLP;
                    break;
                }
                case lbp::LBP_SOLVER_CLP: {
                    aboutSolver                              = "    Calling CLP.\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_CLP;
                    break;
                }
                case lbp::LBP_SOLVER_SUBDOMAIN: {
                    aboutSolver                              = "    Subdomain solver is not available as a linear solver. Calling CLP.\n";
                    _maingoSettings->UBP_solverPreprocessing = ubp::UBP_SOLVER_CLP;
                    break;
                }
                default: {
                    std::ostringstream errmsg;
                    errmsg << "    Error in _solve_MIQP: Unknown lower bounding solver: " << _maingoSettings->LBP_solver;
                    throw MAiNGOException(errmsg.str());
                }
            }
#endif
            _print_third_party_software_miqp();

            _initialize_solve();
            _logger->print_message(aboutSolver, VERB_NORMAL, BAB_VERBOSITY);
            _preprocessTime          = get_cpu_time() - _preprocessTime;
            _preprocessTimeWallClock = get_wall_time() - _preprocessTimeWallClock;

            // ---------------------------------------------------------------------------------
            // 2: Solve the problem
            // ---------------------------------------------------------------------------------
            _babTime    = get_cpu_time();
            _babTimeWallClock = get_wall_time();
            _miqpStatus = _myUBSPre->solve(_rootNode, _solutionValue, _solutionPoint);
            _babTime    = get_cpu_time() - _babTime;
            _babTimeWallClock = get_wall_time() - _babTimeWallClock;

            // ---------------------------------------------------------------------------------
            // 3: Determine return code
            // ---------------------------------------------------------------------------------
            if (_miqpStatus == SUBSOLVER_FEASIBLE) {
                _maingoStatus = GLOBALLY_OPTIMAL;
            }
            else if (_miqpStatus == SUBSOLVER_INFEASIBLE) {
                _maingoStatus = INFEASIBLE;
                _solutionPoint.clear();
            }

#ifdef HAVE_MAiNGO_MPI
            BCAST_TAG bcastTag = BCAST_FEASIBLE;
            MPI_Bcast(&bcastTag, 1, MPI_INT, 0, MPI_COMM_WORLD);
#endif
        }
#ifdef HAVE_MAiNGO_MPI
        catch (MAiNGOMpiException& e) {
            BCAST_TAG bcastTag = BCAST_EXCEPTION;
            MPI_Bcast(&bcastTag, 1, MPI_INT, 0, MPI_COMM_WORLD);
            std::ostringstream errmsg;
            errmsg << e.what() << "\n  Encountered a fatal error during MIQP solution.";
            _write_files_error(errmsg.str());
            throw MAiNGOException("  Encountered a fatal error during MIQP solution.", e);
        }
#endif
        catch (const std::exception& e) {   // GCOVR_EXCL_START
#ifdef HAVE_MAiNGO_MPI
            BCAST_TAG bcastTag = BCAST_EXCEPTION;
            MPI_Bcast(&bcastTag, 1, MPI_INT, 0, MPI_COMM_WORLD);
#endif
            std::ostringstream errmsg;
            errmsg << e.what() << "\n  Encountered a fatal error during MIQP solution.";
            _write_files_error(errmsg.str());
            throw MAiNGOException("  Encountered a fatal error during MIQP solution.", e);
        }
        catch (...) {
#ifdef HAVE_MAiNGO_MPI
            BCAST_TAG bcastTag = BCAST_EXCEPTION;
            MPI_Bcast(&bcastTag, 1, MPI_INT, 0, MPI_COMM_WORLD);
#endif
            _write_files_error("  Encountered an unknown fatal error during MIQP solution.");
            throw MAiNGOException("  Encountered an unknown fatal error during MIQP solution.");
        }
#ifdef HAVE_MAiNGO_MPI
        MAiNGO_ELSE    // Workers just wait for a broadcast
            // Check whether an exception was raised
            BCAST_TAG tag;
            MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
            if (tag == BCAST_EXCEPTION) {
                throw MAiNGOMpiException("  Worker " + std::to_string(_rank) + " received message about an exception during MIQP solution.", MAiNGOMpiException::ORIGIN_OTHER);
            }
        MAiNGO_END_IF
#endif
        // GCOVR_EXCL_STOP
        return _maingoStatus;
}


////////////////////////////////////////////////////////////////////////
// solve function for MINLPs
RETCODE
MAiNGO::_solve_MINLP()
{
    assert(_nobj == 1);

    try {

#ifdef HAVE_MAiNGO_MPI
        // Auxiliary variables for parallelization
        std::ostringstream mutestream;
        std::streambuf* coutBuf = std::cout.rdbuf();

        // Mute cout for workers
        MAiNGO_IF_BAB_WORKER
            std::cout.rdbuf(mutestream.rdbuf());
        MAiNGO_END_IF
#endif

        // ---------------------------------------------------------------------------------
        // 1: Pre-processing at root node
        // ---------------------------------------------------------------------------------

        // 1a: Initialize
        MAiNGO_IF_BAB_MANAGER
            _print_third_party_software_minlp();

            _logger->print_message("\n  Pre-processing at root node:\n", VERB_NORMAL, BAB_VERBOSITY);
            if (_maingoSettings->LBP_addAuxiliaryVars) {
                std::ostringstream ostr;
                if (_nvarLbd - _nvar == 1) {
                    ostr << "    Added " << _nvarLbd - _nvar << " auxiliary variable...\n";
                }
                else {
                    ostr << "    Added " << _nvarLbd - _nvar << " auxiliary variables...\n";
                }
                _logger->print_message(ostr.str(), VERB_NORMAL, BAB_VERBOSITY);
            }
            // This stands BEFORE _initialize_solve, since it is checked in _initialize_solve() whether the user has CPLEX installed
            _logger->print_message("    Initialize subsolvers...\n", VERB_NORMAL, BAB_VERBOSITY);
        MAiNGO_END_IF
        _initialize_solve();

#ifdef HAVE_GROWING_DATASETS
        // Warn user when skipping bound tightening
        if ((!_maingoSettings->PRE_pureMultistart) && (_maingoSettings->growing_approach == GROW_APPR_MSEHEURISTIC)) {
            if ((_maingoSettings->BAB_constraintPropagation) || (_maingoSettings->PRE_obbtMaxRounds > 0)) {
                _logger->print_message("  Warning: No bound tightening performed in pre-processing since it may be erroneous for MSE heuristic (cf. growing_approach).\n", VERB_NORMAL, BAB_VERBOSITY);
            }
        }
#endif    // HAVE_GROWING_DATASETS

        if ( (!_maingoSettings->PRE_pureMultistart) && (_maingoSettings->growing_approach != GROW_APPR_MSEHEURISTIC) ) {

            // 1b: Check set options (large values in LP and additional option checks based on chosen lower bounding strategy)
            _myLBS->preprocessor_check_options(_rootNode);
            MAiNGO_MPI_BARRIER

            // 1c: Constraint propagation before a local search is executed
            if (_maingoSettings->BAB_constraintPropagation)
            {
                _root_constraint_propagation();
            }
            MAiNGO_MPI_BARRIER

            if (_rootConPropStatus != TIGHTENING_INFEASIBLE)
            {    // If we haven't proven infeasibility, continue

                // 1d: Optimization-based bound tightening (OBBT) at the root node considering feasibility only
                if (_maingoSettings->PRE_obbtMaxRounds > 0) {
                    _root_obbt_feasibility();
                }
                MAiNGO_MPI_BARRIER

                if (_rootObbtStatus != TIGHTENING_INFEASIBLE)
                {    // If we haven't proven infeasibility, continue

                    // 1e: Try to get a good feasible point using a multi-start heuristic
                    _root_multistart();
                    MAiNGO_MPI_BARRIER

                    if (_rootMultistartStatus == SUBSOLVER_FEASIBLE && !_maingoSettings->terminateOnFeasiblePoint && _solutionValue > _maingoSettings->targetUpperBound)
                    {    // If we have found a feasible point, but it isn't good enough yet, continue

                        // 1f: Constraint propagation after a local search has been executed
                        if (_maingoSettings->BAB_constraintPropagation) {
                            _root_constraint_propagation();
                        }
                        MAiNGO_MPI_BARRIER

                        // 1g: OBBT at the root node considering both feasibility and optimality
                        if (_maingoSettings->PRE_obbtMaxRounds > 0)
                        {
                            _root_obbt_feasibility_optimality();
                        }
                        MAiNGO_MPI_BARRIER
                    }
                }
            }
        }
        else {
            // 1b-g alternative: multi-start only
            _root_multistart();
            MAiNGO_MPI_BARRIER
        }

        // 1h: Timing
        MAiNGO_IF_BAB_MANAGER
            _preprocessTime          = get_cpu_time() - _preprocessTime;
            _preprocessTimeWallClock = get_wall_time() - _preprocessTimeWallClock;

            std::ostringstream outstr;
            outstr << "    CPU time:        " << std::setprecision(6) << _preprocessTime << " s." << std::endl;
            outstr << "    Wall clock time: " << std::setprecision(6) << _preprocessTimeWallClock << " s." << std::endl;
            outstr << "  Done." << std::endl;
            _logger->print_message(outstr.str(), VERB_NORMAL, BAB_VERBOSITY);
        MAiNGO_END_IF

#ifdef HAVE_MAiNGO_MPI
        MAiNGO_IF_BAB_WORKER
            // Turn on cout again for workers
            std::cout.rdbuf(coutBuf);
        MAiNGO_END_IF
#endif
        MAiNGO_MPI_BARRIER

            // ----------------- End 1: Pre-processing at root node ----------------------------


            // ---------------------------------------------------------------------------------
            // 2: Branch & Bound
            // ---------------------------------------------------------------------------------

            if (_rootConPropStatus != TIGHTENING_INFEASIBLE && _rootObbtStatus != TIGHTENING_INFEASIBLE && !_maingoSettings->PRE_pureMultistart && !(_maingoSettings->terminateOnFeasiblePoint && _rootMultistartStatus == SUBSOLVER_FEASIBLE) && _solutionValue > _maingoSettings->targetUpperBound)
        {
#ifdef HAVE_GROWING_DATASETS
            _myBaB->pass_datasets_to_bab(_datasets);

            // Check whether there is at least one free optimization variable
            bool isFree = false;
            for (auto i = 0; i < _nvar; i++) {
                if (_originalVariables[i].get_upper_bound() > _originalVariables[i].get_lower_bound()) {
                    isFree = true;
                    break;
                }
            }
            // Change full dataset (root for pre-processing) to smallest reduced dataset (root of BaB) if these are different and problem is not fixed
            if ((_ndata > 1) && isFree) {
                _rootNode.set_index_dataset(1);
            }
            else {
                if (_ndata > 1) {
                    _logger->print_message("\n  Warning: Growing datasets will not be used since all optimization variables are fixed anyway.\n", VERB_NORMAL, BAB_VERBOSITY);
                }
                else {
                    _logger->print_message("\n  Warning: Growing datasets will not be used since only a single objective_per_data (1 data point) has been provided.\n", VERB_NORMAL, BAB_VERBOSITY);
                }
            }
#endif
            _logger->create_iterations_csv_file(_maingoSettings->writeCsv);
            _babStatus = _myBaB->solve(_rootNode, _solutionValue, _solutionPoint, _preprocessTime, _preprocessTimeWallClock, _babTime, _babTimeWallClock);
            // Get the B&B time only
            _babTime          -= _preprocessTime;
            _babTimeWallClock -= _preprocessTimeWallClock;
        }
        // ------------------------- End 2: Branch & Bound ---------------------------------


        // ---------------------------------------------------------------------------------
        // 3: Determine return code
        // ---------------------------------------------------------------------------------
        MAiNGO_IF_BAB_MANAGER
            if (_rootObbtStatus == TIGHTENING_INFEASIBLE || _rootConPropStatus == TIGHTENING_INFEASIBLE) {
                _maingoStatus = INFEASIBLE;
            }
            else {
                if (_babStatus == babBase::enums::BAB_RETCODE::GLOBALLY_OPTIMAL) {
                    _maingoStatus = GLOBALLY_OPTIMAL;
                }
                else if (_babStatus == babBase::enums::BAB_RETCODE::INFEASIBLE) {
                    _maingoStatus = INFEASIBLE;
                }
                else if (_babStatus == babBase::enums::BAB_RETCODE::TARGET_UBD || _babStatus == babBase::enums::BAB_RETCODE::TARGET_LBD) {
                    _maingoStatus = BOUND_TARGETS;
                }
                else {
                    if (!_solutionPoint.empty()) {
                        if (_solutionValue <= _maingoSettings->targetUpperBound) {
                            _maingoStatus = BOUND_TARGETS;
                        }
                        else {
                            _maingoStatus = FEASIBLE_POINT;
                        }
                    }
                    else {
                        _maingoStatus = NO_FEASIBLE_POINT_FOUND;
                    }
                }
            }
        MAiNGO_END_IF

        // ----------------------------- End 3: Output -------------------------------------


#ifdef HAVE_GROWING_DATASETS
        // ---------------------------------------------------------------------------------
        // 4: Post-processing for heuristic mode with growing datasets
        // ---------------------------------------------------------------------------------
        if ((_maingoSettings->growing_approach > GROW_APPR_DETERMINISTIC) && (_maingoSettings->growing_maxTimePostprocessing > 0)) {
            if (_solutionValue < _maingoSettings->infinity) {
                _myBaB->postprocess(_solutionValue);
            }
            else {
                MAiNGO_IF_BAB_MANAGER
                _logger->print_message("  Warning: No feasible solution found during heuristic B&B algorithm with growing datasets. Skipping post-processing...\n", VERB_NORMAL, BAB_VERBOSITY);
                MAiNGO_END_IF
            }
        }
        // ------------------------ End 4: Post-processing ---------------------------------
#endif // HAVE_GROWING_DATASETS

        return _maingoStatus;
    }
    // GCOVR_EXCL_START
#ifdef HAVE_MAiNGO_MPI
    catch (MAiNGOMpiException& e) {
        MAiNGO_IF_BAB_MANAGER
            std::ostringstream errmsg;
            errmsg << e.what() << "\n  Encountered a fatal error during solution.";
            _write_files_error(errmsg.str());
            throw MAiNGOException("  Encountered a fatal error during solution.", e);
            MAiNGO_ELSE
                throw;
            MAiNGO_END_IF
    }
#endif
    catch (const std::exception& e) {
        MAiNGO_IF_BAB_MANAGER
            std::ostringstream errmsg;
            errmsg << e.what() << "\n  Encountered a fatal error during solution.";
            _write_files_error(errmsg.str());
            throw MAiNGOException("  Encountered a fatal error during solution.", e);
            MAiNGO_ELSE
                throw;
            MAiNGO_END_IF
    }
    catch (...) {
        MAiNGO_IF_BAB_MANAGER
            _write_files_error("  Encountered an unknown fatal error during solution.");
            throw MAiNGOException("  Encountered an unknown fatal error during solution.");
            MAiNGO_ELSE
                throw;
            MAiNGO_END_IF
    }
    // GCOVR_EXCL_STOP
}

/////////////////////////////////////////////////////////////////////////
// initializes internal model representation
void
MAiNGO::set_model(std::shared_ptr<MAiNGOmodel> myModel)
{

    // Set correct status
    MAiNGO_IF_BAB_MANAGER
        _maingoStatus = NOT_SOLVED_YET;
#ifdef HAVE_MAiNGO_MPI
        MAiNGO_ELSE
            _maingoStatus = JUST_A_WORKER_DONT_ASK_ME;
#endif
        MAiNGO_END_IF
        _problemStructure   = MINLP;    // default
        _feasibilityProblem = false;
        _modelSpecified     = false;
        _DAGconstructed     = false;

        // Store pointer to problem
        _myFFVARmodel = myModel;

        // Read optimization variables (and optionally initial point)
        _originalVariables = myModel->get_variables();
        if (_originalVariables.empty()) {
            throw MAiNGOException("  MAiNGO: Error while setting model: Empty vector of optimization variables.");
        }
        _initialPointOriginal = myModel->get_initial_point();
        if ((!_initialPointOriginal.empty()) && (_initialPointOriginal.size() != _originalVariables.size())) {
            std::ostringstream errmsg;
            errmsg << "  MAiNGO: Error while setting model: Dimension of initial guess (" << _initialPointOriginal.size() << ") is inconsistent with number of variables (" << _originalVariables.size() << ").";
            throw MAiNGOException(errmsg.str());
        }

        // Save the size of original variables, this is needed since some of the user-defined variables may be not used in the problem and will be eliminated when the DAG is constructed
        _nvarOriginal           = _originalVariables.size();
        _nvarOriginalContinuous = 0;
        _nvarOriginalBinary     = 0;
        _nvarOriginalInteger    = 0;
        for (size_t i = 0; i < _originalVariables.size(); i++) {
            switch (_originalVariables[i].get_variable_type()) {
                case babBase::enums::VT_CONTINUOUS:
                    _nvarOriginalContinuous++;
                    break;
                case babBase::enums::VT_BINARY:
                    _nvarOriginalBinary++;
                    break;
                case babBase::enums::VT_INTEGER:
                    _nvarOriginalInteger++;
                    break;
                default:    // GCOVR_EXCL_LINE
                    throw MAiNGOException("  MAiNGO: Error while setting model: unknown variable type " + std::to_string(_originalVariables[i].get_variable_type()));   //GCOVR_EXCL_LINE
            }
        }

        // Check if the specified variable bounds define a non-empty set
        _infeasibleVariables.clear();
        for (unsigned iVar = 0; iVar < _originalVariables.size(); ++iVar) {
            if (!_originalVariables.at(iVar).has_nonempty_host_set()) {
                _infeasibleVariables.push_back(&(_originalVariables.at(iVar)));
            }
        }

        // Confirm model is ready to use
        _modelSpecified = true;
}


////////////////////////////////////////////////////////////////////////
// construct DAG
void
MAiNGO::_construct_DAG()
{

    // Build temporary DAG from problem definition first (before getting rid of unused variables)
    mc::FFGraph tmpDAG;
    std::vector<mc::FFVar> tmpDAGVars;
    tmpDAGVars.reserve(_nvarOriginal);  // reserve to avoid reallocating and creating unnecessary copies!
    std::vector<mc::FFVar> tmpFunctions;
    // Declare the correct amount of DAG variables
    for (unsigned int i = 0; i < _nvarOriginal; i++) {
        tmpDAGVars.emplace_back(&tmpDAG);
    }

    _modelOutput.clear();
    try {
        _modelOutput = _myFFVARmodel->evaluate(tmpDAGVars);
#ifdef HAVE_GROWING_DATASETS
        _initialize_objective_from_objective_per_data();
#endif
    }
    catch (std::exception& e) {
        throw MAiNGOException("  MAiNGO: Error while evaluating specified model to construct DAG.", e);
    }
    catch (...) {
        throw MAiNGOException("  MAiNGO: Unknown error while evaluating specified model to construct DAG.");
    }

    _classify_objective_and_constraints(tmpFunctions, tmpDAGVars);
#ifdef HAVE_GROWING_DATASETS
    _initialize_dataset();
#endif

    // Recognize and remove variables that do not participate in the actual problem
    // Recognize first
    _removedVariables = std::vector<bool>(_nvarOriginal, false);
    _variables.clear();
    _variablesLbd.clear();
    mc::FFGraph::t_Vars Vars = tmpDAG.Vars();
    mc::FFGraph::it_Vars itv = Vars.begin();
    unsigned nRemoved        = 0;
    for (unsigned i = 0; itv != Vars.end() && (*itv)->id().first <= mc::FFVar::VAR; ++itv, ++i) {
        // It is possible that a variable is used alone in a constraint, e.g., x <= 0 or in any output (don't ask me why someone would do that but it is possible)
        // and we have to recognize that and not remove this constraint/variable
        bool used_in_functions = false;
        for (unsigned j = 0; j < tmpFunctions.size() && !used_in_functions; j++) {
            if (tmpFunctions[j].id() == (*itv)->id()) {
                used_in_functions = true;
            }
        }
        if ((*itv)->ops().second.empty() && !used_in_functions) {
            _removedVariables[i] = true;
            nRemoved++;
        }
        else {
            _variables.push_back(_originalVariables[i]);
            _variablesLbd.push_back(_originalVariables[i]);
        }
    }
    _nvar = _nvarOriginal - nRemoved;

    // Make actual DAG without these unnecessary variables
    _DAG.clear();
    _DAGvars.clear();
    _DAGvars.reserve(_nvar);
    unsigned iNewVars = 0;
    for (unsigned int iOldVars = 0; iOldVars < _nvarOriginal; iOldVars++) {
        if (!_removedVariables[iOldVars]) {
            _DAGvars.emplace_back(&_DAG);
            iNewVars++;
        }
    }
    for (int i = _nvarOriginal - 1; i >= 0; i--) {
        if (_removedVariables[i]) {
            tmpDAGVars.erase(tmpDAGVars.begin() + i);
        }
    }
    // Re-evaluate the DAG to recognize hidden zeros
    std::vector<mc::FFVar> tmpDAGoutputFunctions;
    bool foundHiddenZero = true;
    while (foundHiddenZero) {    // Re-evaluate until no more hidden zeros are found
        for (size_t i = 0; i < tmpDAGoutputFunctions.size(); i++) {
            tmpFunctions.push_back(tmpDAGoutputFunctions[i]);
        }
        mc::FFSubgraph tmpSubgraph = tmpDAG.subgraph(tmpFunctions.size(), tmpFunctions.data());
        std::vector<mc::FFVar> tmpDummy(tmpFunctions.size());
        _resultVars.clear();
        _resultVars.resize(tmpFunctions.size());
        tmpDAG.eval(tmpSubgraph, tmpDummy, tmpFunctions.size(), tmpFunctions.data(), _resultVars.data(), tmpDAGVars.size(), tmpDAGVars.data(), tmpDAGVars.data());    // Get functions
        tmpFunctions.clear();
        tmpDAGoutputFunctions.clear();
        foundHiddenZero = _check_for_hidden_zero_constraints(tmpDAGVars, tmpFunctions, tmpDAGoutputFunctions);
    }

    // After no more hidden zero are found, construct the actual DAG
    for (size_t i = 0; i < tmpDAGoutputFunctions.size(); i++) {
        tmpFunctions.push_back(tmpDAGoutputFunctions[i]);
    }
    mc::FFSubgraph tmpSubgraph = tmpDAG.subgraph(tmpFunctions.size(), tmpFunctions.data());
    std::vector<mc::FFVar> tmpDummy(tmpFunctions.size());
    _resultVars.clear();
    _resultVars.resize(tmpFunctions.size());
    tmpDAG.eval(tmpSubgraph, tmpDummy, tmpFunctions.size(), tmpFunctions.data(), _resultVars.data(), tmpDAGVars.size(), tmpDAGVars.data(), _DAGvars.data());    // Get functions

    _DAGfunctions.clear();
    _DAGoutputFunctions.clear();

    // Just to make sure, check one last time
    _check_for_hidden_zero_constraints(_DAGvars, _DAGfunctions, _DAGoutputFunctions);

    // Set initial point properly -- remove not used variables
    _initialPoint.clear();
    for (unsigned int i = 0; i < _initialPointOriginal.size(); i++) {
        if (!_removedVariables[i]) {
            _initialPoint.push_back(_initialPointOriginal[i]);
        }
    }

    _DAGlbd.clear();
    _DAGvarsLbd.clear();
    _DAGvarsLbd.reserve(_DAGvars.size());
    _DAGfunctionsLbd.clear();
    _DAGoutputFunctionsLbd.clear();
    _nvarLbd              = _nvar;
    _nauxiliaryRelOnlyEqs = 0;
    if (_maingoSettings->LBP_addAuxiliaryVars) {
        for (size_t i = 0; i < _DAGvars.size(); i++) {
            _DAGvarsLbd.emplace_back(&_DAGlbd);
        }

        _resultVars.clear();
        _resultVars.resize(tmpFunctions.size());
        tmpDAG.eval(tmpSubgraph, tmpDummy, tmpFunctions.size(), tmpFunctions.data(), _resultVars.data(), tmpDAGVars.size(), tmpDAGVars.data(), _DAGvarsLbd.data());    // Get functions

        // Just to make sure, check one last time
        _check_for_hidden_zero_constraints(_DAGvarsLbd, _DAGfunctionsLbd, _DAGoutputFunctionsLbd);

        try {
            _add_auxiliary_variables_to_lbd_dag();
        }
        catch (const filib::interval_io_exception& e) { // GCOVR_EXCL_START
            MAiNGO_IF_BAB_MANAGER
                const std::string errmsg = "  Encountered a fatal error in intervals while adding auxiliary variables to the DAG used for lower bounding.";
                std::ostringstream completeMessage;
                completeMessage << e.what() << std::endl
                                << errmsg;
                _write_files_error(completeMessage.str());
                throw MAiNGOException(completeMessage.str());
                MAiNGO_ELSE
                    throw;
                MAiNGO_END_IF
        }
        catch (const MC::Exceptions& e) {
            MAiNGO_IF_BAB_MANAGER
                const std::string errmsg = "  Encountered a fatal error in McCormick relaxations while adding auxiliary variables to the DAG used for lower bounding.";
                std::ostringstream completeMessage;
                completeMessage << e.what() << std::endl
                                << errmsg;
                _write_files_error(completeMessage.str());
                throw MAiNGOException(completeMessage.str());
                MAiNGO_ELSE
                    throw;
                MAiNGO_END_IF
        }
        catch (const vMC::Exceptions& e) {
            MAiNGO_IF_BAB_MANAGER
                const std::string errmsg = "  Encountered a fatal error in vMcCormick relaxations while adding auxiliary variables to the DAG used for lower bounding.";
                std::ostringstream completeMessage;
                completeMessage << e.what() << std::endl
                                << errmsg;
                _write_files_error(completeMessage.str());
                throw MAiNGOException(completeMessage.str());
                MAiNGO_ELSE
                    throw;
                MAiNGO_END_IF
        }
        catch (const std::exception& e) {
            MAiNGO_IF_BAB_MANAGER
                const std::string errmsg = "  Encountered a fatal error while adding auxiliary variables to the DAG used for lower bounding.";
                std::ostringstream completeMessage;
                completeMessage << e.what() << std::endl
                                << errmsg;
                _write_files_error(completeMessage.str());
                throw MAiNGOException(errmsg, e);
                MAiNGO_ELSE
                    throw;
                MAiNGO_END_IF
        }
        catch (...) {
            MAiNGO_IF_BAB_MANAGER
                const std::string errmsg = "  Encountered an unknown fatal error while adding auxiliary variables to the DAG used for lower bounding.";
                _write_files_error(errmsg);
                throw MAiNGOException(errmsg);
                MAiNGO_ELSE
                    throw;
                MAiNGO_END_IF
        }
        // GCOVR_EXCL_STOP
    }

    _DAGconstructed = true;
    // ----- debugging purposes ----
    // std::ofstream o_F("DAG.txt", std::ios_base::out);
    // o_F<< _DAG <<std::endl;
    // print DAG as dot file, it can be converted to a nice image with a dot script, which can be found, e.g., on the RWTH cluster
    // std::ofstream o_F("F.dot", std::ios_base::out);
    // _DAG.dot_script(_DAGfunctions.size(), _DAGfunctions.data(), o_F);
    // o_F.close();
}


////////////////////////////////////////////////////////////////////////
// initializes subsolvers and internal solution variables for NLPs and MINLPs
void
MAiNGO::_initialize_solve()
{

    // Initialize subsolvers (upper bounding is always needed, lower bounding and B&B are not)

    _myUBSPre = ubp::make_ubp_solver(_DAG, _DAGvars, _DAGfunctions, _variables, _nineq, _neq, _nineqSquash, _maingoSettings, _logger, _nonconstantConstraintsUBP, ubp::UpperBoundingSolver::USE_PRE);
#ifdef HAVE_GROWING_DATASETS
    //objective per data saved after obj and non-constant constraints
    _myUBSPre->pass_data_position_to_solver(_datasets, 1 + _nineq + _neq + _nineqSquash + _nineqRelaxationOnly + _neqRelaxationOnly);
    if (_maingoSettings->growing_approach == GROW_APPR_MSEHEURISTIC) {
        _myUBSPre->pass_use_mse_to_solver(true);
    }
    else {
        _myUBSPre->pass_use_mse_to_solver(false);
    }
#endif    // HAVE_GROWING_DATASETS

    _myUBSBab = nullptr;
    _myLBS    = nullptr;
    _myBaB    = nullptr;
    if ((_problemStructure >= NLP) || (_myTwoStageFFVARmodel && _maingoSettings->TS_useLowerBoundingSubsolvers)) {
        if (!_maingoSettings->PRE_pureMultistart) {    // For a pure multistart, lower bounding solver and the B&B tree are not needed
            if (_myTwoStageFFVARmodel && _maingoSettings->TS_useUpperBoundingSubsolvers)
                _myUBSBab = ubp::make_ubpTwoStage_solver(_myTwoStageFFVARmodel, _DAG, _DAGvars, _DAGfunctions, _variables, _nineq, _neq, _nineqSquash,
                                                         _maingoSettings, _logger, _nonconstantConstraintsUBP, ubp::UpperBoundingSolver::USE_BAB);
            else
                _myUBSBab = ubp::make_ubp_solver(_DAG, _DAGvars, _DAGfunctions, _variables, _nineq, _neq, _nineqSquash,
                                                 _maingoSettings, _logger, _nonconstantConstraintsUBP, ubp::UpperBoundingSolver::USE_BAB);
            if (_maingoSettings->LBP_addAuxiliaryVars) {
                if (_myTwoStageFFVARmodel && _maingoSettings->TS_useLowerBoundingSubsolvers)
                    _myLBS = lbp::make_two_stage_lbp_solver(_myTwoStageFFVARmodel, _DAGlbd, _DAGvarsLbd, _DAGfunctionsLbd, _variablesLbd, _variableIsLinear, _nineq, _neq,
                                                            _nineqRelaxationOnly, _neqRelaxationOnly + _nauxiliaryRelOnlyEqs, _nineqSquash,
                                                            _maingoSettings, _logger, _nonconstantConstraints);
                else
                    _myLBS = lbp::make_lbp_solver(_DAGlbd, _DAGvarsLbd, _DAGfunctionsLbd, _variablesLbd, _variableIsLinear, _nineq, _neq,
                                                  _nineqRelaxationOnly, _neqRelaxationOnly + _nauxiliaryRelOnlyEqs, _nineqSquash,
                                                  _maingoSettings, _logger, _nonconstantConstraints);
            }
            else {
                if (_myTwoStageFFVARmodel && _maingoSettings->TS_useLowerBoundingSubsolvers)
                    _myLBS = lbp::make_two_stage_lbp_solver(_myTwoStageFFVARmodel, _DAG, _DAGvars, _DAGfunctions, _variables, _variableIsLinear, _nineq, _neq,
                                                          _nineqRelaxationOnly, _neqRelaxationOnly, _nineqSquash,
                                                          _maingoSettings, _logger, _nonconstantConstraints);
                else
                    _myLBS = lbp::make_lbp_solver(_DAG, _DAGvars, _DAGfunctions, _variables, _variableIsLinear, _nineq, _neq,
                                                  _nineqRelaxationOnly, _neqRelaxationOnly, _nineqSquash,
                                                  _maingoSettings, _logger, _nonconstantConstraints);
            }
#ifdef HAVE_GROWING_DATASETS
            //objective per data saved after obj and non-constant constraints
            _myUBSBab->pass_data_position_to_solver(_datasets, 1 + _nineq + _neq + _nineqSquash + _nineqRelaxationOnly + _neqRelaxationOnly);
            _myLBS->pass_data_position_to_solver(_datasets, 1 + _nineq + _neq + _nineqSquash + _nineqRelaxationOnly + _neqRelaxationOnly + _nauxiliaryRelOnlyEqs);
            if (_maingoSettings->growing_approach == GROW_APPR_MSEHEURISTIC) {
                _myUBSBab->pass_use_mse_to_solver(true);
                _myLBS->pass_use_mse_to_solver(true);
            }
            else {
                _myUBSBab->pass_use_mse_to_solver(false);
                _myLBS->pass_use_mse_to_solver(false);
            }
            if (_maingoSettings->growing_useResampling) {
                _myLBS->pass_resampled_dataset_to_solver(_datasetResampled);
            }
#endif    // HAVE_GROWING_DATASETS

            _myBaB = std::make_shared<bab::BranchAndBound>(_variablesLbd, _myLBS, _myUBSBab, _maingoSettings, _logger, /*number of variables w/o auxiliaries*/ _nvar, _inputStream, _babFileName);

#if defined(MAiNGO_DEBUG_MODE) && defined(HAVE_GROWING_DATASETS)
            _myLBSFull = nullptr;
            if (_maingoSettings->LBP_addAuxiliaryVars) {
                _myLBSFull = lbp::make_lbp_solver(_DAGlbd, _DAGvarsLbd, _DAGfunctionsLbd, _variablesLbd, _variableIsLinear, _nineq, _neq, _nineqRelaxationOnly, _neqRelaxationOnly + _nauxiliaryRelOnlyEqs,
                                                  _nineqSquash, _maingoSettings, _logger, _nonconstantConstraints);
            }
            else {
                _myLBSFull = lbp::make_lbp_solver(_DAG, _DAGvars, _DAGfunctions, _variables, _variableIsLinear, _nineq, _neq, _nineqRelaxationOnly, _neqRelaxationOnly,
                                                  _nineqSquash, _maingoSettings, _logger, _nonconstantConstraints);
            }
            _myBaB->pass_LBSFull_to_bab(_myLBSFull);
#endif

            if (_maingoSettings->TS_useLowerBoundingSubsolvers) {
                // Preprocessor macro to avoid excessive code duplication
                #define ASSIGN_CALLBACK(subsolver_class) {                                           \
                  auto ptr = std::dynamic_pointer_cast<lbp::LbpTwoStage<subsolver_class>>(_myLBS);   \
                  if (ptr != nullptr) {                                                              \
                    _myBaB->setup_two_stage_branching(                                               \
                      _myTwoStageFFVARmodel->Nx,                                                     \
                      _myTwoStageFFVARmodel->Ny,                                                     \
                      _myTwoStageFFVARmodel->w,                                                      \
                      ptr->_subproblemBounds,                                                        \
                      /** Callback for solve_sibling_subproblems */                                  \
                      [=](                                                                           \
                        lbp::SiblingResults& siblingResults,                                         \
                        double ubd,                                                                  \
                        int obbtType                                                                 \
                      ) {                                                                            \
                        return ptr->solve_sibling_subproblems(                                       \
                          siblingResults,                                                            \
                          ubd,                                                                       \
                          obbtType                                                                   \
                        );                                                                           \
                      },                                                                             \
                      _maingoSettings->TS_strongBranchingThreshold,                                  \
                      _maingoSettings->TS_maxBranchingPower                                          \
                    );                                                                               \
                  };                                                                                 \
                }
                switch (_maingoSettings->LBP_solver) {
                    case lbp::LBP_SOLVER::LBP_SOLVER_MAiNGO: {
                        ASSIGN_CALLBACK(lbp::LowerBoundingSolver)
                        break;
                    }
                    case lbp::LBP_SOLVER::LBP_SOLVER_INTERVAL: {
                        ASSIGN_CALLBACK(lbp::LbpInterval)
                        break;
                    }
#ifdef HAVE_CPLEX
                    case lbp::LBP_SOLVER::LBP_SOLVER_CPLEX: {
                        ASSIGN_CALLBACK(lbp::LbpCplex)
                        break;
                    }
#endif
#ifdef HAVE_GUROBI
                    case lbp::LBP_SOLVER::LBP_SOLVER_GUROBI: {
                        ASSIGN_CALLBACK(lbp::LbpGurobi)
                        break;
                    }
#endif
                    case lbp::LBP_SOLVER::LBP_SOLVER_CLP: {
                        ASSIGN_CALLBACK(lbp::LbpClp)
                        break;
                    }
                    case lbp::LBP_SOLVER::LBP_SOLVER_SUBDOMAIN: {
                        ASSIGN_CALLBACK(lbp::LbpSubinterval)
                        break;
                    }
                }
            } // End if Two Stage
        } // End if multistart
    } // End (>=NLP || Two Stage)


    // Initialize solution variables
    _solutionPoint.clear();
    _solutionValue    = _maingoSettings->infinity;
    _babTime          = 0.;
    _babTimeWallClock = 0.;

    // Initialize status
    MAiNGO_IF_BAB_MANAGER
        _maingoStatus = NO_FEASIBLE_POINT_FOUND;
#ifdef HAVE_MAiNGO_MPI
        MAiNGO_ELSE
            _maingoStatus = JUST_A_WORKER_DONT_ASK_ME;
#endif
        MAiNGO_END_IF
        _rootObbtStatus       = TIGHTENING_UNCHANGED;
        _rootConPropStatus    = TIGHTENING_UNCHANGED;
        _rootMultistartStatus = SUBSOLVER_INFEASIBLE;
        _miqpStatus           = SUBSOLVER_INFEASIBLE;
        _babStatus            = babBase::enums::NOT_SOLVED_YET;

        // Initialize root node
        // with full dataset (MAiNGO with growing datasets)
        if (_maingoSettings->LBP_addAuxiliaryVars) {
            _rootNode = babBase::BabNode(-_maingoSettings->infinity, _variablesLbd);
        }
        else {
            _rootNode = babBase::BabNode(-_maingoSettings->infinity, _variables);
        }

        // Clear logging (except for settings)
        _objectivesAtRoot.clear();
        _feasibleAtRoot.clear();
        _initialPointFeasible = false;

        // Tell user about changed variable bounds
        for (size_t i = 0; i < _originalVariables.size(); i++) {
            std::string variableType = "";
            switch (_originalVariables[i].get_variable_type()) {
                case babBase::enums::VT_BINARY:
                    variableType = "binary";
                    break;
                case babBase::enums::VT_INTEGER:
                    variableType = "integer";
                    break;
                default:
                    break;
            }
            if (_originalVariables[i].bounds_changed_from_user_input()) {
                std::ostringstream ostr;
                ostr << "    Changing bounds of " << variableType << " variable " << _originalVariables[i].get_name() << " from "
                     << "[" << _originalVariables[i].get_user_lower_bound() << ", " << _originalVariables[i].get_user_upper_bound() << "] to "
                     << "[" << _originalVariables[i].get_lower_bound() << ", " << _originalVariables[i].get_upper_bound() << "].\n";
                _logger->print_message(ostr.str(), VERB_NORMAL, BAB_VERBOSITY);
            }
        }

        std::srand(42);    // For reproducible results despite (pseudo-)random starting points
}


////////////////////////////////////////////////////////////////////////
// conducts feasibility-based bound tightening at the root node
void
MAiNGO::_root_obbt_feasibility()
{

    MAiNGO_IF_BAB_MANAGER
        _logger->print_message("    Optimization-based bound tightening (feasibility only)...\n", VERB_NORMAL, BAB_VERBOSITY);

        for (unsigned iLP = 0; iLP < _maingoSettings->PRE_obbtMaxRounds; iLP++) {

            _logger->print_message("        Run " + std::to_string(iLP + 1) + "\n", VERB_ALL, BAB_VERBOSITY);
            try {
                _rootObbtStatus = _myLBS->solve_OBBT(_rootNode, _maingoSettings->infinity, lbp::OBBT_FEAS, true /*include linear variables*/);
            }
            catch (std::exception& e) { // GCOVR_EXCL_START
#ifdef HAVE_MAiNGO_MPI
                // Inform workers about exceptions
                BCAST_TAG bcastTag = BCAST_EXCEPTION;
                MPI_Bcast(&bcastTag, 1, MPI_INT, 0, MPI_COMM_WORLD);
#endif
                throw MAiNGOException("  Encountered a fatal error during feasibility-based OBBT during pre-processing.", e);
            }
            catch (...) {
#ifdef HAVE_MAiNGO_MPI
                // Inform workers about exceptions
                BCAST_TAG bcastTag = BCAST_EXCEPTION;
                MPI_Bcast(&bcastTag, 1, MPI_INT, 0, MPI_COMM_WORLD);
#endif
                throw MAiNGOException("  Encountered an unknown fatal error during feasibility-based OBBT during pre-processing.");
            }
            // GCOVR_EXCL_STOP

            // If we make no more progress or prove infeasibility, terminate
            if ((_rootObbtStatus == TIGHTENING_INFEASIBLE) || (_rootObbtStatus == TIGHTENING_UNCHANGED)) {
                break;
            }
        }

        if (_rootObbtStatus == TIGHTENING_INFEASIBLE) {
            _logger->print_message("      Found problem to be infeasible.\n", VERB_NORMAL, BAB_VERBOSITY);
        }
#ifdef HAVE_MAiNGO_MPI
        // Send results to workers
        if (_rootObbtStatus == TIGHTENING_INFEASIBLE) {
            BCAST_TAG tag = BCAST_INFEASIBLE;
            MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
        }
        else {
            BCAST_TAG tag = BCAST_FEASIBLE;
            MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
            for (unsigned int i = 1; i < (unsigned int)_nProcs; i++) {
                send_babnode(_rootNode, i);
            }
        }
        MAiNGO_ELSE    // MAiNGO_IF_BAB_WORKER
            // Check whether an exception was raised
            BCAST_TAG tag;
            MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
            if (tag == BCAST_EXCEPTION) {
                throw MAiNGOMpiException("  Worker " + std::to_string(_rank) + " received message about an exception during feasibility-based OBBT during pre-processing.", MAiNGOMpiException::ORIGIN_OTHER);
            }
            else if (tag == BCAST_INFEASIBLE) {
                _rootObbtStatus = TIGHTENING_INFEASIBLE;
            }
            else {
                recv_babnode(_rootNode, 0, _nvarLbd);
            }
#endif
        MAiNGO_END_IF
}


////////////////////////////////////////////////////////////////////////
// conducts feasibility- and optimality-based bound tightening at the root node
void
MAiNGO::_root_obbt_feasibility_optimality()
{

    MAiNGO_IF_BAB_MANAGER
        _logger->print_message("    Optimization-based bound tightening (feasibility and optimality)...\n", VERB_NORMAL, BAB_VERBOSITY);

        babBase::BabNode tmpNode(_rootNode);
        try {
            _rootObbtStatus = _myLBS->solve_OBBT(tmpNode, _solutionValue, lbp::OBBT_FEASOPT, true /*include linear variables*/);
        }
        catch (std::exception& e) { // GCOVR_EXCL_START
#ifdef HAVE_MAiNGO_MPI
            // Inform workers about exceptions
            BCAST_TAG bcastTag = BCAST_EXCEPTION;
            MPI_Bcast(&bcastTag, 1, MPI_INT, 0, MPI_COMM_WORLD);
#endif
            throw MAiNGOException("  Encountered a fatal error during feasibility- and optimality-based OBBT during pre-processing.", e);
        }
        catch (...) {
#ifdef HAVE_MAiNGO_MPI
            BCAST_TAG tag = BCAST_EXCEPTION;
            MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
#endif
            throw MAiNGOException("  Encountered an unknown fatal error during feasibility- and optimality-based OBBT during pre-processing.");
        }
        // GCOVR_EXCL_STOP

        if (_rootObbtStatus == TIGHTENING_INFEASIBLE) { // GCOVR_EXCL_START
            std::string str = "      Warning: OBBT declared the problem infeasible although a feasible point was found.\n";
            str += "               This may be caused by numerical difficulties or an isolated optimum in your model.\n";
            str += "               Turning off OBBT, restoring valid bounds and proceeding...\n";
            _logger->print_message(str, VERB_NORMAL, BAB_VERBOSITY);
            _maingoSettings->PRE_obbtMaxRounds   = 0;
            _maingoSettings->BAB_alwaysSolveObbt = false;
            _rootObbtStatus                      = TIGHTENING_UNCHANGED;
#ifdef HAVE_MAiNGO_MPI
            BCAST_TAG tag = BCAST_TIGHTENING_INFEASIBLE;
            MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
        }
        else if (_rootObbtStatus == TIGHTENING_UNCHANGED) {
            BCAST_TAG tag = BCAST_FEASIBLE;
            MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
#endif
        // GCOVR_EXCL_STOP
        }
        else if (_rootObbtStatus == TIGHTENING_CHANGED) {
            _rootNode = tmpNode;
#ifdef HAVE_MAiNGO_MPI
            BCAST_TAG tag = BCAST_FEASIBLE;
            MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
            // Manager does not send the root node to workers, since they will get the node in the B&B algorithm
#endif
        }
#ifdef HAVE_MAiNGO_MPI
        MAiNGO_ELSE    // MAiNGO_IF_BAB_WORKER
            // Check whether an exception was raised or if tightening provided an incorrect claim
            BCAST_TAG tag;
            MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
            if (tag == BCAST_EXCEPTION) {
                throw MAiNGOMpiException("  Worker " + std::to_string(_rank) + " received message about an exception during feasibility- and optimality-based during pre-processing.", MAiNGOMpiException::ORIGIN_OTHER);
            }
            else if (tag == BCAST_TIGHTENING_INFEASIBLE) {
                _maingoSettings->PRE_obbtMaxRounds   = 0;
                _maingoSettings->BAB_alwaysSolveObbt = 0;
            }
            // Note that workers don't need the possibly changed node, since they will get new nodes in the B&B algorithm
#endif
        MAiNGO_END_IF    //MAiNGO_IF_BAB_MANAGER
}


////////////////////////////////////////////////////////////////////////
// conducts constraint propagation at root node
void
MAiNGO::_root_constraint_propagation()
{

    MAiNGO_IF_BAB_MANAGER
        _logger->print_message("    Constraint propagation...\n", VERB_NORMAL, BAB_VERBOSITY);

        babBase::BabNode tmpNode(_rootNode);
        if (_rootMultistartStatus == SUBSOLVER_FEASIBLE) {
            _rootConPropStatus = _myLBS->do_constraint_propagation(tmpNode, _solutionValue, 30);
        }
        else {
            _rootConPropStatus = _myLBS->do_constraint_propagation(tmpNode, _maingoSettings->infinity, 30);
        }

        // If we prove infeasibility, don't overwrite root node
        if (_rootConPropStatus == TIGHTENING_INFEASIBLE) {
            // Don't overwrite root node
            if (_rootMultistartStatus == SUBSOLVER_FEASIBLE) {    // GCOVR_EXCL_START
                std::string str = "      Warning: Constraint propagation declared the problem infeasible although a feasible point was found.\n";
                str += "               This may be caused by numerical difficulties.\n";
                str += "               Turning off constraint propagation, restoring valid bounds and proceeding...\n";
                _logger->print_message(str, VERB_NORMAL, BAB_VERBOSITY);
                _maingoSettings->BAB_constraintPropagation = false;
                _rootConPropStatus                         = TIGHTENING_UNCHANGED;
#ifdef HAVE_MAiNGO_MPI
                BCAST_TAG tag = BCAST_CONSTR_PROP_INFEASIBLE;
                MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
#endif
            // GCOVR_EXCL_STOP
            }
            else {
                _logger->print_message("      Found problem to be infeasible.\n", VERB_NORMAL, BAB_VERBOSITY);
#ifdef HAVE_MAiNGO_MPI
                BCAST_TAG tag = BCAST_INFEASIBLE;
                MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
#endif
            }
        }
        else if (_rootConPropStatus == TIGHTENING_CHANGED) {
            _rootNode = tmpNode;
#ifdef HAVE_MAiNGO_MPI
            BCAST_TAG tag = BCAST_FEASIBLE;
            MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
#endif
        }
#ifdef HAVE_MAiNGO_MPI
        else {
            BCAST_TAG tag = BCAST_FEASIBLE;
            MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
        }
        MAiNGO_ELSE    // MAiNGO_IF_BAB_WORKER
            // Check what happened
            BCAST_TAG tag;
            MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
            if (tag == BCAST_CONSTR_PROP_INFEASIBLE) {
                _maingoSettings->BAB_constraintPropagation = false;
            }
            else if (tag == BCAST_INFEASIBLE) {
                _rootConPropStatus = TIGHTENING_INFEASIBLE;
            }
            // Note that workers don't need the possibly changed node, since they will get new nodes in the B&B algorithm or before multistart in root_feas_obbt
#endif
        MAiNGO_END_IF    //MAiNGO_IF_BAB_MANAGER
}


////////////////////////////////////////////////////////////////////////
// conducts multistart local search at the root node
void
MAiNGO::_root_multistart()
{

    MAiNGO_IF_BAB_MANAGER
        if (_maingoSettings->PRE_pureMultistart) {
            if (_maingoSettings->PRE_maxLocalSearches > 0) {
                std::ostringstream outstr;
                outstr << "    Multistart with " << _maingoSettings->PRE_maxLocalSearches << " initial points...\n";
                _logger->print_message(outstr.str(), VERB_NORMAL, BAB_VERBOSITY);
            }
            else {
                // users... :-/
                _logger->print_message("    Requested pure multistart with 0 local searches. Only checking user-specified initial point for feasibility ...\n", VERB_NORMAL, BAB_VERBOSITY);
            }
        }
        else if (_maingoSettings->PRE_maxLocalSearches > 0) {
            _logger->print_message("    Multistart local searches...\n", VERB_NORMAL, BAB_VERBOSITY);
        }
        else if (_initialPoint.size() == _nvar) {
            _logger->print_message("    Checking user-specified initial point...\n", VERB_NORMAL, BAB_VERBOSITY);
        }
    MAiNGO_END_IF
    _solutionPoint        = _initialPoint;
    _rootMultistartStatus = _myUBSPre->multistart(_rootNode, _solutionValue, _solutionPoint, _feasibleAtRoot, _objectivesAtRoot, _initialPointFeasible);

#ifdef HAVE_MAiNGO_MPI
    MAiNGO_IF_BAB_MANAGER
        if (_rootMultistartStatus == SUBSOLVER_INFEASIBLE) {
            BCAST_TAG tag = BCAST_INFEASIBLE;
            MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
        }
        else {
            BCAST_TAG tag = BCAST_FEASIBLE;
            MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
            MPI_Bcast(&_solutionValue, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
        }
        MAiNGO_ELSE
            // Process results
            BCAST_TAG tag;
            MPI_Bcast(&tag, 1, MPI_INT, 0, MPI_COMM_WORLD);
            if (tag == BCAST_INFEASIBLE) {
                _rootMultistartStatus = SUBSOLVER_INFEASIBLE;
            }
            else {
                _rootMultistartStatus = SUBSOLVER_FEASIBLE;
                MPI_Bcast(&_solutionValue, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
            }
        MAiNGO_END_IF
#endif

        MAiNGO_IF_BAB_MANAGER
            if (_rootMultistartStatus == SUBSOLVER_INFEASIBLE) {
                _solutionPoint.clear();
            }
            else {
                if (!_maingoSettings->PRE_pureMultistart) {
                    _myLBS->update_incumbent_LBP(_solutionPoint);
                }
            }

            // Check whether the incumbent fullfils relaxation only constraints
            if (_rootMultistartStatus == SUBSOLVER_FEASIBLE && (_nineqRelaxationOnly > 0 || _neqRelaxationOnly > 0)) {    // Note that constant functions have been checked in _constructDAG
                std::string str;
                std::string whitespaces = "      ";
                _check_feasibility_of_relaxation_only_constraints(_solutionPoint, str, whitespaces);
                _logger->print_message(str, VERB_NORMAL, BAB_VERBOSITY);
            }
        MAiNGO_END_IF
}


////////////////////////////////////////////////////////////////////////
// recognizes structure of the problem
void
MAiNGO::_recognize_structure()
{

    _problemStructure = LP;

    // Get dependency sets of all functions
    // Note that we don't care about relaxation only (in)equalities and output
    std::vector<std::map<int, int>> func_dep;
    func_dep.resize(1 + _nineq + _neq);
    for (unsigned int i = 0; i < 1 + _nineq + _neq; i++) {
        func_dep[i] = _DAGfunctions[i].dep().dep();
    }
    std::vector<mc::FFDep::TYPE> functionsStructure(1 + _nineq + _neq, mc::FFDep::L);

    // Check if it is a mixed-integer program
    bool integer = false;
    for (unsigned int i = 0; i < _nvar && !integer; i++) {
        if (_variables[i].get_variable_type() > babBase::enums::VT_CONTINUOUS) {
            integer = true;
        }
    }

    // Set problem structure
    for (unsigned int i = 0; i < 1 + _nineq + _neq; i++) {
        for (unsigned int j = 0; j < _nvar; j++) {
            auto ito = func_dep[i].find(j);
            if (ito != func_dep[i].end()) {
                mc::FFDep::TYPE variableDep = (mc::FFDep::TYPE)(ito->second);
                if (functionsStructure[i] < variableDep) {
                    functionsStructure[i] = variableDep;
                }
            }
        }

        PROBLEM_STRUCTURE temp;
        switch (functionsStructure[i]) {
            case mc::FFDep::L:
                temp = integer ? MIP : LP;
                break;
            case mc::FFDep::B:
            case mc::FFDep::Q:
                // Check for quadratic inequalities or equalities <- they have to be convex, otherwise we get a CPLEX error
                if (i > 0) {    // i>0 are (in)equalities
                    temp = integer ? MINLP : NLP;
                }
                else {
                    temp = integer ? MIQP : QP;
                }
                break;
            case mc::FFDep::P:
            case mc::FFDep::R:
            case mc::FFDep::N:
                temp = integer ? MINLP : NLP;
                break;
            case mc::FFDep::D:
                temp = integer ? MINLP : DNLP;
                break;
            default:    // GCOVR_EXCL_LINE
                throw MAiNGOException("Error recognizing structure: unknown dependency type " + std::to_string(functionsStructure[i])); //GCOVR_EXCL_LINE
        }
        _problemStructure = std::max(_problemStructure, temp);
    }

    switch (_problemStructure) {
        case LP:
            _logger->print_message("\n  The problem is an LP", VERB_ALL, BAB_VERBOSITY);
            break;
        case MIP:
            _logger->print_message("\n  The problem is an MIP", VERB_ALL, BAB_VERBOSITY);
            break;
        case QP:
            _logger->print_message("\n  The problem is a QP", VERB_ALL, BAB_VERBOSITY);
            break;
        case MIQP:
            _logger->print_message("\n  The problem is an MIQP", VERB_ALL, BAB_VERBOSITY);
            break;
        case NLP:
            _logger->print_message("\n  The problem is an NLP", VERB_ALL, BAB_VERBOSITY);
            break;
        case DNLP:
            _logger->print_message("\n  The problem is a DNLP", VERB_ALL, BAB_VERBOSITY);
            break;
        case MINLP:
            _logger->print_message("\n  The problem is an MINLP", VERB_ALL, BAB_VERBOSITY);
            break;
        default:    // GCOVR_EXCL_LINE
            throw MAiNGOException("Error recognizing structure: unknown problem structure " + std::to_string(_problemStructure)); //GCOVR_EXCL_LINE
    }
}


////////////////////////////////////////////////////////////////////////
// check if point satisfies relaxation only constraints and give a warning if not
bool
MAiNGO::_check_feasibility_of_relaxation_only_constraints(const std::vector<double>& solutionPoint, std::string& str, const std::string& whitespaces)
{

    bool isFeasible;
    std::vector<double> modelValues;
    std::tie(modelValues, isFeasible) = _evaluate_model_at_point(solutionPoint);
    std::vector<unsigned> infeasibleRelOnlyIneqs;
    std::vector<unsigned> infeasibleRelOnlyEqs;
    const unsigned startingIndex = 1 + _nineq + _nconstantIneq + _neq + _nconstantEq;
    if (!isFeasible) {
        // Since the UBS found a feasible point, the point can only be infeasible in the relaxation only constraints
        // Relaxation only inequalities
        for (unsigned i = 0; i < _nineqRelaxationOnly + _nconstantIneqRelOnly; i++) {
            if (modelValues[i + startingIndex] > _maingoSettings->deltaIneq) {
                infeasibleRelOnlyIneqs.push_back(i);
                isFeasible = false;
            }
        }
        // Relaxations only equalities
        for (unsigned int i = 0; i < _neqRelaxationOnly + _nconstantEqRelOnly; i++) {
            if (modelValues[i + startingIndex + _nineqRelaxationOnly + _nconstantIneqRelOnly] > _maingoSettings->deltaEq || modelValues[i + startingIndex + _nineqRelaxationOnly + _nconstantIneqRelOnly] < -_maingoSettings->deltaEq) {
                infeasibleRelOnlyEqs.push_back(i);
                isFeasible = false;
            }
        }
    }
    if (infeasibleRelOnlyIneqs.size() > 0 || infeasibleRelOnlyEqs.size() > 0) {
        std::ostringstream outstr;
        if (infeasibleRelOnlyIneqs.size() > 0) {
            if (infeasibleRelOnlyIneqs.size() == 1) {
                outstr << whitespaces << "Warning: Current best feasible point does not satisfy relaxation only inequality";
            }
            else {
                outstr << whitespaces << "Warning: Current best feasible point does not satisfy relaxation only inequalities";
            }
            // Write all violated relaxation only inequalities
            for (size_t i = 0; i < infeasibleRelOnlyIneqs.size(); i++) {
                outstr << "\n"
                       << whitespaces << "         number " << infeasibleRelOnlyIneqs[i] + 1
                       << " (violation = " << std::setprecision(16) << modelValues[infeasibleRelOnlyIneqs[i] + startingIndex]
                       << " > " << std::setprecision(9) << _maingoSettings->deltaIneq << " = deltaIneq)";
            }
            outstr << ".\n";
        }
        if (infeasibleRelOnlyEqs.size() > 0) {
            if (infeasibleRelOnlyEqs.size() == 1) {
                outstr << whitespaces << "Warning: Current best feasible point does not satisfy relaxation only equality";
            }
            else {
                outstr << whitespaces << "Warning: Current best feasible point does not satisfy relaxation only equalities";
            }
            // Write all violated relaxation only equalities
            for (size_t i = 0; i < infeasibleRelOnlyEqs.size(); i++) {
                outstr << "\n"
                       << whitespaces << "         number " << infeasibleRelOnlyEqs[i] + 1
                       << " (violation = " << std::setprecision(9) << modelValues[infeasibleRelOnlyEqs[i] + startingIndex + _nineqRelaxationOnly + _nconstantIneqRelOnly]
                       << " not in [-" << std::setprecision(9) << _maingoSettings->deltaEq << "," << std::setprecision(9) << _maingoSettings->deltaEq << "] = deltaEq)";
            }
            outstr << ".\n";
        }
        str += outstr.str();
    }
    return isFeasible;
}


/////////////////////////////////////////////////////////////////////////
// fills the constraints vectors (and output vectors)
void
MAiNGO::_classify_objective_and_constraints(std::vector<mc::FFVar>& tmpFunctions, const std::vector<mc::FFVar>& tmpDAGVars)
{

    // Assign the array of functions
    _constantConstraintsFeasible = true;
    _originalConstraints         = std::make_shared<std::vector<Constraint>>();
    _constantConstraints         = std::make_shared<std::vector<Constraint>>();
    _nonconstantConstraints      = std::make_shared<std::vector<Constraint>>();
    _constantOutputs             = std::make_shared<std::vector<Constraint>>();
    _nonconstantOutputs          = std::make_shared<std::vector<Constraint>>();
    unsigned indexNonconstant = 0, indexOriginal = 0, indexConstant = 0, indexType = 0, indexTypeNonconstant = 0, indexTypeConstant = 0;
    _nobj                 = 0;
    _nineq                = 0;
    _neq                  = 0;
    _nineqRelaxationOnly  = 0;
    _neqRelaxationOnly    = 0;
    _nineqSquash          = 0;
    _nconstantIneq        = 0;
    _nconstantEq          = 0;
    _nconstantIneqRelOnly = 0;
    _nconstantEqRelOnly   = 0;
    _nconstantIneqSquash  = 0;
    _ndata                = 0;
    // Objective(s)
    _ensure_valid_objective_function_using_dummy_variable(tmpDAGVars[0]);
    for (size_t i = 0; i < _modelOutput.objective.size(); i++) {
        tmpFunctions.push_back(_modelOutput.objective.value[i]);
        _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::OBJ, indexOriginal, indexType, indexNonconstant, indexTypeNonconstant, _modelOutput.objective.name[i]));
        _nonconstantConstraints->push_back(Constraint(CONSTRAINT_TYPE::OBJ, indexOriginal++, indexType++, indexNonconstant++, indexTypeNonconstant++, _modelOutput.objective.name[i]));
        _nobj++;
    }
    // Inequalities
    indexType            = 0;
    indexTypeNonconstant = 0;
    indexTypeConstant    = 0;
    for (unsigned int i = 0; i < _modelOutput.ineq.size(); i++) {
        if (!_modelOutput.ineq[i].dag()) {    // Check if DAG pointer is set, if not the constraint is a constant
            double val = _modelOutput.ineq[i].num().val();
            _nconstantIneq++;
            if (val > _maingoSettings->deltaIneq) {
                _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ, indexOriginal, indexType, indexConstant, indexTypeConstant,
                                                           /*isConstant*/ true, /*isFeasible*/ false, val, _modelOutput.ineq.name[i]));
                _constantConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ, indexOriginal++, indexType++, indexConstant++, indexTypeConstant++,
                                                           /*isConstant*/ true, /*isFeasible*/ false, val, _modelOutput.ineq.name[i]));
                _constantConstraintsFeasible = false;
            }
            else {
                _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ, indexOriginal, indexType, indexConstant, indexTypeConstant,
                                                           /*isConstant*/ true, /*isFeasible*/ true, val, _modelOutput.ineq.name[i]));
                _constantConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ, indexOriginal++, indexType++, indexConstant++, indexTypeConstant++,
                                                           /*isConstant*/ true, /*isFeasible*/ true, val, _modelOutput.ineq.name[i]));
            }
        }
        else {    // Function is non-constant
            _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ, indexOriginal, indexType, indexNonconstant,
                                                       indexTypeNonconstant, _modelOutput.ineq.name[i]));
            _nonconstantConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ, indexOriginal++, indexType++, indexNonconstant++,
                                                          indexTypeNonconstant++, _modelOutput.ineq.name[i]));
            tmpFunctions.push_back(_modelOutput.ineq[i]);
            _nineq++;
        }
    }
    // Equalities
    indexType            = 0;
    indexTypeNonconstant = 0;
    indexTypeConstant    = 0;
    for (unsigned int i = 0; i < _modelOutput.eq.size(); i++) {
        if (!_modelOutput.eq[i].dag()) {    // Check if DAG pointer is set, if not the constraint is a constant
            double val = _modelOutput.eq[i].num().val();
            _nconstantEq++;
            if (std::fabs(val) > _maingoSettings->deltaEq) {
                _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::EQ, indexOriginal, indexType, indexConstant, indexTypeConstant,
                                                           /*isConstant*/ true, /*isFeasible*/ false, val, _modelOutput.eq.name[i]));
                _constantConstraints->push_back(Constraint(CONSTRAINT_TYPE::EQ, indexOriginal++, indexType++, indexConstant++, indexTypeConstant++,
                                                           /*isConstant*/ true, /*isFeasible*/ false, val, _modelOutput.eq.name[i]));
                _constantConstraintsFeasible = false;
            }
            else {
                _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::EQ, indexOriginal, indexType, indexConstant, indexTypeConstant,
                                                           /*isConstant*/ true, /*isFeasible*/ true, val, _modelOutput.eq.name[i]));
                _constantConstraints->push_back(Constraint(CONSTRAINT_TYPE::EQ, indexOriginal++, indexType++, indexConstant++, indexTypeConstant++,
                                                           /*isConstant*/ true, /*isFeasible*/ true, val, _modelOutput.eq.name[i]));
            }
        }
        else {
            _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::EQ, indexOriginal, indexType, indexNonconstant,
                                                       indexTypeNonconstant, _modelOutput.eq.name[i]));
            _nonconstantConstraints->push_back(Constraint(CONSTRAINT_TYPE::EQ, indexOriginal++, indexType++, indexNonconstant++,
                                                          indexTypeNonconstant++, _modelOutput.eq.name[i]));
            tmpFunctions.push_back(_modelOutput.eq[i]);
            _neq++;
        }
    }
    // Relaxation-only inequalities
    indexType            = 0;
    indexTypeNonconstant = 0;
    indexTypeConstant    = 0;
    for (unsigned int i = 0; i < _modelOutput.ineqRelaxationOnly.size(); i++) {
        if (!_modelOutput.ineqRelaxationOnly[i].dag()) {    // Check if DAG pointer is set, if not the constraint is a constant
            double val = _modelOutput.ineqRelaxationOnly[i].num().val();
            _nconstantIneqRelOnly++;
            if (val > _maingoSettings->deltaIneq) {
                _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ_REL_ONLY, indexOriginal, indexType, indexConstant, indexTypeConstant,
                                                           /*isConstant*/ true, /*isFeasible*/ false, val, _modelOutput.ineqRelaxationOnly.name[i]));
                _constantConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ_REL_ONLY, indexOriginal++, indexType++, indexConstant++, indexTypeConstant++,
                                                           /*isConstant*/ true, /*isFeasible*/ false, val, _modelOutput.ineqRelaxationOnly.name[i]));
                _constantConstraintsFeasible = false;
            }
            else {
                _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ_REL_ONLY, indexOriginal, indexType, indexConstant, indexTypeConstant,
                                                           /*isConstant*/ true, /*isFeasible*/ true, val, _modelOutput.ineqRelaxationOnly.name[i]));
                _constantConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ_REL_ONLY, indexOriginal++, indexType++, indexConstant++, indexTypeConstant++,
                                                           /*isConstant*/ true, /*isFeasible*/ true, val, _modelOutput.ineqRelaxationOnly.name[i]));
            }
        }
        else {
            _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ_REL_ONLY, indexOriginal, indexType,
                                                       indexNonconstant, indexTypeNonconstant, _modelOutput.ineqRelaxationOnly.name[i]));
            _nonconstantConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ_REL_ONLY, indexOriginal++, indexType++,
                                                          indexNonconstant++, indexTypeNonconstant++, _modelOutput.ineqRelaxationOnly.name[i]));
            tmpFunctions.push_back(_modelOutput.ineqRelaxationOnly[i]);
            _nineqRelaxationOnly++;
        }
    }
    // Relaxation-only equalities
    indexType            = 0;
    indexTypeNonconstant = 0;
    indexTypeConstant    = 0;
    for (unsigned int i = 0; i < _modelOutput.eqRelaxationOnly.size(); i++) {
        if (!_modelOutput.eqRelaxationOnly[i].dag()) {    // Check if DAG pointer is set, if not the constraint is a constant
            double val = _modelOutput.eqRelaxationOnly[i].num().val();
            _nconstantEqRelOnly++;
            if (std::fabs(val) > _maingoSettings->deltaEq) {
                _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::EQ_REL_ONLY, indexOriginal, indexType, indexConstant, indexTypeConstant,
                                                           /*isConstant*/ true, /*isFeasible*/ false, val, _modelOutput.eqRelaxationOnly.name[i]));
                _constantConstraints->push_back(Constraint(CONSTRAINT_TYPE::EQ_REL_ONLY, indexOriginal++, indexType++, indexConstant++, indexTypeConstant++,
                                                           /*isConstant*/ true, /*isFeasible*/ false, val, _modelOutput.eqRelaxationOnly.name[i]));
                _constantConstraintsFeasible = false;
            }
            else {
                _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::EQ_REL_ONLY, indexOriginal, indexType, indexConstant, indexTypeConstant,
                                                           /*isConstant*/ true, /*isFeasible*/ true, val, _modelOutput.eqRelaxationOnly.name[i]));
                _constantConstraints->push_back(Constraint(CONSTRAINT_TYPE::EQ_REL_ONLY, indexOriginal++, indexType++, indexConstant++, indexTypeConstant++,
                                                           /*isConstant*/ true, /*isFeasible*/ true, val, _modelOutput.eqRelaxationOnly.name[i]));
            }
        }
        else {
            _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::EQ_REL_ONLY, indexOriginal, indexType,
                                                       indexNonconstant, indexTypeNonconstant, _modelOutput.eqRelaxationOnly.name[i]));
            _nonconstantConstraints->push_back(Constraint(CONSTRAINT_TYPE::EQ_REL_ONLY, indexOriginal++, indexType++,
                                                          indexNonconstant++, indexTypeNonconstant++, _modelOutput.eqRelaxationOnly.name[i]));
            tmpFunctions.push_back(_modelOutput.eqRelaxationOnly[i]);
            _neqRelaxationOnly++;
        }
    }
    // Squash inequalities
    indexType            = 0;
    indexTypeNonconstant = 0;
    indexTypeConstant    = 0;
    for (unsigned int i = 0; i < _modelOutput.ineqSquash.size(); i++) {
        if (!_modelOutput.ineqSquash[i].dag()) {    // Check if DAG pointer is set, if not the constraint is a constant
            double val = _modelOutput.ineqSquash[i].num().val();
            _nconstantIneqSquash++;
            if (val > 0) {    // No tolerances are allowed for squash inequalities!
                _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ_SQUASH, indexOriginal, indexType, indexConstant, indexTypeConstant,
                                                           /*isConstant*/ true, /*isFeasible*/ false, val, _modelOutput.ineqSquash.name[i]));
                _constantConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ_SQUASH, indexOriginal++, indexType++, indexConstant++, indexTypeConstant++,
                                                           /*isConstant*/ true, /*isFeasible*/ false, val, _modelOutput.ineqSquash.name[i]));
                _constantConstraintsFeasible = false;
            }
            else {
                _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ_SQUASH, indexOriginal, indexType, indexConstant, indexTypeConstant,
                                                           /*isConstant*/ true, /*isFeasible*/ true, val, _modelOutput.ineqSquash.name[i]));
                _constantConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ_SQUASH, indexOriginal++, indexType++, indexConstant++, indexTypeConstant++,
                                                           /*isConstant*/ true, /*isFeasible*/ true, val, _modelOutput.ineqSquash.name[i]));
            }
        }
        else {
            _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ_SQUASH, indexOriginal, indexType,
                                                       indexNonconstant, indexTypeNonconstant, _modelOutput.ineqSquash.name[i]));
            _nonconstantConstraints->push_back(Constraint(CONSTRAINT_TYPE::INEQ_SQUASH, indexOriginal++, indexType++,
                                                          indexNonconstant++, indexTypeNonconstant++, _modelOutput.ineqSquash.name[i]));
            tmpFunctions.push_back(_modelOutput.ineqSquash[i]);
            _nineqSquash++;
        }
    }
#ifdef HAVE_GROWING_DATASETS
    // Objective per data
    _ndata               = _modelOutput.objective_per_data.size();
    indexType            = 0;
    indexTypeNonconstant = 0;
    _ensure_valid_objective_per_data_function_using_dummy_variable(tmpDAGVars[0]);
    if (_maingoSettings->growing_shuffleData) {    // Pick datasets randomly
        // Generating a random sequence of indices with Mersenne Twister algorithm with fixed seed
        std::vector<unsigned int> indices;
        indices.resize(_ndata);
        for (auto i = 0; i < _ndata; i++) {
            indices[i] = i;
        }
        std::mt19937 randomNumberGenerator(55);
        std::shuffle(indices.begin(), indices.end(), randomNumberGenerator);

        // Shuffle data points when copying from _modelOutput into tmpFunctions
        for (auto idx : indices) {
            tmpFunctions.push_back(_modelOutput.objective_per_data[idx]);
        }
    }
    else {     // Keep order of objective_per_data for picking sorted data points sequentially
        for (size_t idx = 0; idx < _ndata; idx++) {
            tmpFunctions.push_back(_modelOutput.objective_per_data[idx]);
        }
    }
#endif

    // Output variables
    indexType                 = 0;
    indexOriginal             = 0;
    indexConstant             = 0;
    indexNonconstant          = 0;
    indexTypeNonconstant      = 0;
    indexTypeConstant         = 0;
    _noutputVariables         = 0;
    _nconstantOutputVariables = 0;
    for (unsigned int i = 0; i < _modelOutput.output.size(); i++) {
        if (!_modelOutput.output[i].value.dag()) {    // Check if DAG pointer is set, if not the output is a constant
            double val = _modelOutput.output[i].value.num().val();
            _constantOutputs->push_back(Constraint(CONSTRAINT_TYPE::OUTPUT, indexOriginal++, indexType++, indexConstant++, indexTypeConstant++,
                                                   /*isConstant*/ true, /*isFeasible*/ true, val, _modelOutput.output[i].description));
            _nconstantOutputVariables++;
        }
        else {
            _nonconstantOutputs->push_back(Constraint(CONSTRAINT_TYPE::OUTPUT, indexOriginal++, indexType++, indexNonconstant++,
                                                      indexTypeNonconstant++, _modelOutput.output[i].description));
            tmpFunctions.push_back(_modelOutput.output[i].value);
            _noutputVariables++;
        }
    }
}


/////////////////////////////////////////////////////////////////////////
// Ensures that the objective function stored in the _modelOutput is valid
void
MAiNGO::_ensure_valid_objective_function_using_dummy_variable(const mc::FFVar& dummyVariable)
{
    if (_modelOutput.objective.size() == 0) {
        // If no objective has been specified, simply add some dummy
        _modelOutput.objective.push_back(dummyVariable + 1.0 + 0 - dummyVariable - 1.0);
        _feasibilityProblem                       = true;
        _maingoSettings->terminateOnFeasiblePoint = true;
        _logger->print_message("\n  Warning: No objective function has been specified. Assuming this is a feasibility problem.\n           During solution, a constant dummy objective with value 0 will be used.",
                               VERB_NORMAL, BAB_VERBOSITY);
    }
    else {
        for (size_t i = 0; i < _modelOutput.objective.size(); i++) {
            if (!_modelOutput.objective[i].dag()) {    // Check if DAG pointer is set, if not the objective is a constant
                // This is basically saying objective = x1 + 1 + constant - x1 - 1 = constant.
                // We are doing this since 0*x1 or x1 - x1 will be recognized by the DAG (this may change in future).
                // Adding and substracting the 1.0 avoids errors in the case of non-defined objective.
                // An alternative would be to define a flag telling whether the objective is constant and propagate it to the LBD and UBD solvers.
                _logger->print_message("\n  Warning: Objective function is a constant with value " + std::to_string(_modelOutput.objective[i].num().val()) + ".",
                                       VERB_NORMAL, BAB_VERBOSITY);
                _modelOutput.objective.set_value(dummyVariable + 1.0 + _modelOutput.objective[i].num().val() - dummyVariable - 1.0, i);
            }
        }
    }
}


#ifdef HAVE_GROWING_DATASETS
/////////////////////////////////////////////////////////////////////////
// Ensures that constant objective_per_data is not removed
void
MAiNGO::_ensure_valid_objective_per_data_function_using_dummy_variable(const mc::FFVar& dummyVariable)
{
    for (size_t i = 0; i < _modelOutput.objective_per_data.size(); i++) {
        if (!_modelOutput.objective_per_data[i].dag()) {    // Check if DAG pointer is set, if not the objective is a constant
            // This is basically saying objective = x1 + 1 + constant - x1 - 1 = constant.
            // We are doing this since 0*x1 or x1 - x1 will be recognized by the DAG (this may change in future).
            // Adding and substracting the 1.0 avoids errors in the case of non-defined objective.
            // An alternative would be to define a flag telling whether the objective is constant and propagate it to the LBD and UBD solvers.
            _logger->print_message("\n  Warning: Objective_per_data [" + std::to_string(i) + "] is a constant with value " + std::to_string(_modelOutput.objective[i].num().val()) + ".",
                                   VERB_NORMAL, BAB_VERBOSITY);
            _modelOutput.objective_per_data.set_value(dummyVariable + 1.0 + _modelOutput.objective_per_data[i].num().val() - dummyVariable - 1.0, i);
        }
    }
}
#endif


/////////////////////////////////////////////////////////////////////////
// checks whether some constraints (or output) is not indeed 0 and also fills the _DAGoutputFunctions vector
bool
MAiNGO::_check_for_hidden_zero_constraints(const std::vector<mc::FFVar>& tmpDAGVars, std::vector<mc::FFVar>& tmpDAGFunctions, std::vector<mc::FFVar>& tmpDAGoutputFunctions)
{

    bool foundHiddenZero = false;
    // We will check again if the resulting functions are constant, since it is possible to construct a "hidden" 0 function which is recognized first after tmpDAG.eval(...)
    bool updateIndices = false;
    for (int i = _resultVars.size() - _noutputVariables - 1; i >= 0; i--) {
        if (!_resultVars[i].dag()) {
            foundHiddenZero = true;
            switch ((*_nonconstantConstraints)[i].type) {
                case OBJ:
                    _resultVars[i] = tmpDAGVars[0] + 1.0 + _modelOutput.objective[i].num().val() - tmpDAGVars[0] - 1.0;
                    tmpDAGFunctions.push_back(_resultVars[i]);    // Get functions
                    continue;
                case INEQ:
                    _nineq--;
                    _nconstantIneq++;
                    break;
                case EQ:
                    _neq--;
                    _nconstantEq++;
                    break;
                case INEQ_REL_ONLY:
                    _nineqRelaxationOnly--;
                    _nconstantIneqRelOnly++;
                    break;
                case EQ_REL_ONLY:
                    _neqRelaxationOnly--;
                    _nconstantEqRelOnly++;
                    break;
                case INEQ_SQUASH:
                    _nineqSquash--;
                    _nconstantIneqSquash++;
                    break;
                default:    // GCOVR_EXCL_LINE
                    throw MAiNGOException("Error recognizing hidden zeros in problem: Unknown constraint type " + std::to_string((*_nonconstantConstraints)[i].type));    // GCOVR_EXCL_LINE

            }    // End of switch
            // Erase the constraint from nonconstant constraints and insert it into the constant constraints vector
            updateIndices  = true;
            Constraint tmp = (*_nonconstantConstraints)[i];
            _nonconstantConstraints->erase(_nonconstantConstraints->begin() + i);
            tmp.isFeasible                             = true;
            tmp.isConstant                             = true;
            tmp.constantValue                          = 0;
            tmp.indexNonconstant                       = 0;
            tmp.indexTypeNonconstant                   = 0;
            (*_originalConstraints)[tmp.indexOriginal] = tmp;
            // Insert the constraint to the constantConstraints vector at the right place
            if (_constantConstraints->empty()) {
                _constantConstraints->push_back(tmp);
            }
            else {
                for (size_t i = 0; i < _constantConstraints->size(); i++) {
                    if ((*_constantConstraints)[i].indexOriginal < tmp.indexOriginal) {
                        if (i == _constantConstraints->size() - 1) {
                            _constantConstraints->insert(_constantConstraints->end(), tmp);
                            break;
                        }
                        continue;
                    }
                    else {
                        _constantConstraints->insert(_constantConstraints->begin() + i, tmp);
                        break;
                    }
                }
            }
        }
        else {
            tmpDAGFunctions.push_back(_resultVars[i]);    // Get functions
        }
    }                                                                // End of for loop over _resultVars - _noutputVariables
    std::reverse(tmpDAGFunctions.begin(), tmpDAGFunctions.end());    // Reverse the ordering to be equal to initial user input

    // Update nonconstant and constant index of constraints
    if (updateIndices) {
        unsigned indexObj = 0, indexIneq = 0, indexEq = 0, indexIneqRelOnly = 0, indexEqRelOnly = 0, indexIneqSquash = 0;
        for (size_t i = 0; i < _nonconstantConstraints->size(); i++) {
            Constraint & nonconstCon = (*_nonconstantConstraints)[i];
            Constraint & origCon     = (*_originalConstraints)[nonconstCon.indexOriginal];

            nonconstCon.indexNonconstant = i;
            origCon.indexNonconstant     = i;
            switch (nonconstCon.type) {
                case OBJ:
                    nonconstCon.indexTypeNonconstant = indexObj;
                    origCon.indexTypeNonconstant     = indexObj++;
                    break;
                case INEQ:
                    nonconstCon.indexTypeNonconstant = indexIneq;
                    origCon.indexTypeNonconstant     = indexIneq++;
                    break;
                case EQ:
                    nonconstCon.indexTypeNonconstant = indexEq;
                    origCon.indexTypeNonconstant     = indexEq++;
                    break;
                case INEQ_REL_ONLY:
                    nonconstCon.indexTypeNonconstant = indexIneqRelOnly;
                    origCon.indexTypeNonconstant     = indexIneqRelOnly++;
                    break;
                case EQ_REL_ONLY:
                    nonconstCon.indexTypeNonconstant = indexEqRelOnly;
                    origCon.indexTypeNonconstant     = indexEqRelOnly++;
                    break;
                case INEQ_SQUASH:
                    nonconstCon.indexTypeNonconstant = indexIneqSquash;
                    origCon.indexTypeNonconstant     = indexIneqSquash++;
                    break;
                default:    // GCOVR_EXCL_LINE
                    throw MAiNGOException("Error recognizing hidden zeros in problem: Unknown constraint type " + std::to_string((*_nonconstantConstraints)[i].type));    // GCOVR_EXCL_LIN
            }
        }
        indexObj         = 0;
        indexIneq        = 0;
        indexEq          = 0;
        indexIneqRelOnly = 0;
        indexEqRelOnly   = 0;
        indexIneqSquash  = 0;
        for (size_t i = 0; i < _constantConstraints->size(); i++) {
            Constraint & constCon = (*_constantConstraints)[i];
            Constraint & origCon  = (*_originalConstraints)[constCon.indexOriginal];

            constCon.indexConstant = i;
            origCon.indexConstant  = i;
            switch (constCon.type) {
                case OBJ:
                    constCon.indexTypeConstant = indexObj;
                    origCon.indexTypeConstant  = indexObj++;
                    break;
                case INEQ:
                    constCon.indexTypeConstant = indexIneq;
                    origCon.indexTypeConstant  = indexIneq++;
                    break;
                case EQ:
                    constCon.indexTypeConstant = indexEq;
                    origCon.indexTypeConstant  = indexEq++;
                    break;
                case INEQ_REL_ONLY:
                    constCon.indexTypeConstant = indexIneqRelOnly;
                    origCon.indexTypeConstant  = indexIneqRelOnly++;
                    break;
                case EQ_REL_ONLY:
                    constCon.indexTypeConstant = indexEqRelOnly;
                    origCon.indexTypeConstant  = indexEqRelOnly++;
                    break;
                case INEQ_SQUASH:
                    constCon.indexTypeConstant = indexIneqSquash;
                    origCon.indexTypeConstant  = indexIneqSquash++;
                    break;
                default:    // GCOVR_EXCL_LINE
                    throw MAiNGOException("Error recognizing hidden zeros in problem: Unknown constraint type " + std::to_string((*_nonconstantConstraints)[i].type));    // GCOVR_EXCL_LINE
            }
        }
    }

    // Check if resulting output functions are constant
    updateIndices               = false;
    unsigned newConstantOutputs = 0;
    int maxIndex                = _resultVars.size() - (_noutputVariables);
    for (int i = _resultVars.size() - 1; i >= maxIndex; i--) {
        if (!_resultVars[i].dag()) {
            foundHiddenZero = true;
            _noutputVariables--;
            _nconstantOutputVariables++;
            newConstantOutputs++;
            updateIndices  = true;
            Constraint tmp = (*_nonconstantOutputs)[_noutputVariables + newConstantOutputs - _resultVars.size() + i];
            _nonconstantOutputs->erase(_nonconstantOutputs->begin() + (_noutputVariables - _resultVars.size() + i + newConstantOutputs));
            tmp.isFeasible       = true;
            tmp.isConstant       = true;
            tmp.constantValue    = 0;
            tmp.indexNonconstant = 0;
            // Insert the constraint to the constantOutputs vector at the right place
            if (_constantOutputs->empty()) {
                _constantOutputs->push_back(tmp);
            }
            else {
                for (size_t j = 0; j < _constantOutputs->size(); j++) {
                    if ((*_constantOutputs)[j].indexOriginal < tmp.indexOriginal) {
                        if (j == _constantOutputs->size() - 1) {
                            _constantOutputs->insert(_constantOutputs->end(), tmp);
                            break;
                        }
                        continue;
                    }
                    else {
                        _constantOutputs->insert(_constantOutputs->begin() + j, tmp);
                        break;
                    }
                }
            }
        }
        else {
            tmpDAGoutputFunctions.push_back(_resultVars[i]);    // Get pointers to functions
        }
    }
    std::reverse(tmpDAGoutputFunctions.begin(), tmpDAGoutputFunctions.end());    // Reverse the ordering to be equal to initial user input
                                                                                 // Update nonconstant and constant index of outputs
    if (updateIndices) {
        for (size_t i = 0; i < _nonconstantOutputs->size(); i++) {
            (*_nonconstantOutputs)[i].indexNonconstant = i;
        }
        for (size_t i = 0; i < _constantOutputs->size(); i++) {
            (*_constantOutputs)[i].indexConstant = i;
        }
    }

    return foundHiddenZero;
}


#ifdef HAVE_GROWING_DATASETS
/////////////////////////////////////////////////////////////////////////
// initializes objective via the user-defined objective_per_data when using the B&B algorithm with growing datasets
void
MAiNGO::_initialize_objective_from_objective_per_data()
{
    if (_modelOutput.objective_per_data.size() == 0) {
        throw MAiNGOException("  Error initializing MAiNGO: MAiNGO with growing datasets requires setting objective per data.");
    }
    else {    // Objective per data is defined: print warning (in manager process)
        MAiNGO_IF_BAB_MANAGER
            if (_modelOutput.objective.size() > 0) {
                _logger->print_message("\n  Warning: Objective is overwritten based on objective_per_data. \n", VERB_NORMAL, BAB_VERBOSITY);
            }
        MAiNGO_END_IF    // End of MAiNGO_IF_BAB_MANAGER
        _modelOutput.objective.clear();

        //objective considering complete dataset for setting up complete DAG
        mc::FFVar obj = 0;
        for (auto i = 0; i < _modelOutput.objective_per_data.size(); i++) {
            obj += _modelOutput.objective_per_data[i];
        }
        if (_maingoSettings->growing_approach == GROW_APPR_MSEHEURISTIC) {// Use mean of summed objective per data as objective
            _modelOutput.objective = obj / _modelOutput.objective_per_data.size();
        }
        else {// Use sum of objective per data as objective
            _modelOutput.objective = obj;
        }
    }
}


////////////////////////////////////////////////////////////////////////
// randomly samples reduced dataset with given size
void
MAiNGO::_sample_initial_dataset(const int ndataInit, std::set<unsigned int> &dataset)
{
    // Generating uniformly distributed random indices with Mersenne Twister algorithm with fixed seed
    std::mt19937 randomNumberGenerator(5);
    std::uniform_int_distribution<> uniformIndex(0,_ndata-1);

    std::pair<std::set<unsigned int>::iterator, bool> ans;
    int count = 0;

    while (count < ndataInit) {
        // Choose from full dataset
        auto idxRand = uniformIndex(randomNumberGenerator);
        ans = dataset.insert(idxRand);
        if (ans.second == true) {
            count++;
        }
    }
}


////////////////////////////////////////////////////////////////////////
// initializes full dataset (= largest set, index 0) and initial reduced dataset (= smallest set, index 1)
// if applicable, initializes also resampled initial dataset
void
MAiNGO::_initialize_dataset()
{
    _datasets = std::make_shared<std::vector<unsigned int>>();

    // First entry: full dataset
    _datasets->push_back(_ndata);

    // Reduced datasets
    if (_ndata > 1) {    // Only if data reduction is possible
        if (_maingoSettings->growing_relativeSizing) {    // Relative sizing
            // Initial dataset
            int ndataNew = std::round((double)_maingoSettings->growing_initPercentage * (double)_ndata);
            ndataNew = std::max(1, ndataNew);
            _datasets->push_back(ndataNew);

            // Augmented datasets
            int ndataAugment = std::round((double)_maingoSettings->growing_augmentPercentage * (double)_ndata);
            ndataAugment = std::max(1, ndataAugment);

            ndataNew += ndataAugment;
            while (ndataNew <= _maingoSettings->growing_maxSize * _ndata) {
                _datasets->push_back(ndataNew); // Augmented dataset
                ndataNew += ndataAugment;       // Next candidate set
            }
        }
        else {    // Absolute sizing
            read_sizing_of_datasets_from_file();
        }

        // Resampled initial dataset
        if (_maingoSettings->growing_useResampling) {
            std::set<unsigned int> tmpReducedSet;
            _sample_initial_dataset((*_datasets)[1], tmpReducedSet);
            _datasetResampled = std::make_shared<std::set<unsigned int>>(tmpReducedSet);
        }
    }
}


////////////////////////////////////////////////////////////////////////
// reads user-given sizes of reduced datasets from file
void
MAiNGO::read_sizing_of_datasets_from_file()
{
    std::string outstr;
    std::vector<double> inputData;
    bool successful = read_vector_from_file("growingDatasetsSizing.txt", false, inputData);

    if (successful) {
        int ndataNew = 0;
        for (auto ndataAugment : inputData) {
            // Calculate size of next dataset
            if ((ndataAugment > 0) && (ndataAugment == (int)ndataAugment)) {
                ndataNew += ndataAugment;
            }
            else {    // User has chosen absolute sizing but provided unexpected data
                successful = false;
                break;
            }
            // Add new dataset
            if (ndataNew <= _maingoSettings->growing_maxSize * _ndata) {
                _datasets->push_back(ndataNew);
            }
            else {
                // Already reached maximum possible reduced dataset
                break;
            }
        }
    }
    else {
            // Could not read file
            // Actually, this should already be caught for this particular file when reading MAiNGOSettings
            successful = false;
    }

    if (!successful) {
        throw MAiNGOException("  Error initializing datasets: File growingDatasetsSizing.txt does not contain valid numbers.");
    }
}
#endif    //HAVE_GROWING_DATASETS

/////////////////////////////////////////////////////////////////////////
// modifies the lower bound DAG _DAGlbd by adding auxiliary optimization variables for intermediate factors occuring multiple times
void
MAiNGO::_add_auxiliary_variables_to_lbd_dag()
{

    // First, we evaluate the model at mid point
    // This is done to get interval bounds for auxiliary factors and compute a score
    std::vector<MC> independentVariablesMC(_DAGvarsLbd.size());    // Vector holding the bounds of optimization variables as intervals
    std::vector<double> lowerVarBounds(_nvar);
    std::vector<double> upperVarBounds(_nvar);
    std::vector<double> referencePoint(_nvar);    // This is the point at which we evaluate the relaxations to assess how far away they are from the functions
    for (unsigned int i = 0; i < _nvar; i++) {
        lowerVarBounds[i]         = _variables[i].get_lower_bound();
        upperVarBounds[i]         = _variables[i].get_upper_bound();
        referencePoint[i]         = 0.5 * (lowerVarBounds[i] + upperVarBounds[i]);
        independentVariablesMC[i] = MC(I(lowerVarBounds[i], upperVarBounds[i]), referencePoint[i]);
        independentVariablesMC[i].sub(_nvar, i);    // Set subgradient dimension
    }

    // Set options for the McCormick relaxations and the subgradient heuristic (these may be reset later in the lower bounding solver)
    if (_maingoSettings->LBP_subgradientIntervals) {
        MC::options.SUB_INT_HEUR_USE = true;
    }
    else {
        MC::options.SUB_INT_HEUR_USE = false;
    }
    MC::subHeur.clear();
    MC::options.ENVEL_USE           = true;
    MC::options.ENVEL_MAXIT         = 100;
    MC::options.ENVEL_TOL           = _maingoSettings->MC_envelTol;
    MC::options.MVCOMP_USE          = _maingoSettings->MC_mvcompUse;
    MC::options.MVCOMP_TOL          = _maingoSettings->MC_mvcompTol;
    MC::subHeur.originalLowerBounds = &lowerVarBounds;
    MC::subHeur.originalUpperBounds = &upperVarBounds;
    MC::subHeur.referencePoint      = &referencePoint;

    // Get the subgraph of those things that actually occur in objective and constraints
    mc::FFSubgraph MCSubgraph = _DAGlbd.subgraph(_DAGfunctionsLbd.size(), _DAGfunctionsLbd.data());

    // Evaluate in McCormick arithmetic
    std::vector<MC> objectiveAndConstraintsMC(_DAGfunctionsLbd.size());    // Dummy vector holding the McCormick objects of all functions in the model
    std::vector<MC> operationResultsMC;                                    // Vector holding the range intervals for each operation in the DAG
    _DAGlbd.eval(MCSubgraph, operationResultsMC, _DAGfunctionsLbd.size(), _DAGfunctionsLbd.data(), objectiveAndConstraintsMC.data(), _DAGvarsLbd.size(), _DAGvarsLbd.data(), independentVariablesMC.data());

    // Evaluate in double arithmetic
    std::vector<double> operationResultsDouble;
    std::vector<double> objectiveAndConstraintsDouble(_DAGfunctionsLbd.size());
    _DAGlbd.eval(MCSubgraph, operationResultsDouble, _DAGfunctionsLbd.size(), _DAGfunctionsLbd.data(), objectiveAndConstraintsDouble.data(), _DAGvarsLbd.size(), _DAGvarsLbd.data(), referencePoint.data());


    // Based on the results, determine which dependent variables are candidates for being converted to auxiliary variables
    // To qualify, a variables has to
    //  - be dependent and non-constant
    //  - occur in at least LBP_minFactorsForAux other operations
    //  - depend nonlinearly on some variables
    //  - depend on at least 2 independent variables
    //  - contribute to the computation of the objective or at least one constraint residual
    // If a variable qualifies, it is added to the list of candidates.
    // The selection from this list is based on the factorRanking which considers (in order of importance)
    //   1. the number of operations the variable
    //   2. the sum of absolute differences between the function and the convex and concave relaxation at the reference point
    mc::FFGraph::t_Vars ffVars = _DAGlbd.Vars();    // Set of all FFVars in the DAG
    mc::FFGraph::it_Vars itv   = ffVars.begin();
    std::multimap<std::pair<unsigned, double>, std::pair<mc::FFVar*, mc::FFDep::TYPE>> factorRanking;
    for (; itv != ffVars.end(); ++itv) {

        // We are interested in non-constant dependent FFVars only
        if ((*itv)->id().first != mc::FFVar::VAR && (*itv)->id().first != mc::FFVar::CINT && (*itv)->id().first != mc::FFVar::CREAL) {
            const typename mc::FFVar::t_Ops operationsUsedIn = (*itv)->ops().second;    // This is a list of all operations where this FFVar is used
            const mc::FFOp* pOperation                       = (*itv)->ops().first;     // This is the operation of this FFVar

            if (operationsUsedIn.size() >= _maingoSettings->LBP_minFactorsForAux) {

                // Determine how the dependent variable depends on the independent ones
                const std::map<int, int> dependenceOnIndependentVars = (*itv)->dep().dep();
                mc::FFDep::TYPE functionStructure                    = mc::FFDep::L;
                std::vector<size_t> participatingVars;
                for (size_t j = 0; j < _nvar; j++) {
                    auto ito2 = dependenceOnIndependentVars.find(j);
                    // Count all participating variables
                    if (ito2 != dependenceOnIndependentVars.end()) {
                        participatingVars.push_back(j);
                        mc::FFDep::TYPE variableDep = (mc::FFDep::TYPE)(ito2->second);
                        // Update function type
                        if (functionStructure < variableDep) {
                            functionStructure = variableDep;
                        }
                    }
                }
                // Only add this auxiliary if it is at least bilinear and has at least 2 original variables
                if (functionStructure > mc::FFDep::L && participatingVars.size() >= 2) {
                    // Find the correct McCormick object for the replaced FFVar by searching the corresponding operation in MCSubgraph
                    size_t index                             = 0;
                    std::list<const mc::FFOp*>::iterator itL = MCSubgraph.l_op.begin();
                    for (; itL != MCSubgraph.l_op.end(); ++itL) {
                        if ((*itL) != pOperation) {
                            index++;
                        }
                        else {
                            break;
                        }
                    }
                    // Only add variable if it was found in MCSubgraph.l_op. Otherwise, it is not actually used in any function (i.e., objective or constraints)
                    if (itL != MCSubgraph.l_op.end()) {
                        const double averageRelaxationOffset = std::fabs(operationResultsMC[index].cv() - operationResultsDouble[index]) + std::fabs(operationResultsMC[index].cc() - operationResultsDouble[index]);
                        factorRanking.insert(std::make_pair(std::make_pair(operationsUsedIn.size(), averageRelaxationOffset), std::make_pair((*itv), functionStructure)));
                    }
                }
            }
        }
    }

    // Go through factor ranking to select the most promising candidates
    std::vector<MC> auxVariablesMCBounds;                                                                                                        // Vector holding McCormick objects to derive the bounds for auxiliary variables which will be added
    unsigned indexOriginal                                                                                   = _DAGfunctions.size() - _ndata;    // objective_per_data are not considered as constraints (without growing datasets: _ndata == 0 by initialization and never changed)
    unsigned indexType                                                                                       = 0;
    unsigned indexTypeNonconstant                                                                            = _neqRelaxationOnly;    // Auxiliary relaxation only constraints are handled as normal eq rel only constraints
    unsigned indexNonconstant                                                                                = 1 + _nineq + _neq + _nineqRelaxationOnly + _neqRelaxationOnly + _nineqSquash;
    unsigned counter                                                                                         = 0;
    std::multimap<std::pair<unsigned, double>, std::pair<mc::FFVar*, mc::FFDep::TYPE>>::reverse_iterator rit = factorRanking.rbegin();
#ifdef HAVE_GROWING_DATASETS
    // Keep obj_per_data behind auxiliary variables
    // Save function pointers into temporary vector
    unsigned int tmpSize = _DAGfunctionsLbd.size();
    std::vector<mc::FFVar> dataFunctions;
    dataFunctions.resize(_ndata);
    for (auto idx = 0; idx < _ndata; idx++) {
        dataFunctions[idx] = _DAGfunctionsLbd[tmpSize - _ndata + idx];
    }
    _DAGfunctionsLbd.resize(tmpSize - _ndata);
#endif    // HAVE_GROWING_DATASETS
    for (; rit != factorRanking.rend() && counter < _maingoSettings->LBP_maxNumberOfAddedFactors; ++rit) {

        mc::FFVar* itv                             = (*rit).second.first;
        mc::FFDep::TYPE functionStructure          = (*rit).second.second;
        typename mc::FFVar::t_Ops operationsUsedIn = itv->ops().second;    // This is a list of all operations where this FFVar is used
        mc::FFOp* pOperation                       = itv->ops().first;     // This is the operation of this FFVar

        // Get new independent variable and add it to list of DAG variables
        mc::FFVar newIndependentVar = _DAGlbd.replace_intermediate_variable_by_independent_copy(itv);
        _DAGvarsLbd.push_back(newIndependentVar);

        // Add the corresponding equality constraint: aux-f(x)=0
        mc::FFVar newConstraintResidual = newIndependentVar - (*itv);
        _DAGfunctionsLbd.push_back(newConstraintResidual);
        _originalConstraints->push_back(Constraint(CONSTRAINT_TYPE::AUX_EQ_REL_ONLY, indexOriginal, indexType,
                                                   indexNonconstant, indexTypeNonconstant));
        _nonconstantConstraints->push_back(Constraint(CONSTRAINT_TYPE::AUX_EQ_REL_ONLY, indexOriginal++, indexType++,
                                                      indexNonconstant++, indexTypeNonconstant++));
        _nauxiliaryRelOnlyEqs++;
        counter++;

        // Find the correct range interval of the replaced FFVar
        size_t index                             = 0;
        std::list<const mc::FFOp*>::iterator itL = MCSubgraph.l_op.begin();
        for (; itL != MCSubgraph.l_op.end(); ++itL) {
            if ((*itL) != pOperation) {
                index++;
            }
            else {
                break;
            }
        }
        auxVariablesMCBounds.push_back(operationResultsMC[index]);
    }
#ifdef HAVE_GROWING_DATASETS
    // Append obj_per_data once again
    for (auto dataPointer : dataFunctions) {
        _DAGfunctionsLbd.push_back(dataPointer);
    }
#endif    // HAVE_GROWING_DATASETS

    // Get valid variable bounds
    _variablesLbd.clear();
    for (size_t i = 0; i < _variables.size(); i++) {
        _variablesLbd.push_back(_variables[i]);
    }

    for (size_t i = 0; i < auxVariablesMCBounds.size(); i++) {
        std::string varName = "auxVar" + std::to_string(i);
        _variablesLbd.push_back(babBase::OptimizationVariable(Bounds(auxVariablesMCBounds[i].l(), auxVariablesMCBounds[i].u()), VT_CONTINUOUS, 0, varName));
    }
    _nvarLbd = _variablesLbd.size();

    // std::ofstream o_F("DAG.txt", std::ios_base::out);
    // o_F << _DAGlbd << std::endl;
    // o_F.close();
}


/////////////////////////////////////////////////////////////////////////
// sets function properties, number of variables and type (linear, bilinear...)
void
MAiNGO::_set_constraint_and_variable_properties()
{

    // Get dependency sets of all functions
    unsigned size = 1 + _nineq + _neq + _nineqRelaxationOnly + _neqRelaxationOnly + _nineqSquash + _nauxiliaryRelOnlyEqs;
    std::vector<std::map<int, int>> func_dep(size);
    for (unsigned int i = 0; i < size; i++) {
        if (_maingoSettings->LBP_addAuxiliaryVars) {
            func_dep[i] = _DAGfunctionsLbd[i].dep().dep();
        }
        else {
            func_dep[i] = _DAGfunctions[i].dep().dep();
        }
    }

    // Prepare for determining which variable occurs only linearly (except in output functions)
    _variableIsLinear = std::vector<bool>(_nvarLbd, true);

    // Loop over all functions
    unsigned indexLinear = 0, indexNonlinear = 0;
    for (unsigned int i = 0; i < size; i++) {
        mc::FFDep::TYPE functionStructure = mc::FFDep::L;
        std::vector<unsigned> participatingVars;
        for (unsigned int j = 0; j < _nvarLbd; j++) {
            auto ito = func_dep[i].find(j);
            // Count all participating variables
            if (ito != func_dep[i].end()) {
                participatingVars.push_back(j);
                mc::FFDep::TYPE variableDep = (mc::FFDep::TYPE)(ito->second);
                // Update function type
                if (functionStructure < variableDep) {
                    functionStructure = variableDep;
                }
                if (variableDep > mc::FFDep::TYPE::L) {
                    _variableIsLinear[j] = false;
                }
            }
        }

        Constraint & nonconstCon = (*_nonconstantConstraints)[i];
        Constraint & origCon     = (*_originalConstraints)[nonconstCon.indexOriginal];

        nonconstCon.nparticipatingVariables = participatingVars.size();
        origCon.nparticipatingVariables     = participatingVars.size();
        nonconstCon.participatingVariables  = participatingVars;
        origCon.participatingVariables      = participatingVars;
        switch (functionStructure) {
            case mc::FFDep::L:
                nonconstCon.dependency  = LINEAR;
                origCon.dependency      = LINEAR;
                nonconstCon.indexLinear = indexLinear;
                origCon.indexLinear     = indexLinear++;
                break;
            case mc::FFDep::B:
                nonconstCon.dependency     = BILINEAR;
                origCon.dependency         = BILINEAR;
                nonconstCon.indexNonlinear = indexNonlinear;
                origCon.indexNonlinear     = indexNonlinear++;
                break;
            case mc::FFDep::Q:
                nonconstCon.dependency     = QUADRATIC;
                origCon.dependency         = QUADRATIC;
                nonconstCon.indexNonlinear = indexNonlinear;
                origCon.indexNonlinear     = indexNonlinear++;
                break;
            case mc::FFDep::P:
                nonconstCon.dependency     = POLYNOMIAL;
                origCon.dependency         = POLYNOMIAL;
                nonconstCon.indexNonlinear = indexNonlinear;
                origCon.indexNonlinear     = indexNonlinear++;
                break;
            case mc::FFDep::R:
                nonconstCon.dependency     = RATIONAL;
                origCon.dependency         = RATIONAL;
                nonconstCon.indexNonlinear = indexNonlinear;
                origCon.indexNonlinear     = indexNonlinear++;
                break;
            case mc::FFDep::N:
            case mc::FFDep::D:
            default:
                nonconstCon.dependency     = NONLINEAR;
                origCon.dependency         = NONLINEAR;
                nonconstCon.indexNonlinear = indexNonlinear;
                origCon.indexNonlinear     = indexNonlinear++;
                break;
        }
        nonconstCon.convexity    = CONV_NONE;
        origCon.convexity        = CONV_NONE;
        nonconstCon.monotonicity = MON_NONE;
        origCon.monotonicity     = MON_NONE;
    }

    // Fill the vector with nonconstant constraints for the UBS properly
    unsigned indexUBP          = 0;
    unsigned offset            = _neq + _nineqRelaxationOnly + _neqRelaxationOnly;    // Auxiliary relaxation only equalities are added at the end
    _nonconstantConstraintsUBP = std::make_shared<std::vector<Constraint>>();
    _nonconstantConstraintsUBP->resize(1 + _nineq + _nineqSquash + _neq);
    for (unsigned int i = 0; i < size; i++) {

        Constraint & nonconstCon = (*_nonconstantConstraints)[i];
        Constraint & origCon     = (*_originalConstraints)[nonconstCon.indexOriginal];

        switch (nonconstCon.type) {
            case OBJ:
            case INEQ:    // Objective and inequalities keep their order
                (*_nonconstantConstraintsUBP)[i]                     = nonconstCon;
                (*_nonconstantConstraintsUBP)[i].indexNonconstantUBP = indexUBP;
                nonconstCon.indexNonconstantUBP                      = indexUBP;
                origCon.indexNonconstantUBP                          = indexUBP++;
                break;
            case EQ:
                (*_nonconstantConstraintsUBP)[i + _nineqSquash]                     = nonconstCon;
                (*_nonconstantConstraintsUBP)[i + _nineqSquash].indexNonconstantUBP = indexUBP + _nineqSquash;
                nonconstCon.indexNonconstantUBP                                     = indexUBP + _nineqSquash;
                origCon.indexNonconstantUBP                                         = indexUBP + _nineqSquash;
                indexUBP++;
                break;
            case INEQ_SQUASH:
                (*_nonconstantConstraintsUBP)[i - offset]                     = nonconstCon;
                (*_nonconstantConstraintsUBP)[i - offset].indexNonconstantUBP = indexUBP - _neq;
                nonconstCon.indexNonconstantUBP                               = indexUBP - _neq;
                origCon.indexNonconstantUBP                                   = indexUBP - _neq;
                indexUBP++;
                break;
            case INEQ_REL_ONLY:
            case EQ_REL_ONLY:
            case AUX_EQ_REL_ONLY:
            default:
                break;    // We don't use relaxation only constraints in the ubp
        }
    }

    // If the model should be solved as a two-stage problem, we are done
    if (_myTwoStageFFVARmodel && (_maingoSettings->TS_useLowerBoundingSubsolvers || _maingoSettings->TS_useUpperBoundingSubsolvers)) {
        return;
    }

    // Set branching priorities on continuous variables occurring only linearly to zero to avoid branching on them
    for (size_t i = 0; i < _nvarLbd; i++) {
        if (_variableIsLinear[i] && (_variablesLbd[i].get_variable_type() == VT_CONTINUOUS)) {
            _variablesLbd[i].set_branching_priority(0.);
        }
    }
}
