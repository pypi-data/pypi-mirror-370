/**********************************************************************************
 * Copyright (c) 2019-2024 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#include "decayingProbability.h"

#include <cmath>
#include <cstdlib>


namespace maingo {


bool
do_based_on_decaying_probability(const double decayCoefficient, const double decisionVariable)
{
    const double probabilityThreshold = std::exp(-decayCoefficient * decisionVariable);
    const double randomNumber         = std::rand() / ((double)RAND_MAX);
    return randomNumber <= probabilityThreshold;
}


}    // end namespace maingo