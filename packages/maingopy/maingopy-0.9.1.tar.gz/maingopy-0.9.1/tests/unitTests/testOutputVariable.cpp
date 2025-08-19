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

#include "outputVariable.h"

#include <gtest/gtest.h>


using maingo::OutputVariable;


///////////////////////////////////////////////////
TEST(TestOutputVariable, Construct)
{
    OutputVariable empytVar;
    EXPECT_EQ(empytVar.value, mc::FFVar());
    EXPECT_EQ(empytVar.description, "");

    mc::FFVar ffVar = 42;
    OutputVariable var1(ffVar, "the answer");
    EXPECT_EQ(var1.value, ffVar);
    EXPECT_EQ(var1.description, "the answer");

    OutputVariable var2("the answer", ffVar);
    EXPECT_EQ(var2.value, ffVar);
    EXPECT_EQ(var2.description, "the answer");

    std::tuple<mc::FFVar, std::string> myTuple1(ffVar, "the answer");
    OutputVariable var3(myTuple1);
    EXPECT_EQ(var3.value, ffVar);
    EXPECT_EQ(var3.description, "the answer");

    std::tuple<std::string, mc::FFVar> myTuple2("the answer", ffVar);
    OutputVariable var4(myTuple2);
    EXPECT_EQ(var4.value, ffVar);
    EXPECT_EQ(var4.description, "the answer");
}


///////////////////////////////////////////////////
TEST(TestOutputVariable, Copy)
{
    mc::FFVar ffVar = 42;
    OutputVariable var1(ffVar, "the answer");
    EXPECT_EQ(var1.value, ffVar);
    EXPECT_EQ(var1.description, "the answer");

    OutputVariable var2(var1);
    EXPECT_EQ(var2.value, ffVar);
    EXPECT_EQ(var2.description, "the answer");

    var1.value = ffVar + 1.5;
    OutputVariable var3(var1);
    EXPECT_EQ(var3.value, ffVar + 1.5);
    EXPECT_EQ(var3.description, "the answer");

    OutputVariable var4;
    var4 = var2;
    EXPECT_EQ(var4.value, ffVar);
    EXPECT_EQ(var4.description, "the answer");
}