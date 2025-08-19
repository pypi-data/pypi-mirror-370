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

#include "logger.h"
#include "MAiNGOException.h"

#include <fstream>
#include <memory>
#include <sstream>


using namespace maingo;


/////////////////////////////////////////////////////////////////////////
Logger::Logger(const std::shared_ptr<Settings> settings):
        _settings(settings)
{}


/////////////////////////////////////////////////////////////////////////
// helper function for print_message which handels printing to the right logging destinations
void
Logger::_print_message_if_verbosity_exceeds_needed(const std::string& message, const VERB verbosityNeeded, const VERB verbosityGiven)
{

    switch (_settings->loggingDestination) {
        case LOGGING_OUTSTREAM:
            // Print to _outStream only
            if (verbosityGiven >= verbosityNeeded) {
                (*_outStream) << message << std::flush;
            }
            break;
        case LOGGING_FILE:
            // Save message in log queue to be written later
            if (verbosityGiven >= verbosityNeeded) {
                babLine.push(message);
            }
            break;
        case LOGGING_FILE_AND_STREAM:
            // Print and write
            if (verbosityGiven >= verbosityNeeded) {
                (*_outStream) << message << std::flush;
                babLine.push(message);
            }
            break;
        case LOGGING_NONE:
        default:
            // Don't print or write
            break;
    }
}


/////////////////////////////////////////////////////////////////////////
// writes a message to outstream and possibly bablog
void
Logger::print_message(const std::string& message, const VERB verbosityNeeded, const SETTING_NAMES settingType)
{
    const VERB verbosityGiven = _get_verb(settingType);
    _print_message_if_verbosity_exceeds_needed(message, verbosityNeeded, verbosityGiven);
}


/////////////////////////////////////////////////////////////////////////
// writes a message to outstream and possibly bablog
void
Logger::print_message(const std::string& message, const VERB verbosityNeeded, const SETTING_NAMES settingType, const SETTING_NAMES optSettingType1)
{
    const VERB verbosityGiven = _get_max_verb(settingType, optSettingType1);
    _print_message_if_verbosity_exceeds_needed(message, verbosityNeeded, verbosityGiven);
}


/////////////////////////////////////////////////////////////////////////
// writes a message to outstream and possibly bablog
void
Logger::print_message(const std::string& message, const VERB verbosityNeeded, const SETTING_NAMES settingType, const SETTING_NAMES optSettingType1, const SETTING_NAMES optSettingType2)
{
    const VERB verbosityGiven = _get_max_verb(settingType, optSettingType1, optSettingType2);
    _print_message_if_verbosity_exceeds_needed(message, verbosityNeeded, verbosityGiven);
}


/////////////////////////////////////////////////////////////////////////
// get verbosities corresponding to the given setting name
VERB
Logger::_get_verb(const SETTING_NAMES settingType) const
{

    VERB verbosity = VERB_NONE;

    switch (settingType) {
        case LBP_VERBOSITY:
            verbosity = _settings->LBP_verbosity;
            break;
        case UBP_VERBOSITY:
            verbosity = _settings->UBP_verbosity;
            break;
        case BAB_VERBOSITY:
            verbosity = _settings->BAB_verbosity;
            break;
        default:
            break;
    }

    return verbosity;
}


/////////////////////////////////////////////////////////////////////////
// get maximum verbosities according to the given setting names
VERB
Logger::_get_max_verb(const SETTING_NAMES settingType, const SETTING_NAMES optSettingType1) const
{

    const std::vector<SETTING_NAMES> verbEnums = {settingType, optSettingType1};
    std::vector<VERB> verbosities              = {VERB_NONE, VERB_NONE};

    for (int i = 0; i < verbEnums.size(); i++) {

        switch (verbEnums[i]) {
            case LBP_VERBOSITY:
                verbosities[i] = _settings->LBP_verbosity;
                break;
            case UBP_VERBOSITY:
                verbosities[i] = _settings->UBP_verbosity;
                break;
            case BAB_VERBOSITY:
                verbosities[i] = _settings->BAB_verbosity;
                break;
            default:
                break;
        }
    }

    const VERB maxVerb = std::max(verbosities[0], verbosities[1]);

    return maxVerb;
}


