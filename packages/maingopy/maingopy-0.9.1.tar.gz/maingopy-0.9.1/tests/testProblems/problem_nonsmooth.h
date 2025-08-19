/**********************************************************************************
 * Copyright (c) 2023 Process Systems Engineering (AVT.SVT), RWTH Aachen University
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


using Var = mc::FFVar;


class Model_nonsmooth: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars);

    std::vector<maingo::OptimizationVariable> get_variables();

    std::vector<double> get_initial_point();
};


//////////////////////////////////////////////////////////////////////////
std::vector<maingo::OptimizationVariable>
Model_nonsmooth::get_variables()
{
    std::vector<maingo::OptimizationVariable> variables;
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), "x"));
    variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), "y"));

    return variables;
}


//////////////////////////////////////////////////////////////////////////
std::vector<double>
Model_nonsmooth::get_initial_point()
{
    return {0., 0.};
}


//////////////////////////////////////////////////////////////////////////
maingo::EvaluationContainer
Model_nonsmooth::evaluate(const std::vector<Var> &optVars)
{
    Var x = optVars[0];
    Var y = optVars[1];

    maingo::EvaluationContainer result;

#ifndef HAVE_GROWING_DATASETS
    result.objective = sqrt(x);
#else
    result.objective_per_data.push_back(sqrt(x));
#endif
    result.ineq.push_back(fabs(x));
    result.ineq.push_back(max(x, y));
    result.ineq.push_back(min(x, y));
    result.ineq.push_back(-fabs(x));
    result.ineq.push_back(-max(x, y));
    result.ineq.push_back(-min(x, y));
    return result;
}
