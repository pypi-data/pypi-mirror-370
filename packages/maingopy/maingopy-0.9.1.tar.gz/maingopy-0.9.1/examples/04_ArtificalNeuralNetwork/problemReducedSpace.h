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

#include "MAiNGOmodel.h"

#include "ffNet.h"    //Include FeedForwardNet header to use Neural Networks


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

  private:
    melon::FeedForwardNet<Var> testNet;
    //It may be advantageous to store neural networks in vectors, making them iterable in for loops.
    //std::vector<FeedForwardNet<Var>> vectorOfNetworks;
};


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    // Required: Define optimization variables by specifying lower bound, upper bound (, optionally variable type, branching priority and a name)
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-3, 3), maingo::VT_CONTINUOUS, "x"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-3, 3), maingo::VT_CONTINUOUS, "y"));

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model::get_initial_point()
{

    //here you can provide an initial point for the local search
    std::vector<double> initialPoint;
    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model::Model()
{

    // load feed forward neural network from file
    const std::string filePath = "";    // Define a file path where the network data is saved. If not defined, network data should be in Release folder of the project
    const std::string netName  = "myTestANN";
    testNet.load_model(filePath, netName, melon::MODEL_FILE_TYPE::CSV);    // Read in network parameters from CSV file
                                                                           //testNet.load_model(filePath, netName, melon::MODEL_FILE_TYPE::XML); // Read in network parameters from XML file
}


//////////////////////////////////////////////////////////////////////////
// Evaluate the model
maingo::EvaluationContainer
Model::evaluate(const std::vector<Var> &optVars)
{

    // rename  inputs
    Var x = optVars[0];
    Var y = optVars[1];
    //create input to evaluate ANNs on as vector:
    std::vector<Var> input{x, y};


    // prepare output
    maingo::EvaluationContainer result;

    /*
	Evaluate FeedForwardNet with FeedForwardNet::calculate_prediction_reduced_space
	Keep in mind, return value is a vector, as it may be multidimensional
	*/
    result.objective = testNet.calculate_prediction_reduced_space(input).at(0);


    return result;
}