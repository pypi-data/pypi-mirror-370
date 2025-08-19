/***
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file test.cpp
*
* @brief File implementing a test for the feedforward net module.
*
***/

#include <iostream>
#include <filesystem>
#include <vector>
#include <string>

#include "ffNet.h"

namespace fs = std::filesystem;
using namespace melon;


int main(int argc, char** argv)
{
	try {

		fs::path modelPath{ fs::path{__FILE__}.parent_path() / "networks" };
		std::vector<double> input{ 1.5, -2.0 };
		double expected{};
		double result{};
		double error{};

		// Network loaded from csv files
		std::cout << "---\n";
		std::cout << "1: Test feedforward network loaded from csv files.\n";
		std::cout << "---" << std::endl;

		// Load model
		std::cout << "\nLoad model.\n";
		FeedForwardNet<double> ffnetCsv{ modelPath.string(), "testFfnet", MODEL_FILE_TYPE::CSV };
		std::cout << "Loading successful." << std::endl;

		// Evaluate prediction
		expected = -0.530376585562241;
		result = ffnetCsv.calculate_prediction_reduced_space(input).at(0);
		error = abs(result - expected);

		std::cout << "\nEvaluate prediction at (" << input[0] << ", " << input[1] << ").\n";
		std::cout << "Expected: " << expected << "\n";
		std::cout << "Result: " << result << "\n";
		std::cout << "Error: " << error << std::endl;


		// Network loaded from xml file
		std::cout << "\n\n---\n";
		std::cout << "2: Test feedforward network loaded from xml file.\n";
		std::cout << "---" << std::endl;

		// Load model
		std::cout << "\nLoad model.\n";
		FeedForwardNet<double> ffnetXml{ modelPath.string(), "testFfnet", MODEL_FILE_TYPE::XML };
		std::cout << "Loading successful." << std::endl;

		// Evaluation
		expected = -0.7832478284835815;
		result = ffnetXml.calculate_prediction_reduced_space(input).at(0);
		error = abs(result - expected);

		std::cout << "\nEvaluate prediction at (" << input[0] << ", " << input[1] << ").\n";
		std::cout << "Expected: " << expected << "\n";
		std::cout << "Result: " << result << "\n";
		std::cout << "Error: " << error << std::endl;

		std::cout << "\nNote: The expected results are computed with Matlab and Keras, respectively. Small deviations are expected." << std::endl;
	}

	catch (std::exception& e) {
		std::cerr << std::endl << "  Encountered exception:" << std::endl << e.what() << std::endl;
	}

	catch (...) {
		std::cerr << std::endl << "  Encountered an unknown fatal error. Terminating." << std::endl;
	}

	return 0;
}
