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

#include <cassert>
#include <string>


namespace maingo {


/////////////////////////////////////////////////////////////////////////
// version using two vectors for the node bounds
bool
point_is_within_node_bounds(const std::vector<double>& point, const std::vector<double>& lowerBounds, const std::vector<double>& upperBounds)
{
    //if(point.empty()) return false;
    assert(lowerBounds.size() == upperBounds.size());
    assert(lowerBounds.size() == point.size());

    for (size_t i = 0; i < point.size(); ++i) {
        if ((point[i] > upperBounds[i]) || (point[i] < lowerBounds[i])) {
            return false;
        }
    }

    return true;
}


/////////////////////////////////////////////////////////////////////////
// version using a BabNode for the node bounds
bool
point_is_within_node_bounds(const std::vector<double>& point, const babBase::BabNode& node)
{
    return point_is_within_node_bounds(point, node.get_lower_bounds(), node.get_upper_bounds());
}


}    // end namespace maingo