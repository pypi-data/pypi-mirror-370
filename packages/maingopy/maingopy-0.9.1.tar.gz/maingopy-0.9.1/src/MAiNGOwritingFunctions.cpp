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

#include "bab.h"
#include "MAiNGO.h"
#include "MAiNGOException.h"
#include "version.h"


using namespace maingo;


////////////////////////////////////////////////////////////////////////
// Writes final logging information, results file, and csv and json files to disk
void
MAiNGO::_write_files()
{
    if ((_maingoSettings->loggingDestination == LOGGING_FILE) || (_maingoSettings->loggingDestination == LOGGING_FILE_AND_STREAM)) {
        _logger->write_all_lines_to_log();
    }

    if (_maingoSettings->writeCsv) {
        _logger->write_all_iterations_to_csv();
        _write_solution_and_statistics_csv();
    }

    if (_maingoSettings->writeJson) {
        _write_json_file();
    }

    if (_maingoSettings->writeResultFile && (!_solutionPoint.empty())) {
        _write_result_file();
    }
}


////////////////////////////////////////////////////////////////////////
// writes final logging information to disk
void
MAiNGO::_write_files_error(const std::string& errorMessage) // GCOVR_EXCL_START
{
    if ((_maingoSettings->loggingDestination == LOGGING_FILE) || (_maingoSettings->loggingDestination == LOGGING_FILE_AND_STREAM)) {
        _logger->write_all_lines_to_log(errorMessage);
    }

    if (_maingoSettings->writeCsv) {
        _logger->write_all_iterations_to_csv();
    }
}
// GCOVR_EXCL_STOP


