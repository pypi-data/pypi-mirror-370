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
#include "mulfilGp.h"


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
    melon::MulfilGp<Var> _mulfilGp;
};


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model::get_variables()
{
    std::vector<maingo::OptimizationVariable> variables;

    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0.0, 1.0), maingo::VT_CONTINUOUS, "x"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0.0, 1.0), maingo::VT_CONTINUOUS, "y"));

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
    const std::string folderPath = "modelData"; // Define a folder path where the multifidelity GP data is stored.
    _mulfilGp.load_model(folderPath, "", melon::MODEL_FILE_TYPE::JSON);
}

//////////////////////////////////////////////////////////////////////////
// function for constructing the optimization problem and defining outputs
maingo::EvaluationContainer
Model::evaluate(const std::vector<Var> &optVars)
{
    std::vector<Var> X = optVars;

    Var meanLow, stdLow, meanHigh, stdHigh;
    meanLow = _mulfilGp.calculate_low_prediction_reduced_space(X);
    stdLow   = sqrt(_mulfilGp.calculate_low_variance_reduced_space(X));
    meanHigh = _mulfilGp.calculate_high_prediction_reduced_space(X);
    stdHigh  = sqrt(_mulfilGp.calculate_high_variance_reduced_space(X));
    
    maingo::EvaluationContainer result;

    result.objective = meanHigh;

    result.output.push_back(maingo::OutputVariable("meanLow: ", meanLow));
    result.output.push_back(maingo::OutputVariable("stdLow: ", stdLow));
    result.output.push_back(maingo::OutputVariable("meanHigh: ", meanHigh));
    result.output.push_back(maingo::OutputVariable("stdHigh: ", stdHigh));

    return result;
}