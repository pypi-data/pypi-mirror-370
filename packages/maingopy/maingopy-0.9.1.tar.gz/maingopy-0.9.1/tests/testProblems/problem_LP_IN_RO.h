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
class Model_LP_IN_RO: public maingo::MAiNGOmodel {

  public:
    /**
    * @brief Default constructor
    */
    Model_LP_IN_RO();

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
Model_LP_IN_RO::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    // Required: Define optimization variables by specifying lower bound, upper bound (, optionally variable type, branching priority and a name)
    // Continuous variables
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 10000000000), maingo::VT_CONTINUOUS, "x1"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 10000000000), maingo::VT_CONTINUOUS, "x2"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 10000000000), maingo::VT_CONTINUOUS, "x3"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 10000000000), maingo::VT_CONTINUOUS, "x4"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 10000000000), maingo::VT_CONTINUOUS, "x5"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 10000000000), maingo::VT_CONTINUOUS, "x6"));
    // Binary variables
    // Integer variables

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model_LP_IN_RO::get_initial_point()
{

    // Here you can provide an initial point for the local search
    std::vector<double> initialPoint;
    // Continuous variables
    initialPoint.push_back(0);
    initialPoint.push_back(0);
    initialPoint.push_back(0);
    initialPoint.push_back(0);
    initialPoint.push_back(0);
    initialPoint.push_back(0);
    // Binary variables
    // Integer variables

    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model_LP_IN_RO::Model_LP_IN_RO()
{
    // Initialize data if necessary:
}


//////////////////////////////////////////////////////////////////////////
// Evaluate the model
maingo::EvaluationContainer
Model_LP_IN_RO::evaluate(const std::vector<Var> &optVars)
{

    // Rename  inputs
    // Continuous variables
    Var x1 = optVars[0];
    Var x2 = optVars[1];
    Var x3 = optVars[2];
    Var x4 = optVars[3];
    Var x5 = optVars[4];
    Var x6 = optVars[5];
    // Binary variables
    // Integer variables

    // Prepare output
    maingo::EvaluationContainer result; /*!< variable holding the actual result consisting of an objective, inequalities, equalities, relaxation only inequalities and relaxation only equalities */
    // Objective function
#ifndef HAVE_GROWING_DATASETS
    result.objective = -(-0.225 * x1 - 0.153 * x2 - 0.162 * x3 - 0.225 * x4 - 0.162 * x5 - 0.126 * x6);
#else
    result.objective_per_data.push_back(-(-0.225 * x1 - 0.153 * x2 - 0.162 * x3 - 0.225 * x4 - 0.162 * x5 - 0.126 * x6));
#endif

    // Inequalities (<=0)

    // Equalities (=0)

    // relaxation only inequalities (<=0):
    result.ineqRelaxationOnly.push_back(x1 + x2 + x3 - (350));
    result.ineqRelaxationOnly.push_back(x4 + x5 + x6 - (600));
    result.ineqRelaxationOnly.push_back(-(x1 + x4) + (325));
    result.ineqRelaxationOnly.push_back(-(x2 + x5) + (300));
    result.ineqRelaxationOnly.push_back(-(x3 + x6) + (275));

    // relaxation only equalities (=0):

    return result;
}
