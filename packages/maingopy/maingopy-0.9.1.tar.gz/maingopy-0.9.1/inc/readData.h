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

#include <string>
#include <vector>
#include <fstream>
#include <sstream>


namespace maingo {

/**
    * @brief Function for reading semicolon-separated data from string
    *
    * @param[in] line is the string containing the data
    * @param[in,out] data is the one dimensional data read from the line
    * @param[in] headerIncluded indicates whether first field is ignored as it contains header information
    */
void read_data_from_line(const std::string& line, std::vector<double>& data, const bool headerIncluded)
{
    data.clear();
    double value;
    std::string tmp;
    std::istringstream stream(line);

    // First entry
    stream >> value;
    if (!headerIncluded) {
        data.push_back(value);
    }
    // Read all remaining entries
    while (std::getline(stream, tmp, ';')) {
        stream >> value;
        data.push_back(value);
    }
}

/**
    * @brief Function for reading semicolon-separated list of numbers from file which may include comments
    *
    * @param[in] fileName is the name of the file containing the data
    * @param[in] headerInFirstColumn indicates whether first entry is ignored as it contains header information
    * @param[in,out] data is the one dimensional data vector to be read
    * @param[out] boolean returned indicates whether data is successfully read into vector data
    */
bool read_vector_from_file(const std::string& fileName, const bool headerInFirstColumn, std::vector<double>& data)
{
    data.clear();

    std::ifstream file;
    file.open(fileName);
    if (file.is_open()) {

        std::string line;
        double value;
        bool firstLine = true;
        while (std::getline(file, line)) {    // Read file line by line
            // If the line is not a comment, proceed (\r is for carriage return)
            if ((line.find_first_not_of(' ') != std::string::npos) && !line.empty() && line[0] != '#' && line[0] != '\r') {
                read_data_from_line(line, data, headerInFirstColumn);
            }
        }
        file.close();

        if (data.size() < 1) {    // No data is read
            return false;
        }

    }
    else {
        return false;
    }

    return true;
}

/**
	* @brief Function for reading semicolon-separated, two dimensional data from file
    *
    * @param[in] fileName is the name of the file containing the data
    * @param[in] headerInFirstRow indicates whether first line is ignored as it contains header information
    * @param[in] headerInFirstColumn indicates whether first entry in each line is ignored as it contains header information
    * @param[in,out] data is the two dimensional data to be read
    * @param[out] boolean returned indicates whether data is successfully read into vector data
	*/
bool read_matrix_from_file(const std::string& fileName, const bool headerInFirstRow, const bool headerInFirstColumn, std::vector<std::vector<double>>& data)
{
    data.clear();
    std::vector<double> dataRow;

    std::ifstream file;
    file.open(fileName);
    if (file.is_open()) {

        std::string line;
        double value;
        bool firstLine = true;
        while (std::getline(file, line)) {    // Read file line by line
            if (firstLine && headerInFirstRow) {    // Exclude header
                firstLine = false;
            }
            else {    // Read data
                dataRow.clear();
                read_data_from_line(line, dataRow, headerInFirstColumn);
                data.push_back(dataRow);
            }
        }
        file.close();
    }
    else {
        return false;
    }

    return true;
}

}    // namespace maingo