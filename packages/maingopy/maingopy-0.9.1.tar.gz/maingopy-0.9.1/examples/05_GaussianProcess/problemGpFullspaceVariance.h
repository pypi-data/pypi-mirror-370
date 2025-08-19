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
    // External objects
    melon::GaussianProcess<Var> _gp;
};


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model::get_variables()
{
    std::vector<maingo::OptimizationVariable> variables;

    std::vector<std::string> variableNames;
    unsigned int numberOfVariables;
    std::vector<std::pair<double, double>> variableBounds;

    // add an optimization variable for every dimension of the problem

    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-3, 3), maingo::VT_CONTINUOUS, "x"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-3, 3), maingo::VT_CONTINUOUS, "y"));


    _gp.get_full_space_variables_variance(numberOfVariables, variableNames, variableBounds);
    for (size_t iVar = 0; iVar < numberOfVariables; ++iVar) {
        auto &bounds = variableBounds.at(iVar);
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(bounds.first, bounds.second), variableNames.at(iVar)));
    }


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

    std::vector<Var> input(optVars.begin(), optVars.begin() + _gp.get_input_dimension());    // inputs of GP are the optimization variables, i.e., optVars
    std::vector<Var> internalVariables(optVars.begin() + _gp.get_input_dimension(), optVars.end());
    std::vector<Var> constraints;

    // Prepare output
    maingo::EvaluationContainer result;

    variance = _gp.calculate_variance_full_space(input, internalVariables, constraints);    // compute variance of GP
    sigma    = sqrt(variance);                                                              // compute standard deviaton of GP

    result.objective = sigma;

    //equalities (=0) given as the circle equality with radius 1:
    for (auto constraint : constraints) {
        result.eq.push_back(constraint);
    }

    return result;
}