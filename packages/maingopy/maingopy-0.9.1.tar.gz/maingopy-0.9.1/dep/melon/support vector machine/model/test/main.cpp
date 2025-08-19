/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file main.cpp
*
* @brief File implementing a test for the one_class_svm  module.
*
**********************************************************************************/

#include <one_class_svm.h>
#include <iostream>
#include <vector>

/////////////////////////////////////////////////////////////////////////////////////////////
// Main function of test
int main(int argc, char** argv)
{
  try {

		// ---------------------------------------------------------------------------------
		// 0: Create Network and define input
		// ---------------------------------------------------------------------------------

		

		// these points were manually calculated in pyhton using the extracted parameters
		// trained on banana_data
		std::vector<double> input1{ -1.99989899 ,-2.04 };
		std::vector<double> input2{ 2.59,  -1.98717172 };
		std::vector<double> input3{ -0.22131313 ,-1.61737374 };
		double expected_output1 = 1*-10.444907164819636;
		double expected_output2 = 1*-9.376704639020787; 
		double expected_output3 = 1*0.39374971448451035; 

		// ---------------------------------------------------------------------------------
		// 1: Test Network parsed from CSV file
		// ---------------------------------------------------------------------------------

		std::cout << "---------------------------------------------------------------------------------" << std::endl;
		std::cout << "1: Test Network parsed from .json file" << std::endl;
		std::cout << "---------------------------------------------------------------------------------" << std::endl;
		std::cout << std::endl;

		// Object construction from .json
		std::cout << "Construct OneClassSvm object from .json file" << std::endl;
		
		one_class_svm::OneClassSvm<double> constraint = {};
		constraint.load_parameters( "data", "one_class_svm_parameters", one_class_svm::JSON ); 
		std::cout << "Constructing object successful." << std::endl;

		std::cout << std::endl;


		// Evaluate constraint
		std::cout << "Evaluating some test points for banana dataset:" << std::endl << std::endl; 
		std::cout << "Evaluate constraint at [" << input1[0] << " , " << input1[1] << " ]" << std::endl; 
		std::cout << "Expected result: " << expected_output1 << std::endl;
		double result = constraint.calculate_prediction_reduced_space(input1); 
		std::cout << "Result: " << result << std::endl;
		std::cout << "Error: " << abs(result - expected_output1) << std::endl;
		std::cout << std::endl;
		std::cout << "Evaluate constraint at [" << input2[0] << " , " << input2[1] << " ]" << std::endl;
		std::cout << "Expected result: " << expected_output2 << std::endl;
	    result = constraint.calculate_prediction_reduced_space(input2);
		std::cout << "Result: " << result << std::endl;
		std::cout << "Error: " << abs(result - expected_output2) << std::endl;
		std::cout << std::endl;

		std::cout << "Evaluate constraint at [" << input3[0] << " , " << input3[1] << " ]" << std::endl;
		std::cout << "Expected result: " << expected_output3 << std::endl;
	    result = constraint.calculate_prediction_reduced_space(input3);
		std::cout << "Result: " << result << std::endl;
		std::cout << "Error: " << abs(result - expected_output3) << std::endl;
		std::cout << std::endl;

		std::cout << "Note: The expected results were computed in Python. Small varientions are expected." << std::endl;

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
