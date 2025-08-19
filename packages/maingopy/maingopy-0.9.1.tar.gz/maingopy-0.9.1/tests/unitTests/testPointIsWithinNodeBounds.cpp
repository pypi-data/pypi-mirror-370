/**********************************************************************************
 * Copyright (c) 2023 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#include "pointIsWithinNodeBounds.h"

#include "babNode.h"

#include <gtest/gtest.h>


using maingo::point_is_within_node_bounds;


///////////////////////////////////////////////////
struct TestPointIsWithinNodeBounds: testing::Test {
    const std::vector<double> lowerBounds = {0., -1., -2., 1.};
    const std::vector<double> upperBounds = {1., 1., -1., 1.};

    const babBase::BabNode node{42. /*pruning score*/, lowerBounds, upperBounds, 0 /*index data set*/, -1 /*parent ID*/, 0 /*ID*/, 0 /*depth*/, false /*augment data*/};
};


///////////////////////////////////////////////////
TEST_F(TestPointIsWithinNodeBounds, AcceptsPointsWithinBounds)
{
    std::vector<double> point = {0.5, 0., -1.5, 1.};
    EXPECT_EQ(point_is_within_node_bounds(point, lowerBounds, upperBounds), true);
    EXPECT_EQ(point_is_within_node_bounds(point, node), true);

    point = {0., -1., -2, 1.};
    EXPECT_EQ(point_is_within_node_bounds(point, lowerBounds, upperBounds), true);
    EXPECT_EQ(point_is_within_node_bounds(point, node), true);

    point = {1., 1., -1, 1.};
    EXPECT_EQ(point_is_within_node_bounds(point, lowerBounds, upperBounds), true);
    EXPECT_EQ(point_is_within_node_bounds(point, node), true);
}


///////////////////////////////////////////////////
TEST_F(TestPointIsWithinNodeBounds, DetectsPointOutsideBounds)
{

    std::vector<double> point = {-1., 0., -1.5, 1.};
    EXPECT_EQ(point_is_within_node_bounds(point, lowerBounds, upperBounds), false);
    EXPECT_EQ(point_is_within_node_bounds(point, node), false);

    point = {1.5, 0., -1.5, 1.};
    EXPECT_EQ(point_is_within_node_bounds(point, lowerBounds, upperBounds), false);
    EXPECT_EQ(point_is_within_node_bounds(point, node), false);

    point = {0.5, 0., -2.5, 1.};
    EXPECT_EQ(point_is_within_node_bounds(point, lowerBounds, upperBounds), false);
    EXPECT_EQ(point_is_within_node_bounds(point, node), false);

    point = {0.5, 0., -0.5, 1.};
    EXPECT_EQ(point_is_within_node_bounds(point, lowerBounds, upperBounds), false);
    EXPECT_EQ(point_is_within_node_bounds(point, node), false);

    point = {0.5, 0., -1.5, 1. - 1e-6};
    EXPECT_EQ(point_is_within_node_bounds(point, lowerBounds, upperBounds), false);
    EXPECT_EQ(point_is_within_node_bounds(point, node), false);

    point = {0.5, 0., -1.5, 1. + 1e-6};
    EXPECT_EQ(point_is_within_node_bounds(point, lowerBounds, upperBounds), false);
    EXPECT_EQ(point_is_within_node_bounds(point, node), false);
}