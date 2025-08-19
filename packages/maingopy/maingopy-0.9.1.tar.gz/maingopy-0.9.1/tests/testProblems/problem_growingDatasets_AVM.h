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

namespace dataAVM {
// Data pairs: inputValues and outputValues must have the same length
const std::vector<double> inputValues = {
    1.0,
    1.0,
    1.0};
const std::vector<double> outputValues = {
    1.0,
    0.6,
    0.0};
}    // namespace dataAVM

/**
* @class Model
* @brief Problem for testing the handling of additional auxiliary variables in MAiNGO with growing datasets
*
* To allow for adding auxiliary variables, we need a nonlinear dependency on at least 2 
* optimization variables which occurs at least 2 times.
* Thus, this class defines a parameter estimation problem for optimizing the slope and offset
* of an affine linear function
* output = slope1*slope2 * input + slope1*slope2
* based on up to three data points, namely (1,1), (1,0.6), and (1,0).
*
*/
class Model_growing_AVM: public maingo::MAiNGOmodel {

  public:
    /**
        * @brief Default constructor
        */
    Model_growing_AVM();

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
    size_t _noOfDataPoints;
};


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model_growing_AVM::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    // Required: Define optimization variables by specifying lower bound, upper bound (, optionally variable type, branching priority and a name)
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0., 5.), maingo::VT_CONTINUOUS, "slope/offset Part I"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0., 5.), maingo::VT_CONTINUOUS, "slope/offset Part II"));

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model_growing_AVM::get_initial_point()
{

    // Here you can provide an initial point for the local search
    std::vector<double> initialPoint;

    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model_growing_AVM::Model_growing_AVM()
{

    _noOfDataPoints = dataAVM::inputValues.size();
}


//////////////////////////////////////////////////////////////////////////
// evaluate the model
maingo::EvaluationContainer
Model_growing_AVM::evaluate(const std::vector<Var> &optVars)
{

    // Rename inputs
    Var slope1 = optVars.at(0);    // We use .at() here to get a vector exception if a wrong access occurs
    Var slope2 = optVars.at(1);    // We use .at() here to get a vector exception if a wrong access occurs

    // Model prediction of linear function
    std::vector<Var> predictedValues;
    for (auto inputValue : dataAVM::inputValues) {
        predictedValues.push_back(slope1 * slope2 * inputValue + slope1 * slope2);
    }

    // Prepare output
    maingo::EvaluationContainer result;

    // Objective given as the mean squared error:
    Var se          = 0;
    Var se_per_data = 0;
    for (auto i = 0; i < _noOfDataPoints; i++) {
        se_per_data = sqr(predictedValues[i] - dataAVM::outputValues[i]);
        se += se_per_data;
        result.objective_per_data.push_back(se_per_data);
    }

    result.objective = se;
    result.output.push_back(maingo::OutputVariable("slope = offset", slope1 * slope2));

    return result;
}
