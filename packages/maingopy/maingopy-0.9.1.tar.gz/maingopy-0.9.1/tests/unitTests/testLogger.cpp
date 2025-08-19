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

#include "logger.h"
#include "settings.h"

#include <gtest/gtest.h>

#include <filesystem>
#include <fstream>
#include <string>
#include <system_error>


///////////////////////////////////////////////////
// struct on which the unit test will be preformed on
struct TestLogger: testing::Test {
    std::shared_ptr<maingo::Settings> settings = std::make_shared<maingo::Settings>();
    std::shared_ptr<maingo::Logger> logger     = std::make_shared<maingo::Logger>(settings);
};


///////////////////////////////////////////////////
// testing all three versions of _get_(max_)verb on different verbosities
TEST_F(TestLogger, Verbosity)
{
    settings->loggingDestination = maingo::LOGGING_OUTSTREAM;

    testing::internal::CaptureStdout();


    // test _get_verb()

    settings->LBP_verbosity = maingo::VERB_NONE;
    settings->UBP_verbosity = maingo::VERB_NORMAL;
    settings->BAB_verbosity = maingo::VERB_ALL;

    logger->print_message("1", maingo::VERB_NONE, maingo::LBP_VERBOSITY);
    logger->print_message("2", maingo::VERB_NORMAL, maingo::LBP_VERBOSITY);
    logger->print_message("3", maingo::VERB_ALL, maingo::LBP_VERBOSITY);

    logger->print_message("4", maingo::VERB_NONE, maingo::UBP_VERBOSITY);
    logger->print_message("5", maingo::VERB_NORMAL, maingo::UBP_VERBOSITY);
    logger->print_message("6", maingo::VERB_ALL, maingo::UBP_VERBOSITY);

    logger->print_message("7", maingo::VERB_NONE, maingo::BAB_VERBOSITY);
    logger->print_message("8", maingo::VERB_NORMAL, maingo::BAB_VERBOSITY);
    logger->print_message("9", maingo::VERB_ALL, maingo::BAB_VERBOSITY);


    // test _get_max_verb() for two input verbosities

    settings->LBP_verbosity = maingo::VERB_NORMAL;
    settings->UBP_verbosity = maingo::VERB_NONE;

    logger->print_message("A", maingo::VERB_NONE, maingo::LBP_VERBOSITY, maingo::UBP_VERBOSITY);
    logger->print_message("B", maingo::VERB_NORMAL, maingo::LBP_VERBOSITY, maingo::UBP_VERBOSITY);
    logger->print_message("C", maingo::VERB_ALL, maingo::LBP_VERBOSITY, maingo::UBP_VERBOSITY);

    logger->print_message("D", maingo::VERB_NONE, maingo::UBP_VERBOSITY, maingo::LBP_VERBOSITY);
    logger->print_message("E", maingo::VERB_NORMAL, maingo::UBP_VERBOSITY, maingo::LBP_VERBOSITY);
    logger->print_message("F", maingo::VERB_ALL, maingo::UBP_VERBOSITY, maingo::LBP_VERBOSITY);

    logger->print_message("G", maingo::VERB_NONE, maingo::UBP_VERBOSITY, maingo::BAB_VERBOSITY);
    logger->print_message("H", maingo::VERB_NORMAL, maingo::UBP_VERBOSITY, maingo::BAB_VERBOSITY);
    logger->print_message("I", maingo::VERB_ALL, maingo::UBP_VERBOSITY, maingo::BAB_VERBOSITY);

    // test _get_max_verb() for three input verbosities

    settings->LBP_verbosity = maingo::VERB_ALL;
    settings->UBP_verbosity = maingo::VERB_NORMAL;
    settings->BAB_verbosity = maingo::VERB_NONE;

    logger->print_message("J", maingo::VERB_NONE, maingo::LBP_VERBOSITY, maingo::UBP_VERBOSITY, maingo::BAB_VERBOSITY);
    logger->print_message("K", maingo::VERB_NORMAL, maingo::LBP_VERBOSITY, maingo::UBP_VERBOSITY, maingo::BAB_VERBOSITY);
    logger->print_message("L", maingo::VERB_ALL, maingo::LBP_VERBOSITY, maingo::UBP_VERBOSITY, maingo::BAB_VERBOSITY);

    logger->print_message("M", maingo::VERB_NONE, maingo::BAB_VERBOSITY, maingo::BAB_VERBOSITY, maingo::BAB_VERBOSITY);
    logger->print_message("N", maingo::VERB_NORMAL, maingo::BAB_VERBOSITY, maingo::BAB_VERBOSITY, maingo::BAB_VERBOSITY);
    logger->print_message("O", maingo::VERB_ALL, maingo::BAB_VERBOSITY, maingo::BAB_VERBOSITY, maingo::BAB_VERBOSITY);


    EXPECT_EQ("145789ABDEGHIJKLM", testing::internal::GetCapturedStdout());
}


