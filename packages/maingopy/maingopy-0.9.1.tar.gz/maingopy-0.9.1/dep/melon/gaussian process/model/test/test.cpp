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
* @brief File implementing a test for the Gaussian process module.
*
***/

#include <iostream>
#include <filesystem>
#include <vector>
#include <string>

#include "gp.h"

namespace fs = std::filesystem;
using namespace melon;


int main(int argc, char** argv)
{
	try {

		std::vector<double> input{ 1.5, -2.0 };
		double expected{};
		double result{};
		double error{};

		std::cout << "---\n";
		std::cout << "Test Gaussian process.\n";
		std::cout << "---" << std::endl;

		// Load model
		std::cout << "\nLoad model.\n";
		fs::path modelPath{ fs::path{__FILE__}.parent_path() };
		GaussianProcess<double> gp{ modelPath.string(), "testGp" };
		std::cout << "Loading successful." << std::endl;

		// Evaluate mean
		expected = -1.525590634967063;
		result = gp.calculate_prediction_reduced_space(input);
		error = abs(result - expected);

		std::cout << "\nEvaluate mean at (" << input[0] << ", " << input[1] << ").\n";
		std::cout << "Expected: " << expected << "\n";
		std::cout << "Result: " << result << "\n";
		std::cout << "Error: " << error << std::endl;

		// Evaluate variance
		expected = 0.7921795860614791;
		result = gp.calculate_variance_reduced_space(input);
		error = abs(result - expected);

		std::cout << "\nEvaluate variance at (" << input[0] << ", " << input[1] << ").\n";
		std::cout << "Expected: " << expected << "\n";
		std::cout << "Result: " << result << "\n";
		std::cout << "Error: " << error << std::endl;

		std::cout << "\nNote: The expected results are computed with the Python library GPy. Small deviations are expected." << std::endl;
	}

	catch (std::exception& e) {
		std::cerr << std::endl << "  Encountered exception:" << std::endl << e.what() << std::endl;
	}

	catch (...) {
		std::cerr << std::endl << "  Encountered an unknown fatal error. Terminating." << std::endl;
	}

	return 0;
}