/////////////////////////////////////////////////////////////////////////
// get maximum verbosities according to the given setting names
VERB
Logger::_get_max_verb(const SETTING_NAMES settingType, const SETTING_NAMES optSettingType1, const SETTING_NAMES optSettingType2) const
{

    const std::vector<SETTING_NAMES> verbEnums = {settingType, optSettingType1, optSettingType2};
    std::vector<VERB> verbosities              = {VERB_NONE, VERB_NONE, VERB_NONE};

    for (int i = 0; i < 3; i++) {

        switch (verbEnums[i]) {
            case LBP_VERBOSITY:
                verbosities[i] = _settings->LBP_verbosity;
                break;
            case UBP_VERBOSITY:
                verbosities[i] = _settings->UBP_verbosity;
                break;
            case BAB_VERBOSITY:
                verbosities[i] = _settings->BAB_verbosity;
                break;
            default:
                break;
        }
    }

    const VERB maxVerb = std::max(verbosities[2], std::max(verbosities[0], verbosities[1]));

    return maxVerb;
}


/////////////////////////////////////////////////////////////////////////
// writes a message to outstream only without asking for vorbosities
void
Logger::print_message_to_stream_only(const std::string& message)
{

    const LOGGING_DESTINATION givenOutstreamVerbosity = _settings->loggingDestination;

    if ((givenOutstreamVerbosity == LOGGING_FILE_AND_STREAM) || (givenOutstreamVerbosity == LOGGING_OUTSTREAM)) {
        (*_outStream) << message << std::flush;
    }
}


/////////////////////////////////////////////////////////////////////////
// creates the log file
void
Logger::create_log_file() const
{
    const LOGGING_DESTINATION givenOutstreamVerbosity = _settings->loggingDestination;

    if ((givenOutstreamVerbosity == LOGGING_FILE_AND_STREAM) || (givenOutstreamVerbosity == LOGGING_FILE)) {
        std::ofstream logFile;
        logFile.open(logFileName, std::ios::out);
        logFile.close();
    }
}


/////////////////////////////////////////////////////////////////////////
// creates the csv file
void
Logger::create_iterations_csv_file(const bool writeCsv) const
{
    if (writeCsv) {
        std::ofstream iterationsFile(csvIterationsName, std::ios::out);

        iterationsFile << " Iters,"
#ifdef MAiNGO_DEBUG_MODE
                       << " NodeId,"
                       << " NodeLBD,"
#endif
                       << " LBD, "
                       << " UBD,"
                       << " NodesLeft,"
                       << " AbsGap,"
                       << " RelGap,"
                       << " CPU,"
					   << " Wall" << std::endl;

        iterationsFile.close();
    }
}


/////////////////////////////////////////////////////////////////////////
// writes all lines currently stored in babLine to logFile
void
Logger::write_all_lines_to_log(const std::string& errorMessage)
{
    const LOGGING_DESTINATION givenOutstreamVerbosity = _settings->loggingDestination;

    if ((givenOutstreamVerbosity == LOGGING_FILE_AND_STREAM) || (givenOutstreamVerbosity == LOGGING_FILE)) {
        std::ofstream logFile;
        logFile.open(logFileName, std::ios::app);
        while (babLine.size() > 0) {
            logFile << babLine.front();
            babLine.pop();
        }
        if (!errorMessage.empty()) {
            logFile << errorMessage << std::endl;
        }
        logFile.close();
    }
}


/////////////////////////////////////////////////////////////////////////
// writes all lines currently stored in babLine to logFile
void
Logger::write_all_iterations_to_csv()
{
    std::ofstream iterationsFile(csvIterationsName, std::ios::app);

    while (babLineCsv.size() > 0) {
        iterationsFile << babLineCsv.front();
        babLineCsv.pop();
    }

    iterationsFile.close();
}


/////////////////////////////////////////////////////////////////////////
// saves a proper string when a user wants to read in a setting file
void
Logger::save_settings_file_name(const std::string& fileName, const bool fileFound)
{

    // User wants to read in a file
    _nSettingFiles++;
    const int mapNumber = -1 * _nSettingFiles;
    std::string str     = "";
    if (fileFound) {
        // If file has been found, generate string
        str = "\n  Read settings from file " + fileName + ".";
    }
    else {
        // If file has not been found generate a different string
        if (fileName == "MAiNGOSettings.txt") {
            str = "\n  Warning: Could not open settings file with default name " + fileName + ".\n";
        }
        else {
            str = "\n  Warning: Could not open settings file " + fileName + ".\n";
        }
        str += "           Proceeding with default settings.";
    }
    // Then insert this string at a proper position in the map
    _userSetSettings[mapNumber] = str;
}


/////////////////////////////////////////////////////////////////////////
// save a user-set setting in map
void
Logger::save_setting(const SETTING_NAMES settingName, const std::string& str)
{

    switch (settingName) {
        case UNKNOWN_SETTING: {
            int wrongSettings = static_cast<int>(settingName);
            while (_userSetSettings.find(wrongSettings) != _userSetSettings.end()) {
                wrongSettings++;
            }
            _userSetSettings[wrongSettings] = str;
            break;
        }
        default:
            // Replace/insert the new setting string
            _userSetSettings[static_cast<int>(settingName)] = str;
            break;
    }
}


