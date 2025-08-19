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
class Model_relaxOnly: public maingo::MAiNGOmodel {

  public:
    /**
    * @brief Default constructor
    */
    Model_relaxOnly();

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
Model_relaxOnly::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    // Required: Define optimization variables by specifying lower bound, upper bound (, optionally variable type, branching priority and a name)
    // Some variables are missing bounds completely.

    variables.push_back(maingo::OptimizationVariable(/*Variable bounds*/ maingo::Bounds(0, 1), /*Variable type*/ maingo::VT_BINARY, /*Variable name*/ "x"));
    variables.push_back(maingo::OptimizationVariable(/*Variable bounds*/ maingo::Bounds(-2, 2), /*Variable type*/ maingo::VT_CONTINUOUS, /*Branching priority*/ 1, /*Variable name*/ "y"));
 
    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model_relaxOnly::get_initial_point()
{

    //here you can provide an initial point for the local search
    std::vector<double> initialPoint;
    // GAMS file did not provide initial values for all variables
    initialPoint.push_back(0);
    initialPoint.push_back(1);

    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model_relaxOnly::Model_relaxOnly()
{

    // Initialize data if necessary:
}


//////////////////////////////////////////////////////////////////////////
// Evaluate the model
maingo::EvaluationContainer
Model_relaxOnly::evaluate(const std::vector<Var> &optVars)
{

    // rename  inputs
    Var x1 = optVars[0];
    Var x2 = optVars[1];

    // Prepare output
    maingo::EvaluationContainer result; /*!< variable holding the actual result consisting of an objective, inequalities, equalities, relaxation only inequalities and relaxation only equalities */
    // objective function:
#ifndef HAVE_GROWING_DATASETS
    result.objective = -20 * exp(-0.2 * sqrt( (pow(x1,2) + pow(x2,2)) / 2 )) - exp((cos(3.14159265358979323846*x1) + cos(3.14159265358979323846*x2)) / 2) + 20 + exp(1);
#else
    result.objective_per_data.push_back(-20 * exp(-0.2 * sqrt( (pow(x1,2) + pow(x2,2)) / 2 )) - exp((cos(3.14159265358979323846*x1) + cos(3.14159265358979323846*x2)) / 2) + 20 + exp(1));
#endif
    // inequalities (<=0):
    result.ineq.push_back(x1 - 1, "x <= 1");

    // equalities (=0):
    result.eq.push_back(pow(x2, 2) + pow(x1, 2) - 1, "circle equality");

    // relaxation only inequalities (<=0):
    result.ineqRelaxationOnly.push_back(x2 - 1,"y <= 1");

    // relaxation only equalities (=0):
    result.eqRelaxationOnly.push_back(x2 + x1 - 1,"y + x = 1");


    return result;
}
