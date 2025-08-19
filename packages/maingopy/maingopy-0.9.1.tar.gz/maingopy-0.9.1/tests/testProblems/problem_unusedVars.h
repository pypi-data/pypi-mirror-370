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
#include "libraries/problemExternalFunctions.h"    // We can also include other headers where we define classes and functions


using Var = mc::FFVar;    // This allows us to write Var instead of mc::FFVar


/**
* @class Model
* @brief Class defining the actual model implemented by the user 
*
* This class is used by the user to implement the model 
*/
class Model_unusedVars: public maingo::MAiNGOmodel {

  public:
    /**
    * @brief Default constructor
    */
    Model_unusedVars();

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
    // Constants
    const double a; /*!< constant a */

    // External objects
    SomeExternalClass ext; /*!< externally implemented object */
};


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model_unusedVars::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    // Required: Define optimization variables by specifying lower bound, upper bound (, optionally variable type, branching priority and a name)
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_BINARY, "x"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-2, 2), maingo::VT_CONTINUOUS, 1, "y"));    // A branching priority 'n' means that we will branch log(n) times more often on that specific variable
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-100, 100), maingo::VT_CONTINUOUS, "unusedVar1"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_BINARY, "unusedVar2"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(-2, 2), maingo::VT_INTEGER, "unusedVar3"));

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model_unusedVars::get_initial_point()
{

    // Here you can provide an initial point for the local search
    std::vector<double> initialPoint;    // Make sure that the size of the initialPoint equals the size of the variables vector
    //initialPoint.push_back(3);
    //initialPoint.push_back(-3);

    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model_unusedVars::Model_unusedVars():
    a(20)
{

    // Initialize data if necessary:
    ext = SomeExternalClass(0.2, M_PI);
}


//////////////////////////////////////////////////////////////////////////
// evaluate the model
maingo::EvaluationContainer
Model_unusedVars::evaluate(const std::vector<Var> &optVars)
{

    // Rename inputs
    Var x = optVars.at(0);    // We use .at() here to get a vector exception if a wrong access occurs
    Var y = optVars.at(1);

    // Model
    Var temp1 = ext.functionOne(x, y);
    Var temp2 = ext.functionTwo(x, y);

    // Prepare output
    maingo::EvaluationContainer result; /*!< variable holding the actual result consisting of an objective, inequalities, equalities, relaxation only inequalities and relaxation only equalities */
    // Objective given as the Ackel Path function:
#ifndef HAVE_GROWING_DATASETS
    result.objective = -a * exp(temp1) - exp(temp2) + a + exp(1);
#else
    result.objective_per_data.push_back(-a * exp(temp1) - exp(temp2) + a + exp(1));
#endif

    // Inequalities (<=0):

    // Equalities (=0) given as the circle equality with radius 1:
    result.eq.push_back(pow(y, 2) + pow(x, 2) - 1);

    // Relaxation only inequalities (<=0):

    // Relaxation only equalities (=0):

    // Additional output:
    result.output.push_back(maingo::OutputVariable("Result of temp1: ", temp1));

    return result;
}
