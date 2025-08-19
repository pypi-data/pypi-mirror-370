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

#include "MAiNGOException.h"

#include "babNode.h"

#include <gtest/gtest.h>

#include <string>
#include <vector>


using maingo::MAiNGOException;


///////////////////////////////////////////////////
TEST(TestMAiNGOException, ErrorMessage)
{
    const MAiNGOException e("my error message");
    const std::string msg = e.what();
    EXPECT_EQ("my error message", msg);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOException, CatchAsStdException)
{
    std::string msg;
    try {
        throw MAiNGOException("my error message");
    }
    catch(std::exception& e) {
        msg = e.what();
    }
    EXPECT_EQ("my error message", msg);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOException, ConstructFromOtherException)
{
    const std::runtime_error originalException("original error message");
    const MAiNGOException e("my error message", originalException);
    const std::string msg = e.what();
    EXPECT_EQ("  Original exception type: ", msg.substr(0, 27));
    EXPECT_EQ(": \n   original error message\nmy error message", msg.substr(msg.length()-45,47));
}


///////////////////////////////////////////////////
TEST(TestMAiNGOException, ConstructWithBabNode)
{
    babBase::BabNode node(42, std::vector<double>(1, 0.), std::vector<double>(1, 1.), 0, 0, 1, 2, true);
    const MAiNGOException e("my error message", node);
    const std::string msg = e.what();
    EXPECT_EQ("my error message\n  Exception was thrown while processing node no. 1:\n    x(0): 0:1", msg);
}


///////////////////////////////////////////////////
TEST(TestMAiNGOException, ConstructWithBabNodeFromOtherException)
{
    babBase::BabNode node(42, std::vector<double>(1, 0.), std::vector<double>(1, 1.), 0, 0, 1, 2, true);
    const std::runtime_error originalException("original error message");
    const MAiNGOException e("my error message", originalException, node);
    const std::string msg = e.what();

    EXPECT_EQ("  Original exception type: ", msg.substr(0, 27));
    EXPECT_EQ(": \n   original error message\nmy error message\n  Exception was thrown while processing node no. 1:\n    x(0): 0:1", msg.substr(msg.length()-111,115));
}