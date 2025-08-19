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
#include "myComplicatedFunctions.h"    // We can also include other headers where we define classes and functions


/**
* @class Model
* @brief Class defining the actual model implemented by the user
*
* This class is used by the user to implement the model
*/
class Model: public maingo::MAiNGOmodel {

  public:
    /**
        * @brief Default constructor
        */
    Model();

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
    // Constants
    const double a; /*!< constant a */

    // External objects
    SomeExternalClass ext; /*!< externally implemented object */
};


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    // Required: Define optimization variables by specifying lower bound, upper bound (, optionally variable type, branching priority and a name)
    variables.push_back(maingo::OptimizationVariable(/*Variable bounds*/ maingo::Bounds(0, 1), /*Variable type*/ maingo::VT_BINARY, /*Variable name*/ "x"));
    variables.push_back(maingo::OptimizationVariable(/*Variable bounds*/ maingo::Bounds(-2, 2), /*Variable type*/ maingo::VT_CONTINUOUS, /*Branching priority*/ 1, /*Variable name*/ "y"));
    /* Variable bounds:
    *  Every variable (except for binary variables) requires finite lower and upper bounds.
    */
    /* Variable type:
    *  There are three variable types in MAiNGO. VT_CONTINUOUS variables, VT_BINARY variables and VT_INTEGER variables.
    *  Double type bounds for binaries and integers will be rounded up for lower bounds and rounded down for upper bounds.
    */
    /* Branching priority:
    *  A branching priority 'n' means that we will branch log_2(n+1) times more often on that specific variable, n will be rounded down to the next integer meaning that a BP of 1.5 equals 1
    *  If you want to branch less on a specific variable just increase the branching priority of all other variables
    *  A branching priority of <1 means that MAiNGO will never branch on this specific variable. This may lead to non-convergence of the B&B algorithm
    */
    /* Variable name:
    *  The name has to be of string type. All ASCII characters are allowed and variables are allowed to have the same name. MAiNGO outputs the variables in the same order as they are set in
    *  the variables vector within this function.
    */

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model::get_initial_point()
{

    // Here you can provide an initial point for the local search
    std::vector<double> initialPoint;
    /* Providing an initial point is optional and you can simply leave it empty, but if you provide one you have to make sure that the size of the initialPoint equals the size of
	*  the variables vector. Otherwise MAiNGO will throw an exception.
    *  The value of an initial point variable does not have to fit the type of the variable, e.g., it is allowed to set a double type value as an initial point for a binary variable
    */
    initialPoint.push_back(0);
    initialPoint.push_back(-1);

    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model::Model():
    a(20)
{

    // Initialize data if necessary:
    ext = SomeExternalClass(0.2, MY_PI);
}


//////////////////////////////////////////////////////////////////////////
// evaluate the model
maingo::EvaluationContainer
Model::evaluate(const std::vector<Var> &optVars)
{

    // The vector optVars is of the same size and sorted in the same order as the user-defined variables vector in function get_variables()
    // Rename inputs
    Var x = optVars.at(0);    // We use .at() here to get a vector exception if a wrong access occurs
    Var y = optVars.at(1);

    // Model
    /* These are intermediate variables which are only used for convenience.
    *  They are not handled as optimization variables.
    */
    Var temp1 = ext.functionOne(x, y);
    Var temp2 = ext.functionTwo(x, y);

    // Prepare output
    maingo::EvaluationContainer result;

    // Objective given as the Ackley function:
    result.objective = -a * exp(temp1) - exp(temp2) + a + exp(1);

    // Inequalities (<=0):
    result.ineq.push_back(x - 1, "x <= 1");

    // Equalities (=0) given as the circle equality with radius 1:
    result.eq.push_back(pow(y, 2) + pow(x, 2) - 1, "circle equality");

    /* Relaxation-only inequalities and equalities are used for lower bounding only.
    *  None of relaxation only (in)equalities are passed to the upper bounding solver.
    *  Only for the best feasible point (if any) found in pre-processing and for the
    *  final solution point, MAiNGO checks whether they satisfy relaxation-only
    *  (in)equalities and warns the user if they do not
    */
    // Relaxation-only inequalities (<=0):
    // result.ineqRelaxationOnly.push_back(y - 1,"y <= 1");

    // Relaxation-only equalities (=0):
    // result.eqRelaxationOnly.push_back(y + x - 1,"y + x = 1");

    // Additional output can be used to access intermediate factors after a problem has been solved.
    // Additional output:
    result.output.push_back(maingo::OutputVariable("Result of temp1: ", temp1));

    return result;
}