/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file svmData.h
*
* @brief File containing declaration of a struct for storing SVM data.
*
**********************************************************************************/

#pragma once

#include <vector>		// std::vector
#include <memory>		// std::shared_ptr, std::unique_ptr

#include "modelData.h"
#include "scaler.h"
#include "kernel.h"

namespace melon {

	/**
	*@enum KERNEL_FUNCTION
	*@brief enum for representing different kernel functions
	*/
	enum KERNEL_FUNCTION {
		RBF                   /*!< Radial Basis Kernel */
	};

	/**
	* @struct SvmData
	*
	* @brief Struct containing all information regarding the support vector machine
	*/
	struct SvmData : public ModelData {
		double rho;												/*!< Constant parameter of the hyperplane*/
		std::vector<std::vector<double>> supportVectors;		/*!< Vector of support vectors*/
		std::vector<double> dualCoefficients;					/*!< Vector with dual coefficients of descision function */
		
		KERNEL_FUNCTION kernelFunction;							/*!< Specification which kernel function should be used */
		std::vector<double> kernelParameters;					/*!< Vector with kernel parameters where the meaning of the parameters depends on which kernel function is specified */
		
		std::shared_ptr<const ScalerData> inputScalerData;		/*!< Object containing the data for the input scaling*/
		std::shared_ptr<const ScalerData> outputScalerData;		/*!< Object containing the data for the output scaling*/
	};
}