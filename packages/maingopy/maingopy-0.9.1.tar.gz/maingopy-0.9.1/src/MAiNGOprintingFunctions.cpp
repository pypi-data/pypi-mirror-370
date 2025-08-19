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
#include "bab.h"
#include "getTime.h"
#include "version.h"

#include <cassert>


using namespace maingo;


////////////////////////////////////////////////////////////////////////
// Evaluate model at initial point and print the values of the variables, objective, constraint residuals and outputs
void
MAiNGO::_print_info_about_initial_point()
{
    assert(_initialPointOriginal.empty() || (_initialPointOriginal.size() == _originalVariables.size()));

    if (_initialPointOriginal.empty()) {
        std::ostringstream outstream;
        outstream << std::endl
                  << "  No initial point given." << std::endl
                  << std::endl;
        _logger->print_message(outstream.str(), VERB_ALL, BAB_VERBOSITY);
        return;
    }

    // Variables:
    std::ostringstream outstream;
    outstream << std::endl
              << "  Initial point:" << std::endl;
    for (size_t i = 0; i < _originalVariables.size(); ++i) {
        outstream << "      '" << _originalVariables[i].get_name() << "' = " << _initialPointOriginal[i];
        babBase::enums::VT varType(_originalVariables[i].get_variable_type());
        if (varType == babBase::enums::VT_BINARY) {
            outstream << (((_initialPointOriginal[i] == 0) || (_initialPointOriginal[i] == 1)) ? " in " : " NOT in ") << "{0, 1}" << std::endl;
        }
        else if (varType == babBase::enums::VT_INTEGER) {
            const bool feasible = (_initialPointOriginal[i] == std::round(_initialPointOriginal[i])) && (_initialPointOriginal[i] >= _originalVariables[i].get_lower_bound()) && (_initialPointOriginal[i] <= _originalVariables[i].get_upper_bound());
            outstream << (feasible ? " in " : " NOT in ") << "{" << _originalVariables[i].get_lower_bound() << ", ..., " << _originalVariables[i].get_upper_bound() << "}" << std::endl;
        }
        else {
            outstream << (((_initialPointOriginal[i] >= _originalVariables[i].get_lower_bound()) && (_initialPointOriginal[i] <= _originalVariables[i].get_upper_bound())) ? " in " : " NOT in ");
            outstream << "[" << _originalVariables[i].get_lower_bound() << ", " << _originalVariables[i].get_upper_bound() << "]" << std::endl;
        }
    }

    // Objective & constraint residuals:
    const std::pair<std::vector<double>, bool> result = evaluate_model_at_point(_initialPointOriginal);
    outstream << "  Model evaluated at initial point:" << std::endl;
    outstream << "      Objective = " << result.first[0] << std::endl;
    outstream << "      Initial point feasible? " << ((result.second == true) ? "yes" : "no") << std::endl;
    if (result.first.size() > 1) {
        outstream << "      Constraint residuals:" << std::endl;
        for (size_t i = 1; i <= _nineq + _nconstantIneq; ++i) {
            outstream << "          ineq # " << i;
            if (_modelOutput.ineq.name[i - 1] != "") {
                outstream << ", '" << _modelOutput.ineq.name[i - 1] << "'";
            }
            outstream << ": " << result.first[i];
            if (result.first[i] > _maingoSettings->deltaIneq) {
                outstream << " (VIOLATED)";
            }
            outstream << std::endl;
        }
        for (size_t i = 1 + _nineq + _nconstantIneq; i <= _nineq + _nconstantIneq + _neq + _nconstantEq; ++i) {
            outstream << "          eq # " << i - _nineq - _nconstantIneq;
            if (_modelOutput.eq.name[i - (_nineq + _nconstantIneq) - 1] != "") {
                outstream << ", '" << _modelOutput.eq.name[i - (_nineq + _nconstantIneq) - 1] << "'";
            }
            outstream << ": " << result.first[i];
            if (std::fabs(result.first[i]) > _maingoSettings->deltaEq) {
                outstream << " (VIOLATED)";
            }
            outstream << std::endl;
        }
    }

    // Additional outputs
    const std::vector<std::pair<std::string, double>> outputs = evaluate_additional_outputs_at_point(_initialPointOriginal);
    if (outputs.size() != 0) {
        outstream << "  Outputs at initial point:" << std::endl;
        for (size_t i = 0; i < outputs.size(); ++i) {
            outstream << "      " << outputs[i].first << ": " << outputs[i].second << std::endl;
        }
    }
    outstream << std::endl;

    _logger->print_message(outstream.str(), VERB_ALL, BAB_VERBOSITY);
}


