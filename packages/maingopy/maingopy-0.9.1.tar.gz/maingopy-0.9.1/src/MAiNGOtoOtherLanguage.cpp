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
#include "version.h"

#include "fftostring.hpp"

#include <cctype>
#include <cstring>
#include <fstream>
#include <string>

using namespace maingo;


/////////////////////////////////////////////////////////////////////////
// writes file in a given modeling language out of MAiNGO DAG
void
MAiNGO::write_model_to_file_in_other_language(const WRITING_LANGUAGE writingLanguage, std::string fileName, const std::string solverName,
                                              const bool useMinMax, const bool useTrig, const bool ignoreBoundingFuncs, const bool writeRelaxationOnly)
{
    if (!_modelSpecified) {
        throw MAiNGOException("  Error trying to write model to file: Model has not been set successfully.");
    }

    try {
        _construct_DAG();
    }
    catch (const std::exception &e) {   // GCOVR_EXCL_START
        std::ostringstream errmsg;
        errmsg << e.what() << "\n  Encountered a fatal error during DAG construction.";
        if (_inMAiNGOsolve) {
            _write_files_error(errmsg.str());
        }
        throw MAiNGOException("  Encountered a fatal error during DAG construction.", e);
    }
    catch (...) {
        if (_inMAiNGOsolve) {
            _write_files_error("\n  Encountered an unknown fatal error during DAG construction.");
        }
        throw MAiNGOException("  Encountered an unknown fatal error during DAG construction.");
    }
    // GCOVR_EXCL_STOP

    // Set options
    mc::FFToString::options.USE_MIN_MAX                   = useMinMax;
    mc::FFToString::options.USE_TRIG                      = useTrig;
    mc::FFToString::options.IGNORE_BOUNDING_FUNCS         = ignoreBoundingFuncs;
    mc::FFToString::options.USED_ENTHALPY_OF_VAPORIZATION = false;    // This is set to false. If it is true after writing of the file, we have to give a warning

    switch (writingLanguage) {
        case LANG_GAMS:
            mc::FFToString::options.WRITING_LANGUAGE = mc::FFToString::LANGUAGE::GAMS;
            if (fileName.empty()) {
                fileName = "MAiNGO_written_model.gms";
            }
            _write_gams_file(fileName, solverName, writeRelaxationOnly);
            break;
        case LANG_ALE:
            mc::FFToString::options.WRITING_LANGUAGE = mc::FFToString::LANGUAGE::ALE;
            if (fileName.empty()) {
                fileName = "MAiNGO_written_model.txt";
            }
            _write_ale_file(fileName, solverName, writeRelaxationOnly);
            break;
        case LANG_NONE:
            _logger->print_message_to_stream_only("\n  WARNING: asked MAiNGO to write model to file, but chosen writing language is NONE. Not writing anything.\n");
            return;
        default:    // GCOVR_EXCL_LINE
            throw MAiNGOException("Error trying to write model to file: unknown modeling language."); // GCOVR_EXCL_LINE
    }

    // Check if we have to warn the user
    if (mc::FFToString::options.USED_ENTHALPY_OF_VAPORIZATION) {
        std::ostringstream ostr;
        ostr << "  Warning: Function ENTHALPY_OF_VAPORIZATION is piecewise defined in MAiNGO. Only the subcritical part will be used.\n";
        if (_inMAiNGOsolve) {
            _logger->print_message(ostr.str(), VERB_NORMAL, BAB_VERBOSITY);
        }
        else {
            _logger->print_message_to_stream_only(ostr.str());
        }
        mc::FFToString::options.USED_ENTHALPY_OF_VAPORIZATION = false;    // Reset this value
    }
}


/////////////////////////////////////////////////////////////////////////
// writes gams file out of MAiNGO DAG
void
MAiNGO::_write_gams_file(const std::string gamsFileName, const std::string solverName, const bool writeRelaxationOnly)
{

    std::ostringstream ostr;
    ostr << "\n  Writing GAMS file. Depending on your model size and complexity, this may need a lot of memory and time...\n";
    if (_inMAiNGOsolve) {
        _logger->print_message(ostr.str(), VERB_NORMAL, BAB_VERBOSITY);
    }
    else {
        _logger->print_message_to_stream_only(ostr.str());
    }

    std::ofstream gamsFile(gamsFileName);

    _print_MAiNGO_header_for_other_modeling_language(LANG_GAMS, gamsFile);
    _write_gams_variables(gamsFile);
    _write_gams_functions(gamsFile, writeRelaxationOnly);
    _write_gams_options(gamsFile, solverName);

    gamsFile.close();

    _uniqueNamesOriginal.clear();
    _uniqueNames.clear();
}


