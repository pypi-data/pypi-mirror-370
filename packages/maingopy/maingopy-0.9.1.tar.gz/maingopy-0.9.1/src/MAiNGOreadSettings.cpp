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
#include "settings.h"

#include <fstream>
#include <sstream>
#include <string>


using namespace maingo;


/////////////////////////////////////////////////////////////////////////
// reads settings from file
void
MAiNGO::read_settings(const std::string& settingsFileName)
{

    std::ifstream file;
    file.open(settingsFileName);
    if (file.is_open()) {

        std::string line;
        std::string word;
        double number;
        bool firstLine = true;
        while (std::getline(file, line)) {    // Read file line by line
            if (firstLine) {
                // Check for BOM in UTF 8, BOM is ALWAYS at the beginning of a file -- NOTE: We only correctly handle UTF 8 setting files!
                if (line.length() >= 3) {
                    if (line[0] == (char)0XEF && line[1] == (char)0XBB && line[2] == (char)0XBF) {
                        line.erase(0, 3);
                    }
                }
                firstLine = false;
            }
            // If the line is not a comment, proceed (\r is for carriage return)
            if ((line.find_first_not_of(' ') != std::string::npos) && !line.empty() && line[0] != '#' && line[0] != '\r') {
                std::istringstream iss(line);    // This allows access to line as real std::string
                iss >> word;
                iss >> number;
                set_option(word, number);
            }
        }
        _logger->save_settings_file_name(settingsFileName, true);
    }
    else {    // File not found
        _logger->save_settings_file_name(settingsFileName, false);
    }

    file.close();
}