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

/**
* @class Model
* @brief Class defining the actual model implemented by the user
*
* This class is used by the user to implement the model
*/
class Model_SubdomainLB: public maingo::MAiNGOmodel {

  public:
    /**
		* @brief Default constructor
		*/
    Model_SubdomainLB();

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
    int a;
    int b;
    int c;
    int d;
};


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model_SubdomainLB::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    // Required: Define optimization variables by specifying lower bound, upper bound (, optionally variable type, branching priority and a name)
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-2.9, 2.9), maingo::VT_CONTINUOUS, "x"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-2.9, 2.9), maingo::VT_CONTINUOUS, "y"));

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model_SubdomainLB::get_initial_point()
{

    //here you can provide an initial point for the local search
    std::vector<double> initialPoint;
    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model_SubdomainLB::Model_SubdomainLB()
{
    a = 1;
    b = 5;
    c = 3;
    d = 10;
}


//////////////////////////////////////////////////////////////////////////
// Evaluate the model
maingo::EvaluationContainer
Model_SubdomainLB::evaluate(const std::vector<Var> &optVars)
{

    // rename  inputs
    Var x = optVars[0];
    Var y = optVars[1];

    Var temp_1 = sqr(a - x) * exp(-sqr(x) - sqr(a + y));
    Var temp_2 = (x/b - pow(x, c) - pow(y, b)) * exp(-sqr(x) - sqr(y));
    Var temp_3 = exp(-sqr(a + x) - sqr(y));
    Var peak = c * temp_1 - d * temp_2 - temp_3/c;

    // prepare output
    maingo::EvaluationContainer result;
    result.objective = peak;

    return result;
}