/////////////////////////////////////////////////////////////////////////
// writes problem variables into gams file
void
MAiNGO::_write_gams_variables(std::ofstream &gamsFile)
{

    std::string contVariables = "";
    std::string binVariables  = "";
    std::string intVariables  = "";

    // Construct strings holding different variable types
    _uniqueNames.clear();
    unsigned lengthCounterCont = 0;
    unsigned lengthCounterBin  = 0;
    unsigned lengthCounterInt  = 0;
    for (unsigned int i = 0; i < _originalVariables.size(); i++) {
        std::string currentName = _originalVariables[i].get_name();
        if (currentName.length() == 0) {
            currentName = "x";
        }
        else if (!std::isalpha(currentName[0])) {    // Check for first character
            currentName = 'x' + currentName;
        }
        // Get rid of forbidden characters and replace them by _
        for (unsigned int j = 0; j < currentName.length(); j++) {
            if (!std::isalpha(currentName[j]) && !std::isdigit(currentName[j])) {
                currentName[j] = '_';
            }
        }
        // Since variable names in MAiNGO need not be unique, we need to make sure it is not already in the GAMS file - else append a number
        if (find(_uniqueNamesOriginal.begin(), _uniqueNamesOriginal.end(), currentName) != _uniqueNamesOriginal.end()) {
            bool finalizedName = false;
            unsigned suffix    = 2;
            while (!finalizedName) {
                std::stringstream tmpName;
                tmpName << currentName << suffix;
                if (find(_uniqueNamesOriginal.begin(), _uniqueNamesOriginal.end(), tmpName.str()) != _uniqueNamesOriginal.end()) {
                    ++suffix;
                }
                else {
                    currentName   = tmpName.str();
                    finalizedName = true;
                }
            }
        }
        if (!_removedVariables[i]) {
            _uniqueNamesOriginal.push_back(currentName);
            _uniqueNames.push_back(currentName);
        }
        else {
            _uniqueNamesOriginal.push_back(currentName);
        }
        // Write the final strings and make sure they are not too long
        if (_originalVariables[i].get_variable_type() == VT_CONTINUOUS) {
            if (contVariables.length() > 200 + lengthCounterCont * 200) {
                contVariables = contVariables + currentName + ",\n          ";
                lengthCounterCont++;
            }
            else {
                contVariables = contVariables + currentName + ", ";
            }
        }
        else if (_originalVariables[i].get_variable_type() == VT_BINARY) {
            if (binVariables.length() + currentName.length() > 200 + lengthCounterBin * 200) {
                binVariables = binVariables + currentName + ",\n                 ";
                lengthCounterBin++;
            }
            else {
                binVariables = binVariables + currentName + ", ";
            }
        }
        else if (_originalVariables[i].get_variable_type() == VT_INTEGER) {
            if (intVariables.length() + currentName.length() > 200 + lengthCounterInt * 200) {
                intVariables = intVariables + currentName + ",\n                  ";
                lengthCounterInt++;
            }
            else {
                intVariables = intVariables + currentName + ", ";
            }
        }
    }

    // Write objective variable
    contVariables = contVariables + "objectiveVar;\n\n";

    // Write the different variable types into the gams file
    gamsFile << "*Continuous variables\n";
    gamsFile << "variables " << contVariables;

    if (!binVariables.empty()) {
        binVariables.pop_back();
        binVariables.pop_back();    // Get rid of last ", "
        gamsFile << "*Binary variables\n";
        gamsFile << "binary variables " << binVariables << ";\n\n";
    }

    if (!intVariables.empty()) {
        intVariables.pop_back();
        intVariables.pop_back();    // Get rid of last ", "
        gamsFile << "*Integer variables\n";
        gamsFile << "integer variables " << intVariables << ";\n\n";
    }

    // Write bounds of all the different variable types (binary variables don't need bounds)
    gamsFile << "*Continuous variable bounds\n";
    std::ostringstream str;    // Dummy ostringstream

    for (unsigned int i = 0; i < _originalVariables.size(); i++) {
        if (_originalVariables[i].get_variable_type() == VT_CONTINUOUS) {
            str << std::setprecision(16) << _originalVariables[i].get_lower_bound();
            gamsFile << _uniqueNamesOriginal[i] + ".LO = " + str.str() + ";\n";
            str.str("");
            str.clear();    // Clear ostringstream properly
            str << std::setprecision(16) << _originalVariables[i].get_upper_bound();
            gamsFile << _uniqueNamesOriginal[i] + ".UP = " + str.str() + ";\n";
            str.str("");
            str.clear();
        }
    }
    gamsFile << "\n";
    if (!intVariables.empty()) {
        gamsFile << "*Integer variable bounds\n";
        for (unsigned int i = 0; i < _originalVariables.size(); i++) {
            if (_originalVariables[i].get_variable_type() == VT_INTEGER) {
                str << std::setprecision(16) << _originalVariables[i].get_lower_bound();
                gamsFile << _uniqueNamesOriginal[i] + ".LO = " + str.str() + ";\n";
                str.str("");
                str.clear();    // Clear ostringstream properly
                str << std::setprecision(16) << _originalVariables[i].get_upper_bound();
                gamsFile << _uniqueNamesOriginal[i] + ".UP = " + str.str() + ";\n";
                str.str("");
                str.clear();
            }
        }
        gamsFile << "\n";
    }

    // Write initial point if provided
    if (!_initialPointOriginal.empty()) {
        gamsFile << "*Initial point\n";
        for (unsigned int i = 0; i < _initialPointOriginal.size(); i++) {
            str << std::setprecision(16) << _initialPointOriginal[i];
            gamsFile << _uniqueNamesOriginal[i] + ".L = " + str.str() + ";\n";
            str.str("");
            str.clear();
        }
        gamsFile << "\n";
    }
}


