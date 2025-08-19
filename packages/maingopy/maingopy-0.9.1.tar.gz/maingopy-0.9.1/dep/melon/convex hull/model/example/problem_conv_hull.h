/**********************************************************************************
 * Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 * @file problem_conv_hull.h
 *
 * @brief File containing an Model class defining the convex hull.
 *
 **********************************************************************************/

#pragma once

#include "MAiNGOmodel.h"
#include "one_class_svm.h"
#include "ffNet.h"
#include <cstdlib>
#include <stdlib.h>
#include <string>
#include <vector>
#include <memory>
#include <nlohmann/json.hpp>
#include <iostream>
#include <fstream>
#include <exceptions.h>
using json = nlohmann::json;
using namespace std;
/**
* @class Model
* @brief Class defining the actual model implemented by the user
*
* This class is used by the user to implement the model
*/
class Model: public maingo::MAiNGOmodel {

  public:
    /**
        * @brief Default constructor
        */
    Model();

    /**
        * @brief Main function used to evaluate the model and construct a directed acyclic graph
        *
        * @param[in] optVars is the optimization variables vector
        */
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars);

    /**
        * @brief Function for getting optimization variables data
        */
    std::vector<maingo::OptimizationVariable> get_variables();

    /**
        * @brief Function for getting initial point data
        */
    std::vector<double> get_initial_point();

    void conv_hull(maingo::EvaluationContainer& result, std::vector<Var>x);

  private:

    // External objects
	one_class_svm::OneClassSvm<mc::FFVar> constraint; /*!< externally implemented object */
	FeedForwardNet<Var> testNet;
    long long  constraintVariableNumber = 0 ;
    long long  objVariableNumber;
	bool FULL_SPACE_OBJECTIVE; 
    int INPUT_DIM;
    double BOUNDS = 4; 
};


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model::Model()
{

    // Objective
    const std::string filePath = "current";
    const std::string netName = "model";

    testNet.load_feed_forward_net(filePath, netName, ANN_FILE_TYPE::XML); // Read in network parameters from CSV file


	if (std::getenv("FULL_SPACE_OBJECTIVE") != NULL) {
		std::string a = std::getenv("FULL_SPACE_OBJECTIVE"); 
		FULL_SPACE_OBJECTIVE = (a == "1") ? true : false; 
	}
	else FULL_SPACE_OBJECTIVE = false; 



	if (std::getenv("BOUNDS") != NULL){
		std::string a = std::getenv("BOUNDS"); 
		BOUNDS = atof(a.c_str()); 
	}
	std::cout << "\nThe following setting will be used for the one class svm: "; 
	std::cout << "\n\tFULL_SPACE_OBJECTIVE = " << FULL_SPACE_OBJECTIVE <<"\n"; 


    INPUT_DIM = 2;
}


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model::get_variables()
{
	//input variables
    std::vector<maingo::OptimizationVariable> variables;
	for (int i = 1; i <= INPUT_DIM; i++) {
		variables.push_back(maingo::OptimizationVariable(/*Variable bounds*/ maingo::Bounds(-BOUNDS, BOUNDS), /*Variable type*/ maingo::VT_CONTINUOUS, /*Variable name*/ "x"+std::to_string(i)));
	}

    unsigned int obj_variableNumber{0};

    if (FULL_SPACE_OBJECTIVE) {

        std::vector<std::string> obj_variableNames;
        std::vector<std::pair<double, double>> obj_variableBounds;
        testNet.get_full_space_variables(obj_variableNumber, obj_variableNames, obj_variableBounds);

        for (unsigned int i = 0; i < obj_variableNumber; ++i) {
            auto& bounds = obj_variableBounds.at(i);

            variables.push_back(maingo::OptimizationVariable(/*Variable bounds*/ maingo::Bounds(bounds.first, bounds.second), /*Variable type*/ maingo::VT_CONTINUOUS,  /*Variable name*/obj_variableNames.at(i)));
        }
    }

	objVariableNumber = obj_variableNumber;


    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model::get_initial_point()
{

    std::vector<double> initialPoint;


    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// evaluate the model
maingo::EvaluationContainer
Model::evaluate(const std::vector<Var> &optVars)
{

    maingo::EvaluationContainer result;
    std::vector<Var> input(optVars.begin(), optVars.begin() + INPUT_DIM);
    std::vector<Var> internal_equations;
    std::vector<Var> constraint_internalVariables(optVars.begin() + INPUT_DIM, optVars.begin()+INPUT_DIM+ constraintVariableNumber);
    std::vector<Var> obj_internalVariables(optVars.begin() + INPUT_DIM +constraintVariableNumber, optVars.begin() +INPUT_DIM+ constraintVariableNumber + objVariableNumber);

    if (FULL_SPACE_OBJECTIVE) {
        result.objective = testNet.calculate_prediction_full_space(input, obj_internalVariables,internal_equations).at(0);
        //result.objective = 2*input[0]+2*input[1];
    }
    else {
        //result.objective = 3*(1-input[0])*(1-input[0])*exp(-(input[0]*input[0]) - (input[0]+1)*(input[0]+1)) - 10*(input[0]/5 - input[0]*input[0]*input[0] - input[0]*input[0]*input[0]*input[0]*input[0])*exp(-input[0]*input[0]-input[0]*input[0])  - 1/3*exp(-(input[0]+1)*(input[0]+1) - input[1]*input[1]) -1.5*input[1];
        result.objective = testNet.calculate_prediction_reduced_space(input).at(0);
        //result.objective = 2*input[0]+2*input[1];

    }

    // Equalities for internal equations (=0)
    for (auto& c : internal_equations) {
		result.eq.push_back(c);
	}

    conv_hull(result,input);


    return result;
}

void Model::conv_hull(maingo::EvaluationContainer& result, std::vector<Var>x){
    json j;
    ifstream i("current/convex_hull.json");
    std::vector<std::vector<double>> A{};
    std::vector<double> b{};
    i >> j;


    json json_A = j["A"];
    for (json::iterator it = json_A.begin(); it != json_A.end(); it++) {
        A.push_back({});
        for (json::iterator jt = (*it).begin(); jt != (*it).end(); jt++) {
            A.back().push_back({ (*jt).get<double>() });
        }
    }

    json json_b = j["b"];
    for (json::iterator it = json_b.begin(); it != json_b.end(); it++) {
        for (json::iterator jt = (*it).begin(); jt != (*it).end(); jt++) {
            b.push_back((*jt).get<double>());
        }
    }

    for (int j = 0 ; j<A.size(); j++){
        auto a = A[j];
        Var ax = 0;
        for (int i = 0; i< a.size(); i++){
            ax = ax + a[i]*x[i];
        }
        result.ineq.push_back(ax+b[j]);
    }


}