////////////////////////////////////////////////////////////////////////
// write file containing additional non-standard information about the problem
void
MAiNGO::_write_result_file()
{
    const std::vector<double> solutionPoint              = get_solution_point();
    const std::vector<double> modelValuesAtSolutionPoint = evaluate_model_at_solution_point();

    std::ofstream resultFile;
    resultFile.open(_resultFileName, std::ios::out);

    resultFile << std::setw(25) << "variables" << std::setw(25) << "lower bound"
               << std::setw(25) << "solution point" << std::setw(25) << "upper bound" << std::endl
               << std::endl;
    for (size_t i = 0; i < solutionPoint.size(); i++) {
        resultFile << std::setw(25) << _originalVariables[i].get_name() << std::setw(25) << std::setprecision(16) << _originalVariables[i].get_lower_bound()
                   << std::setw(25) << solutionPoint[i] << std::setw(25) << _originalVariables[i].get_upper_bound() << std::endl;
    }
    resultFile << std::endl;
    resultFile << "-------------------------------------------------------------------------------------------------------------" << std::endl
               << std::endl;

    resultFile << std::setw(25) << "objective value" << std::setw(25) << std::setprecision(16) << modelValuesAtSolutionPoint[0] << std::endl
               << std::endl;
    if (_nineq > 0 || _nconstantIneq > 0) {
        resultFile << "-------------------------------------------------------------------------------------------------------------" << std::endl
                   << std::endl;
        resultFile << std::setw(25) << "inequalities" << std::setw(25) << "value" << std::setw(25) << "at bound" << std::setw(25) << "tolerance = " << _maingoSettings->deltaIneq << std::endl
                   << std::endl;

        for (size_t i = 1; i < 1 + _nineq + _nconstantIneq; i++) {
            std::string ineq = (*_originalConstraints)[i].name;
            resultFile << std::setw(25) << ineq << std::setw(25) << std::setprecision(16) << modelValuesAtSolutionPoint[i];
            if (modelValuesAtSolutionPoint[i] > _maingoSettings->deltaIneq) {   // Should never occur, but just to be sure
                resultFile << std::setw(25) << "VIOLATED" << std::endl; // GCOVR_EXCL_LINE
            }
            else if (modelValuesAtSolutionPoint[i] < _maingoSettings->deltaIneq && modelValuesAtSolutionPoint[i] >= 0.) {
                resultFile << std::setw(25) << " * " << std::endl;
            }
            else if (modelValuesAtSolutionPoint[i] < 0 && modelValuesAtSolutionPoint[i] >= -_maingoSettings->deltaIneq) {
                resultFile << std::setw(25) << "(*)" << std::endl;
            }
            else {
                resultFile << std::endl;
            }
        }
        resultFile << std::endl;
    }
    resultFile << "-------------------------------------------------------------------------------------------------------------" << std::endl
               << std::endl;

    if (_neq > 0 || _nconstantEq > 0) {
        resultFile << std::setw(25) << "equalities" << std::setw(25) << "value" << std::setw(25) << " " << std::setw(25) << "tolerance = " << _maingoSettings->deltaEq << std::endl
                   << std::endl;

        for (size_t i = 1 + _nineq + _nconstantIneq; i < 1 + _nineq + _nconstantIneq + _neq + _nconstantEq; i++) {
            std::string eq = (*_originalConstraints)[i].name;
            resultFile << std::setw(25) << eq << std::setw(25) << std::setprecision(16) << modelValuesAtSolutionPoint[i];
            if (modelValuesAtSolutionPoint[i] > _maingoSettings->deltaEq || modelValuesAtSolutionPoint[i] < -_maingoSettings->deltaEq) {   // Should never occur, but just to be sure
                resultFile << std::setw(25) << "VIOLATED" << std::endl; // GCOVR_EXCL_LINE
            }
            else {
                resultFile << std::endl;
            }
        }
        resultFile << std::endl;
    }

    if (_nineqRelaxationOnly > 0 || _nconstantIneqRelOnly > 0) {
        resultFile << "-------------------------------------------------------------------------------------------------------------" << std::endl
                   << std::endl;

        resultFile << std::setw(25) << "rel only inequalities" << std::setw(25) << "value" << std::setw(25) << "at bound" << std::setw(25) << "tolerance = " << _maingoSettings->deltaIneq << std::endl
                   << std::endl;

        for (size_t i = 1 + _nineq + _nconstantIneq + _neq + _nconstantEq; i < 1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly; i++) {
            std::string ineq = (*_originalConstraints)[i].name;
            resultFile << std::setw(25) << ineq << std::setw(25) << std::setprecision(16) << modelValuesAtSolutionPoint[i];
            if (modelValuesAtSolutionPoint[i] > _maingoSettings->deltaIneq) {   // Should never occur, but just to be sure
                resultFile << std::setw(25) << "VIOLATED" << std::endl; // GCOVR_EXCL_LINE
            }
            else if (modelValuesAtSolutionPoint[i] < _maingoSettings->deltaIneq && modelValuesAtSolutionPoint[i] >= 0.) {
                resultFile << std::setw(25) << " * " << std::endl;
            }
            else if (modelValuesAtSolutionPoint[i] < 0 && modelValuesAtSolutionPoint[i] >= -_maingoSettings->deltaIneq) {
                resultFile << std::setw(25) << "(*)" << std::endl;
            }
            else {
                resultFile << std::endl;
            }
        }
        resultFile << std::endl;
    }

    if (_neqRelaxationOnly > 0 || _nconstantEqRelOnly > 0) {
        resultFile << "-------------------------------------------------------------------------------------------------------------" << std::endl
                   << std::endl;

        resultFile << std::setw(25) << "rel only equalities" << std::setw(25) << "value" << std::setw(25) << " " << std::setw(25) << "tolerance = " << _maingoSettings->deltaEq << std::endl
                   << std::endl;

        for (size_t i = 1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly; i < 1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly + _neqRelaxationOnly + _nconstantEqRelOnly; i++) {
            std::string eq = (*_originalConstraints)[i].name;
            resultFile << std::setw(25) << eq << std::setw(25) << std::setprecision(16) << modelValuesAtSolutionPoint[i];
            if (modelValuesAtSolutionPoint[i] > _maingoSettings->deltaEq || modelValuesAtSolutionPoint[i] < -_maingoSettings->deltaEq) {   // Should never occur, but just to be sure
                resultFile << std::setw(25) << "VIOLATED" << std::endl; // GCOVR_EXCL_LINE
            }
            else {
                resultFile << std::endl;
            }
        }
        resultFile << std::endl;
    }

    if (_nineqSquash > 0 || _nconstantIneqSquash > 0) {
        resultFile << "-------------------------------------------------------------------------------------------------------------" << std::endl
                   << std::endl;

        resultFile << std::setw(25) << "squash inequalities" << std::setw(25) << "value" << std::setw(25) << " " << std::setw(25) << "tolerance = " << 0 << std::endl
                   << std::endl;

        for (size_t i = 1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly + _neqRelaxationOnly + _nconstantEqRelOnly; i < _originalConstraints->size(); i++) {
            std::string ineq = (*_originalConstraints)[i].name;
            resultFile << std::setw(25) << ineq << std::setw(25) << std::setprecision(16) << modelValuesAtSolutionPoint[i];
            if (modelValuesAtSolutionPoint[i] > 0) {   // Should never occur, but just to be sure
                resultFile << std::setw(25) << "VIOLATED" << std::endl; // GCOVR_EXCL_LINE
            }
            else if (modelValuesAtSolutionPoint[i] < 0 && modelValuesAtSolutionPoint[i] >= -_maingoSettings->deltaIneq) {
                resultFile << std::setw(25) << "(*)" << std::endl;
            }
            else {
                resultFile << std::endl;
            }
        }
        resultFile << std::endl;
    }

    resultFile.close();
}


