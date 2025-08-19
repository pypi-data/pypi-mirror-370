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
#include "gp.h"


/**
* @class Model
* @brief Class defining the actual model implemented by the user
*
* This class is used by the user to implement the model
*/
class Model: public maingo::MAiNGOmodel {

  public:
    Model();

    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars);
    std::vector<maingo::OptimizationVariable> get_variables();
    std::vector<double> get_initial_point();

  private:
    melon::GaussianProcess<Var> _gp;
};


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model::get_variables()
{
    std::vector<maingo::OptimizationVariable> variables;

    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-3, 3), maingo::VT_CONTINUOUS, "x"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-3, 3), maingo::VT_CONTINUOUS, "y"));

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

Model::Model()
{

    // load GP from file
    const std::string filePath = "";    // Define a file path where the GP data is saved. If not defined, GP data should be in Release folder of the project
    const std::string netName  = "testGP";
    _gp.load_model(filePath, netName, melon::MODEL_FILE_TYPE::JSON);    // Read in network parameters from JSON file
}

maingo::EvaluationContainer
Model::evaluate(const std::vector<Var> &optVars)
{
    Var mu, variance, sigma;

    std::vector<Var> X = optVars;    // inputs of GP are the optimization variables, i.e., optVars

    // Prepare output
    maingo::EvaluationContainer result;

    mu = _gp.calculate_prediction_reduced_space(X);    // compute prediction of GP
                                                       //variance = _gp.calculate_variance_reduced_space(X) ;         // compute variance of GP
                                                       //sigma = sqrt(variance) ;									  // compute standard deviaton of GP

    // Objective given as the prediction or standard deviation of GP
    result.objective = mu;
    //result.objective = mu + sigma;

    return result;
}