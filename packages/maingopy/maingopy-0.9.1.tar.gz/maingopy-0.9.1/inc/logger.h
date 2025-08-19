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

#pragma once

#include "MAiNGOdebug.h"
#include "returnCodes.h"
#include "settings.h"

#include <iostream>
#include <map>
#include <memory>
#include <queue>
#include <vector>


namespace maingo {


/**
* @class Logger
* @brief This class contains all logging and output information
*
* This class is used for a central and proper storing of output and logging information.
*/
class Logger {


  public:
    /**
        * @brief Constructor.
        * @param[in] settings shared pointer to _maingoSettings
        */

    Logger(const std::shared_ptr<Settings> settings);

    /**
        * @brief The main function used for printing a given message and storing it in log and/or csv
        *
        * @param[in] message is the message to be printed or written
        * @param[in] settingType sets if the LBP, UBP or BAB verbosity should be used
        * @param[in] verbosityNeeded is the least verbosity needed for the message to be printed/written
        */
    void print_message(const std::string& message, const VERB verbosityNeeded, const SETTING_NAMES settingType);

    /**
        * @brief The main function used for printing a given message and storing it in log and/or csv
        *
        * @param[in] message is the message to be printed or written
        * @param[in] settingType sets if the LBP, UBP or BAB verbosity should be used
        * @param[in] verbosityNeeded is the least verbosity needed for the message to be printed/written
        * @param[in] optSettingType1 is an optinal argument that can be used if the logger needs to choose the maximum verbosity of two or three verbosity types
        */
    void print_message(const std::string& message, const VERB verbosityNeeded, const SETTING_NAMES settingType, const SETTING_NAMES optSettingType1);

    /**
        * @brief The main function used for printing a given message and storing it in log and/or csv
        *
        * @param[in] message is the message to be printed or written
        * @param[in] settingType sets if the LBP, UBP or BAB verbosity should be used
        * @param[in] verbosityNeeded is the least verbosity needed for the message to be printed/written
        * @param[in] optSettingType1 is an optinal argument that can be used if the logger needs to choose the maximum verbosity of two or three verbosity types
        * @param[in] optSettingType2 is an optinal argument that can be used if the logger needs to choose the maximum verbosity of three verbosity types
        */
    void print_message(const std::string& message, const VERB verbosityNeeded, const SETTING_NAMES settingType, const SETTING_NAMES optSettingType1, const SETTING_NAMES optSettingType2);

    /**
        * @brief Function used for printing a given message only to the stream specified in the Logger
        *
        * @param[in] message is the message to be printed
        */
    void print_message_to_stream_only(const std::string& message);

    /**
        *  @brief Sets output stream
        *
        *  @param[in] outputStream is the new output stream to be used by MAiNGO.
        */
    void set_output_stream(std::ostream* const outputStream) { _outStream = outputStream; }

    /**
        * @brief Function used for creating the log file
        *
        */
    void create_log_file() const;

    /**
        * @brief Function used for creating the csv file with information on the B&B iterations
        *
        * @param[in] writeCsv says whether to write the csv file
        */
    void create_iterations_csv_file(const bool writeCsv) const;

    /**
        * @brief Function used for writing all lines stored in queue babLine to log
        *
        * @param[in] errorMessage is a possible additional error message
        */
    void write_all_lines_to_log(const std::string& errorMessage = "");

    /**
        * @brief Function used for writing all iterations currently stored queue babLineCsv to csv
        */
    void write_all_iterations_to_csv();

    /**
        * @brief Function used for saving the names of setting files set by the user
        *
        * @param[in] fileName it the name of the file set by the user
        * @param[in] fileFound tells whether the wanted file has been found
        */
    void save_settings_file_name(const std::string& fileName, const bool fileFound);

    /**
        * @brief Function used for saving the user-set settings
        *
        * @param[in] settingName is the changed setting
        * @param[in] str is the corresponding string
        */
    void save_setting(const SETTING_NAMES settingName, const std::string& str);

    /**
        * @brief Function for printing and writing user-set settings
        *
        * @param[in] verbosityNeeded is the least verbosity needed for the message to be printed/written
        * @param[in] settingType sets if the LBP, UBP or BAB verbosity should be used
        */
    void print_settings(const VERB verbosityNeeded, const SETTING_NAMES settingType);

