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

#include <map>
#include <tuple>


using Var = mc::FFVar;    // This allows us to write Var instead of mc::FFVar


/**
* @class Model
* @brief Class defining the actual model implemented by the user
*
* This class is used by the user to implement the model
*/
class Model_MILP_sudoku: public maingo::MAiNGOmodel {

  public:
    /**
    * @brief Default constructor
    */
    Model_MILP_sudoku();

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
    std::map<std::tuple<int, int, int>, int> pos;
};


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model_MILP_sudoku::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    // Required: Define optimization variables by specifying lower bound, upper bound (, optionally variable type, branching priority and a name)
    // Continuous variables

    // Binary variables
    for (int i = 0; i < 9; i++)
        for (int j = 0; j < 9; j++)
            for (int k = 0; k < 9; k++) {
                pos.insert({{i, j, k}, (int)variables.size()});
                variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0.0, 2.0), maingo::VT_BINARY, "x" + std::to_string(i) + std::to_string(j) + std::to_string(k)));
            }

    // Integer variables

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model_MILP_sudoku::get_initial_point()
{

    // Here you can provide an initial point for the local search
    std::vector<double> initialPoint;
    for (int i = 0; i < 9; i++)
        for (int j = 0; j < 9; j++)
            for (int k = 0; k < 9; k++) {
                initialPoint.push_back(0);
            }
    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// constructor for the model
Model_MILP_sudoku::Model_MILP_sudoku()
{

    // Initialize data if necessary:
}


//////////////////////////////////////////////////////////////////////////
// Evaluate the model
maingo::EvaluationContainer
Model_MILP_sudoku::evaluate(const std::vector<Var> &optVars)
{
    // Prepare output
    maingo::EvaluationContainer result; /*!< variable holding the actual result consisting of an objective, inequalities, equalities, relaxation only inequalities and relaxation only equalities */    // Rename  inputs
    // Continuous variables
    // Objective function

    Var obj = optVars.front();
#ifndef HAVE_GROWING_DATASETS
    result.objective = obj + 5;
#else
    result.objective_per_data.push_back(obj + 5);
#endif
    // Equalities (=0)
    // each cell can only contain one number
    for (int i = 0; i < 9; i++) {
        for (int j = 0; j < 9; j++) {
            Var constraint = -1;
            for (int k = 0; k < 9; k++) {
                constraint += optVars.at(pos.at({i, j, k}));
            }
            result.eq.push_back(constraint);
        }
    }
    // each column can only contain each number once
    for (int i = 0; i < 9; i++) {
        for (int k = 0; k < 9; k++) {
            Var constraint = -1;
            for (int j = 0; j < 9; j++) {
                constraint += optVars.at(pos.at({i, j, k}));
            }
            result.eq.push_back(constraint);
        }
    }
    // each row can only contain each number once
    for (int j = 0; j < 9; j++) {
        for (int k = 0; k < 9; k++) {
            Var constraint = -1;
            for (int i = 0; i < 9; i++) {
                constraint += optVars.at(pos.at({i, j, k}));
            }
            result.eq.push_back(constraint);
        }
    }

    //each grid 3x3 cell can only contain each number once
    for (int k = 0; k < 9; k++) {
        for (int a = 0; a <= 2; a++) {
            for (int b = 0; b <= 2; b++) {
                Var constraint = -1;
                for (int i = 0; i < 3; i++) {
                    for (
                        int j = 0;
                        j < 3; j++) {
                        constraint += optVars.at(pos.at({3 * a + i, 3 * b + j, k}));
                    }
                }
                result.eq.push_back(constraint);
            }
        }
    }

    //ALE input:
    /*
    definitions:
    binary[9, 9, 9] x;

    objective:
    x[1,1,1];

    constraints:
    forall i in {1 .. 9} :
        forall j in {1 .. 9} :
            sum(k in {1 .. 9} : x[i,j,k]) = 1; # each cell can only contain one number

    forall i in {1 .. 9} :
        forall k in {1 .. 9} :
            sum(j in {1 .. 9} : x[i,j,k]) = 1; # each column can only contain each number once

    forall j in {1 .. 9} :
        forall k in {1 .. 9} :
            sum(i in {1 .. 9} : x[i,j,k]) = 1; # each row can only contain each number once

    forall k in {1 .. 9} :
        forall a in {0 .. 2} :
            forall b in {0 .. 2} :
                sum(i in {1 .. 3} : sum(j in {1 .. 3} : x[3*a + i,3*b + j,k])) = 1; # each grid-cell can only contain each number once
    */

    // relaxation only inequalities (<=0):

    // relaxation only equalities (=0):

    return result;
}
