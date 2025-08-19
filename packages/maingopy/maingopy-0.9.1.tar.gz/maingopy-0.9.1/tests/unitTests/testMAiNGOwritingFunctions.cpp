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
TEST(TestMAiNGOwritingFunctions, WriteLogFile) {
    std::error_code errorCode;
    std::filesystem::remove("tmpLogFileForTesting.log", errorCode);

    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel1>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_FILE);
    maingo.set_option("writeResultFile", false);
    maingo.set_option("writeCsv", false);
    maingo.set_option("writeJson", false);
    maingo.set_log_file_name("tmpLogFileForTesting.log");
    maingo.solve();

    EXPECT_EQ(true, std::filesystem::exists("tmpLogFileForTesting.log"));
    std::filesystem::remove("tmpLogFileForTesting.log", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOwritingFunctions, WriteResultFile) {
    std::error_code errorCode;
    std::filesystem::remove("tmpResultFileForTesting.txt", errorCode);

    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel1>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("writeResultFile", true);
    maingo.set_option("writeCsv", false);
    maingo.set_option("writeJson", false);
    maingo.set_result_file_name("tmpResultFileForTesting.txt");
    maingo.solve();

    EXPECT_EQ(true, std::filesystem::exists("tmpResultFileForTesting.txt"));
    std::filesystem::remove("tmpResultFileForTesting.txt", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOwritingFunctions, WriteCsvFiles) {
    std::error_code errorCode;
    std::filesystem::remove("tmpCsvIterationsFileForTesting.csv", errorCode);
    std::filesystem::remove("tmpCsvSolutionFileForTesting.csv", errorCode);

    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel1>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("writeResultFile", false);
    maingo.set_option("writeCsv", true);
    maingo.set_option("writeJson", false);
    maingo.set_option("PRE_printEveryLocalSearch", true);
    maingo.set_iterations_csv_file_name("tmpCsvIterationsFileForTesting.csv");
    maingo.set_solution_and_statistics_csv_file_name("tmpCsvSolutionFileForTesting.csv");
    maingo.solve();
    EXPECT_EQ(true, std::filesystem::exists("tmpCsvIterationsFileForTesting.csv"));
    std::filesystem::remove("tmpCsvIterationsFileForTesting.csv", errorCode);
    EXPECT_EQ(true, std::filesystem::exists("tmpCsvSolutionFileForTesting.csv"));
    std::filesystem::remove("tmpCsvSolutionFileForTesting.csv", errorCode);

    maingo.set_option("PRE_pureMultistart", true);
    maingo.solve();
    EXPECT_EQ(true, std::filesystem::exists("tmpCsvIterationsFileForTesting.csv"));
    std::filesystem::remove("tmpCsvIterationsFileForTesting.csv", errorCode);
    EXPECT_EQ(true, std::filesystem::exists("tmpCsvSolutionFileForTesting.csv"));
    std::filesystem::remove("tmpCsvSolutionFileForTesting.csv", errorCode);

    maingo.set_option("PRE_pureMultistart", false);
    model = std::make_shared<BasicLP>();
    maingo.set_model(model);
    maingo.solve();
    EXPECT_EQ(true, std::filesystem::exists("tmpCsvIterationsFileForTesting.csv"));
    std::filesystem::remove("tmpCsvIterationsFileForTesting.csv", errorCode);
    EXPECT_EQ(true, std::filesystem::exists("tmpCsvSolutionFileForTesting.csv"));
    std::filesystem::remove("tmpCsvSolutionFileForTesting.csv", errorCode);

    model = std::make_shared<BasicNLP>();
    maingo.set_model(model);
    maingo.solve();
    EXPECT_EQ(true, std::filesystem::exists("tmpCsvIterationsFileForTesting.csv"));
    std::filesystem::remove("tmpCsvIterationsFileForTesting.csv", errorCode);
    EXPECT_EQ(true, std::filesystem::exists("tmpCsvSolutionFileForTesting.csv"));
    std::filesystem::remove("tmpCsvSolutionFileForTesting.csv", errorCode);

    model = std::make_shared<BasicDNLP>();
    maingo.set_model(model);
    maingo.solve();
    EXPECT_EQ(true, std::filesystem::exists("tmpCsvIterationsFileForTesting.csv"));
    std::filesystem::remove("tmpCsvIterationsFileForTesting.csv", errorCode);
    EXPECT_EQ(true, std::filesystem::exists("tmpCsvSolutionFileForTesting.csv"));
    std::filesystem::remove("tmpCsvSolutionFileForTesting.csv", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOwritingFunctions, WriteJsonFile) {
    std::error_code errorCode;
    std::filesystem::remove("tmpJsonFileForTesting.json", errorCode);

    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicModel1>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("writeResultFile", false);
    maingo.set_option("writeCsv", false);
    maingo.set_option("writeJson", true);
    maingo.set_json_file_name("tmpJsonFileForTesting.json");
    maingo.solve();
    EXPECT_EQ(true, std::filesystem::exists("tmpJsonFileForTesting.json"));
    std::filesystem::remove("tmpJsonFileForTesting.json", errorCode);

    model = std::make_shared<BasicLP>();
    maingo.set_model(model);
    maingo.solve();
    EXPECT_EQ(true, std::filesystem::exists("tmpJsonFileForTesting.json"));
    std::filesystem::remove("tmpJsonFileForTesting.json", errorCode);

#ifdef HAVE_CPLEX
    model = std::make_shared<BasicQP>();
    maingo.set_model(model);
    maingo.solve();
    EXPECT_EQ(true, std::filesystem::exists("tmpJsonFileForTesting.json"));
    std::filesystem::remove("tmpJsonFileForTesting.json", errorCode);

    model = std::make_shared<BasicMIP>();
    maingo.set_model(model);
    maingo.solve();
    EXPECT_EQ(true, std::filesystem::exists("tmpJsonFileForTesting.json"));
    std::filesystem::remove("tmpJsonFileForTesting.json", errorCode);

    model = std::make_shared<BasicMIQP>();
    maingo.set_model(model);
    maingo.solve();
    EXPECT_EQ(true, std::filesystem::exists("tmpJsonFileForTesting.json"));
    std::filesystem::remove("tmpJsonFileForTesting.json", errorCode);
#endif

    model = std::make_shared<BasicNLP>();
    maingo.set_model(model);
    maingo.solve();
    EXPECT_EQ(true, std::filesystem::exists("tmpJsonFileForTesting.json"));
    std::filesystem::remove("tmpJsonFileForTesting.json", errorCode);

    model = std::make_shared<BasicDNLP>();
    maingo.set_model(model);
    maingo.solve();
    EXPECT_EQ(true, std::filesystem::exists("tmpJsonFileForTesting.json"));
    std::filesystem::remove("tmpJsonFileForTesting.json", errorCode);

    model = std::make_shared<BasicDNLP>();
    maingo.set_model(model);
    maingo.set_option("BAB_maxIterations", 0);
    maingo.solve();
    EXPECT_EQ(true, std::filesystem::exists("tmpJsonFileForTesting.json"));
    std::filesystem::remove("tmpJsonFileForTesting.json", errorCode);

    model = std::make_shared<BasicDNLP>();
    maingo.set_model(model);
    maingo.set_option("targetUpperBound", 10);
    maingo.solve();
    EXPECT_EQ(true, std::filesystem::exists("tmpJsonFileForTesting.json"));
    std::filesystem::remove("tmpJsonFileForTesting.json", errorCode);

    model = std::make_shared<BasicDNLP>();
    maingo.set_model(model);
    maingo.set_option("PRE_maxLocalSearches", 0);
    maingo.solve();
    EXPECT_EQ(true, std::filesystem::exists("tmpJsonFileForTesting.json"));
    std::filesystem::remove("tmpJsonFileForTesting.json", errorCode);

    model = std::make_shared<ProblemInfeasibleBounds>();
    maingo.set_model(model);
    maingo.solve();
    EXPECT_EQ(true, std::filesystem::exists("tmpJsonFileForTesting.json"));
    std::filesystem::remove("tmpJsonFileForTesting.json", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOwritingFunctions, WriteEpsilonConstraintResult) {
    std::error_code errorCode;
    std::filesystem::remove("MAiNGO_epsilon_constraint_objective_values.csv", errorCode);

    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicBiobjectiveModel>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("writeResultFile", false);
    maingo.set_option("writeCsv", false);
    maingo.set_option("writeJson", false);
    maingo.set_option("EC_nPoints", 2);
    maingo.solve_epsilon_constraint();

    EXPECT_EQ(true, std::filesystem::exists("MAiNGO_epsilon_constraint_objective_values.csv"));
    std::filesystem::remove("MAiNGO_epsilon_constraint_objective_values.csv", errorCode);
}