/////////////////////////////////////////////////////////////////////////
// writes all problem functions into gams file
void
MAiNGO::_write_gams_functions(std::ofstream &gamsFile, bool writeRelaxationOnly)
{

    std::ostringstream ostr;     // Dummy ostringstream
    std::string str     = "";    // Dummy string
    std::string longstr = "";    // Dummy string for functions
    // Write equation variables
    gamsFile << "*Equation variables\n";
    str = "equations objective, ";
    // Don't forget about the constant functions
    // Inequalities
    if (_nineq > 0 || _nconstantIneq > 0) {
        str = str + "\n";
        for (unsigned int i = 1; i < _nineq + _nconstantIneq + 1; i++) {
            ostr << (*_originalConstraints)[i].indexType + 1;
            str = str + "ineq" + ostr.str();
            if ("ineq" + ostr.str() != (*_originalConstraints)[i].name) {
                str = str + " \"" + (*_originalConstraints)[i].name + "\"";
            }
            str = str + ",\n";
            ostr.str("");
            ostr.clear();
        }
    }
    // Equalities
    if (_neq > 0 || _nconstantEq > 0) {
        str = str + "\n";
        for (unsigned int i = 1 + _nineq + _nconstantIneq; i < 1 + _nineq + _nconstantIneq + _neq + _nconstantEq; i++) {
            ostr << (*_originalConstraints)[i].indexType + 1;
            str = str + "eq" + ostr.str();
            if ("eq" + ostr.str() != (*_originalConstraints)[i].name) {
                str = str + " \"" + (*_originalConstraints)[i].name + "\"";
            }
            str = str + ",\n";
            ostr.str("");
            ostr.clear();
        }
    }
    if (writeRelaxationOnly) {
        // Relaxation-only inequalities
        if (_nineqRelaxationOnly > 0 || _nconstantIneqRelOnly > 0) {
            str = str + "\n";
            for (unsigned int i = 1 + _nineq + _nconstantIneq + _neq + _nconstantEq; i < 1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly; i++) {
                ostr << (*_originalConstraints)[i].indexType + 1;
                str = str + "relOnlyIneq" + ostr.str();
                if ("relOnlyIneq" + ostr.str() != (*_originalConstraints)[i].name) {
                    str = str + " \"" + (*_originalConstraints)[i].name + "\"";
                }
                str = str + ",\n";
                ostr.str("");
                ostr.clear();
            }
        }
        // Relaxation-only equalities
        if (_neqRelaxationOnly > 0 || _nconstantEqRelOnly > 0) {
            str = str + "\n";
            for (unsigned int i = 1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly; i < 1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly + _neqRelaxationOnly + _nconstantEqRelOnly; i++) {
                ostr << (*_originalConstraints)[i].indexType + 1;
                str = str + "relOnlyEq" + ostr.str();
                if ("relOnlyEq" + ostr.str() != (*_originalConstraints)[i].name) {
                    str = str + " \"" + (*_originalConstraints)[i].name + "\"";
                }
                str = str + ",\n";
                ostr.str("");
                ostr.clear();
            }
        }
    }
    // Squash inequalities
    if (_nineqSquash > 0 || _nconstantIneqSquash > 0) {
        str = str + "\n";
        for (unsigned int i = 1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly + _neqRelaxationOnly + _nconstantEqRelOnly; i < _originalConstraints->size(); i++) {
            ostr << (*_originalConstraints)[i].indexType + 1;
            str = str + "squashIneq" + ostr.str();
            if ("squashIneq" + ostr.str() != (*_originalConstraints)[i].name) {
                str = str + " \"" + (*_originalConstraints)[i].name + "\"";
            }
            str = str + ",\n";
            ostr.str("");
            ostr.clear();
        }
    }

    str.pop_back();
    str.pop_back();    // Get rid of last ", "
    str = str + ";\n\n";

    gamsFile << str;
    str.clear();

    // Evaluate the functions in FFToString arithmetic
    mc::FFSubgraph tmpSubgraph = _DAG.subgraph(_DAGfunctions.size(), _DAGfunctions.data());

    std::vector<mc::FFToString> stringVars(_nvar);
    std::vector<mc::FFToString> stringDummy(tmpSubgraph.l_op.size());    // Dummy for faster evaluation
    std::vector<mc::FFToString> resultString(_DAGfunctions.size());      // This has to be a vector in order to use the eval function
    for (unsigned int i = 0; i < _nvar; i++) {
        stringVars[i] = mc::FFToString(_uniqueNames[i], mc::FFToString::PRIO);    // Name the variables
    }
    _DAG.eval(tmpSubgraph, stringDummy, _DAGfunctions.size(), _DAGfunctions.data(), resultString.data(), _nvar, _DAGvars.data(), stringVars.data());

    // Write the functions
    // Objective function first
    gamsFile << "*Objective function\n";
    longstr = resultString[0].get_function_string();
    _add_linebreaks_to_gams_string(longstr);
    gamsFile << "objective .. objectiveVar =E= " << longstr << ";\n\n";
    longstr.clear();

    // Don't forget about constant functions
    // The ordering of printing functions matches the input ordering of the user
    // Inequalities
    if (_nineq > 0 || _nconstantIneq > 0) {
        str = str + "*Inequalities\n";
        for (unsigned int i = 1; i < 1 + _nineq + _nconstantIneq; i++) {
            ostr << (*_originalConstraints)[i].indexType + 1;
            if ((*_originalConstraints)[i].isConstant) {
                longstr = std::to_string((*_originalConstraints)[i].constantValue);
            }
            else {
                longstr = resultString[(*_originalConstraints)[i].indexNonconstant].get_function_string();
            }
            _add_linebreaks_to_gams_string(longstr);
            str = str + "ineq" + ostr.str() + " .. " + longstr + " =L= 0;\n";
            ostr.str("");
            ostr.clear();
            longstr.clear();
        }
        str = str + "\n";
    }
    gamsFile << str;
    str.clear();
    // Equalities
    if (_neq > 0 || _nconstantEq > 0) {
        str = str + "*Equalities\n";
        for (unsigned int i = 1 + _nineq + _nconstantIneq; i < 1 + _nineq + _nconstantIneq + _neq + _nconstantEq; i++) {
            ostr << (*_originalConstraints)[i].indexType + 1;
            if ((*_originalConstraints)[i].isConstant) {
                longstr = std::to_string((*_originalConstraints)[i].constantValue);
            }
            else {
                longstr = resultString[(*_originalConstraints)[i].indexNonconstant].get_function_string();
            }
            _add_linebreaks_to_gams_string(longstr);
            str = str + "eq" + ostr.str() + " .. " + longstr + " =E= 0;\n";
            ostr.str("");
            ostr.clear();
            longstr.clear();
        }
        str = str + "\n";
    }
    gamsFile << str;
    str.clear();


    if (writeRelaxationOnly && ((_nineqRelaxationOnly > 0) || (_neqRelaxationOnly > 0) || (_nconstantIneqRelOnly > 0) || (_nconstantEqRelOnly > 0))) {
        std::ostringstream outstr;
        outstr << "  Warning: Your model contains relaxation-only constraints. These will be written to the GAMS model, but it is up to you to mark them as relaxation-only!" << std::endl
               << "           Otherwise, they will be treated as regular constraints. To our knowledge, BARON is the only solver in GAMS that supports relaxation-only constraints." << std::endl;
        if (_inMAiNGOsolve) {
            _logger->print_message(outstr.str(), VERB_NORMAL, BAB_VERBOSITY);
        }
        else {
            _logger->print_message_to_stream_only(outstr.str());
        }
        gamsFile << "*Warning: Your model contains relaxation-only constraints. These have been written to the GAMS model, but it is up to you to mark them as relaxation-only!" << std::endl
                 << "*         Otherwise, they will be treated as regular constraints. To our knowledge, BARON is the only solver in GAMS that supports relaxation-only constraints." << std::endl;

        // Relaxation-only inequalities
        if (_nineqRelaxationOnly > 0 || _nconstantIneqRelOnly > 0) {
            str = str + "*Relaxation-only inequalities\n";
            for (unsigned int i = 1 + _nineq + _nconstantIneq + _neq + _nconstantEq; i < 1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly; i++) {
                ostr << (*_originalConstraints)[i].indexType + 1;
                if ((*_originalConstraints)[i].isConstant) {
                    longstr = std::to_string((*_originalConstraints)[i].constantValue);
                }
                else {
                    longstr = resultString[(*_originalConstraints)[i].indexNonconstant].get_function_string();
                }
                _add_linebreaks_to_gams_string(longstr);
                str = str + "relOnlyIneq" + ostr.str() + " .. " + longstr + " =L= 0;\n";
                ostr.str("");
                ostr.clear();
                longstr.clear();
            }
            str = str + "\n";
        }
        gamsFile << str;
        str.clear();
        // Relaxation-only equalities
        if (_neqRelaxationOnly > 0 || _nconstantEqRelOnly > 0) {
            str = str + "*Relaxation-only equalities\n";
            for (size_t i = 1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly; i < 1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly + _neqRelaxationOnly + _nconstantEqRelOnly; i++) {
                ostr << (*_originalConstraints)[i].indexType + 1;
                if ((*_originalConstraints)[i].isConstant) {
                    longstr = std::to_string((*_originalConstraints)[i].constantValue);
                }
                else {
                    longstr = resultString[(*_originalConstraints)[i].indexNonconstant].get_function_string();
                }
                _add_linebreaks_to_gams_string(longstr);
                str = str + "relOnlyEq" + ostr.str() + " .. " + longstr + " =E= 0;\n";
                ostr.str("");
                ostr.clear();
                longstr.clear();
            }
            str = str + "\n";
        }
        gamsFile << str;
        str.clear();
    }

    // Squash inequalities
    if (_nineqSquash > 0 || _nconstantIneqSquash > 0) {
        std::ostringstream outstr;
        outstr << "  Warning: Your model contains squash inequalities. These have been written to the GAMS model and will be treated as regular constraints." << std::endl
               << "           To our knowledge, GAMS does not supports squash inequalities." << std::endl;
        if (_inMAiNGOsolve) {
            _logger->print_message(outstr.str(), VERB_NORMAL, BAB_VERBOSITY);
        }
        else {
            _logger->print_message_to_stream_only(outstr.str());
        }
        str = str + "*Warning: Your model contains squash inequalities. These have been written to the GAMS model and will be treated as regular constraints. To our knowledge, GAMS does not supports squash inequalities.\n";
        str = str + "*Squash Inequalities\n";
        for (unsigned int i = 1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly + _neqRelaxationOnly + _nconstantEqRelOnly; i < _originalConstraints->size(); i++) {
            ostr << (*_originalConstraints)[i].indexType + 1;
            if ((*_originalConstraints)[i].isConstant) {
                longstr = std::to_string((*_originalConstraints)[i].constantValue);
            }
            else {
                longstr = resultString[(*_originalConstraints)[i].indexNonconstant].get_function_string();
            }
            _add_linebreaks_to_gams_string(longstr);
            str = str + "squashIneq" + ostr.str() + " .. " + longstr + " =L= 0;\n";
            ostr.str("");
            ostr.clear();
            longstr.clear();
        }
        str = str + "\n";
    }
    gamsFile << str;
    str.clear();
}