////////////////////////////////////////////////////////////////////////
// write csv summaries
void
MAiNGO::_write_solution_and_statistics_csv()
{

    std::ofstream solutionStatisticsFile;
    solutionStatisticsFile.open(_csvSolutionStatisticsName, std::ios::out);

    if (_maingoSettings->PRE_pureMultistart) {
        solutionStatisticsFile << "  Pure Multistart " << std::endl;
        solutionStatisticsFile << "  No of local searches," << _maingoSettings->PRE_maxLocalSearches << std::endl;
    }

    if (_maingoSettings->PRE_printEveryLocalSearch) {
        for (unsigned i = 0; i < _maingoSettings->PRE_maxLocalSearches; i++) {
            if (_feasibleAtRoot[i] == SUBSOLVER_FEASIBLE) {
                solutionStatisticsFile << "  \tRun No," << i + 1 << ",objective value," << _objectivesAtRoot[i] << std::endl;
            }
            else {
                solutionStatisticsFile << "  \tRun No," << i + 1 << ",No feasible point found" << std::endl;
            }
        }
    }

    solutionStatisticsFile << "Problem type,";
    switch (_problemStructure) {
        case LP:
            solutionStatisticsFile << "0" << std::endl;
            break;
        case QP:
            solutionStatisticsFile << "1" << std::endl;
            break;
        case MIP:
            solutionStatisticsFile << "2" << std::endl;
            break;
        case MIQP:
            solutionStatisticsFile << "3" << std::endl;
            break;
        case NLP:
            solutionStatisticsFile << "4" << std::endl;
            break;
        case DNLP:
            solutionStatisticsFile << "5" << std::endl;
            break;
        case MINLP:
            solutionStatisticsFile << "6" << std::endl;
            break;
        default:    // GCOVR_EXCL_LINE
            throw MAiNGOException("Error writing solution csv file: unknown problem structure " + std::to_string(_problemStructure)); // GCOVR_EXCL_LINE
    }

    if (!_maingoSettings->PRE_pureMultistart && _problemStructure > MIQP) {
        solutionStatisticsFile << "No of Iterations," << _myBaB->get_iterations() << std::endl;
        solutionStatisticsFile << "Total LBD problems solved," << _myBaB->get_LBP_count() << std::endl;
        solutionStatisticsFile << "Total UBD problems solved," << _myBaB->get_UBP_count() << std::endl;
        solutionStatisticsFile << "Maximum number of nodes in memory," << _myBaB->get_max_nodes_in_memory() << std::endl;
        solutionStatisticsFile << "No of nodes left," << _myBaB->get_nodes_left() << std::endl;
    }

    solutionStatisticsFile << "CPU time pre-processing (s)," << _preprocessTime << std::endl;
    solutionStatisticsFile << "Wall-clock time pre-processing (s)," << _preprocessTimeWallClock << std::endl;
    solutionStatisticsFile << "CPU time branch-and-bound (s)," << _solutionTime - _preprocessTime << std::endl;
    solutionStatisticsFile << "Wall-clock time branch-and-bound (s)," << _solutionTimeWallClock - _preprocessTimeWallClock << std::endl;
    solutionStatisticsFile << "Total CPU solution time (s)," << _solutionTime << std::endl;
    solutionStatisticsFile << "Total wall-clock solution time (s)," << _solutionTimeWallClock << std::endl;
    solutionStatisticsFile << "Found feasible solution," << (!_solutionPoint.empty()) << std::endl;


    if (!_solutionPoint.empty()) {
        solutionStatisticsFile << "Optimal Solution," << _solutionValue << std::endl;
        if (!_maingoSettings->PRE_pureMultistart && _problemStructure > MIQP) {
            solutionStatisticsFile << "Best solution: First found at iteration," << _myBaB->get_first_found() << std::endl;
            solutionStatisticsFile << "Final absolute gap," << _myBaB->get_final_abs_gap() << std::endl;
            solutionStatisticsFile << "Final relative gap," << _myBaB->get_final_rel_gap() << std::endl;
        }
        solutionStatisticsFile << "Solution point";
        std::vector<double> solutionPoint = get_solution_point();
        // We write only the used non-constant (output) variables into the csv file
        for (unsigned i = 0; i < _nvarOriginal; ++i) {
            solutionStatisticsFile << "," << solutionPoint[i];
        }
        solutionStatisticsFile << std::endl;
        solutionStatisticsFile << "Additional output";
        std::vector<std::pair<std::string, double>> additionalOutput = evaluate_additional_outputs_at_solution_point();
        for (unsigned i = 0; i < additionalOutput.size(); ++i) {
            solutionStatisticsFile << "," << additionalOutput[i].second;
        }
        solutionStatisticsFile << std::endl;
    }

    solutionStatisticsFile.close();
}


