/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file convexhullData.h
*
* @brief File containing declaration of a struct for storing convexhull data
*
**********************************************************************************/

#pragma once

#include "modelData.h"

namespace melon {

	/*
	* @struct ConvexHullData
	*
	* @brief struct containing all information regarding the convex hull
	*/
	struct ConvexHullData :  ModelData{
		std::vector<std::vector<double>> A;
		std::vector<double> b;
	};
}