///////////////////////////////////////////////////
TEST_F(TestLogger, OutputStream)
{
    settings->LBP_verbosity = maingo::VERB_NONE;
    settings->UBP_verbosity = maingo::VERB_NORMAL;
    settings->BAB_verbosity = maingo::VERB_ALL;


    // testing setting option LOGGING_OUTSTREAM by capturing output to console
    settings->loggingDestination = maingo::LOGGING_OUTSTREAM;

    testing::internal::CaptureStdout();

    logger->print_message("1", maingo::VERB_NONE, maingo::BAB_VERBOSITY);
    logger->print_message("2", maingo::VERB_ALL, maingo::LBP_VERBOSITY);
    logger->print_message("3", maingo::VERB_NORMAL, maingo::UBP_VERBOSITY);

    // second message should not be printed
    EXPECT_EQ("13", testing::internal::GetCapturedStdout());
}


///////////////////////////////////////////////////
TEST_F(TestLogger, OutputFile)
{
    settings->LBP_verbosity = maingo::VERB_NONE;
    settings->UBP_verbosity = maingo::VERB_NORMAL;
    settings->BAB_verbosity = maingo::VERB_ALL;


    // testing setting option LOGGING_FILE
    settings->loggingDestination = maingo::LOGGING_FILE;
    testing::internal::CaptureStdout();

    logger->print_message("1", maingo::VERB_NONE, maingo::BAB_VERBOSITY);
    logger->print_message("2", maingo::VERB_ALL, maingo::LBP_VERBOSITY);
    logger->print_message("3", maingo::VERB_NORMAL, maingo::UBP_VERBOSITY);

    // second message should not be printed
    EXPECT_EQ("1", logger->babLine.front());
    logger->babLine.pop();
    EXPECT_EQ("3", logger->babLine.front());
    logger->babLine.pop();

    // nothing should have been printed to stream
    EXPECT_EQ("", testing::internal::GetCapturedStdout());
}


///////////////////////////////////////////////////
TEST_F(TestLogger, OutputClear)
{
    settings->LBP_verbosity = maingo::VERB_NONE;
    settings->UBP_verbosity = maingo::VERB_NORMAL;
    settings->BAB_verbosity = maingo::VERB_ALL;


    // testing setting option LOGGING_FILE
    settings->loggingDestination = maingo::LOGGING_FILE;

    logger->print_message("1", maingo::VERB_NONE, maingo::BAB_VERBOSITY);
    logger->print_message("2", maingo::VERB_ALL, maingo::LBP_VERBOSITY);
    logger->print_message("3", maingo::VERB_NORMAL, maingo::UBP_VERBOSITY);

    logger->clear();

    // testing clear()
    EXPECT_EQ(true, logger->babLine.empty());
}