////////////////////////////////////////////////////////////////////////
// prints model and solution statistics on screen
void
MAiNGO::_print_statistics()
{

    std::ostringstream outstream;

    // Print solution status in case of pure multistart or termination during pre-processing
    if (_babStatus == babBase::enums::BAB_RETCODE::NOT_SOLVED_YET) {
        if ((_rootConPropStatus == TIGHTENING_INFEASIBLE) || (_rootObbtStatus == TIGHTENING_INFEASIBLE) || (_problemStructure < NLP) || (!_constantConstraintsFeasible) || (!_infeasibleVariables.empty())) {
            _print_message(std::string("*** Regular termination. ***"));
        }
        else if (_maingoSettings->terminateOnFeasiblePoint && _rootMultistartStatus == SUBSOLVER_FEASIBLE) {
            _print_message(std::string("*** Found feasible point. ***"));
        }
        else if (_maingoSettings->PRE_pureMultistart) {
            _print_message(std::string("*** Finished multistart. ***"));
        }
        else if (_solutionValue <= _maingoSettings->targetUpperBound) {
            _print_message(std::string("*** Reached target upper bound. ***"));
        }
    }

    // Model statistics
    outstream << std::endl
              << "  Problem statistics: " << std::endl;
    // Variables
    outstream << "    Variables" << std::setw(34) << "= " << _nvarOriginal << std::endl;
    if (_nvarOriginalContinuous > 0) {
        outstream << "      Thereof continuous " << std::setw(22) << "= " << _nvarOriginalContinuous << std::endl;
    }
    if (_nvarOriginalBinary > 0) {
        outstream << "      Thereof binary " << std::setw(26) << "= " << _nvarOriginalBinary << std::endl;
    }
    if (_nvarOriginalInteger > 0) {
        outstream << "      Thereof integer " << std::setw(25) << "= " << _nvarOriginalInteger << std::endl;
    }
    // Constraints
    outstream << "    Inequality constraints" << std::setw(21) << "= " << _nineq + _nconstantIneq << std::endl;
    if (_nconstantIneq > 0) {
        outstream << "      Thereof constant " << std::setw(24) << "= " << _nconstantIneq << std::endl;
    }
    outstream << "    Equality constraints" << std::setw(23) << "= " << _neq + _nconstantEq << std::endl;
    if (_nconstantEq > 0) {
        outstream << "      Thereof constant " << std::setw(24) << "= " << _nconstantEq << std::endl;
    }
    if (_nineqRelaxationOnly + _nconstantIneqRelOnly > 0) {
        outstream << "    Inequality constraints (relaxation only)" << std::setw(3) << "= " << _nineqRelaxationOnly + _nconstantIneqRelOnly << std::endl;
    }
    if (_nconstantIneqRelOnly > 0) {
        outstream << "      Thereof constant " << std::setw(24) << "= " << _nconstantIneqRelOnly << std::endl;
    }
    if (_neqRelaxationOnly + _nconstantEqRelOnly > 0) {
        outstream << "    Equality constraints (relaxation only)" << std::setw(5) << "= " << _neqRelaxationOnly + _nconstantEqRelOnly << std::endl;
    }
    if (_nconstantEqRelOnly > 0) {
        outstream << "      Thereof constant " << std::setw(24) << "= " << _nconstantEqRelOnly << std::endl;
    }
    if (_nineqSquash + _nconstantIneqSquash > 0) {
        outstream << "    Inequality constraints (squash)" << std::setw(12) << "= " << _nineqSquash + _nconstantIneqSquash << std::endl;
    }
    if (_nconstantIneqSquash > 0) {
        outstream << "      Thereof constant " << std::setw(24) << "= " << _nconstantIneqSquash << std::endl;
    }

    // B&B solution statistics
    if (_babStatus != babBase::enums::BAB_RETCODE::NOT_SOLVED_YET) {
        outstream << std::endl
                  << "  Solution statistics: " << std::endl;
        outstream << "    Total UBD problems solved " << std::setw(10) << "= " << _myBaB->get_UBP_count() << std::endl;
        outstream << "    Total LBD problems solved " << std::setw(10) << "= " << _myBaB->get_LBP_count() << std::endl;
        outstream << "    Total number of iterations " << std::setw(9) << "= " << _myBaB->get_iterations() << std::endl;
        outstream << "    Maximum number of nodes in memory = " << _myBaB->get_max_nodes_in_memory() << std::endl;
        if (!_solutionPoint.empty()) {
            if (_feasibilityProblem) {
                outstream << "    Feasible point first found at iteration " << _myBaB->get_first_found() << std::endl;
            }
            else {
                outstream << "    Best solution first found at iteration " << _myBaB->get_first_found() << std::endl;
            }
        }
    }

    outstream << std::endl
              << "===================================================================" << std::endl;

    _logger->print_message(outstream.str(), VERB_NORMAL, BAB_VERBOSITY);
}


