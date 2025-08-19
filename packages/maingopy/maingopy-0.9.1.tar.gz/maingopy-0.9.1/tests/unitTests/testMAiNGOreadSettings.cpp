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

#include <gtest/gtest.h>

#include <filesystem>
#include <fstream>


using maingo::MAiNGO;


///////////////////////////////////////////////////
TEST(TestMAiNGOreadSettings, NonexistingFile) {
    if (std::filesystem::exists("bogusFileName")) {
        FAIL() << "Eror testing read from non-existing file: File bogusFileName exists.";
    }

    MAiNGO maingo;
    EXPECT_NO_THROW(maingo.read_settings("bogusFileName"));
}


///////////////////////////////////////////////////
TEST(TestMAiNGOreadSettings, Existing) {
    if (std::filesystem::exists("testSettingsFile.txt")) {
        FAIL() << "Eror writing dummy file to test reading of settings: File testSettingsFile.txt already exists.";
    }

    std::ofstream file("testSettingsFile.txt");
    // Add BOM character at beginning of file (happens on some systems; MAiNGO should ignore it)
    unsigned char bom[] = {0xEF,0xBB,0xBF };
    file.write((char*)bom, sizeof(bom));
    file << "epsilonR 0.42e-2" << std::endl;
    file << "# This line is a comment." << std::endl;
    file << "# epsilonA 0.42e-2" << std::endl;
    file << "   deltaIneq 0.42e-2" << std::endl;
    file.close();

    MAiNGO maingo;
    maingo.read_settings("testSettingsFile.txt");
    EXPECT_EQ(maingo.get_option("epsilonA"), 1.0e-2);
    EXPECT_EQ(maingo.get_option("epsilonR"), 0.42e-2);
    EXPECT_EQ(maingo.get_option("deltaIneq"), 0.42e-2);
    std::filesystem::remove("testSettingsFile.txt");
}