/**********************************************************************************
 * Copyright (c) 2021 Process Systems Engineering (AVT.SVT), RWTH Aachen University
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
class Model_QP: public maingo::MAiNGOmodel {

  public:
    /**
    * @brief Default constructor
    */
    Model_QP();

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
Model_QP::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    // Required: Define optimization variables by specifying lower bound, upper bound (, optionally variable type, branching priority and a name)
    // Continuous variables

    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 10000000000), maingo::VT_CONTINUOUS, "x"));
    for (int i = 0; i < 100; i++) {
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 10000000000), maingo::VT_CONTINUOUS, "none" + std::to_string(i)));
    }
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 10000000000), maingo::VT_CONTINUOUS, "y"));

    // Binary variables
    // Integer variables

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model_QP::get_initial_point()
{

    // Here you can provide an initial point for the local search
    std::vector<double> initialPoint;
    // Continuous variables
    initialPoint.push_back(0);
    for (int i = 0; i < 100; i++) {
        initialPoint.push_back(0);
    }
    initialPoint.push_back(0);
    // Binary variables
    // Integer variables

    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model_QP::Model_QP()
{

    // Initialize data if necessary:
}


//////////////////////////////////////////////////////////////////////////
// Evaluate the model
maingo::EvaluationContainer
Model_QP::evaluate(const std::vector<Var> &optVars)
{
    // Prepare output
    maingo::EvaluationContainer result; /*!< variable holding the actual result consisting of an objective, inequalities, equalities, relaxation only inequalities and relaxation only equalities */    // Rename  inputs
    // Continuous variables
    Var x = optVars.front();
    Var y = optVars.back();
    // Binary variables
    // Integer variables

    // Objective function

    Var obj = 2 * x * x + pow(x + y, 2);
    obj += x / 2.0 * 2.0;
    obj -= 2;
    obj += 6 * y + 4.0;
#ifndef HAVE_GROWING_DATASETS
    result.objective = obj;    // (((x*x * 2 + pow(x + y, 2)) + x * 0.5 * 2 - 2) + y * 6 + 4);
#else
    result.objective_per_data.push_back(obj);
#endif
    // Inequalities (<=0)
    result.ineq.push_back(-2 * x + -3 * y + 4.0);
    auto temp = x - x;
    for (int i = 1; i < 100; i++) {
        temp += optVars.at(i);
    }

    // Equalities (=0)
    result.eq.push_back(temp - 1.0);
    // relaxation only inequalities (<=0):

    // relaxation only equalities (=0):

    return result;
}