////////////////////////////////////////////////////////////////////////
// prints solution on screen
void
MAiNGO::_print_solution()
{

    std::ostringstream outstream;

    // Get max name length of the variables for nicer output
    size_t maxWordLength = 0;
    for (unsigned i = 0; i < _nvarOriginal; ++i) {
        maxWordLength = std::max(maxWordLength, _originalVariables[i].get_name().length());
    }

    if (!_infeasibleVariables.empty()) {
        outstream << std::endl
                  << "  Problem is infeasible." << std::endl;
        outstream << "\n  The problem is infeasible because of inconsistent bounds for the following variables:" << std::endl;
        for (unsigned int i = 0; i < _infeasibleVariables.size(); i++) {
            outstream << "  " << *(_infeasibleVariables.at(i)) << std::endl;
        }
    }
    else if (!_constantConstraintsFeasible) {
        outstream << std::endl
                  << "  Problem is infeasible." << std::endl;
        outstream << "\n  The problem is infeasible because of the following constant constraints:" << std::endl;
        for (size_t i = 0; i < _constantConstraints->size(); i++) {
            if (!(*_constantConstraints)[i].isFeasible) {
                switch ((*_constantConstraints)[i].type) {
                    case INEQ:
                        outstream << "  Inequality " << (*_constantConstraints)[i].name << " has value "
                                  << (*_constantConstraints)[i].constantValue << " > " << _maingoSettings->deltaIneq << std::endl;
                        break;
                    case EQ:
                        outstream << "  Equality " << (*_constantConstraints)[i].name << " has value "
                                  << (*_constantConstraints)[i].constantValue << " and is not in [-" << _maingoSettings->deltaEq << "," << _maingoSettings->deltaEq << "]" << std::endl;
                        break;
                    case INEQ_REL_ONLY:
                        outstream << "  Inequality (relaxation only) " << (*_constantConstraints)[i].name << " has value "
                                  << (*_constantConstraints)[i].constantValue << " > " << _maingoSettings->deltaIneq << std::endl;
                        break;
                    case EQ_REL_ONLY:
                        outstream << "  Equality (relaxation only) " << (*_constantConstraints)[i].name << " has value "
                                  << (*_constantConstraints)[i].constantValue << " and is not in [-" << _maingoSettings->deltaEq << "," << _maingoSettings->deltaEq << "]" << std::endl;
                        break;
                    case INEQ_SQUASH:
                        outstream << "  Inequality (squash) " << (*_constantConstraints)[i].name << " has value "
                                  << (*_constantConstraints)[i].constantValue << " > 0" << std::endl;
                        break;
                    default:    // GCOVR_EXCL_LINE
                        throw MAiNGOException("Error printing solution: unknown constraint type " + std::to_string((*_constantConstraints)[i].type));   // GCOVR_EXCL_LINE
                }
            }
        }
    }
    else if (_problemStructure >= NLP || (_myTwoStageFFVARmodel && (_maingoSettings->TS_useLowerBoundingSubsolvers || _maingoSettings->TS_useUpperBoundingSubsolvers))) {
        if (!_solutionPoint.empty()) {
            outstream << std::endl;
            if (!_feasibilityProblem) {
                if (_babStatus != babBase::enums::BAB_RETCODE::NOT_SOLVED_YET) {
                    outstream << "  Final LBD " << std::setw(11) << "= " << std::setprecision(16) << _myBaB->get_final_LBD() << std::endl;
                    outstream << "  Final absolute gap = " << _myBaB->get_final_abs_gap() << std::endl;
                    if (mc::isequal(_solutionValue, 0, mc::machprec(), mc::machprec())) {
                        outstream << "  Final relative gap = not defined" << std::endl;
                    }
                    else {
                        outstream << "  Final relative gap = " << _myBaB->get_final_rel_gap() << std::endl;
                    }
                    if (_myBaB->get_final_abs_gap() < 0) {    // GCOVR_EXCL_START
                        if (_myBaB->get_final_abs_gap() >= -_maingoSettings->MC_mvcompTol) {
                            outstream << "  Warning: Final gap is negative. This is probably due to numerical precision and probably okay.\n";
                            outstream << "           You can try to re-run the problem with decreased MC_mvcompTol." << std::endl;
                        }
                        else {
                            outstream << "  Warning: Final gap is negative. Please report this issue to the developers." << std::endl;
                        }
                    }
                    // GCOVR_EXCL_STOP
                }
                outstream << "  Objective value = " << _solutionValue << std::endl;
            }
            outstream << "  Solution point:" << std::endl;
            unsigned removed = 0;
            for (unsigned i = 0; i < _nvarOriginal; ++i) {
                std::string varName(_originalVariables[i].get_name());
                if (varName != "") {
                    // Use user-defined variable name
                }
                else {    // Use default name
                    varName = " var(" + std::to_string(i + 1) + ")";
                }
                if (_removedVariables[i]) {
                    std::string s;
                    switch (_originalVariables[i].get_variable_type()) {
                        case babBase::enums::VT_BINARY:
                            s = "{0,1}";
                            break;
                        case babBase::enums::VT_INTEGER:
                            s = "{" + std::to_string((int)_originalVariables[i].get_lower_bound()) + ",..., " + std::to_string((int)_originalVariables[i].get_upper_bound()) + "}";
                            break;
                        case babBase::enums::VT_CONTINUOUS:
                        default:
                            s = "[" + std::to_string(_originalVariables[i].get_lower_bound()) + "," + std::to_string(_originalVariables[i].get_upper_bound()) + "]";
                            break;
                    }
                    outstream << "    " << std::setw(maxWordLength) << varName << std::setw(3) << " = " << std::setw(20) << s << std::endl;
                    removed++;
                }
                else {
                    outstream << "    " << std::setw(maxWordLength) << varName << std::setw(3) << " = " << std::setw(20) << std::setprecision(16) << _solutionPoint[i - removed] << std::endl;
                }
            }
            // Check whether the incumbent fullfils relaxation only constraints
            std::string str;
            std::string whitespaces = "    ";
            if (!_check_feasibility_of_relaxation_only_constraints(_solutionPoint, str, whitespaces)) { // GCOVR_EXCL_START
                if (_myBaB->get_final_abs_gap() < 0) {
                    str += "             This may also explain the negative final optimality gap.\n";
                }
            }
            // GCOVR_EXCL_STOP
            outstream << str;
        }
        else {
            if ((_babStatus == babBase::enums::INFEASIBLE) || (_rootObbtStatus == TIGHTENING_INFEASIBLE) || (_rootConPropStatus == TIGHTENING_INFEASIBLE)) {
                outstream << std::endl
                          << "  Problem is infeasible!" << std::endl;
            }
            else {
                outstream << std::endl
                          << "  No feasible point found." << std::endl;
            }
        }
    }
    else {

        if (_miqpStatus == SUBSOLVER_INFEASIBLE) {
            outstream << std::endl
                      << "  Problem is infeasible." << std::endl;
        }
        else {
            outstream << std::endl;
            if (!_feasibilityProblem) {
                outstream << "  Objective value = " << _solutionValue << std::endl;
            }
            if (!_solutionPoint.empty()) {
                outstream << "  Solution point: " << std::endl;
                unsigned removed = 0;
                for (unsigned i = 0; i < _nvarOriginal; ++i) {
                    std::string varName(_originalVariables[i].get_name());
                    if (varName != "") {
                        // Use user-defined variable name
                    }
                    else {    // Use default name
                        varName = " var(" + std::to_string(i + 1) + ")";
                    }
                    if (_removedVariables[i]) {
                        std::string s;
                        switch (_originalVariables[i].get_variable_type()) {
                            case babBase::enums::VT_BINARY:
                                s = "{0,1}";
                                break;
                            case babBase::enums::VT_INTEGER:
                                s = "{" + std::to_string((int)_originalVariables[i].get_lower_bound()) + ",..., " + std::to_string((int)_originalVariables[i].get_upper_bound()) + "}";
                                break;
                            case babBase::enums::VT_CONTINUOUS:
                            default:
                                s = "[" + std::to_string(_originalVariables[i].get_lower_bound()) + "," + std::to_string(_originalVariables[i].get_upper_bound()) + "]";
                                break;
                        }
                        outstream << "    " << std::setw(maxWordLength) << varName << std::setw(3) << " = " << std::setw(20) << s << std::endl;
                        removed++;
                    }
                    else {
                        outstream << "    " << std::setw(maxWordLength) << varName << std::setw(3) << " = " << std::setw(20) << std::setprecision(16) << _solutionPoint[i - removed] << std::endl;
                    }
                }
                // Check whether the incumbent fullfils relaxation only constraints
                std::string str         = "";
                std::string whitespaces = "    ";
                _check_feasibility_of_relaxation_only_constraints(_solutionPoint, str, whitespaces);
                outstream << str;
            }
            else {
                outstream << std::endl
                          << "\n  Solution point could not be obtained from (MI)LP / (MI)QP solver although optimal objective was reported." << std::endl; // GCOVR_EXCL_LINE
            }
        }
    }

    outstream << std::endl
              << "===================================================================" << std::endl;

    _logger->print_message(outstream.str(), VERB_NORMAL, BAB_VERBOSITY);
}


