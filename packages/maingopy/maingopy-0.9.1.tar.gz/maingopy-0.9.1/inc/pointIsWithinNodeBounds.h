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

#pragma once

#include "babNode.h"

#include <vector>


namespace maingo {


/**
	* @brief Checks if a given point lies wihtin the variable bounds of a branch-and-bound node.
	*        Integrality of variables is not considered (e.g., if a binary variable has value 0.5 at the point,
	*        this is considered to be within the node bounds).
	*
	* @param[in] point is the point to be checked
	* @param[in] lowerBounds is the vector of lower variable bounds of the node
	* @param[in] upperBounds is the vector of upper variable bounds of the node
	*/
bool point_is_within_node_bounds(const std::vector<double>& point, const std::vector<double>& lowerBounds, const std::vector<double>& upperBounds);


/**
	* @brief Checks if a given point lies wihtin the variable bounds of a branch-and-bound node.
	*        Integrality of variables is not considered (e.g., if a binary variable has value 0.5 at the point,
	*        this is considered to be within the node bounds).
	*
	* @param[in] point is the point to be checked
	* @param[in] node is the branch-and-bound node to be checked
	*/
bool point_is_within_node_bounds(const std::vector<double>& point, const babBase::BabNode& node);


}    // end namespace maingo