////////////////////////////////////////////////////////////////////////
// write json summaries
void
MAiNGO::_write_json_file()
{
    std::ofstream jsonFile;
    jsonFile.open(_jsonFileName, std::ios::out);

    jsonFile << "{" << std::endl;
    jsonFile << "  \"MAiNGOversion\" : \"" << get_version() << "\"";

    jsonFile << "," << std::endl;
    jsonFile << "  \"ProblemType\" : \"";
    switch (_problemStructure) {
        case LP:
            jsonFile << "LP\"";
            break;
        case QP:
            jsonFile << "QP\"";
            break;
        case MIP:
            jsonFile << "MIP\"";
            break;
        case MIQP:
            jsonFile << "MIQP\"";
            break;
        case NLP:
            jsonFile << "NLP\"";
            break;
        case DNLP:
            jsonFile << "DNLP\"";
            break;
        case MINLP:
            jsonFile << "MINLP\"";
            break;
        default:    // GCOVR_EXCL_LINE
            throw MAiNGOException("Error writing json file: unknown problem structure " + std::to_string(_problemStructure)); // GCOVR_EXCL_LINE
    }

    if (!_maingoSettings->PRE_pureMultistart && _problemStructure > MIQP) {
        jsonFile << "," << std::endl;
        jsonFile << "  \"SolutionStatistics\" : {" << std::endl;
        jsonFile << "    \"NumberOfIterations\" : " << _myBaB->get_iterations() << "," << std::endl;
        jsonFile << "    \"LBDProblemsSolved\" : " << _myBaB->get_LBP_count() << "," << std::endl;
        jsonFile << "    \"UBPProblemsSolved\" : " << _myBaB->get_UBP_count() << "," << std::endl;
        jsonFile << "    \"MaximumNodesInMemory\" : " << _myBaB->get_max_nodes_in_memory() << "," << std::endl;
        jsonFile << "    \"NumberOfNodesLeft\" : " << _myBaB->get_nodes_left() << std::endl;
        jsonFile << "  }";
    }

    jsonFile << "," << std::endl;
    jsonFile << "  \"Timing\" : {" << std::endl;
    jsonFile << "    \"PreProcessingCPU\" : " << _preprocessTime << "," << std::endl;
    jsonFile << "    \"PreProcessingWall\" : " << _preprocessTimeWallClock << "," << std::endl;
    jsonFile << "    \"BranchAndBoundCPU\" : " << _solutionTime - _preprocessTime << "," << std::endl;
    jsonFile << "    \"BranchAndBoundWall\" : " << _solutionTimeWallClock - _preprocessTimeWallClock << "," << std::endl;
    jsonFile << "    \"TotalCPU\" : " << _solutionTime << "," << std::endl;
    jsonFile << "    \"TotalWall\" : " << _solutionTimeWallClock << std::endl;
    jsonFile << "  }";

    jsonFile << "," << std::endl;
    jsonFile << "  \"Solution\" : {" << std::endl;
    const std::string str = (!_solutionPoint.empty()) ? "true" : "false";
    jsonFile << "    \"FoundFeasiblePoint\" : " << str << "," << std::endl;
    jsonFile << "    \"MAiNGOstatus\" : ";
    switch (_maingoStatus) {
        case GLOBALLY_OPTIMAL:
            jsonFile << "\"Globally optimal\"";
            break;
        case INFEASIBLE:
            jsonFile << "\"Infeasible\"";
            break;
        case FEASIBLE_POINT:
            jsonFile << "\"Feasible point\"";
            break;
        case NO_FEASIBLE_POINT_FOUND:
            jsonFile << "\"No feasible point found\"";
            break;
        case BOUND_TARGETS:
            jsonFile << "\"Reached target bound\"";
            break;
        case NOT_SOLVED_YET: // GCOVR_EXCL_START
            jsonFile << "\"Not solved yet\"";
            break;
        case JUST_A_WORKER_DONT_ASK_ME:
            jsonFile << "\"Just a worker\"";
            break;
        default:
            throw MAiNGOException("Error writing json file: unknown status " + std::to_string(_maingoStatus));
        // GCOVR_EXCL_STOP
    }


    if (!_solutionPoint.empty()) {
        jsonFile << "," << std::endl;
        jsonFile << "    \"BestSolutionValue\" : " << _solutionValue << "," << std::endl;
        if (!_maingoSettings->PRE_pureMultistart && _problemStructure > MIQP) {
            jsonFile << "    \"FoundAtNode\" : " << _myBaB->get_first_found() << "," << std::endl;
            jsonFile << "    \"AbsoluteGap\" : " << _myBaB->get_final_abs_gap() << "," << std::endl;
            jsonFile << "    \"RelativeGap\" : " << _myBaB->get_final_rel_gap() << "," << std::endl;
        }
        jsonFile << "    \"SolutionPoint\" : [" << std::endl;
        std::vector<double> solutionPoint = get_solution_point();
        // We write only the used non-constant (output) variables into the csv file
        for (unsigned i = 0; i < _nvarOriginal; ++i) {
            jsonFile << "      {" << std::endl;
            jsonFile << "        \"VariableName\" : \"" << _originalVariables[i].get_name() << "\"," << std::endl;
            jsonFile << "        \"VariableValue\" : " << solutionPoint[i] << std::endl;
            if (i + 1 < _nvarOriginal) {
                jsonFile << "      }," << std::endl;
            }
            else {
                jsonFile << "      }" << std::endl;
            }
        }
        jsonFile << "    ]," << std::endl;
        jsonFile << "    \"AdditionalOutput\" : [" << std::endl;
        std::vector<std::pair<std::string, double>> additionalOutput = evaluate_additional_outputs_at_solution_point();
        for (unsigned i = 0; i < additionalOutput.size(); ++i) {
            jsonFile << "      {" << std::endl;
            jsonFile << "        \"VariableName\" : \"" << additionalOutput[i].first << "\"," << std::endl;
            jsonFile << "        \"VariableValue\" : " << additionalOutput[i].second << std::endl;
            if (i + 1 < additionalOutput.size()) {
                jsonFile << "      }," << std::endl;
            }
            else {
                jsonFile << "      }" << std::endl;
            }
        }
        jsonFile << "    ]" << std::endl;
    }
    jsonFile << std::endl << "  }";
    jsonFile << std::endl << "}";

    jsonFile.close();
}


