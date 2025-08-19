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
TEST(TestMAiNGOprintingFunctions, RegularProgress) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicNLPcustomInitialPoint>(std::vector<double>({0.5, 1, 0, 1, 1, 1, 1, 1, 1}));
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_OUTSTREAM);

    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOprintingFunctions, FeasiblePointOnly) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicNLPcustomInitialPoint>(std::vector<double>({0.5, 1, 0, 1, 1, 1, 1, 1, 1}));
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_OUTSTREAM);
    maingo.set_option("terminateOnFeasiblePoint", 1);

    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOprintingFunctions, RegularProgressLP) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicLP>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_OUTSTREAM);

    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOprintingFunctions, InfeasibleLP) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<InfeasibleLP>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_OUTSTREAM);

    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOprintingFunctions, InitialPoint) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicNLPcustomInitialPoint>(std::vector<double>({2.5, 0.5, 1, 0.5, 1, 0.5, 1, 1, 1}));
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_OUTSTREAM);

    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOprintingFunctions, InfeasibleBounds) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<ProblemInfeasibleBounds>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_OUTSTREAM);

    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOprintingFunctions, ConstantConstraintsInfeasible) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<ProblemConstantConstraintsInfeasible>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_OUTSTREAM);

    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOprintingFunctions, Subsolvers) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicNLPcustomInitialPoint>(std::vector<double>({0.5, 1, 0, 1, 1, 1, 1, 1, 1}));
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_OUTSTREAM);

    maingo.set_option("LBP_solver", 0);
    maingo.set_option("UBP_solverPreprocessing", 0);
    maingo.set_option("UBP_solverBab", 0);
    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);

    maingo.set_option("LBP_solver", 1);
    maingo.set_option("UBP_solverPreprocessing", 1);
    maingo.set_option("UBP_solverBab", 1);
    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);

#ifdef HAVE_CPLEX
    maingo.set_option("LBP_solver", 2);
#endif
    maingo.set_option("UBP_solverPreprocessing", 2);
    maingo.set_option("UBP_solverBab", 2);
    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);

    maingo.set_option("LBP_solver", 3);
    maingo.set_option("UBP_solverPreprocessing", 3);
    maingo.set_option("UBP_solverBab", 3);
    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);

    // Cannot test Gurobi (LBP_solver 4) since stdout of license information clashes with CaptureStdout
    maingo.set_option("UBP_solverPreprocessing", 4);
    maingo.set_option("UBP_solverBab", 4);
    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);

    maingo.set_option("UBP_solverPreprocessing", 5);
    maingo.set_option("UBP_solverBab", 5);
    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);

#ifdef HAVE_KNITRO
    maingo.set_option("UBP_solverPreprocessing", 6);
    maingo.set_option("UBP_solverBab", 6);
    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);
#endif

    model = std::make_shared<BasicLP>();
    maingo.set_model(model);
    maingo.set_option("UBP_solverPreprocessing", 43); // CLP
    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOprintingFunctions, PrintMAiNGO) {
    MAiNGO maingo;
    maingo.set_option("loggingDestination", maingo::LOGGING_OUTSTREAM);
    testing::internal::CaptureStdout();
    maingo.print_MAiNGO();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOprintingFunctions, PureMultistart) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicNLPcustomInitialPoint>(std::vector<double>({0.5, 1, 0, 1, 1, 1, 1, 1, 1}));
    MAiNGO maingo(model);
    maingo.set_option("PRE_pureMultistart", true);
    maingo.set_option("loggingDestination", maingo::LOGGING_OUTSTREAM);

    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOprintingFunctions, FeasibilityOnly) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<FeasibilityProblem>();
    MAiNGO maingo(model);
    maingo.set_option("PRE_maxLocalSearches", 0);
    maingo.set_option("loggingDestination", maingo::LOGGING_OUTSTREAM);

    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOprintingFunctions, TargetUpperBound) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicNLPcustomInitialPoint>(std::vector<double>({0.5, 1, 0, 1, 1, 1, 1, 1, 1}));
    MAiNGO maingo(model);
    maingo.set_option("targetUpperBound", 1e9);
    maingo.set_option("loggingDestination", maingo::LOGGING_OUTSTREAM);

    testing::internal::CaptureStdout();
    maingo.solve();
    EXPECT_GT(testing::internal::GetCapturedStdout().size(), 0);
}