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
#include <algorithm>
#include <numeric>
#include <random>
#include <vector>

using Var = mc::FFVar;    // This allows us to write Var instead of mc::FFVar


/**
* @class Model
* @brief Class defining the actual model implemented by the user 
*
* This class is used by the user to implement the model 
*/
class Model_LP_random: public maingo::MAiNGOmodel {

  public:
    /**
    * @brief Default constructor
    */
    Model_LP_random(unsigned problemSize = 100, double density = 0.5):
        _problemSize(problemSize), _density(density)
    {
        //gives us the indices 0 to n^2+n-1. We shuffle them and choose density*100 percent of them from the front of the shuffled vector.
        //The selected indices represent non zero elements of the problem. The first n correspond to the objective vector. The constraint matrix is assumed to be quadratic.
        std::vector<unsigned int> indices(problemSize + problemSize * problemSize);
        std::iota(indices.begin(), indices.end(), 0);
        std::shuffle(indices.begin(), indices.end(), std::mt19937(std::random_device()()));
        _indices = std::vector<unsigned>(indices.begin(), indices.begin() + indices.size() * density);
        std::sort(_indices.begin(), _indices.end());
        std::random_device rd;                                  //Will be used to obtain a seed for the random number engine
        std::mt19937 gen(rd());                                 //Standard mersenne_twister_engine seeded with rd()
        std::uniform_real_distribution<> dis(-100.0, 100.0);    // entries are randomly picked
        _values   = std::vector<double>(std::round(indices.size() * density));
        auto gen2 = [&dis, &gen]() {
            return dis(gen);
        };
        std::generate(_values.begin(), _values.end(), gen2);
    }

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
    unsigned _problemSize;
    double _density;
    std::vector<unsigned> _indices;
    std::vector<double> _values;
};


//////////////////////////////////////////////////////////////////////////
// function for providing optimization variable data to the Branch-and-Bound solver
std::vector<maingo::OptimizationVariable>
Model_LP_random::get_variables()
{

    std::vector<maingo::OptimizationVariable> variables;
    // Required: Define optimization variables by specifying lower bound, upper bound (, optionally variable type, branching priority and a name)
    // Continuous variables


    for (unsigned i = 0; i < _problemSize; i++) {
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 10000000000), maingo::VT_CONTINUOUS, "none" + std::to_string(i)));
    }

    // Binary variables
    // Integer variables

    return variables;
}


//////////////////////////////////////////////////////////////////////////
// function for providing initial point data to the Branch-and-Bound solver
std::vector<double>
Model_LP_random::get_initial_point()
{

    // Here you can provide an initial point for the local search
    std::vector<double> initialPoint;
    // Continuous variables

    for (unsigned i = 0; i < _problemSize; i++) {
        initialPoint.push_back(0);
    }

    // Binary variables
    // Integer variables

    return initialPoint;
}


//////////////////////////////////////////////////////////////////////////
// Evaluate the model
maingo::EvaluationContainer
Model_LP_random::evaluate(const std::vector<Var> &optVars)
{

    // Prepare output
    maingo::EvaluationContainer result; /*!< variable holding the actual result consisting of an objective, inequalities, equalities, relaxation only inequalities and relaxation only equalities */    // Rename  input
    Var objective;
    //indices is sorted, only the first n indices can be from objective
    unsigned problemSize    = _problemSize;
    auto getRowColFromIndex = [problemSize](unsigned index) {
        //i=row*ncolums+col
        unsigned ncolums = problemSize;
        unsigned col     = index % ncolums;
        unsigned row     = (index - col) / ncolums;
        return std::make_pair(row, col);
    };
    unsigned j = 0;
    while (_indices.at(j) < _problemSize && j < _indices.size())    //objective term
    {
        objective += optVars.at(_indices.at(j)) * _values.at(j) * 0;
        j++;
    }
    objective += -2;

#ifndef HAVE_GROWING_DATASETS
    result.objective = objective;
#else
    result.objective_per_data.push_back(objective);
#endif
    for (unsigned row = 0; row < _problemSize; row++) {
        Var currentRow;
        bool rowUsed = false;
        while (j < _indices.size() && getRowColFromIndex(_indices.at(j)).first == row) {
            unsigned col = getRowColFromIndex(_indices.at(j)).second;
            rowUsed      = true;
            currentRow += _values.at(j) * optVars.at(col);
            j++;
        }
        if (rowUsed)
            result.ineq.push_back(currentRow);
    }

    return result;
}