///////////////////////////////////////////////////
TEST_F(TestLogger, OutputStreamAndFile)
{
    settings->LBP_verbosity = maingo::VERB_NONE;
    settings->UBP_verbosity = maingo::VERB_NORMAL;
    settings->BAB_verbosity = maingo::VERB_ALL;

    // testing setting option LOGGING_FILE_AND_STREAM
    settings->loggingDestination = maingo::LOGGING_FILE_AND_STREAM;

    testing::internal::CaptureStdout();

    logger->print_message("1", maingo::VERB_NONE, maingo::BAB_VERBOSITY);
    logger->print_message("2", maingo::VERB_ALL, maingo::LBP_VERBOSITY);
    logger->print_message("3", maingo::VERB_NORMAL, maingo::UBP_VERBOSITY);

    // second message should not be printed
    EXPECT_EQ("1", logger->babLine.front());
    logger->babLine.pop();
    EXPECT_EQ("3", logger->babLine.front());
    logger->babLine.pop();

    EXPECT_EQ("13", testing::internal::GetCapturedStdout());
}


///////////////////////////////////////////////////
TEST_F(TestLogger, OutputNone)
{
    settings->LBP_verbosity = maingo::VERB_NONE;
    settings->UBP_verbosity = maingo::VERB_NORMAL;
    settings->BAB_verbosity = maingo::VERB_ALL;


    // testing setting option LOGGING_NONE to suppress all output
    settings->loggingDestination = maingo::LOGGING_NONE;

    testing::internal::CaptureStdout();

    logger->print_message("1", maingo::VERB_NONE, maingo::BAB_VERBOSITY);
    logger->print_message("2", maingo::VERB_ALL, maingo::LBP_VERBOSITY);
    logger->print_message("3", maingo::VERB_NORMAL, maingo::UBP_VERBOSITY);

    // second message should not be printed
    EXPECT_EQ("", testing::internal::GetCapturedStdout());
    EXPECT_EQ(true, logger->babLine.empty());
}


///////////////////////////////////////////////////
TEST_F(TestLogger, OutputForceStreamOnly)
{
    settings->LBP_verbosity = maingo::VERB_NONE;
    settings->UBP_verbosity = maingo::VERB_NORMAL;
    settings->BAB_verbosity = maingo::VERB_ALL;


    // for LOGGING_OUTSTREAM, everything should be printed (irrespective of verbosity), but not stored for later printing to file
    settings->loggingDestination = maingo::LOGGING_OUTSTREAM;

    testing::internal::CaptureStdout();

    logger->print_message_to_stream_only("1");
    logger->print_message_to_stream_only("2");
    logger->print_message_to_stream_only("3");

    EXPECT_EQ("123", testing::internal::GetCapturedStdout());
    EXPECT_EQ(true, logger->babLine.empty());
    logger->clear();


    // for LOGGING_FILE, nothing should be printed
    settings->loggingDestination = maingo::LOGGING_FILE;

    testing::internal::CaptureStdout();

    logger->print_message_to_stream_only("1");
    logger->print_message_to_stream_only("2");
    logger->print_message_to_stream_only("3");

    EXPECT_EQ("", testing::internal::GetCapturedStdout());
    EXPECT_EQ(true, logger->babLine.empty());
    logger->clear();


    // for LOGGING_FILE_AND_STREAM, everything should be printed (considering verbosity), but not stored for later printing to file
    settings->loggingDestination = maingo::LOGGING_FILE_AND_STREAM;

    testing::internal::CaptureStdout();

    logger->print_message_to_stream_only("1");
    logger->print_message_to_stream_only("2");
    logger->print_message_to_stream_only("3");

    EXPECT_EQ("123", testing::internal::GetCapturedStdout());
    EXPECT_EQ(true, logger->babLine.empty());
    logger->clear();
}


///////////////////////////////////////////////////
//testing the output of print_vector() by capturing the output to the consol and comparing it to the expected output
TEST_F(TestLogger, PrintVector)
{
    std::vector<double> testVector = {0.0, 1.0};

    settings->LBP_verbosity      = maingo::VERB_NONE;
    settings->loggingDestination = maingo::LOGGING_OUTSTREAM;


    // capturing output of print_vector second statement should not create output
    testing::internal::CaptureStdout();

    logger->print_vector(2, testVector, "TestString", maingo::VERB_NONE, maingo::LBP_VERBOSITY);
    logger->print_vector(1, testVector, "TestString", maingo::VERB_NORMAL, maingo::LBP_VERBOSITY);


    std::string output = testing::internal::GetCapturedStdout();


    // expected output
    std::ostringstream compString;

    compString << "TestString" << std::endl;
    for (unsigned int i = 0; i < 2; i++) {
        compString << "   x(" << i << "): " << testVector[i] << std::endl;
    }


    EXPECT_EQ(compString.str(), output);

    // expecting error if the numbers of values to be printed exceed the number of elements in the testVector
    ASSERT_ANY_THROW(logger->print_vector(3, testVector, "TestString", maingo::VERB_NONE, maingo::LBP_VERBOSITY));
}


