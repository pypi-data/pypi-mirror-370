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
using maingo::MAiNGOException;


class TestProblemForWriting: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        Var x = optVars[0];
        Var y = optVars[1];
        result.objective = pow(x*y,5) + watson_dhvap(x, 100., 0.5, 0.5, 100., 2500.);
        result.ineq.push_back(pow(x,3) - y + 0.5, "constraintName");
        result.ineq.push_back(0.5, "constraintName");
        result.ineqRelaxationOnly.push_back(pow(x,3) - y + 0.5, "constraintName");
        result.ineqRelaxationOnly.push_back(0.5, "constraintName");
        result.ineqSquash.push_back(pow(x,3) - y + 0.5, "constraintName");
        result.ineqSquash.push_back(0.5, "constraintName");
        result.eq.push_back(pow(x,3) - y + 0.5, "constraintName");
        result.eq.push_back(0.5, "constraintName");
        result.eqRelaxationOnly.push_back(pow(x,3) - y + 0.5, "constraintName");
        result.eqRelaxationOnly.push_back(0.5, "constraintName");
        result.output.push_back(maingo::OutputVariable(0.5, "outputName"));
        result.output.push_back(maingo::OutputVariable(x - 0.5, "outputName"));
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "x"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "x"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "123!?_"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_BINARY));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_INTEGER));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "LOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUM"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "LOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUM"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_BINARY, "LOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUM"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_INTEGER, "LOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUMLOREMIPSUM"));
        return variables;
    }

    std::vector<double> get_initial_point() {
        return std::vector<double>(10, 0.);
    }
};


class TestProblemForWritingLongExpressions: public maingo::MAiNGOmodel {
  public:
    maingo::EvaluationContainer evaluate(const std::vector<Var> &optVars) {
        maingo::EvaluationContainer result;
        Var x = optVars[0];
        Var y = optVars[1];
        Var obj = 1;
        for (size_t i = 0; i < 20; ++i) {
            obj = obj*(obj + y);
        }
        result.objective = obj;
        return result;
    }

    std::vector<maingo::OptimizationVariable> get_variables() {
        std::vector<maingo::OptimizationVariable> variables;
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "x"));
        variables.push_back(maingo::OptimizationVariable(maingo::Bounds(0, 1), maingo::VT_CONTINUOUS, "y"));
        return variables;
    }
};


