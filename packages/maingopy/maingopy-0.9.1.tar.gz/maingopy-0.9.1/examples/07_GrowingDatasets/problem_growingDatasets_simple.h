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

namespace data {
// Data pairs: inputValues and outputValues must have the same length
const std::vector<double> inputValues = {
    1.0,
    1.0,
    1.0};
const std::vector<double> outputValues = {
    1.0,
    0.6,
    0.0};
}    // end namespace data

/**
* @class Model
* @brief Simple test problem for MAiNGO with growing datasets
*
* This class defines a parameter estimation problem for optimizing the slope of a linear function
* output = slope * input through the origin and up to three data points, namely (1,1), (1,0.6), and (1,0).
* When using all data points, we expect optimal slope = 0.53
* as we optimize min_slope [(slope*1-1)^2 + (slope*1-0.6)^2 + (slope*1-0)^2].
* When using a single data point, we expect optimal slope = y value of the data point, and objective = 0.
* When using (1,0) and (1,0.6), we expect optimal slope = 0.3.
* When using (1,0) and (1,1.0), we expect optimal slope = 0.5.
* When using (1,0.6) and (1,1), we expect optimal slope = 0.8.
* To avoid MAiNGO passing this problem as a QP to CPLEX, we use sqroot(slope) as optimization variable.
* 
* Note that augmentation rule SCALING can not trigger augmentation and, thus, does not give convergence
* for this model due to overfitting. In particular, 1 data point can be fitted perfectly, while there is
* a deviation between predictions and data when using at least 2 data points.
*
*/
class Model: public maingo::MAiNGOmodel {

  public:
    Model();

    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars);
    std::vector<maingo::OptimizationVariable> get_variables();
    std::vector<double> get_initial_point();

  private:
    size_t _noOfDataPoints;
};


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;

    variables.push_back(maingo::OptimizationVariable( maingo::Bounds(0., 5.), maingo::VT_CONTINUOUS, "sqrt(slope)"));

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
// constructor for the model
Model::Model(){

    _noOfDataPoints = data::inputValues.size();
}


//////////////////////////////////////////////////////////////////////////
// evaluate the model
maingo::EvaluationContainer
Model::evaluate(const std::vector<Var> &optVars)
{

    // Rename inputs
    Var sqrt_slope = optVars.at(0);

    // Model prediction of linear function
    std::vector<Var> predictedValues;
    for (auto inputValue: data::inputValues){
        predictedValues.push_back(sqr(sqrt_slope)*inputValue);
    }

    // Prepare output
    maingo::EvaluationContainer result;

    // Objective given as the summed squared error:
    Var se = 0;
    Var se_per_data = 0;
    for (auto i = 0; i < _noOfDataPoints; i++){
        se_per_data = sqr(predictedValues[i] - data::outputValues[i]);
        se += se_per_data;
        result.objective_per_data.push_back(se_per_data);
    }

    result.objective = se;
	result.output.push_back(maingo::OutputVariable("slope", sqr(sqrt_slope)));

    return result;
}