///////////////////////////////////////////////////
TEST_F(TestLogger, CreateLogFile)
{
    logger->logFileName = "tmpLogFileForTesting.log";

    // For LOGGING_FILE, should create a log file
    settings->loggingDestination = maingo::LOGGING_FILE;
    std::error_code errorCode;
    std::filesystem::remove("tmpLogFileForTesting.log", errorCode);
    logger->create_log_file();
    EXPECT_EQ(true, std::filesystem::exists("tmpLogFileForTesting.log"));
    std::filesystem::remove("tmpLogFileForTesting.log", errorCode);


    // For LOGGING_FILE_AND_STREAM, should create a log file
    settings->loggingDestination = maingo::LOGGING_FILE_AND_STREAM;
    std::filesystem::remove("tmpLogFileForTesting.log", errorCode);
    logger->create_log_file();
    EXPECT_EQ(true, std::filesystem::exists("tmpLogFileForTesting.log"));
    std::filesystem::remove("tmpLogFileForTesting.log", errorCode);


    // For LOGGING_OUTSTREAM, no log file should be created
    settings->loggingDestination = maingo::LOGGING_OUTSTREAM;
    std::filesystem::remove("tmpLogFileForTesting.log", errorCode);
    logger->create_log_file();
    EXPECT_EQ(false, std::filesystem::exists("tmpLogFileForTesting.log"));
    std::filesystem::remove("tmpLogFileForTesting.log", errorCode);
}


///////////////////////////////////////////////////
TEST_F(TestLogger, WriteToLogFile)
{
    settings->LBP_verbosity = maingo::VERB_NONE;
    settings->UBP_verbosity = maingo::VERB_NORMAL;
    settings->BAB_verbosity = maingo::VERB_ALL;
    logger->logFileName = "tmpLogFileForTesting.log";


    // If logging destination includes file, should write log
    settings->loggingDestination = maingo::LOGGING_FILE;
    std::error_code errorCode;
    std::filesystem::remove("tmpLogFileForTesting.log", errorCode);
    logger->print_message("1\n", maingo::VERB_NONE, maingo::BAB_VERBOSITY);
    logger->print_message("2\n", maingo::VERB_ALL, maingo::LBP_VERBOSITY);
    logger->print_message("3\n", maingo::VERB_NORMAL, maingo::UBP_VERBOSITY);
    logger->write_all_lines_to_log("test error message at end");

    std::ifstream file;
    file.open("tmpLogFileForTesting.log");
    if (file.is_open()) {
        std::string line;;
        std::getline(file, line);
        EXPECT_EQ("1", line);
        std::getline(file, line);
        EXPECT_EQ("3", line);
        std::getline(file, line);
        EXPECT_EQ("test error message at end", line);
        std::getline(file, line);
        EXPECT_EQ(true, file.eof());
    } else {
        FAIL() << "Failed to open tmpLogFileForTesting.log";
    }
    std::filesystem::remove("tmpLogFileForTesting.log", errorCode);


    // If logging destination is only outstream, should not write log
    settings->loggingDestination = maingo::LOGGING_OUTSTREAM;

    testing::internal::CaptureStdout();
    logger->print_message("1", maingo::VERB_NONE, maingo::BAB_VERBOSITY);
    logger->print_message("2", maingo::VERB_ALL, maingo::LBP_VERBOSITY);
    logger->print_message("3", maingo::VERB_NORMAL, maingo::UBP_VERBOSITY);
    logger->write_all_lines_to_log("test error message at end");
    testing::internal::GetCapturedStdout();

    file.open("tmpLogFileForTesting.log");
    if (file.is_open()) {
        EXPECT_EQ(true, file.eof());
    } else {
        FAIL() << "Failed to open tmpLogFileForTesting.log";
    }
    std::filesystem::remove("tmpLogFileForTesting.log", errorCode);
}