///////////////////////////////////////////////////
TEST(TestMAiNGOtoOtherLanguage, ModelNotSet) {
    MAiNGO maingo;
    EXPECT_THROW(maingo.write_model_to_file_in_other_language(maingo::LANG_ALE), MAiNGOException);
    EXPECT_THROW(maingo.write_model_to_file_in_other_language(maingo::LANG_GAMS), MAiNGOException);
    EXPECT_THROW(maingo.write_model_to_file_in_other_language(maingo::LANG_NONE), MAiNGOException);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOtoOtherLanguage, LanguageNone) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<TestProblemForWriting>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_OUTSTREAM);

    std::error_code errorCode;
    std::filesystem::remove("tmpTestFileForWritingToOtherLanguage.txt", errorCode);

    testing::internal::CaptureStdout();
    maingo.write_model_to_file_in_other_language(maingo::LANG_NONE, "tmpTestFileForWritingToOtherLanguage.txt");
    EXPECT_EQ(testing::internal::GetCapturedStdout(), "\n  WARNING: asked MAiNGO to write model to file, but chosen writing language is NONE. Not writing anything.\n");

    EXPECT_EQ(std::filesystem::exists("tmpTestFileForWritingToOtherLanguage.txt"), false);
    std::filesystem::remove("tmpTestFileForWritingToOtherLanguage.txt", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOtoOtherLanguage, LanguageGams) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<TestProblemForWriting>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    std::error_code errorCode;
    std::filesystem::remove("tmpTestFileForWritingToOtherLanguage.txt", errorCode);

    maingo.write_model_to_file_in_other_language(maingo::LANG_GAMS, "tmpTestFileForWritingToOtherLanguage.txt");
    EXPECT_EQ(std::filesystem::exists("tmpTestFileForWritingToOtherLanguage.txt"), true);
    std::filesystem::remove("tmpTestFileForWritingToOtherLanguage.txt", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOtoOtherLanguage, LanguageGamsLP) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicLP>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    std::error_code errorCode;
    std::filesystem::remove("tmpTestFileForWritingToOtherLanguage.txt", errorCode);

    maingo.write_model_to_file_in_other_language(maingo::LANG_GAMS, "tmpTestFileForWritingToOtherLanguage.txt");
    EXPECT_EQ(std::filesystem::exists("tmpTestFileForWritingToOtherLanguage.txt"), true);
    std::filesystem::remove("tmpTestFileForWritingToOtherLanguage.txt", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOtoOtherLanguage, LanguageGamsNLP) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicNLP>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    std::error_code errorCode;
    std::filesystem::remove("tmpTestFileForWritingToOtherLanguage.txt", errorCode);

    maingo.write_model_to_file_in_other_language(maingo::LANG_GAMS, "tmpTestFileForWritingToOtherLanguage.txt");
    EXPECT_EQ(std::filesystem::exists("tmpTestFileForWritingToOtherLanguage.txt"), true);
    std::filesystem::remove("tmpTestFileForWritingToOtherLanguage.txt", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOtoOtherLanguage, LanguageGamsDNLP) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicDNLP>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    std::error_code errorCode;
    std::filesystem::remove("tmpTestFileForWritingToOtherLanguage.txt", errorCode);

    maingo.write_model_to_file_in_other_language(maingo::LANG_GAMS, "tmpTestFileForWritingToOtherLanguage.txt");
    EXPECT_EQ(std::filesystem::exists("tmpTestFileForWritingToOtherLanguage.txt"), true);
    std::filesystem::remove("tmpTestFileForWritingToOtherLanguage.txt", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOtoOtherLanguage, LanguageGamsMINLP) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<BasicMINLP>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    std::error_code errorCode;
    std::filesystem::remove("tmpTestFileForWritingToOtherLanguage.txt", errorCode);

    maingo.write_model_to_file_in_other_language(maingo::LANG_GAMS, "tmpTestFileForWritingToOtherLanguage.txt");
    EXPECT_EQ(std::filesystem::exists("tmpTestFileForWritingToOtherLanguage.txt"), true);
    std::filesystem::remove("tmpTestFileForWritingToOtherLanguage.txt", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOtoOtherLanguage, LanguageGamsNoFileName) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<TestProblemForWriting>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    std::error_code errorCode;
    std::filesystem::remove("MAiNGO_written_model.gms", errorCode);

    maingo.write_model_to_file_in_other_language(maingo::LANG_GAMS);
    EXPECT_EQ(std::filesystem::exists("MAiNGO_written_model.gms"), true);
    std::filesystem::remove("MAiNGO_written_model.gms", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOtoOtherLanguage, LanguageGamsLongExpressions) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<TestProblemForWritingLongExpressions>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    std::error_code errorCode;
    std::filesystem::remove("tmpTestFileForWritingToOtherLanguage.txt", errorCode);

    maingo.write_model_to_file_in_other_language(maingo::LANG_GAMS, "tmpTestFileForWritingToOtherLanguage.txt");
    EXPECT_EQ(std::filesystem::exists("tmpTestFileForWritingToOtherLanguage.txt"), true);
    std::filesystem::remove("tmpTestFileForWritingToOtherLanguage.txt", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOtoOtherLanguage, LanguageGamsInSolve) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<TestProblemForWriting>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("modelWritingLanguage", maingo::LANG_GAMS);

    std::error_code errorCode;
    std::filesystem::remove("MAiNGO_written_model.gms", errorCode);

    maingo.solve();
    EXPECT_EQ(maingo.get_status(), maingo::INFEASIBLE);

    EXPECT_EQ(std::filesystem::exists("MAiNGO_written_model.gms"), true);
    std::filesystem::remove("MAiNGO_written_model.gms", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOtoOtherLanguage, LanguageAle) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<TestProblemForWriting>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    std::error_code errorCode;
    std::filesystem::remove("tmpTestFileForWritingToOtherLanguage.txt", errorCode);

    maingo.write_model_to_file_in_other_language(maingo::LANG_ALE, "tmpTestFileForWritingToOtherLanguage.txt");
    EXPECT_EQ(std::filesystem::exists("tmpTestFileForWritingToOtherLanguage.txt"), true);
    std::filesystem::remove("tmpTestFileForWritingToOtherLanguage.txt", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOtoOtherLanguage, LanguageAleNoFileName) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<TestProblemForWriting>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);

    std::error_code errorCode;
    std::filesystem::remove("MAiNGO_written_model.txt", errorCode);

    maingo.write_model_to_file_in_other_language(maingo::LANG_ALE);
    EXPECT_EQ(std::filesystem::exists("MAiNGO_written_model.txt"), true);
    std::filesystem::remove("MAiNGO_written_model.txt", errorCode);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOtoOtherLanguage, LanguageAleInSolve) {
    std::shared_ptr<maingo::MAiNGOmodel> model = std::make_shared<TestProblemForWriting>();
    MAiNGO maingo(model);
    maingo.set_option("loggingDestination", maingo::LOGGING_NONE);
    maingo.set_option("modelWritingLanguage", maingo::LANG_ALE);

    std::error_code errorCode;
    std::filesystem::remove("MAiNGO_written_model.txt", errorCode);

    maingo.solve();
    EXPECT_EQ(maingo.get_status(), maingo::INFEASIBLE);

    EXPECT_EQ(std::filesystem::exists("MAiNGO_written_model.txt"), true);
    std::filesystem::remove("MAiNGO_written_model.txt", errorCode);
}