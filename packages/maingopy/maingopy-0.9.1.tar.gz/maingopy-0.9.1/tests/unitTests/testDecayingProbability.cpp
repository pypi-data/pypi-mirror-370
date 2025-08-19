/**********************************************************************************
 * Copyright (c) 2021 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#include "decayingProbability.h"

#include <gtest/gtest.h>


///////////////////////////////////////////////////
// testing if an optional step is always conducted if the decay coefficient is zero
TEST(TestDecayingProbability, TestZeroDecay)
{

    const double decayCoefficient = 0.;

    bool alwaysDecidedToDoOptionalStep = true;

    const size_t nTrials = 100;
    for (size_t i = 0; i < nTrials; ++i) {
        const double babNodeDepth = i;
        if (maingo::do_based_on_decaying_probability(decayCoefficient, babNodeDepth) == false) {
            alwaysDecidedToDoOptionalStep = false;
            break;
        }
    }

    EXPECT_TRUE(alwaysDecidedToDoOptionalStep);
}


///////////////////////////////////////////////////
// testing if an optional step is always conducted at zero depth
TEST(TestDecayingProbability, TestZeroDepth)
{

    const double babNodeDepth = 0.;

    bool alwaysDecidedToDoOptionalStep = true;

    const size_t nTrials = 100;
    for (size_t i = 0; i < nTrials; ++i) {
        const double decayCoefficient = ((double)i) / ((double)nTrials);
        if (maingo::do_based_on_decaying_probability(decayCoefficient, babNodeDepth) == false) {
            alwaysDecidedToDoOptionalStep = false;
            break;
        }
    }

    EXPECT_TRUE(alwaysDecidedToDoOptionalStep);
}