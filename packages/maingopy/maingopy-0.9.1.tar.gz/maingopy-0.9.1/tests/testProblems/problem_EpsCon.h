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

#include "MAiNGOmodelEpsCon.h"

#define MY_PI 3.14159265358979323846 /* pi */

/**
* @class Model
* @brief Class defining the actual model implemented by the user
*
* This class is used by the user to implement the model
*/
class Model_EpsCon: public maingo::MAiNGOmodelEpsCon {

  public:
    /**
      * @brief Default constructor
      */
    Model_EpsCon();

    /**
      * @brief Main function used to evaluate the model and construct a directed acyclic graph
      *
      * @param[in] optVars is the optimization variables vector
      */
    maingo::EvaluationContainer evaluate_user_model(const std::vector<Var> &optVars);

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
Model_EpsCon::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    // Required: Define optimization variables by specifying lower bound, upper bound (, optionally variable type, branching priority and a name)
    // Continuous variables   
    variables.push_back(maingo::OptimizationVariable(/*Variable bounds*/ maingo::Bounds(-MY_PI, MY_PI), /*Variable type*/ maingo::VT_CONTINUOUS, /*Variable name*/ "x"));
    variables.push_back(maingo::OptimizationVariable(/*Variable bounds*/ maingo::Bounds(-MY_PI, MY_PI), /*Variable type*/ maingo::VT_CONTINUOUS, /*Variable name*/ "y"));
    // Binary variables
    // Integer variables

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model_EpsCon::get_initial_point()
{

    // Here you can provide an initial point for the local search
    std::vector<double> initialPoint;

    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model_EpsCon::Model_EpsCon()
{
      // Initialize data if necessary:
}


//////////////////////////////////////////////////////////////////////////
// evaluate the model
maingo::EvaluationContainer
Model_EpsCon::evaluate_user_model(const std::vector<Var> &optVars)
{

    // The vector optVars is of the same size and sorted in the same order as the user-defined variables vector in function get_variables()
    // Rename inputs
    Var x = optVars.at(0);    // We use .at() here to get a vector exception if a wrong access occurs
    Var y = optVars.at(1);

    Var A1 = 0.5 * sin(1) - 2 * cos(1) + sin(2) - 1.5 * cos(2);
    Var A2 = 1.5 * sin(1) - cos(1) + 2 * sin(2) - 0.5 * cos(2);
    Var B1 = 0.5 * sin(x) - 2 * cos(x) + sin(y) - 1.5 * cos(y);
    Var B2 = 1.5 * sin(x) - cos(x) + 2 * sin(y) - 0.5 * cos(y);


    // Prepare output
    maingo::EvaluationContainer result;
    // Objective: Kursawe function
    result.objective.push_back(1 + sqr(A1 - B1) + pow(A2 - B2, 2));
    result.objective.push_back(sqr(x + 3) + sqr(y + 1));
    // Inequalities (<=0):
    // Equalities (=0):
    // Relaxation only inequalities (<=0):
    // Relaxation only equalities (=0):
    // Additional output:

    return result;
}