/////////////////////////////////////////////////////////////////////////
// writes problem variables into gams file
void
MAiNGO::_write_gams_options(std::ofstream &gamsFile, std::string solverName)
{

    std::ostringstream ostr;    // Dummy ostringstream
    std::string str = "";       // Dummy string

    // Define model and possible optionfile
    gamsFile << "*Model information and options\n"
             << "model m / all /;\n\n";
    gamsFile << "*Optional option file\n"
             << "m.optfile = 1;\n\n";

    // Optimality tolerances and time
    gamsFile << "*Optimality tolerances, time and solver\n";
    ostr << _maingoSettings->epsilonA;
    gamsFile << "option OPTCA = " << ostr.str() << ";\n";
    ostr.str("");
    ostr.clear();
    ostr << _maingoSettings->epsilonR;
    gamsFile << "option OPTCR = " << ostr.str() << ";\n";
    ostr.str("");
    ostr.clear();
    ostr << _maingoSettings->maxTime;
    gamsFile << "option RESLIM = " << ostr.str() << ";\n";
    ostr.str("");
    ostr.clear();

    // Get problem structure to set the correct option
    _recognize_structure();
    switch (_problemStructure) {
        case LP:
            str = "LP";
            break;
        case MIP:
            str = "MIP";
            break;
        case QP:
            str = "QCP";
            break;
        case MIQP:
            str = "MIQCP";
            break;
        case NLP:
            str = "NLP";
            break;
        case DNLP:
            str = "DNLP";
            break;
        case MINLP:
            str = "MINLP";
            break;
        default:    // GCOVR_EXCL_LINE
            throw MAiNGOException("Error writing GAMS options while writing problem to file: unknown problem structure.");  // GCOVR_EXCL_LINE
    }
    gamsFile << "option " << str << " = " << solverName << ";\n\n";

    // Solve statement
    gamsFile << "*Solve statement\n";
    gamsFile << "solve m using " << str << " minimizing objectiveVar;";
}