    /**
        * @brief Function for printing and writing user-set settings
        *
        * @param[in] verbosityNeeded is the least verbosity needed for the message to be printed/written
        * @param[in] settingType sets if the LBP, UBP or BAB verbosity should be used
        * @param[in] optSettingType1 is an optinal argument that can be used if the logger needs to choose the maximum verbosity of two or three verbosity types
        */
    void print_settings(const VERB verbosityNeeded, const SETTING_NAMES settingType, const SETTING_NAMES optSettingType1);

    /**
        * @brief Function for printing and writing user-set settings
        *
        * @param[in] verbosityNeeded is the least verbosity needed for the message to be printed/written
        * @param[in] settingType sets if the LBP, UBP or BAB verbosity should be used
        * @param[in] optSettingType1 is an optinal argument that can be used if the logger needs to choose the maximum verbosity of two or three verbosity types
        * @param[in] optSettingType2 is an optinal argument that can be used if the logger needs to choose the maximum verbosity of three verbosity types
        */
    void print_settings(const VERB verbosityNeeded, const SETTING_NAMES settingType, const SETTING_NAMES optSettingType1, const SETTING_NAMES optSettingType2);

    /**
        * @brief Prints any vector<double> in a standardized form
        *
        * @param[in] length is the length of the arrary if it is printed as a whole or the index of the last double that is written if not the whole vector is printed
        * @param[in] vec is the vector to be printed or written
        * @param[in] preString is a string to be printed/written before vec
        * @param[in] verbosityNeeded is the least verbosity needed for the message to be printed/written
        * @param[in] settingType sets if the LBP, UBP or BAB verbosity should be used
        */

    void print_vector(const unsigned length, const std::vector<double>& vec, const std::string& preString, const VERB verbosityNeeded, const SETTING_NAMES settingType);


    /**
        * @brief Clears all logging information
        */
    void clear();

    /**
        * @name Auxiliary public variables for storing output and logging information
        */
    /**@{*/
    std::queue<std::string> babLine{};                /*!< queue for storing lines of B&B output */
    std::queue<std::string> babLineCsv{};             /*!< queue for storing lines of B&B output for CSV file */
    std::string logFileName       = "maingo.log";     /*!< name of the txt file into which the log may be written */
    std::string csvIterationsName = "iterations.csv"; /*!< name of the csv file into which information on the individual B&B iterations may be written */
    bool reachedMinNodeSize;                          /*!< bool for saving information if minimum node size has been reached within B&B */
                                                      /**@}*/


  private:
    /**
        * @brief Gives the max verbosity from one to three three diffrent settingTypes
        *
        * @param[in] settingType sets if the LBP, UBP or BAB verbosity should be used
        */
    VERB _get_verb(const SETTING_NAMES settingType) const;

    /**
        * @brief Gives the max verbosity from one to three three diffrent settingTypes
        *
        * @param[in] settingType sets if the LBP, UBP or BAB verbosity should be used
        * @param[in] optSettingType1 is an optinal argument that can be used if the logger needs to choose the maximum verbosity of two or three verbosity types
        */
    VERB _get_max_verb(const SETTING_NAMES settingType, const SETTING_NAMES optSettingType1) const;

    /**
        * @brief Gives the max verbosity from one to three three diffrent settingTypes
        *
        * @param[in] settingType sets if the LBP, UBP or BAB verbosity should be used
        * @param[in] optSettingType1 is an optinal argument that can be used if the logger needs to choose the maximum verbosity of two or three verbosity types
        * @param[in] optSettingType2 is an optinal argument that can be used if the logger needs to choose the maximum verbosity of three verbosity types
        */
    VERB _get_max_verb(const SETTING_NAMES settingType, const SETTING_NAMES optSettingType1, const SETTING_NAMES optSettingType2) const;


    /**
        * @brief Helper function for printing a given message and storing it in log and/or csv
        *
        * @param[in] message is the message to be printed or written
        * @param[in] verbosityNeeded is the least verbosity needed for the message to be printed/written
        * @param[in] verbosityGiven is the verbosity settings that should be considered to decide whether the message should be printed
        */
    void _print_message_if_verbosity_exceeds_needed(const std::string& message, const VERB verbosityNeeded, const VERB verbosityGiven);

    /**
        * @name Private variable storing the output
        */
    /**@{*/
    std::ostream* _outStream    = &std::cout;    /*!< default MAiNGO output stream is set to std::cout */
    unsigned int _nSettingFiles = 0;             /*!< number of setting files from which the user has read, default is set to 0 */
    std::map<int, std::string> _userSetSettings; /*!< map holding settings set by the user */
    std::shared_ptr<Settings> _settings;         /*!< shared pointer to _maingoSettings*/
                                                 /**@}*/
};


}    // end namespace maingo
