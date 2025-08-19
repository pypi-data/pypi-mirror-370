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
class Model_chance: public maingo::MAiNGOmodel {

  public:
    /**
    * @brief Default constructor
    */
    Model_chance();

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
Model_chance::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    // Required: Define optimization variables by specifying lower bound, upper bound (, optionally variable type, branching priority and a name)
    // Continuous variables
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 10000000000), maingo::VT_CONTINUOUS, "x1"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 10000000000), maingo::VT_CONTINUOUS, "x2"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 10000000000), maingo::VT_CONTINUOUS, "x3"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 10000000000), maingo::VT_CONTINUOUS, "x4"));
    // Binary variables
    // Integer variables

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model_chance::get_initial_point()
{

    // Here you can provide an initial point for the local search
    std::vector<double> initialPoint;
    // Continuous variables
    initialPoint.push_back(0.685244910300343);
    initialPoint.push_back(0.0126990526103601);
    initialPoint.push_back(0.302056037089293);
    initialPoint.push_back(500000000000);
    // Binary variables
    // Integer variables

    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model_chance::Model_chance()
{
    // Initialize data if necessary:
}


//////////////////////////////////////////////////////////////////////////
// Evaluate the model
maingo::EvaluationContainer
Model_chance::evaluate(const std::vector<Var> &optVars)
{

    // Rename  inputs
    // Continuous variables
    Var x1 = optVars[0];
    Var x2 = optVars[1];
    Var x3 = optVars[2];
    Var x4 = optVars[3];
    // Binary variables
    // Integer variables

    // Prepare output
    maingo::EvaluationContainer result; /*!< variable holding the actual result consisting of an objective, inequalities, equalities, relaxation only inequalities and relaxation only equalities */
    // Objective function
#ifndef HAVE_GROWING_DATASETS
    result.objective = (24.55 * x1 + 26.75 * x2 + 39 * x3 + 40.5 * x4 );
#else
    result.objective_per_data.push_back( 24.55 * x1 + 26.75 * x2 + 39 * x3 + 40.5 * x4 );
#endif

    // Inequalities (<=0)
    result.ineq.push_back( -( 12 * x1  -1.645 * sqrt(0.28 * sqr(x1) + 0.19 * sqr(x2) + 20.5 * sqr(x3) + 0.62 *sqr(x4)) + 11.9 * x2 + 41.8 * x3 + 52.1 * x4  ) + ( 21 ), "e3" );
    result.ineq.push_back( -( 2.3 * x1 + 5.6 * x2 + 11.1 * x3 + 1.3 * x4  ) + ( 5 ), "e4" );

    // Equalities (=0)
    result.eq.push_back( x1 + x2 + x3 + x4 - 1 , "e2" );

    // Relaxation only inequalities (<=0):

    // Relaxation only equalities (=0):

    return result;
}
