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
class Model_1d: public maingo::MAiNGOmodel {

  public:
    /**
    * @brief Default constructor
    */
    Model_1d();

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
Model_1d::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    // Required: Define optimization variables by specifying lower bound, upper bound (, optionally variable type, branching priority and a name)
    // Continuous variables
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-10000000000, 10000000000), maingo::VT_CONTINUOUS, "x1"));
    // Binary variables
    // Integer variables

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model_1d::get_initial_point()
{

    // Here you can provide an initial point for the local search
    std::vector<double> initialPoint;
    // Continuous variables
    // Binary variables
    // Integer variables

    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model_1d::Model_1d()
{
    // Initialize data if necessary:
}


//////////////////////////////////////////////////////////////////////////
// Evaluate the model
maingo::EvaluationContainer
Model_1d::evaluate(const std::vector<Var> &optVars)
{

    // Rename  inputs
    // Continuous variables
    Var x1 = optVars[0];
    // Binary variables
    // Integer variables

    // Prepare output
    maingo::EvaluationContainer result; /*!< variable holding the actual result consisting of an objective, inequalities, equalities, relaxation only inequalities and relaxation only equalities */
    // Objective function
#ifndef HAVE_GROWING_DATASETS
    result.objective = pow(x1,4);
#else
    result.objective_per_data.push_back(pow(x1,4));
#endif

    // Inequalities (<=0)

    // Equalities (=0)

    // relaxation only inequalities (<=0):

    // relaxation only equalities (=0):

    return result;
}
