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
* @brief File implementing a test for the multifidelity Gaussian process module.
*
***/

#include <iostream>
#include <filesystem>
#include <vector>
#include <string>

#include "mulfilGpData.h"
#include "mulfilGpParser.h"
#include "mulfilGp.h"

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
		std::cout << "Test multifidelity Gaussian process.\n";
		std::cout << "---" << std::endl;

		// Load model
		std::cout << "\nLoad model.\n";
		fs::path modelPath{ fs::path{__FILE__}.parent_path()};
		MulfilGp<double> mulfilGp{ modelPath.string(), "testMulfilGp" };
		std::cout << "Loading successful." << std::endl;

		// Evaluate low fidelity mean
		expected = -0.9611433781683445;
		result = mulfilGp.calculate_low_prediction_reduced_space(input);
		error = abs(result - expected);

		std::cout << "\nEvaluate low fidelity mean at (" << input[0] << ", " << input[1] << ").\n";
		std::cout << "Expected: " << expected << "\n";
		std::cout << "Result: " << result << "\n";
		std::cout << "Error: " << error << std::endl;

		// Evaluate low fidelity variance
		expected = 0.47916529575013556;
		result = mulfilGp.calculate_low_variance_reduced_space(input);
		error = abs(result - expected);

		std::cout << "\nEvaluate low fidelity variance at (" << input[0] << ", " << input[1] << ").\n";
		std::cout << "Expected: " << expected << "\n";
		std::cout << "Result: " << result << "\n";
		std::cout << "Error: " << error << std::endl;

		// Evaluate high fidelity mean
		expected = 0.042740436911117285;
		result = mulfilGp.calculate_high_prediction_reduced_space(input);
		error = abs(result - expected);

		std::cout << "\nEvaluate high fidelity mean at (" << input[0] << ", " << input[1] << ").\n";
		std::cout << "Expected: " << expected << "\n";
		std::cout << "Result: " << result << "\n";
		std::cout << "Error: " << error << std::endl;

		// Evaluate high fidelity variance
		expected = 0.579790436080657;
		result = mulfilGp.calculate_high_variance_reduced_space(input);
		error = abs(result - expected);

		std::cout << "\nEvaluate high fidelity variance at (" << input[0] << ", " << input[1] << ").\n";
		std::cout << "Expected: " << expected << "\n";
		std::cout << "Result: " << result << "\n";
		std::cout << "Error: " << error << std::endl;
	}

	catch (std::exception& e) {
		std::cerr << std::endl << "  Encountered exception:" << std::endl << e.what() << std::endl;
	}

	catch (...) {
		std::cerr << std::endl << "  Encountered an unknown fatal error. Terminating." << std::endl;
	}

	return 0;
}