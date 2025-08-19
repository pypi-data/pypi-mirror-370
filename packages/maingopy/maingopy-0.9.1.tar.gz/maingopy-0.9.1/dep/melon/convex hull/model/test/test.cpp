/**********************************************************************************
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
* @brief File implementing a test for the convex hull module.
*
**********************************************************************************/

#include <iostream>
#include <filesystem>
#include <vector>
#include <string>

#include "convexhull.h"

namespace fs = std::filesystem;
using namespace melon;


int main(int argc, char** argv)
{
	try {

		std::vector<double> input{ 1.5, -2.0 };
		std::vector<double> expected{};
		std::vector<double> result{};
		std::vector<double> error{};

		std::cout << "---\n";
		std::cout << "Test convex hull.\n";
		std::cout << "---" << std::endl;

		// Load model
		std::cout << "\nLoad model.\n";
		fs::path modelPath{ fs::path{__FILE__}.parent_path() };
		ConvexHull<double> hull{ modelPath.string(), "testConvexHull" };
		std::cout << "Loading successful." << std::endl;

		// Evaluate constraints
		expected = { -4.6786465205886065, -4.396340448451905, -4.890897480663698, -3.085966704231039, 0.13719785251177674, -0.45537916353622787, 0.04232145767458606 };
		result = hull.generate_constraints(input);
		error = result - expected;
		for (std::size_t i{ 0 }; i < error.size(); ++i) {
			error[i] = abs(error[i]);
		}

		std::cout << "\nEvaluate first constraint at (" << input[0] << ", " << input[1] << ").\n";
		std::cout << "Expected: " << expected[0] << "\n";
		std::cout << "Result: " << result[0] << "\n";
		std::cout << "Error: " << error[0] << std::endl;

		std::cout << "\nEvaluate last constraint at (" << input[0] << ", " << input[1] << ").\n";
		std::cout << "Expected: " << expected[expected.size()-1] << "\n";
		std::cout << "Result: " << result[result.size()-1] << "\n";
		std::cout << "Error: " << error[error.size()-1] << std::endl;

		std::cout << std::endl;
		std::cout << "Note: The expected results are with the Python library SciPy. Small deviations are expected." << std::endl;

	}
	catch (std::exception &e) {
		std::cerr << std::endl
			<< "  Encountered exception:" << std::endl
			<< e.what() << std::endl;
	}
	catch (...) {
		std::cerr << std::endl
			<< "  Encountered an unknown fatal error. Terminating." << std::endl;
	}
}