/////////////////////////////////////////////////////////////////////////
// adds linebreaks to too long gams string
void
MAiNGO::_add_linebreaks_to_gams_string(std::string &str)
{

    if (str.length() / 40000 > 1) {
        unsigned int charNr = 39001;
        while (charNr < str.length()) {
            while (str[charNr] != ' ' && str[charNr] != '+' && str[charNr] != '*' && str[charNr] != ')' && str[charNr] != '(') {
                charNr++;
                if (str[charNr] == ';') {
                    break;
                }
            }
            str.insert(charNr, "\n            ");
            charNr += 39000;
        }
    }
}


/////////////////////////////////////////////////////////////////////////
// writes ale file out of MAiNGO DAG
void
MAiNGO::_write_ale_file(const std::string aleFileName, const std::string solverName, const bool writeRelaxationOnly)
{

    std::ostringstream ostr;
    ostr << "\n  Writing ALE file. Depending on your model size and complexity, this may need a lot of memory and time...\n";
    if (_inMAiNGOsolve) {
        _logger->print_message(ostr.str(), VERB_NORMAL, BAB_VERBOSITY);
    }
    else {
        _logger->print_message_to_stream_only(ostr.str());
    }

    std::ofstream aleFile(aleFileName);

    _print_MAiNGO_header_for_other_modeling_language(LANG_ALE, aleFile);

    _write_ale_variables(aleFile);
    _write_ale_functions(aleFile, writeRelaxationOnly);
    /* Currently not supported
    _write_ale_options(aleFile, solverName);
    */
    aleFile.close();

    _uniqueNamesOriginal.clear();
    _uniqueNames.clear();
}


