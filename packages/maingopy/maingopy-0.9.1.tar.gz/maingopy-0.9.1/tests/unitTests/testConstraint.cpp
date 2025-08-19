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

#include "constraint.h"

#include <gtest/gtest.h>


using maingo::Constraint;
using maingo::CONSTRAINT_CONVEXITY;
using maingo::CONSTRAINT_DEPENDENCY;
using maingo::CONSTRAINT_MONOTONICITY;
using maingo::CONSTRAINT_TYPE;


///////////////////////////////////////////////////
TEST(TestConstraint, DefaultConstruct)
{
    Constraint con;
    EXPECT_EQ(con.name, "");
    EXPECT_EQ(con.isFeasible, true);
    EXPECT_EQ(con.type, CONSTRAINT_TYPE::TYPE_UNKNOWN);
    EXPECT_EQ(con.convexity, CONSTRAINT_CONVEXITY::CONV_NONE);
    EXPECT_EQ(con.monotonicity, CONSTRAINT_MONOTONICITY::MON_NONE);
    EXPECT_EQ(con.dependency, CONSTRAINT_DEPENDENCY::DEP_UNKNOWN);
    EXPECT_EQ(con.nparticipatingVariables, 0);
}


///////////////////////////////////////////////////
TEST(TestConstraint, ConstructNonConstant)
{
    Constraint con(CONSTRAINT_TYPE::INEQ, 0, 1, 2, 3, "my constraint");
    EXPECT_EQ(con.name, "my constraint");
    EXPECT_EQ(con.type, maingo::CONSTRAINT_TYPE::INEQ);
    EXPECT_EQ(con.convexity, maingo::CONSTRAINT_CONVEXITY::CONV_NONE);
    EXPECT_EQ(con.monotonicity, maingo::CONSTRAINT_MONOTONICITY::MON_NONE);
    EXPECT_EQ(con.dependency, maingo::CONSTRAINT_DEPENDENCY::DEP_UNKNOWN);
    EXPECT_EQ(con.indexOriginal, 0);
    EXPECT_EQ(con.indexType, 1);
    EXPECT_EQ(con.indexNonconstant, 2);
    EXPECT_EQ(con.indexTypeNonconstant, 3);
}


///////////////////////////////////////////////////
TEST(TestConstraint, ConstructNonConstantWithoutName)
{
    Constraint con(CONSTRAINT_TYPE::OBJ, 0, 1, 2, 3);
    EXPECT_EQ(con.name, "obj2");

    con = Constraint(CONSTRAINT_TYPE::INEQ, 0, 1, 2, 3);
    EXPECT_EQ(con.name, "ineq2");

    con = Constraint(CONSTRAINT_TYPE::EQ, 0, 1, 2, 3);
    EXPECT_EQ(con.name, "eq2");

    con = Constraint(CONSTRAINT_TYPE::INEQ_REL_ONLY, 0, 1, 2, 3);
    EXPECT_EQ(con.name, "relOnlyIneq2");

    con = Constraint(CONSTRAINT_TYPE::EQ_REL_ONLY, 0, 1, 2, 3);
    EXPECT_EQ(con.name, "relOnlyEq2");

    con = Constraint(CONSTRAINT_TYPE::INEQ_SQUASH, 0, 1, 2, 3);
    EXPECT_EQ(con.name, "squashIneq2");

    con = Constraint(CONSTRAINT_TYPE::AUX_EQ_REL_ONLY, 0, 1, 2, 3);
    EXPECT_EQ(con.name, "auxRelOnlyEq2");

    con = Constraint(CONSTRAINT_TYPE::OUTPUT, 0, 1, 2, 3);
    EXPECT_EQ(con.name, "output2");

    con = Constraint(CONSTRAINT_TYPE::TYPE_UNKNOWN, 0, 1, 2, 3);
    EXPECT_EQ(con.name, "constraint2");

    con = Constraint((CONSTRAINT_TYPE)-42, 0, 1, 2, 3);
    EXPECT_EQ(con.name, "constraint2");
}


///////////////////////////////////////////////////
TEST(TestConstraint, ConstructConstant)
{
    Constraint con(CONSTRAINT_TYPE::INEQ, 0, 1, 2, 3, true, false, 42.0, "my constraint");
    EXPECT_EQ(con.name, "my constraint");
    EXPECT_EQ(con.type, maingo::CONSTRAINT_TYPE::INEQ);
    EXPECT_EQ(con.convexity, maingo::CONSTRAINT_CONVEXITY::CONV_NONE);
    EXPECT_EQ(con.monotonicity, maingo::CONSTRAINT_MONOTONICITY::MON_NONE);
    EXPECT_EQ(con.dependency, maingo::CONSTRAINT_DEPENDENCY::DEP_UNKNOWN);
    EXPECT_EQ(con.indexOriginal, 0);
    EXPECT_EQ(con.indexType, 1);
    EXPECT_EQ(con.indexConstant, 2);
    EXPECT_EQ(con.indexTypeConstant, 3);
    EXPECT_EQ(con.isConstant, true);
    EXPECT_EQ(con.isFeasible, false);
    EXPECT_EQ(con.constantValue, 42.0);
}


///////////////////////////////////////////////////
TEST(TestConstraint, ConstructConstantWithoutName)
{
    Constraint con(CONSTRAINT_TYPE::OBJ, 0, 1, 2, 3, true, false, 42.0);
    EXPECT_EQ(con.name, "obj2");

    con = Constraint(CONSTRAINT_TYPE::INEQ, 0, 1, 2, 3, true, false, 42.0);
    EXPECT_EQ(con.name, "ineq2");

    con = Constraint(CONSTRAINT_TYPE::EQ, 0, 1, 2, 3, true, false, 42.0);
    EXPECT_EQ(con.name, "eq2");

    con = Constraint(CONSTRAINT_TYPE::INEQ_REL_ONLY, 0, 1, 2, 3, true, false, 42.0);
    EXPECT_EQ(con.name, "relOnlyIneq2");

    con = Constraint(CONSTRAINT_TYPE::EQ_REL_ONLY, 0, 1, 2, 3, true, false, 42.0);
    EXPECT_EQ(con.name, "relOnlyEq2");

    con = Constraint(CONSTRAINT_TYPE::INEQ_SQUASH, 0, 1, 2, 3, true, false, 42.0);
    EXPECT_EQ(con.name, "squashIneq2");

    con = Constraint(CONSTRAINT_TYPE::AUX_EQ_REL_ONLY, 0, 1, 2, 3, true, false, 42.0);
    EXPECT_EQ(con.name, "auxRelOnlyEq2");

    con = Constraint(CONSTRAINT_TYPE::OUTPUT, 0, 1, 2, 3, true, false, 42.0);
    EXPECT_EQ(con.name, "output2");

    con = Constraint(CONSTRAINT_TYPE::TYPE_UNKNOWN, 0, 1, 2, 3, true, false, 42.0);
    EXPECT_EQ(con.name, "constraint2");

    con = Constraint((CONSTRAINT_TYPE)-42, 0, 1, 2, 3, true, false, 42.0);
    EXPECT_EQ(con.name, "constraint2");
}