/**********************************************************************************
 * Copyright (c) 2021-2024 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#include "MAiNGO.h"
#include "MAiNGOException.h"

#include "utilities/testProblems.h"

#include <gtest/gtest.h>

#include <filesystem>



using maingo::MAiNGO;


class BabTestProblemRegular: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        Var x = optVars[0];
        Var y = optVars[1];
        result.objective = pow(x,3)*pow(y-0.5,5)*log(sqrt(exp(x)*(x-pow(x,3)))+1.5)*pow(x*y,5);
        result.ineq.push_back(pow(x,3) - y + 0.5);
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "x"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "y"));
        return variables;
    }

  private:
};


class BabTestProblemInfeasible: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        Var x = optVars[0];
        Var y = optVars[1];
        result.objective = log(sqrt(exp(x)*(x-pow(x,3)))+1.5)*pow(x*y,5);
        result.ineq.push_back(pow(x,3) - y + 0.5);
        result.ineq.push_back(pow(x,3) - y + 3.5);
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "x"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "y"));
        return variables;
    }

  private:
};


///////////////////////////////////////////////////
TEST(TestBab, RegularSolve) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BabTestProblemRegular>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("BAB_verbosity", maingo::VERB_ALL);
    maingo.set_option("LBP_verbosity", maingo::VERB_ALL);
    maingo.set_option("UBP_verbosity", maingo::VERB_ALL);
    maingo.set_option("PRE_maxLocalSearches", 0);
    maingo.set_option("PRE_obbtMaxRounds", 0);
    maingo.set_option("UBP_solverBab", 0);
    maingo.set_option("LBP_addAuxiliaryVars", true);
    maingo.set_option("epsilonA", 1e-9);
    maingo.set_option("epsilonR", 1e-9);

    maingo.solve();
    EXPECT_DOUBLE_EQ(maingo.get_objective_value(), 0.);
    EXPECT_DOUBLE_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);
}


///////////////////////////////////////////////////
TEST(TestBab, Infeasible) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BabTestProblemInfeasible>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("BAB_verbosity", maingo::VERB_ALL);
    maingo.set_option("PRE_maxLocalSearches", 0);
    maingo.set_option("PRE_obbtMaxRounds", 0);
    maingo.set_option("BAB_constraintPropagation", 0);
    maingo.set_option("UBP_solverBab", 0);

    maingo.solve();
    EXPECT_DOUBLE_EQ(maingo.get_status(), maingo::INFEASIBLE);
}


///////////////////////////////////////////////////
TEST(TestBab, TargetUpperBound) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BabTestProblemRegular>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("BAB_verbosity", maingo::VERB_ALL);
    maingo.set_option("PRE_maxLocalSearches", 0);
    maingo.set_option("PRE_obbtMaxRounds", 0);
    maingo.set_option("UBP_solverBab", 5);
    maingo.set_option("LBP_addAuxiliaryVars", true);
    maingo.set_option("BAB_alwaysSolveObbt", 0);
    maingo.set_option("BAB_dbbt", 0);
    maingo.set_option("targetUpperBound", 1e5);

    maingo.solve();
    EXPECT_DOUBLE_EQ(maingo.get_status(), maingo::BOUND_TARGETS);
}


///////////////////////////////////////////////////
TEST(TestBab, TargetLowerBound) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BabTestProblemRegular>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("BAB_verbosity", maingo::VERB_ALL);
    maingo.set_option("PRE_maxLocalSearches", 0);
    maingo.set_option("PRE_obbtMaxRounds", 0);
    maingo.set_option("UBP_solverBab", 5);
    maingo.set_option("LBP_addAuxiliaryVars", true);
    maingo.set_option("BAB_alwaysSolveObbt", 0);
    maingo.set_option("BAB_dbbt", 0);
    maingo.set_option("targetLowerBound", -1e5);

    maingo.solve();
    EXPECT_DOUBLE_EQ(maingo.get_status(), maingo::BOUND_TARGETS);
}


///////////////////////////////////////////////////
TEST(TestBab, FeasiblePointOnly) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BabTestProblemRegular>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("BAB_verbosity", maingo::VERB_ALL);
    maingo.set_option("PRE_maxLocalSearches", 0);
    maingo.set_option("PRE_obbtMaxRounds", 0);
    maingo.set_option("UBP_solverBab", 5);
    maingo.set_option("LBP_addAuxiliaryVars", true);
    maingo.set_option("BAB_alwaysSolveObbt", 0);
    maingo.set_option("BAB_dbbt", 0);
    maingo.set_option("terminateOnFeasiblePoint", 1);

    maingo.solve();
    EXPECT_DOUBLE_EQ(maingo.get_status(), maingo::FEASIBLE_POINT);
}


///////////////////////////////////////////////////
TEST(TestBab, IterationsLimit) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BabTestProblemRegular>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("BAB_verbosity", maingo::VERB_ALL);
    maingo.set_option("PRE_maxLocalSearches", 3);
    maingo.set_option("PRE_obbtMaxRounds", 0);
    maingo.set_option("UBP_solverBab", 0);
    maingo.set_option("LBP_addAuxiliaryVars", true);
    maingo.set_option("BAB_alwaysSolveObbt", 0);
    maingo.set_option("BAB_dbbt", 0);
    maingo.set_option("BAB_maxIterations", 1);

    maingo.solve();
    EXPECT_DOUBLE_EQ(maingo.get_status(), maingo::FEASIBLE_POINT);
}


///////////////////////////////////////////////////
TEST(TestBab, NodeLimit) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BabTestProblemRegular>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("BAB_verbosity", maingo::VERB_ALL);
    maingo.set_option("PRE_maxLocalSearches", 3);
    maingo.set_option("PRE_obbtMaxRounds", 0);
    maingo.set_option("UBP_solverBab", 0);
    maingo.set_option("LBP_addAuxiliaryVars", true);
    maingo.set_option("BAB_alwaysSolveObbt", 0);
    maingo.set_option("BAB_dbbt", 0);
    maingo.set_option("BAB_maxNodes", 1);

    maingo.solve();
    EXPECT_DOUBLE_EQ(maingo.get_status(), maingo::FEASIBLE_POINT);
}


///////////////////////////////////////////////////
TEST(TestBab, TimeLimit) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BabTestProblemRegular>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("BAB_verbosity", maingo::VERB_ALL);
    maingo.set_option("PRE_maxLocalSearches", 3);
    maingo.set_option("PRE_obbtMaxRounds", 0);
    maingo.set_option("UBP_solverBab", 0);
    maingo.set_option("LBP_addAuxiliaryVars", true);
    maingo.set_option("BAB_alwaysSolveObbt", 0);
    maingo.set_option("BAB_dbbt", 0);
    maingo.set_option("maxTime", 0);

    maingo.solve();
    EXPECT_DOUBLE_EQ(maingo.get_status(), maingo::FEASIBLE_POINT);
}


///////////////////////////////////////////////////
TEST(TestBab, ConfirmTermination) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BabTestProblemRegular>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("BAB_verbosity", maingo::VERB_ALL);
    maingo.set_option("PRE_maxLocalSearches", 3);
    maingo.set_option("PRE_obbtMaxRounds", 0);
    maingo.set_option("UBP_solverBab", 0);
    maingo.set_option("LBP_addAuxiliaryVars", true);
    maingo.set_option("BAB_alwaysSolveObbt", 0);
    maingo.set_option("BAB_dbbt", 0);
    maingo.set_option("BAB_maxIterations", 1);
    maingo.set_option("confirmTermination", 1);

    std::stringstream inputStream("bogusinput\nn");
    maingo.set_input_stream(&inputStream);
    maingo.solve();
    EXPECT_DOUBLE_EQ(maingo.get_status(), maingo::FEASIBLE_POINT);

    inputStream = std::stringstream("y\n150");
    maingo.set_input_stream(&inputStream);
    maingo.solve();
    EXPECT_DOUBLE_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);

    inputStream = std::stringstream("bogusinput\ny\n-10\n1e150000");
    maingo.set_input_stream(&inputStream);
    maingo.solve();
    EXPECT_DOUBLE_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);

    inputStream = std::stringstream("y\n\n");
    maingo.set_input_stream(&inputStream);
    EXPECT_THROW(maingo.solve(), maingo::MAiNGOException);
}