/////////////////////////////////////////////////////////////////////////
// writes problem variables into ale file
void
MAiNGO::_write_ale_variables(std::ofstream &aleFile)
{

    std::string contVariables = "";
    std::string binVariables  = "";
    std::string intVariables  = "";

    // Construct strings holding different variable types
    _uniqueNames.clear();
    unsigned lengthCounterCont = 0;
    unsigned lengthCounterBin  = 0;
    unsigned lengthCounterInt  = 0;
    for (unsigned int i = 0; i < _originalVariables.size(); i++) {
        std::string currentName = _originalVariables[i].get_name();
        if (currentName.length() == 0) {
            currentName = "x";
        }
        else if (!std::isalpha(currentName[0])) {    // Check for first character
            currentName = 'x' + currentName;
        }
        // Get rid of forbidden characters
        for (unsigned int j = 0; j < currentName.length(); j++) {
            if (!std::isalpha(currentName[j]) && !std::isdigit(currentName[j])) {
                currentName[j] = '_';
            }
        }
        // Since variable names in MAiNGO need not be unique, we need to make sure it is not already in the ALE file - else append a number
        if (find(_uniqueNamesOriginal.begin(), _uniqueNamesOriginal.end(), currentName) != _uniqueNamesOriginal.end()) {
            bool finalizedName = false;
            unsigned suffix    = 2;
            while (!finalizedName) {
                std::stringstream tmpName;
                tmpName << currentName << suffix;
                if (find(_uniqueNamesOriginal.begin(), _uniqueNamesOriginal.end(), tmpName.str()) != _uniqueNamesOriginal.end()) {
                    ++suffix;
                }
                else {
                    currentName   = tmpName.str();
                    finalizedName = true;
                }
            }
        }
        if (!_removedVariables[i]) {
            _uniqueNamesOriginal.push_back(currentName);
            _uniqueNames.push_back(currentName);
        }
        else {
            _uniqueNamesOriginal.push_back(currentName);
        }
        // Write the final strings and make sure they are not too long
        if (_originalVariables[i].get_variable_type() == VT_CONTINUOUS) {
            std::ostringstream str;
            str << std::setprecision(16) << _originalVariables[i].get_lower_bound();
            contVariables = contVariables + "  real " + currentName + " in [" + str.str();
            str.str("");
            str.clear();    // Clear ostringstream properly
            str << std::setprecision(16) << _originalVariables[i].get_upper_bound();
            contVariables = contVariables + "," + str.str() + "];\n";
        }
        else if (_originalVariables[i].get_variable_type() == VT_BINARY) {
            binVariables = binVariables + "  binary " + currentName + ";\n";
        }
        else if (_originalVariables[i].get_variable_type() == VT_INTEGER) {
            std::ostringstream str;
            str << _originalVariables[i].get_lower_bound();
            intVariables = intVariables + "  integer " + currentName + " in [" + str.str();
            str.str("");
            str.clear();    // Clear ostringstream properly
            str << _originalVariables[i].get_upper_bound();
            intVariables = intVariables + "," + str.str() + "];\n";
        }
    }

    aleFile << "definitions:\n";

    // Write the different variable types into the ale file
    aleFile << "#Continuous variables\n";
    aleFile << contVariables;

    if (!binVariables.empty()) {
        binVariables.pop_back();
        binVariables.pop_back();    // Get rid of last ", "
        aleFile << "#Binary variables\n";
        aleFile << binVariables << ";\n\n";
    }

    if (!intVariables.empty()) {
        intVariables.pop_back();
        intVariables.pop_back();    // Get rid of last ", "
        aleFile << "#Integer variables\n";
        aleFile << intVariables << ";\n\n";
    }

    // Write initial point if provided
    if (!_initialPointOriginal.empty()) {
        aleFile << "#Initial point\n";
        for (unsigned int i = 0; i < _initialPointOriginal.size(); i++) {
            aleFile << _uniqueNamesOriginal[i] << ".init <- " << std::setprecision(16) << _initialPointOriginal[i] << ";\n";
        }
        aleFile << "\n";
    }

    aleFile << "\n";
}


