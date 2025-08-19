/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file modelData.h
*
* @brief File containing declaration of the ModelData struct.
*
**********************************************************************************/

#pragma once 

/**
*  @struct ModelData
*  @brief Abstract class from which specific model data object can be derived and enabling polymorphism
*/
struct ModelData {
// removed protected keyword for pybind 
// protected:
	ModelData() = default;
	virtual ~ModelData() = default;
};