///////////////////////////////////////////////////
TEST_F(TestLogger, CreateIterationsCsvFile)
{
    // Iterations csv file should be created irrespective of logging destination, but only if writeCsv is true
    settings->loggingDestination = maingo::LOGGING_OUTSTREAM;
    logger->csvIterationsName = "tmpIterationsCsvForTesting.csv";
    std::error_code errorCode;
    std::filesystem::remove("tmpIterationsCsvForTesting.csv", errorCode);

    logger->create_iterations_csv_file(true);
    EXPECT_EQ(true, std::filesystem::exists("tmpIterationsCsvForTesting.csv"));
    std::filesystem::remove("tmpIterationsCsvForTesting.csv", errorCode);


    logger->create_iterations_csv_file(false);
    EXPECT_EQ(false, std::filesystem::exists("tmpIterationsCsvForTesting.csv"));
    std::filesystem::remove("tmpIterationsCsvForTesting.csv", errorCode);
}


///////////////////////////////////////////////////
TEST_F(TestLogger, WriteToIterationsCsvFile)
{
    std::error_code errorCode;
    std::filesystem::remove("tmpIterationsCsvForTesting.csv", errorCode);
    logger->csvIterationsName = "tmpIterationsCsvForTesting.csv";

    logger->babLineCsv.push("Line 1\n");
    logger->babLineCsv.push("Line 2\n");

    logger->write_all_iterations_to_csv();


    std::ifstream file;
    file.open("tmpIterationsCsvForTesting.csv");
    if (file.is_open()) {
        std::string line;;
        std::getline(file, line);
        EXPECT_EQ("Line 1", line);
        std::getline(file, line);
        EXPECT_EQ("Line 2", line);
        std::getline(file, line);
        EXPECT_EQ(true, file.eof());
    } else {
        FAIL() << "Failed to open tmpIterationsCsvForTesting.csv";
    }
    std::filesystem::remove("tmpIterationsCsvForTesting.csv", errorCode);
}


///////////////////////////////////////////////////
TEST_F(TestLogger, PrintSettingsNothingChanged)
{
    settings->LBP_verbosity = maingo::VERB_NONE;
    settings->UBP_verbosity = maingo::VERB_NORMAL;
    settings->BAB_verbosity = maingo::VERB_ALL;
    settings->loggingDestination = maingo::LOGGING_OUTSTREAM;

    testing::internal::CaptureStdout();
    logger->print_settings(maingo::VERB_NONE, maingo::BAB_VERBOSITY);
    EXPECT_EQ("", testing::internal::GetCapturedStdout());

    testing::internal::CaptureStdout();
    logger->print_settings(maingo::VERB_NORMAL, maingo::BAB_VERBOSITY, maingo::LBP_VERBOSITY);
    EXPECT_EQ("", testing::internal::GetCapturedStdout());

    testing::internal::CaptureStdout();
    logger->print_settings(maingo::VERB_NORMAL, maingo::BAB_VERBOSITY, maingo::LBP_VERBOSITY, maingo::UBP_VERBOSITY);
    EXPECT_EQ("", testing::internal::GetCapturedStdout());
}


