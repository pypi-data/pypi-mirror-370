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


using Var = mc::FFVar;    // This allows us to write Var instead of mc::FFVar

/**
* @class Model
* @brief Class defining the actual model implemented by the user
*
* This class is used by the user to implement the model
*/
class Model_bin1: public maingo::MAiNGOmodel {

  public:
    /**
        * @brief Default constructor
        */
    Model_bin1();

    /**
    * @brief Main function used to evaluate the model and construct a directed acyclic graph
    *
    * @param[in] optVars is the optimization variables vector
    * @param[in] writeAdditionalOutput defines whether to write additional output
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
};


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model_bin1::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    // Required: Define optimization variables by specifying lower bound, upper bound (, optionally variable type, branching priority and a name)
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_BINARY, "x"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_BINARY, "y"));

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model_bin1::get_initial_point()
{
    // Here you can provide an initial point for the local search
    std::vector<double> initialPoint;
    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model_bin1::Model_bin1() {}

//////////////////////////////////////////////////////////////////////////
// Evaluate the model
maingo::EvaluationContainer
Model_bin1::evaluate(const std::vector<Var> &optVars)
{
    // Rename  inputs
    Var x = optVars[0];
    Var y = optVars[1];

    // Prepare output
    maingo::EvaluationContainer result; /*!< variable holding the actual result consisting of an objective, inequalities, equalities, relaxation only inequalities and relaxation only equalities */
    // Objective
#ifndef HAVE_GROWING_DATASETS
    result.objective = exp(4.5 * pow(x, 2) - 5 * x * y + pow(y, 2));
#else
    result.objective_per_data.push_back(exp(4.5 * pow(x, 2) - 5 * x * y + pow(y, 2)));
#endif

    return result;
}