/////////////////////////////////////////////////////////////////////////
// print and/or write user-set settings
void
Logger::print_settings(const VERB verbosityNeeded, const SETTING_NAMES settingType)
{

    // First check if any setting was changed at all
    if (!_userSetSettings.empty()) {
        bool someSettingChanged = (_userSetSettings.rbegin()->first > 0);    // This checks if there is at least one entry with a positive key, since these belong to the actual settings


        // If so, we print two additional lines two frame the actual settings (otherwise, we only give output about potential read attempts to empty or non-existing settings files
        if (someSettingChanged) {
            _userSetSettings[0] = "Settings set by the user:";
        }
        std::string str = "";
        for (std::map<int, std::string>::iterator it = _userSetSettings.begin(); it != _userSetSettings.end(); ++it) {
            if (it->first > 0) {
                str += "    " + (it->second) + "\n";
            }
            else {
                str += "  " + (it->second) + "\n";
            }
        }
        if (someSettingChanged) {
            str += "  Done.\n";
        }
        print_message(str, verbosityNeeded, settingType);
    }
}


/////////////////////////////////////////////////////////////////////////
// print and/or write user-set settings
void
Logger::print_settings(const VERB verbosityNeeded, const SETTING_NAMES settingType, const SETTING_NAMES optSettingType1)
{

    // First check if any setting was changed at all
    if (!_userSetSettings.empty()) {
        bool someSettingChanged = (_userSetSettings.rbegin()->first > 0);    // This checks if there is at least one entry with a positive key, since these belong to the actual settings


        // If so, we print two additional lines two frame the actual settings (otherwise, we only give output about potential read attempts to empty or non-existing settings files
        if (someSettingChanged) {
            _userSetSettings[0] = "Settings set by the user:";
        }
        std::string str = "";
        for (std::map<int, std::string>::iterator it = _userSetSettings.begin(); it != _userSetSettings.end(); ++it) {
            if (it->first > 0) {
                str += "    " + (it->second) + "\n";
            }
            else {
                str += "  " + (it->second) + "\n";
            }
        }
        if (someSettingChanged) {
            str += "  Done.\n";
        }
        print_message(str, verbosityNeeded, settingType, optSettingType1);
    }
}


/////////////////////////////////////////////////////////////////////////
// print and/or write user-set settings
void
Logger::print_settings(const VERB verbosityNeeded, const SETTING_NAMES settingType, const SETTING_NAMES optSettingType1, const SETTING_NAMES optSettingType2)
{

    // First check if any setting was changed at all
    if (!_userSetSettings.empty()) {
        bool someSettingChanged = (_userSetSettings.rbegin()->first > 0);    // This checks if there is at least one entry with a positive key, since these belong to the actual settings


        // If so, we print two additional lines two frame the actual settings (otherwise, we only give output about potential read attempts to empty or non-existing settings files
        if (someSettingChanged) {
            _userSetSettings[0] = "Settings set by the user:";
        }
        std::string str = "";
        for (std::map<int, std::string>::iterator it = _userSetSettings.begin(); it != _userSetSettings.end(); ++it) {
            if (it->first > 0) {
                str += "    " + (it->second) + "\n";
            }
            else {
                str += "  " + (it->second) + "\n";
            }
        }
        if (someSettingChanged) {
            str += "  Done.\n";
        }
        print_message(str, verbosityNeeded, settingType, optSettingType1, optSettingType2);
    }
}


/////////////////////////////////////////////////////////////////////////
// print and/or write vector in standardized format
void
Logger::print_vector(const unsigned length, const std::vector<double>& vec, const std::string& preString, const VERB verbosityNeeded, const SETTING_NAMES settingType)
{
    if (_get_verb(settingType) >= verbosityNeeded) {
        if (vec.size() < length) {
            throw MAiNGOException("Given length is greater than the actual size of the given vec");
        }
        else {
            std::ostringstream outstr;
            outstr << preString << std::endl;
            for (unsigned int i = 0; i < length; i++) {
                outstr << "   x(" << i << "): " << vec[i] << std::endl;
            }
            print_message(outstr.str(), verbosityNeeded, settingType);
        }
    }
}


/////////////////////////////////////////////////////////////////////////
// clear logging information
void
Logger::clear()
{
    babLine            = std::queue<std::string>();
    babLineCsv         = std::queue<std::string>();
    reachedMinNodeSize = false;
}