///////////////////////////////////////////////////
TEST_F(TestLogger, PrintSettingsSettingsChanged)
{
    settings->LBP_verbosity = maingo::VERB_NONE;
    settings->UBP_verbosity = maingo::VERB_NORMAL;
    settings->BAB_verbosity = maingo::VERB_ALL;
    settings->loggingDestination = maingo::LOGGING_OUTSTREAM;

    logger->save_setting(maingo::SETTING_NAMES::EPSILONA, "epsilon A: 1e-42");
    logger->save_setting(maingo::SETTING_NAMES::EPSILONR, "epsilon R: 1e-43");
    logger->save_setting(maingo::SETTING_NAMES::UNKNOWN_SETTING, "unknown setting 1: not known!");
    logger->save_setting(maingo::SETTING_NAMES::UNKNOWN_SETTING, "unknown setting 2: not known!");

    testing::internal::CaptureStdout();
    logger->print_settings(maingo::VERB_NORMAL, maingo::BAB_VERBOSITY);
    EXPECT_EQ("  Settings set by the user:\n    epsilon A: 1e-42\n    epsilon R: 1e-43\n    unknown setting 1: not known!\n    unknown setting 2: not known!\n  Done.\n", testing::internal::GetCapturedStdout());

    testing::internal::CaptureStdout();
    logger->print_settings(maingo::VERB_NORMAL, maingo::BAB_VERBOSITY, maingo::LBP_VERBOSITY);
    EXPECT_EQ("  Settings set by the user:\n    epsilon A: 1e-42\n    epsilon R: 1e-43\n    unknown setting 1: not known!\n    unknown setting 2: not known!\n  Done.\n", testing::internal::GetCapturedStdout());

    testing::internal::CaptureStdout();
    logger->print_settings(maingo::VERB_NORMAL, maingo::BAB_VERBOSITY, maingo::LBP_VERBOSITY, maingo::UBP_VERBOSITY);
    EXPECT_EQ("  Settings set by the user:\n    epsilon A: 1e-42\n    epsilon R: 1e-43\n    unknown setting 1: not known!\n    unknown setting 2: not known!\n  Done.\n", testing::internal::GetCapturedStdout());
}


///////////////////////////////////////////////////
TEST_F(TestLogger, PrintSettingsFileNameChangedSuccessful)
{
    settings->LBP_verbosity = maingo::VERB_NONE;
    settings->UBP_verbosity = maingo::VERB_NORMAL;
    settings->BAB_verbosity = maingo::VERB_ALL;
    settings->loggingDestination = maingo::LOGGING_OUTSTREAM;

    // user specified settings file, which was successfully read 
    logger->save_settings_file_name("myFileName", true);
    testing::internal::CaptureStdout();
    logger->print_settings(maingo::VERB_NORMAL, maingo::BAB_VERBOSITY);
    EXPECT_EQ("  \n  Read settings from file myFileName.\n", testing::internal::GetCapturedStdout());

    // user specified settings file, which was successfully read 
    logger->save_setting(maingo::SETTING_NAMES::EPSILONA, "epsilon A: 1e-42");
    testing::internal::CaptureStdout();
    logger->print_settings(maingo::VERB_NORMAL, maingo::BAB_VERBOSITY);
    EXPECT_EQ("  \n  Read settings from file myFileName.\n  Settings set by the user:\n    epsilon A: 1e-42\n  Done.\n", testing::internal::GetCapturedStdout());
}


///////////////////////////////////////////////////
TEST_F(TestLogger, PrintSettingsFileNameChangedUnsuccessful)
{
    settings->LBP_verbosity = maingo::VERB_NONE;
    settings->UBP_verbosity = maingo::VERB_NORMAL;
    settings->BAB_verbosity = maingo::VERB_ALL;
    settings->loggingDestination = maingo::LOGGING_OUTSTREAM;

    // user specified settings file, which was *not* successfully read 
    logger->save_settings_file_name("myFileName", false);
    testing::internal::CaptureStdout();
    logger->print_settings(maingo::VERB_NORMAL, maingo::BAB_VERBOSITY);
    EXPECT_EQ("  \n  Warning: Could not open settings file myFileName.\n           Proceeding with default settings.\n", testing::internal::GetCapturedStdout());

    // user specified settings file, which was *not* successfully read 
    logger->save_settings_file_name("MAiNGOSettings.txt", false);
    testing::internal::CaptureStdout();
    logger->print_settings(maingo::VERB_NORMAL, maingo::BAB_VERBOSITY);
    EXPECT_EQ("  \n  Warning: Could not open settings file with default name MAiNGOSettings.txt.\n           Proceeding with default settings.\n  \n  Warning: Could not open settings file myFileName.\n           Proceeding with default settings.\n", testing::internal::GetCapturedStdout());
}