////////////////////////////////////////////////////////////////////////
// prints solution time on screen
void
MAiNGO::_print_time()
{

    // CPU time
    _outputTime   = get_cpu_time() - _outputTime;
    _solutionTime = _preprocessTime + _babTime + _outputTime;

    std::ostringstream outstr;
    outstr << "\n  CPU time:        " << std::fixed << std::setprecision(3) << (_solutionTime) << " seconds (Preprocessing + B&B).\n";
    if (_solutionTime > 60) {
        outstr << "                   This equals ";
        unsigned int hours = 0;
        if (_solutionTime > 3600) {
            hours = (unsigned int)(_solutionTime / 3600);
            outstr << hours << "h ";
        }
        unsigned int minutes = (unsigned int)((_solutionTime - hours * 3600) / 60);
        outstr << minutes << "m " << std::fixed << std::setprecision(3) << (_solutionTime - hours * 3600. - minutes * 60.) << "s (CPU).\n";
    }
    _logger->print_message(outstr.str(), VERB_NORMAL, BAB_VERBOSITY);

    // Wall-clock time
    outstr.str("");
    outstr.clear();
    _outputTimeWallClock   = get_wall_time() - _outputTimeWallClock;
    _solutionTimeWallClock = _preprocessTimeWallClock + _babTimeWallClock + _outputTimeWallClock;

    outstr << "  Wall-clock time: " << std::fixed << std::setprecision(3) << (_solutionTimeWallClock) << " seconds (Preprocessing + B&B).\n";
    if (_solutionTimeWallClock > 60) {
        outstr << "                   This equals ";
        unsigned int hours = 0;
        if (_solutionTimeWallClock > 3600) {
            hours = (unsigned int)(_solutionTimeWallClock / 3600);
            outstr << hours << "h ";
        }
        unsigned int minutes = (unsigned int)((_solutionTimeWallClock - hours * 3600) / 60);
        outstr << minutes << "m " << std::fixed << std::setprecision(3) << (_solutionTimeWallClock - hours * 3600. - minutes * 60.) << "s (wall clock).\n";
    }

    outstr << std::endl;


    _logger->print_message(outstr.str(), VERB_NORMAL, BAB_VERBOSITY);
}