/////////////////////////////////////////////////////////////////////////
// writes all problem functions into gams file
void
MAiNGO::_write_ale_functions(std::ofstream &aleFile, bool writeRelaxationOnly)
{

    std::ostringstream ostr;     // Dummy ostringstream
    std::string str     = "";    // Dummy string
    std::string longstr = "";    // Dummy string for functions

    // Evaluate the functions in FFToString arithmetic
    mc::FFSubgraph tmpSubgraph = _DAG.subgraph(_DAGfunctions.size(), _DAGfunctions.data());

    std::vector<mc::FFToString> stringVars(_nvar);
    std::vector<mc::FFToString> stringDummy(tmpSubgraph.l_op.size());    // Dummy for faster evaluation
    std::vector<mc::FFToString> resultString(_DAGfunctions.size());      // This has to be a vector in order to use the eval function
    for (unsigned int i = 0; i < _nvar; i++) {
        stringVars[i] = mc::FFToString(_uniqueNames[i], mc::FFToString::PRIO);    // Name the variables
    }
    _DAG.eval(tmpSubgraph, stringDummy, _DAGfunctions.size(), _DAGfunctions.data(), resultString.data(), _nvar, _DAGvars.data(), stringVars.data());

    // Don't forget about constant functions
    // The ordering of printing functions matches the input ordering of the user
    if (_nineq > 0 || _nconstantIneq > 0 || _neq > 0 || _nconstantEq > 0) {
        str = str + "constraints:\n";
    }
    // Inequalities
    if (_nineq > 0 || _nconstantIneq > 0) {
        str = str + "#Inequalities\n";
        for (unsigned int i = 1; i < 1 + _nineq + _nconstantIneq; i++) {
            ostr << (*_originalConstraints)[i].indexType + 1;
            if ((*_originalConstraints)[i].isConstant) {
                longstr = std::to_string((*_originalConstraints)[i].constantValue);
            }
            else {
                longstr = resultString[(*_originalConstraints)[i].indexNonconstant].get_function_string();
            }
            _add_linebreaks_to_gams_string(longstr);
            str = str + " " + longstr + " <= 0";
            if ((*_originalConstraints)[i].name != "ineq" + ostr.str()) {
                str = str + " \"" + (*_originalConstraints)[i].name + "\"";
            }
            str = str + ";\n";
            ostr.str("");
            ostr.clear();
            longstr.clear();
        }
        str = str + "\n";
    }
    aleFile << str;
    str.clear();
    // Equalities
    if (_neq > 0 || _nconstantEq > 0) {
        str = str + "#Equalities\n";
        for (unsigned int i = 1 + _nineq + _nconstantIneq; i < 1 + _nineq + _nconstantIneq + _neq + _nconstantEq; i++) {
            ostr << (*_originalConstraints)[i].indexType + 1;
            if ((*_originalConstraints)[i].isConstant) {
                longstr = std::to_string((*_originalConstraints)[i].constantValue);
            }
            else {
                longstr = resultString[(*_originalConstraints)[i].indexNonconstant].get_function_string();
            }
            _add_linebreaks_to_gams_string(longstr);
            str = str + " " + longstr + " = 0";
            if ((*_originalConstraints)[i].name != "eq" + ostr.str()) {
                str = str + " \"" + (*_originalConstraints)[i].name + "\"";
            }
            str = str + ";\n";
            ostr.str("");
            ostr.clear();
            longstr.clear();
        }
        str = str + "\n";
    }
    aleFile << str;
    str.clear();

    if (writeRelaxationOnly && ((_nineqRelaxationOnly > 0) || (_neqRelaxationOnly > 0) || (_nconstantIneqRelOnly > 0) || (_nconstantEqRelOnly > 0))) {
        str = str + "relaxation only constraints:\n";
        // Relaxation-only inequalities
        if (_nineqRelaxationOnly > 0 || _nconstantIneqRelOnly > 0) {
            str = str + "#Relaxation-only inequalities\n";
            for (unsigned int i = 1 + _nineq + _nconstantIneq + _neq + _nconstantEq; i < 1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly; i++) {
                ostr << (*_originalConstraints)[i].indexType + 1;
                if ((*_originalConstraints)[i].isConstant) {
                    longstr = std::to_string((*_originalConstraints)[i].constantValue);
                }
                else {
                    longstr = resultString[(*_originalConstraints)[i].indexNonconstant].get_function_string();
                }
                _add_linebreaks_to_gams_string(longstr);
                str = str + " " + longstr + " <= 0";
                if ((*_originalConstraints)[i].name != "relOnlyIneq" + ostr.str()) {
                    str = str + " \"" + (*_originalConstraints)[i].name + "\"";
                }
                str = str + ";\n";
                ostr.str("");
                ostr.clear();
                longstr.clear();
            }
            str = str + "\n";
        }
        aleFile << str;
        str.clear();
        // Relaxation-only equalities
        if (_neqRelaxationOnly > 0 || _nconstantEqRelOnly > 0) {
            str = str + "#Relaxation-only equalities\n";
            for (size_t i = 1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly; i < 1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly + _neqRelaxationOnly + _nconstantEqRelOnly; i++) {
                ostr << (*_originalConstraints)[i].indexType + 1;
                if ((*_originalConstraints)[i].isConstant) {
                    longstr = std::to_string((*_originalConstraints)[i].constantValue);
                }
                else {
                    longstr = resultString[(*_originalConstraints)[i].indexNonconstant].get_function_string();
                }
                _add_linebreaks_to_gams_string(longstr);
                str = str + " " + longstr + " = 0";
                if ((*_originalConstraints)[i].name != "relOnlyEq" + ostr.str()) {
                    str = str + " \"name=" + (*_originalConstraints)[i].name + "\"";
                }
                str = str + ";\n";
                ostr.str("");
                ostr.clear();
                longstr.clear();
            }
            str = str + "\n";
        }
        aleFile << str;
        str.clear();
    }

    // Squash Inequalities
    if (_nineqSquash > 0 || _nconstantIneqSquash > 0) {
        str = str + "squashing constraints:\n";
        str = str + "#Squash inequalities\n";
        for (unsigned int i = 1 + _nineq + _nconstantIneq + _neq + _nconstantEq + _nineqRelaxationOnly + _nconstantIneqRelOnly + _neqRelaxationOnly + _nconstantEqRelOnly; i < _originalConstraints->size(); i++) {
            ostr << (*_originalConstraints)[i].indexType + 1;
            if ((*_originalConstraints)[i].isConstant) {
                longstr = std::to_string((*_originalConstraints)[i].constantValue);
            }
            else {
                longstr = resultString[(*_originalConstraints)[i].indexNonconstant].get_function_string();
            }
            _add_linebreaks_to_gams_string(longstr);
            str = str + " " + longstr + " <= 0";
            if ((*_originalConstraints)[i].name != "squashIneq" + ostr.str()) {
                str = str + " \"name=" + (*_originalConstraints)[i].name + "\"";
            }
            str = str + ";\n";
            ostr.str("");
            ostr.clear();
            longstr.clear();
        }
        str = str + "\n";
    }
    aleFile << str;
    str.clear();

#ifdef HAVE_GROWING_DATASETS
    aleFile << "objectivePerData:\n";
    // Objective per data
    aleFile << "#The sum over all objective per data functions,\n";
    aleFile << "#i.e., equal to the objective considering the full dataset stated below \n ";
    longstr = resultString[0].get_function_string();
    _add_linebreaks_to_gams_string(longstr);
    str = str + " " + longstr + " = 0;\n";
    aleFile << "  " << str << "\n";
    longstr.clear();
    str.clear();
#endif    // HAVE_GROWING_DATASETS

    aleFile << "objective:\n";
    // Objective function last
    aleFile << "#Objective function\n";
    longstr = resultString[0].get_function_string();
    _add_linebreaks_to_gams_string(longstr);
    aleFile << "  " << longstr << ";";
    longstr.clear();

    if (_DAGoutputFunctions.size() > 0) {
        // Outputs
        tmpSubgraph = _DAG.subgraph(_DAGoutputFunctions.size(), _DAGoutputFunctions.data());
        resultString.resize(_DAGoutputFunctions.size());
        _DAG.eval(tmpSubgraph, stringDummy, _DAGoutputFunctions.size(), _DAGoutputFunctions.data(), resultString.data(), _nvar, _DAGvars.data(), stringVars.data());
        std::vector<std::tuple<std::string, std::string, unsigned>> outputStrings(_noutputVariables + _nconstantOutputVariables);    // This vector will hold the output function string, name and index of each output
        // Get the outputs in correct order
        // Non-constant outputs first
        for (size_t i = 0; i < _noutputVariables; i++) {
            longstr = resultString[(*_nonconstantOutputs)[i].indexTypeNonconstant].get_function_string();
            _add_linebreaks_to_gams_string(longstr);
            outputStrings[(*_nonconstantOutputs)[i].indexType] = std::make_tuple(longstr, (*_nonconstantOutputs)[i].name, (*_nonconstantOutputs)[i].indexType + 1);
        }
        // Constant outputs second
        for (size_t i = 0; i < _nconstantOutputVariables; i++) {
            outputStrings[(*_constantOutputs)[i].indexType] = std::make_tuple(std::to_string((*_constantOutputs)[i].constantValue), (*_constantOutputs)[i].name, (*_constantOutputs)[i].indexType + 1);
        }
        str = str + "\n\noutputs:\n";
        str = str + "#Additional outputs\n";
        for (size_t i = 0; i < outputStrings.size(); i++) {
            str = str + " " + std::get<0>(outputStrings[i]);
            if (std::get<1>(outputStrings[i]) != "output" + std::to_string(std::get<2>(outputStrings[i]))) {
                str = str + " \"" + std::get<1>(outputStrings[i]) + "\"";
            }
            str = str + ";\n";
            longstr.clear();
        }
        aleFile << str;
        str.clear();
    }
}


