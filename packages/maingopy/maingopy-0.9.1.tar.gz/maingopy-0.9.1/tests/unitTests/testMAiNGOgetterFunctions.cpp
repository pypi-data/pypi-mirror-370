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


///////////////////////////////////////////////////
TEST(TestMAiNGOgetterFunctions, GetObjectiveValue) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel2>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.get_objective_value(), maingo::MAiNGOException);

    maingo.solve();
    EXPECT_DOUBLE_EQ(maingo.get_objective_value(), 0.);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOgetterFunctions, GetSolutonPoint) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel2>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.get_solution_point(), maingo::MAiNGOException);

    maingo.solve();
    const std::vector<double> solutionPoint = maingo.get_solution_point();
    EXPECT_DOUBLE_EQ(solutionPoint.size(), 2);
    EXPECT_DOUBLE_EQ(solutionPoint[0], 0);
    EXPECT_DOUBLE_EQ(solutionPoint[1], 0.5);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOgetterFunctions, GetCpuSolutionTime) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel2>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.get_cpu_solution_time(), maingo::MAiNGOException);

    maingo.solve();
    EXPECT_GE(maingo.get_cpu_solution_time(), 0.);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOgetterFunctions, GetWallSolutionTime) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel2>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.get_wallclock_solution_time(), maingo::MAiNGOException);

    maingo.solve();
    EXPECT_GE(maingo.get_wallclock_solution_time(), 0.);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOgetterFunctions, GetIterations) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel2>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.get_iterations(), maingo::MAiNGOException);

    maingo.set_option("PRE_pureMultistart", 1);
    maingo.solve();
    EXPECT_EQ(maingo.get_iterations(), 0);

    maingo.set_option("PRE_maxLocalSearches", 0);
    maingo.set_option("PRE_pureMultistart", 0);
    maingo.solve();
    EXPECT_GE(maingo.get_iterations(), 1);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOgetterFunctions, GetMaxNodes) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel2>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.get_max_nodes_in_memory(), maingo::MAiNGOException);

    maingo.set_option("PRE_pureMultistart", 1);
    maingo.solve();
    EXPECT_EQ(maingo.get_max_nodes_in_memory(), 1);

    maingo.set_option("PRE_maxLocalSearches", 0);
    maingo.set_option("PRE_pureMultistart", 0);
    maingo.solve();
    EXPECT_GE(maingo.get_max_nodes_in_memory(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOgetterFunctions, GetUbpCount) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel2>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.get_UBP_count(), maingo::MAiNGOException);

    maingo.set_option("PRE_pureMultistart", 1);
    maingo.solve();
    EXPECT_EQ(maingo.get_UBP_count(), 1);

    maingo.set_option("PRE_maxLocalSearches", 0);
    maingo.set_option("PRE_pureMultistart", 0);
    maingo.solve();
    EXPECT_GE(maingo.get_UBP_count(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOgetterFunctions, GetLbpCount) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel2>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.get_LBP_count(), maingo::MAiNGOException);

    maingo.set_option("PRE_pureMultistart", 1);
    maingo.solve();
    EXPECT_EQ(maingo.get_LBP_count(), 0);

    maingo.set_option("PRE_maxLocalSearches", 0);
    maingo.set_option("PRE_pureMultistart", 0);
    maingo.solve();
    EXPECT_GE(maingo.get_LBP_count(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOgetterFunctions, GetFinalLbd) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel2>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.get_final_LBD(), maingo::MAiNGOException);

    maingo.set_option("PRE_pureMultistart", 1);
    maingo.solve();
    EXPECT_DOUBLE_EQ(maingo.get_final_LBD(), 0);

    maingo.set_option("PRE_maxLocalSearches", 0);
    maingo.set_option("PRE_pureMultistart", 0);
    maingo.solve();
    EXPECT_DOUBLE_EQ(maingo.get_final_LBD(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOgetterFunctions, GetFinalAbsGap) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel2>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.get_final_abs_gap(), maingo::MAiNGOException);

    maingo.set_option("PRE_pureMultistart", 1);
    maingo.solve();
    EXPECT_LT(maingo.get_final_abs_gap(), 1e-1);

    maingo.set_option("PRE_maxLocalSearches", 0);
    maingo.set_option("PRE_pureMultistart", 0);
    maingo.solve();
    EXPECT_EQ(maingo.get_final_abs_gap(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOgetterFunctions, GetFinalRelGap) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel2>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_THROW(maingo.get_final_rel_gap(), maingo::MAiNGOException);

    maingo.set_option("PRE_pureMultistart", 1);
    maingo.solve();
    EXPECT_LT(maingo.get_final_rel_gap(), 1e-1);

    maingo.set_option("PRE_maxLocalSearches", 0);
    maingo.set_option("PRE_pureMultistart", 0);
    maingo.solve();
    EXPECT_EQ(maingo.get_final_rel_gap(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOgetterFunctions, GetStatus) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel2>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    EXPECT_EQ(maingo.get_status(), maingo::NOT_SOLVED_YET);

    maingo.solve();
    EXPECT_EQ(maingo.get_status(), maingo::GLOBALLY_OPTIMAL);
}