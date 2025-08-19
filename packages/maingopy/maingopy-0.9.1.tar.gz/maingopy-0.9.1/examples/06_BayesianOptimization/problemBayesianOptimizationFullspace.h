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
#include <tuple>    //std::tie

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

    // add an optimization variable for every dimension of the problem
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-3, 3), maingo::VT_CONTINUOUS, "x"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-3, 3), maingo::VT_CONTINUOUS, "y"));


    std::vector<std::string> variableNames;
    unsigned int numberOfVariables;
    std::vector<std::pair<double, double>> variableBounds;
    _gp.get_full_space_variables_prediction_and_variance(numberOfVariables, variableNames, variableBounds);
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

    //////////////////////////////////////////////////////////////////////////
    // evaluate the Gaussian process

    std::tie(mu, variance) = _gp.calculate_prediction_and_variance_full_space(input, internalVariables, constraints);
    sigma                  = sqrt(variance);    // compute standard deviaton of GP

    // equalities (=0) given as the circle equality with radius 1:
    for (auto constraint : constraints) {
        result.eq.push_back(constraint);
    }

    //////////////////////////////////////////////////////////////////////////
    // maximize the aquisition function.
    // note that the aquisition function tries to minimize the output of the Gp

    // reads out the current minimum of the training data outputs and sets this as the target
    const double fmin = _gp.get_minimum_of_training_data_outputs();

    // set kappa for lower confidence bound acquisition function
    const double kappa = 2;

    result.objective = -af_ei(mu, sigma, fmin);    // expected improvement aquisition function

    // result.objective = -af_pi(mu, sigma, fmin); // Probability of improvement

    // result.objective = af_lcb(mu, sigma, kappa); // minimize the lower confidence bound

    //////////////////////////////////////////////////////////////////////////
    // Additional output:
    result.output.push_back(maingo::OutputVariable("mu: ", mu));
    result.output.push_back(maingo::OutputVariable("sigma: ", sigma));
    result.output.push_back(maingo::OutputVariable("f min: ", fmin));
    result.output.push_back(maingo::OutputVariable("Expected improvement: ", af_ei(mu, sigma, fmin)));
    // result.output.push_back(maingo::OutputVariable("Probability of improvement: ", af_pi(mu, sigma, fmin)));
    result.output.push_back(maingo::OutputVariable("Lower confidence bound: ", af_lcb(mu, sigma, kappa)));


    return result;
}