////////////////////////////////////////////////////////////////////////
// gets additional model output for printing in screen and logging
void
MAiNGO::_print_additional_output()
{

    std::ostringstream outstream;

    if ((!_solutionPoint.empty()) && (_noutputVariables > 0 || _nconstantOutputVariables > 0) && (_constantConstraintsFeasible)) {

        outstream << "\n  Additional Model outputs: " << std::endl;

        // Get maximal output name length for nicer output
        size_t maxWordLength = 0;
        for (unsigned int i = 0; i < _noutputVariables; i++) {
            maxWordLength = std::max(maxWordLength, (*_nonconstantOutputs)[i].name.length());
        }
        for (unsigned int i = 0; i < _nconstantOutputVariables; i++) {
            maxWordLength = std::max(maxWordLength, (*_constantOutputs)[i].name.length());
        }

        std::vector<std::pair<std::string, double>> output = evaluate_additional_outputs_at_solution_point();
        for (unsigned int i = 0; i < output.size(); i++) {
            outstream << "    " << std::setw(maxWordLength) << output[i].first << " = " << std::setprecision(16) << output[i].second << std::endl;
        }
        outstream << std::endl
                  << "===================================================================" << std::endl;
    }

    _logger->print_message(outstream.str(), VERB_NORMAL, BAB_VERBOSITY);
}