/////////////////////////////////////////////////////////////////////////
// print MAiNGO header for other modeling language
void
MAiNGO::_print_MAiNGO_header_for_other_modeling_language(const WRITING_LANGUAGE writingLanguage, std::ofstream &file)
{

    std::string commentSign;

    switch (writingLanguage) {
        case LANG_GAMS:
            commentSign = "*";
            break;
        case LANG_ALE:
            commentSign = "#";
            break;
         default:    // GCOVR_EXCL_LINE
            throw MAiNGOException("Error printing MAiNGO header while writing model to file: unknown modeling language."); // GCOVR_EXCL_LINE
    }

    // This is not the same header as in function print_header()
    file << commentSign << " ------------------------------------------------------------------------------------------------------------------- " << commentSign << "\n";
    file << commentSign << "                                                                                                          /)_        " << commentSign << "\n";
    file << commentSign << "                                                                                                         //\\  `.     " << commentSign << "\n";
    file << commentSign << "                                                                                                  ____,.//, \\   \\    " << commentSign << "\n";
    file << commentSign << "                           This file was generated by MAiNGO " << get_version() << "                          _.-'         `.`.  \\   " << commentSign << "\n";
    file << commentSign << "                                                                                            ,'               : `..\\  " << commentSign << "\n";
    file << commentSign << "                                                                                           :         ___      :      " << commentSign << "\n";
    file << commentSign << " Copyright (c) 2019 Process Systems Engineering (AVT.SVT), RWTH Aachen University         :       .'     `.    :     " << commentSign << "\n";
    file << commentSign << "                                                                                         :         `.    /     ;     " << commentSign << "\n";
    file << commentSign << " MAiNGO and the accompanying materials are made available under the                     :           /   /     ;      " << commentSign << "\n";
    file << commentSign << " terms of the Eclipse Public License 2.0 which is available at                         :        __.'   /     :       " << commentSign << "\n";
    file << commentSign << " http://www.eclipse.org/legal/epl-2.0.                                                 ;      /       /     :        " << commentSign << "\n";
    file << commentSign << "                                                                                       ;      `------'     /         " << commentSign << "\n";
    file << commentSign << " SPDX-License-Identifier: EPL-2.0                                                      :                  :          " << commentSign << "\n";
    file << commentSign << " Authors: Dominik Bongartz, Jaromil Najman, Susanne Sass, Alexander Mitsos             \\                 /           " << commentSign << "\n";
    file << commentSign << "                                                                                        `.             .`            " << commentSign << "\n";
    file << commentSign << " Please provide all feedback and bugs to the developers.                                  '-._     _.-'              " << commentSign << "\n";
    file << commentSign << " E-mail: MAiNGO@avt.rwth-aachen.de                                                            `'''`                  " << commentSign << "\n";
    file << commentSign << " ------------------------------------------------------------------------------------------------------------------- " << commentSign << "\n\n";
}