/////////////////////////////////////////////////////////////////////////
// write files containing the results of the solution of a bi-objective problem solved via the epsilon constraint method
void
MAiNGO::_write_epsilon_constraint_result(const std::vector<std::vector<double>>& objectiveValues, const std::vector<std::vector<double>>& solutionPoints)
{
    std::ofstream objectiveValuesFile("MAiNGO_epsilon_constraint_objective_values.csv", std::ios::out);
    if (_maingoStatus == INFEASIBLE) {
        objectiveValuesFile << "Problem is infeasible." << std::endl;
    } else {
        objectiveValuesFile << "obj1, obj2" << std::endl;
        for (size_t i = 0; i < objectiveValues.size(); i++) {
            objectiveValuesFile << objectiveValues[i][0];
            for (size_t j = 1; j < objectiveValues[i].size(); j++) {
                objectiveValuesFile << ", " << objectiveValues[i][j];
            }
            objectiveValuesFile << std::endl;
        }
    }
    objectiveValuesFile.close();

    std::ofstream pointsFile("MAiNGO_epsilon_constraint_solution_points.csv", std::ios::out);
    if (_maingoStatus == INFEASIBLE) {
        pointsFile << "Problem is infeasible." << std::endl;
    } else {
        pointsFile << "x0";
        for (size_t i = 1; i < solutionPoints[0].size(); i++) {
            pointsFile << ", x" << i;
        }
        pointsFile << std::endl;
        for (size_t i = 0; i < solutionPoints.size(); i++) {
            pointsFile << solutionPoints[i][0];
            for (size_t j = 1; j < solutionPoints[i].size(); j++) {
                pointsFile << ", " << solutionPoints[i][j];
            }
            pointsFile << std::endl;
        }
    }
    pointsFile.close();
}