#ifdef HAVE_GROWING_DATASETS
////////////////////////////////////////////////////////////////////////
// prints statistics of post-processing for heuristic B&B algorithm with growing datasets on screen
void
MAiNGO::_print_statistics_postprocessing()
{

    std::ostringstream outstream;

    outstream << "===================================================================" << std::endl;

    outstream << std::endl
              << "  Post-processing statistics: " << std::endl;
    outstream << "    Total number of nodes tracked "   << std::setw(4) << "= " << _myBaB->get_nodes_tracked_for_postprocessing() << std::endl;
    outstream << "    Total number of nodes processed " << std::setw(1) << "= " << _myBaB->get_nodes_processed_in_postprocessing() << std::endl;
    outstream << "    Final LBD "                      << std::setw(24) << "= " << std::setprecision(6) <<  _myBaB->get_lower_bound_after_postprocessing();
    if (_myBaB->get_lower_bound_after_postprocessing() < _myBaB->get_final_LBD()) {
        outstream << " (changed)" << std::endl;
    }
    else {
        outstream << " (unchanged)" << std::endl;
    }
    outstream << "    CPU time " << std::setw(25) << "= " << _myBaB->get_time_for_postprocessing() << " seconds";
#ifdef HAVE_MAiNGO_MPI
    outstream << " (manager process) ";
#endif // HAVE_MAiNGO_MPI
    outstream << std::endl;

    _logger->print_message(outstream.str(), VERB_NORMAL, BAB_VERBOSITY);
}
#endif // HAVE_GROWING_DATASETS


/////////////////////////////////////////////////////////////////////////
// print an ASCII MAiNGO and copyright
void
MAiNGO::print_MAiNGO(std::ostream& outstream)
{
    // This may look weird and badly shifted but it is due to the double backslash
    outstream << std::endl;
    outstream << "+---------------------------------------------------------------------------------------------------------------------+\n";
    outstream << "|                                                                                                          /)_        |\n";
    outstream << "|                                                                                                         //\\  `.     |\n";
    outstream << "|                                                                                                  ____,.//, \\   \\    |\n";
    outstream << "|                               You are using MAiNGO " << get_version() << "                                   _.-'         `.`.  \\   |\n";
    outstream << "|                                                                                            ,'               : `..\\  |\n";
    outstream << "|                                                                                           :         ___      :      |\n";
    outstream << "| Copyright (c) 2019 Process Systems Engineering (AVT.SVT), RWTH Aachen University         :       .'     `.    :     |\n";
    outstream << "|                                                                                         :         `.    /     ;     |\n";
    outstream << "| This program and the accompanying materials are made available under the               :           /   /     ;      |\n";
    outstream << "| terms of the Eclipse Public License 2.0 which is available at                         :        __.'   /     :       |\n";
    outstream << "| http://www.eclipse.org/legal/epl-2.0.                                                 ;      /       /     :        |\n";
    outstream << "|                                                                                       ;      `------'     /         |\n";
    outstream << "| SPDX-License-Identifier: EPL-2.0                                                      :                  :          |\n";
    outstream << "| Authors: Dominik Bongartz, Jaromil Najman, Susanne Sass, Alexander Mitsos             \\                 /           |\n";
    outstream << "|                                                                                        `.             .`            |\n";
    outstream << "| Please provide all feedback and bugs to the developers.                                  '-._     _.-'              |\n";
    outstream << "| E-mail: MAiNGO@avt.rwth-aachen.de                                                            `'''`                  |\n";
    outstream << "+---------------------------------------------------------------------------------------------------------------------+\n";
}


/////////////////////////////////////////////////////////////////////////
// print MAiNGO header
void
MAiNGO::_print_MAiNGO_header()
{
    std::ostringstream outstream;

    outstream << std::endl
              << "************************************************************************************************************************" << std::endl;
    outstream << "*                                                                                                                      *" << std::endl;
    outstream << "*                                             You are using MAiNGO " << get_version() << "                                            *" << std::endl;
    outstream << "*                                                                                                                      *" << std::endl;
    outstream << "*  Please cite the latest MAiNGO report from http://permalink.avt.rwth-aachen.de/?id=729717 :                          *" << std::endl;
    outstream << "*  Bongartz, D., Najman, J., Sass, S. and Mitsos, A., MAiNGO - McCormick-based Algorithm for mixed-integer Nonlinear   *" << std::endl;
    outstream << "*  Global Optimization. Technical Report, Process Systems Engineering (AVT.SVT), RWTH Aachen University (2018).        *" << std::endl;
    outstream << "*                                                                                                                      *" << std::endl;
    outstream << "************************************************************************************************************************" << std::endl;

    _logger->print_message(outstream.str(), VERB_NORMAL, BAB_VERBOSITY);
}


