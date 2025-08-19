/**********************************************************************************
 * Copyright (c) 2021-2023 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#include "MAiNGOmodelEpsCon.h"
#include "MAiNGOException.h"

#include "utilities/testProblems.h"

#include <gtest/gtest.h>


using Var = mc::FFVar;


///////////////////////////////////////////////////
TEST(TestMAiNGOmodelEpsCon, ThrowsIfOnlyOneObjective)
{
    MultiobjectiveModelOneObjective model;
    std::vector<Var> x(1);
    EXPECT_THROW(model.evaluate(x), maingo::MAiNGOException);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOmodelEpsCon, ThrowsIfInconsistenEpsilonDimension)
{
    BasicBiobjectiveModel model;
    model.set_epsilon({1});
    std::vector<Var> x = {0.5, 0.5};
    EXPECT_THROW(model.evaluate(x), maingo::MAiNGOException);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOmodelEpsCon, ConstructSingleObjectiveProblem)
{
    BasicBiobjectiveModel model;
    model.set_epsilon({0.1, 0.1});
    model.set_single_objective(true);
    std::vector<Var> x = {0.5, 0.5};
    maingo::EvaluationContainer results = model.evaluate(x);
    EXPECT_EQ(results.objective.size(), 1);
    EXPECT_EQ(results.ineq.size(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOmodelEpsCon, ConstructEpsilonConstraintProblem)
{
    BasicBiobjectiveModel model;
    model.set_epsilon({0.1, 0.1});
    model.set_single_objective(false);
    std::vector<Var> x = {0.5, 0.5};
    maingo::EvaluationContainer results = model.evaluate(x);
    EXPECT_EQ(results.objective.size(), 1);
    EXPECT_EQ(results.ineq.size(), 1);
}