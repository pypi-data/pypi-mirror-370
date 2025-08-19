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
class Model_ex8_1_3: public maingo::MAiNGOmodel {

  public:
    /**
    * @brief Default constructor
    */
    Model_ex8_1_3();

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
Model_ex8_1_3::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    // Required: Define optimization variables by specifying lower bound, upper bound (, optionally variable type, branching priority and a name)
    // Some variables are missing bounds completely.

    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-9, 9), "x1"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-9, 9), "x2"));

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model_ex8_1_3::get_initial_point()
{

    //here you can provide an initial point for the local search
    std::vector<double> initialPoint;
    // GAMS file did not provide initial values for all variables
    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model_ex8_1_3::Model_ex8_1_3()
{

    // Initialize data if necessary:
}


//////////////////////////////////////////////////////////////////////////
// Evaluate the model
maingo::EvaluationContainer
Model_ex8_1_3::evaluate(const std::vector<Var> &optVars)
{

    // rename  inputs
    Var x1 = optVars[0];
    Var x2 = optVars[1];

    // Prepare output
    maingo::EvaluationContainer result; /*!< variable holding the actual result consisting of an objective, inequalities, equalities, relaxation only inequalities and relaxation only equalities */
    // objective function:
#ifndef HAVE_GROWING_DATASETS
    result.objective = -(-(1 + sqr(1 + x1 + x2) * (19 + 3 * sqr(x1) - 14 * x1 + 6 * x1 * x2 - 14 * x2 + 3 * sqr(x2))) * (30 + sqr(2 * x1 - 3 * x2) * (18 + 12 * sqr(x1) - 32 * x1 - 36 * x1 * x2 + 48 * x2 + 27 * sqr(x2))) - (0));
#else
    result.objective_per_data.push_back(-(-(1 + sqr(1 + x1 + x2) * (19 + 3 * sqr(x1) - 14 * x1 + 6 * x1 * x2 - 14 * x2 + 3 * sqr(x2))) * (30 + sqr(2 * x1 - 3 * x2) * (18 + 12 * sqr(x1) - 32 * x1 - 36 * x1 * x2 + 48 * x2 + 27 * sqr(x2))) - (0)));
#endif
    // inequalities (<=0):

    // equalities (=0):

    // relaxation only inequalities (<=0):

    // relaxation only equalities (=0):

    return result;
}