////////////////////////////////////////////////////////////////////////
// prints message
void
MAiNGO::_print_message(const std::string& message)
{


    std::ostringstream outstream;
    outstream << std::endl
              << "************************************************************************************************************************" << std::endl;
    outstream << "*                                                                                                                      *" << std::endl;

    size_t L                      = message.length();
    size_t whitespacesToFillLeft  = (118 - L) / 2;
    size_t whitespacesToFillRight = (118 - L) % 2 ? (118 - L) / 2 + 1 : (118 - L) / 2;
    std::string leftString(whitespacesToFillLeft, ' ');
    std::string rightString(whitespacesToFillRight, ' ');

    outstream << "*" << leftString << message << rightString << "*" << std::endl;
    outstream << "*                                                                                                                      *" << std::endl;
    outstream << "************************************************************************************************************************" << std::endl;

    _logger->print_message(outstream.str(), VERB_NORMAL, BAB_VERBOSITY, UBP_VERBOSITY, LBP_VERBOSITY);
}


/////////////////////////////////////////////////////////////////////////
// print information about the major pieces of third-party software used
// when using the (MI)NLP solution algorithm
void
MAiNGO::_print_third_party_software_minlp()
{
    _logger->print_message("\n  Major third-party software used:\n", VERB_NORMAL, BAB_VERBOSITY);

    // First, determine which third-party UBP and LBP solvers are used:
    bool usingCobyla = false, usingBobyqa = false, usingLbfgs = false, usingSlsqp = false, usingIpopt = false, usingKnitro = false;
    if (_maingoSettings->PRE_maxLocalSearches > 0) {
        switch (_maingoSettings->UBP_solverPreprocessing) {
            case ubp::UBP_SOLVER_EVAL:
                // Just evaluating, nothing to report
                break;
            case ubp::UBP_SOLVER_COBYLA:
                usingCobyla = true;
                break;
            case ubp::UBP_SOLVER_BOBYQA:
                usingBobyqa = true;
                break;
            case ubp::UBP_SOLVER_LBFGS:
                usingLbfgs = true;
                break;
            case ubp::UBP_SOLVER_SLSQP:
                usingSlsqp = true;
                break;
            case ubp::UBP_SOLVER_IPOPT:
                usingIpopt = true;
                break;
            case ubp::UBP_SOLVER_KNITRO:
                usingKnitro = true;
                break;
            default:    // GCOVR_EXCL_LINE
                throw MAiNGOException("    ERROR printing third-party software: unknown upper bounding solver for pre-processing");    // GCOVR_EXCL_LINE
        }
    }
    if (!_maingoSettings->PRE_pureMultistart) {
        switch (_maingoSettings->UBP_solverBab) {
            case ubp::UBP_SOLVER_EVAL:
                // Just evaluating, nothing to report
                break;
            case ubp::UBP_SOLVER_COBYLA:
                usingCobyla = true;
                break;
            case ubp::UBP_SOLVER_BOBYQA:
                usingBobyqa = true;
                break;
            case ubp::UBP_SOLVER_LBFGS:
                usingLbfgs = true;
                break;
            case ubp::UBP_SOLVER_SLSQP:
                usingSlsqp = true;
                break;
            case ubp::UBP_SOLVER_IPOPT:
                usingIpopt = true;
                break;
            case ubp::UBP_SOLVER_KNITRO:
                usingKnitro = true;
                break;
            default:    // GCOVR_EXCL_LINE
                throw MAiNGOException("    ERROR printing third-party software: unknown upper bounding solver for B&B");    // GCOVR_EXCL_LINE
        }
    }
    bool usingCplex = false, usingGurobi = false, usingClp = false;
    switch (_maingoSettings->LBP_solver) {
        case lbp::LBP_SOLVER_MAiNGO:
            // Nothing to report
            break;
        case lbp::LBP_SOLVER_INTERVAL:
            // Nothing to report
            break;
        case lbp::LBP_SOLVER_CLP:
            usingClp = true;
            break;
        case lbp::LBP_SOLVER_SUBDOMAIN:
            // Nothing to report
            break;
        case lbp::LBP_SOLVER_CPLEX:
            usingCplex = true;
            break;
        case lbp::LBP_SOLVER_GUROBI:
            usingGurobi = true;
            break;
        default:    // GCOVR_EXCL_LINE
            throw MAiNGOException("    ERROR printing third-party software: unknown lower bounding solver");    // GCOVR_EXCL_LINE
    }

    // Always using MC++ and Filib++
    if (_maingoSettings->LBP_solver != lbp::LBP_SOLVER_INTERVAL) {
        _logger->print_message("    - MC++ by B. Chachuat et al. (DAG & relaxations)\n", VERB_NORMAL, BAB_VERBOSITY);
    }
    else {
        _logger->print_message("    - MC++ by B. Chachuat et al. (DAG)\n", VERB_NORMAL, BAB_VERBOSITY);
    }
    _logger->print_message("    - Filib++ by M. Lerch et al. (interval extensions)\n", VERB_NORMAL, BAB_VERBOSITY);

    // Depending on UBP and LBP solvers, may use Fadbad++, MUMPS, BLAS, and LAPACK
    if (usingLbfgs || usingSlsqp || usingIpopt || usingKnitro) {
        _logger->print_message("    - FADBAD++ by O. Stauning and C. Bendtsen (automatic differentiation)\n", VERB_NORMAL, BAB_VERBOSITY);
    }
    if (usingIpopt || usingClp) {
        _logger->print_message("    - MUMPS by P.R. Amestoy et al. (sparse linear solver)\n", VERB_NORMAL, BAB_VERBOSITY);
        _logger->print_message("    - Netlib BLAS and LAPACK (linear algebra)\n", VERB_NORMAL, BAB_VERBOSITY);
    }

    // Print UBP solvers
    if (usingCobyla) {
        _logger->print_message("    - COBYLA by M.J.D. Powell implemented in NLopt by S.G. Johnson (local NLP solver)\n", VERB_NORMAL, BAB_VERBOSITY);
    }
    if (usingBobyqa) {
        _logger->print_message("    - BOBYQA by M.J.D. Powell implemented in NLopt by S.G. Johnson (local NLP solver)\n", VERB_NORMAL, BAB_VERBOSITY);
    }
    if (usingLbfgs) {
        _logger->print_message("    - L-BFGS by L. Luksan implemented in NLopt by S.G. Johnson (local NLP solver)\n", VERB_NORMAL, BAB_VERBOSITY);
    }
    if (usingSlsqp) {
        _logger->print_message("    - SLSQP by D. Kraft implemented in NLopt by S.G. Johnson (local NLP solver)\n", VERB_NORMAL, BAB_VERBOSITY);
    }
    if (usingIpopt) {
        _logger->print_message("    - IPOPT by A. Waechter and L.T. Biegler (local NLP solver)\n", VERB_NORMAL, BAB_VERBOSITY);
    }
    if (usingKnitro) {
        _logger->print_message("    - Artelys KNITRO by R.H. Byrd, J. Nocedal, and R.A. Waltz (local NLP solver)\n", VERB_NORMAL, BAB_VERBOSITY);
    }

    // Print LBP solvers
    if (usingCplex) {
        _logger->print_message("    - IBM CPLEX (LP solver)\n", VERB_NORMAL, BAB_VERBOSITY);
    }
    if (usingGurobi) {
        _logger->print_message("    - Gurobi (LP solver)\n", VERB_NORMAL, BAB_VERBOSITY);
    }
    if (usingClp) {
        _logger->print_message("    - CLP by J.J. Forrest et al. (LP solver)\n", VERB_NORMAL, BAB_VERBOSITY);
    }
}


