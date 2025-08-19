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
* @brief File implementing a test for the support vector machine module.
*
***/

#include <iostream>
#include <filesystem>
#include <vector>
#include <string>

#include "svm.h"

namespace fs = std::filesystem;
using namespace melon;


int main(int argc, char** argv)
{
	try {

		fs::path modelPath{ fs::path{__FILE__}.parent_path() };
		std::vector<double> input{ 1.5, -2.0 };
		double expected{};
		double result{};
		double error{};
		
		// Regression SVM
		std::cout << "---\n";
		std::cout << "1: Test regression support vector machine.\n";
		std::cout << "---" << std::endl;

		// Load model
		std::cout << "\nLoad model.\n";
		SupportVectorRegression<double> svmRegression{ modelPath.string(), "testSvmRegression" };
		std::cout << "Loading successful." << std::endl;

		// Evaluate prediction
		expected = -0.8378441630544555;
		result = svmRegression.calculate_prediction_reduced_space(input);
		error = abs(result - expected);

		std::cout << "\nEvaluate prediction at (" << input[0] << ", " << input[1] << ").\n";
		std::cout << "Expected: " << expected << "\n";
		std::cout << "Result: " << result << "\n";
		std::cout << "Error: " << error << std::endl;


		// One class SVM
		std::cout << "\n\n---\n";
		std::cout << "2: Test one class support vector machine.\n";
		std::cout << "---" << std::endl;

		// Load model
		std::cout << "\nLoad model.\n";
		SupportVectorMachineOneClass<double> svmOneClass{ modelPath.string(), "testSvmOneClass" };
		std::cout << "Loading successful." << std::endl;

		// Evaluate prediction
		expected = -28.41561667664624;
		result = svmOneClass.calculate_prediction_reduced_space(input);
		error = abs(result - expected);

		std::cout << "\nEvaluate prediction at (" << input[0] << ", " << input[1] << ").\n";
		std::cout << "Expected: " << expected << "\n";
		std::cout << "Result: " << result << "\n";
		std::cout << "Error: " << error << std::endl;

		std::cout << "\nNote: The expected results were computed with Scikit-learn. Small deviations are expected." << std::endl;
	}

	catch (std::exception &e) {
		std::cerr << std::endl << "  Encountered exception:" << std::endl << e.what() << std::endl;
	}

	catch (...) {
		std::cerr << std::endl << "  Encountered an unknown fatal error. Terminating." << std::endl;
	}

	return 0;
}
	