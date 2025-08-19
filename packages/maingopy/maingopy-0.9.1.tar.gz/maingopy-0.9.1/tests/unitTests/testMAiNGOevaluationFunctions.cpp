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



using maingo::MAiNGO;


///////////////////////////////////////////////////
TEST(TestMAiNGOevaluationFunctions, EvaluateModelAtPoint) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel1>();
    MAiNGO maingo(model);
    const std::pair<std::vector<double>, bool> result = maingo.evaluate_model_at_point({0.5, 0.5, 0.5, 0.5});
    EXPECT_EQ(result.first.size(), 11);
    EXPECT_EQ(result.first[0], 0.25);
    EXPECT_EQ(result.second, false);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOevaluationFunctions, EvaluateModelAtPointNoModel) {
    MAiNGO maingo;
    EXPECT_THROW(maingo.evaluate_model_at_point({0.5, 0.5}), maingo::MAiNGOException);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOevaluationFunctions, EvaluateModelAtPointIncompatiblePoint) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel1>();
    MAiNGO maingo(model);
    EXPECT_THROW(maingo.evaluate_model_at_point({0.5, 0.5}), maingo::MAiNGOException);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOevaluationFunctions, EvaluateAdditionalOutputAtPoint) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel1>();
    MAiNGO maingo(model);
    const std::vector<std::pair<std::string, double>> output = maingo.evaluate_additional_outputs_at_point({0.5, 0.5, 0.5, 0.5});
    EXPECT_EQ(output.size(), 2);
    EXPECT_EQ(output[0].first, "the answer");
    EXPECT_EQ(output[0].second, 42.0);
    EXPECT_EQ(output[1].first, "still the answer");
    EXPECT_EQ(output[1].second, 42.0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOevaluationFunctions, EvaluateAdditionalOutputAtPointNoModel) {
    MAiNGO maingo;
    EXPECT_THROW(maingo.evaluate_additional_outputs_at_point({0.5, 0.5}), maingo::MAiNGOException);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOevaluationFunctions, EvaluateAdditionalOutputAtPointIncompatiblePoint) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel1>();
    MAiNGO maingo(model);
    EXPECT_THROW(maingo.evaluate_additional_outputs_at_point({0.5, 0.5}), maingo::MAiNGOException);
}

///////////////////////////////////////////////////
TEST(TestMAiNGOevaluationFunctions, EvaluateModelAtSolutionPoint) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel1>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", 0);
    maingo.set_option("writeResultFile", 0);
    maingo.solve();

    const std::vector<double> result = maingo.evaluate_model_at_solution_point();
    EXPECT_EQ(result.size(), 11);
    EXPECT_EQ(result[0], 0.);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOevaluationFunctions, EvaluateModelAtSolutionPointNotSolvedYet) {
    MAiNGO maingo;
    EXPECT_THROW(maingo.evaluate_model_at_solution_point(), maingo::MAiNGOException);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOevaluationFunctions, EvaluateAdditionalOutputAtSolutionPoint) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel1>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", 0);
    maingo.set_option("writeResultFile", 0);
    maingo.solve();

    const std::vector<std::pair<std::string, double>> output = maingo.evaluate_additional_outputs_at_solution_point();
    EXPECT_EQ(output.size(), 2);
    EXPECT_EQ(output[0].first, "the answer");
    EXPECT_EQ(output[0].second, 41.5);
    EXPECT_EQ(output[1].first, "still the answer");
    EXPECT_EQ(output[1].second, 42.0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOevaluationFunctions, EvaluateAdditionalOutputAtSolutionPointNoOutputs) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel2>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", 0);
    maingo.set_option("writeResultFile", 0);
    maingo.solve();

    const std::vector<std::pair<std::string, double>> output = maingo.evaluate_additional_outputs_at_solution_point();
    EXPECT_EQ(output.size(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOevaluationFunctions, EvaluateAdditionalOutputAtSolutionPointNotSolvedYet) {
    MAiNGO maingo;
    EXPECT_THROW(maingo.evaluate_additional_outputs_at_solution_point(), maingo::MAiNGOException);
}