/////////////////////////////////////////////////////////////////////////
// print information about the major pieces of third-party software used
// when solving an (MI)QP or (MI)LP with the corresponding specialized solvers
void
MAiNGO::_print_third_party_software_miqp()
{
    _logger->print_message("\n  This MAiNGO run uses the following major pieces of third-party software:\n", VERB_NORMAL, BAB_VERBOSITY);

    _logger->print_message("    - MC++ by B. Chachuat et al. (DAG)\n", VERB_NORMAL, BAB_VERBOSITY);
    if (_maingoSettings->UBP_solverPreprocessing == ubp::UBP_SOLVER_CLP) {
        _logger->print_message("    - MUMPS by P.R. Amestoy et al. (sparse linear solver)\n", VERB_NORMAL, BAB_VERBOSITY);
        _logger->print_message("    - Netlib BLAS and LAPACK (linear algebra)\n", VERB_NORMAL, BAB_VERBOSITY);
    }

    // UBP solvers:
    if (_maingoSettings->UBP_solverPreprocessing == ubp::UBP_SOLVER_CPLEX) {
        _logger->print_message("    - IBM CPLEX ((MI)LP/(MI)QP solver)\n", VERB_NORMAL, BAB_VERBOSITY);
    }
    if (_maingoSettings->UBP_solverPreprocessing == ubp::UBP_SOLVER_GUROBI) {
        _logger->print_message("    - Gurobi ((MI)LP/(MI)QP solver)\n", VERB_NORMAL, BAB_VERBOSITY);
    }
    if (_maingoSettings->UBP_solverPreprocessing == ubp::UBP_SOLVER_CLP) {
        _logger->print_message("    - CLP by J.J. Forrest et al. (LP solver)\n", VERB_NORMAL, BAB_VERBOSITY);
    }
    _logger->print_message("\n", VERB_NORMAL, BAB_VERBOSITY);
}