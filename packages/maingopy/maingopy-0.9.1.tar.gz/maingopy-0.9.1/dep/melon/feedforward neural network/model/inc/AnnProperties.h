/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file AnnProperties.h
*
* @brief File containing declaration of enums and structs for ann properties.
*
**********************************************************************************/

#pragma once

#include <vector>	// std::vector
#include <memory>	// std::shared_ptr

#include "modelData.h"
#include "scaler.h"


namespace melon {
	/**
	*  @enum ACTIVATION_FUNCTION
	*  @brief Enum for representing the available types of activation functions
	*/
	enum ACTIVATION_FUNCTION {
		PURE_LIN = 0,           /*!< no activation function (y=x)*/
		TANH,                   /*!< tanh */
		RELU,                   /*!< ReLU */
		RELU6,                  /*!< ReLU that is bounded to a maximal value of 6*/
	};


	/**
	*  @struct AnnStructure
	*  @brief struct containing all information regarding the structure of a feedforward neural network
	*/
	struct AnnStructure {
		int numLayers;                                          /*!< Number of network layers */
		int inputSize;                                          /*!< Size of the input vector */
		std::vector<int> layerSize;                             /*!< Vector containing the size of each layer */
		std::vector<ACTIVATION_FUNCTION> activationFunction;    /*!< Vector containing the type of activation function for each layer */
		std::vector<int> biasConnect;                           /*!< Vector containing an indicator for each layer that shows wether this layer has a bias or not */
		std::vector<int> inputConnect;                          /*!< Vector containing an indicator for each layer that shows wether the network input is incident to this layer or not*/
		std::vector<std::vector<int>> layerConnect;             /*!< 2D-Vector Indication the connections of each layer*/
		bool scaledInput;										/*!< Flag indicating if scaling is used for input*/
		bool normalizedOutput;									/*!< Flag indicating if output should be normalized*/
	};


	/**
	*  @struct AnnWeights
	*  @brief struct containing the different weights of a feedforward neural network
	*/
	struct AnnWeights {
		std::vector<std::vector<double>> biasWeight;                                /*!< 2D-vector containing the biases for all neurons in the network. First dimension: layer; second dimension: neuron within that layer*/
		std::vector<std::vector<std::vector<double>>> inputWeight;                  /*!< 3D-vector containing the weights that are used for the network inputs at neurons they are incident to. First dimension: layer; second dimension: neuron within that layer; third dimension: input variable*/
		std::vector<std::vector<std::vector<std::vector<double>>>> layerWeight;     /*!< 4D-vector containing the weights for inter layer connections. First dimension: target layer; second dimension: source layer; third dimension: neurons within target layer; fourth dimension: neurons within source layer*/
	};


	/**
	*  @struct AnnNormalizationParameters
	*  @brief struct containing the parameters required for input normalization and output denormalization of a feedforward neural network
	*/
	struct AnnNormalizationParameters {
		std::vector<double> inputLowerBound;                /*!< Vector containing the lower bounds of the input (Min-Max-Normalization is used for input)*/
		std::vector<double> inputUpperBound;                /*!< Vector containing the upper bounds of the input (Min-Max-Normalization is used for input)*/
		std::vector<double> outputDenormalizationFactor;    /*!< Vector containing denormalizaiton factors *a* of the output for any linear denormlaization x = a*x_norm + b */
		std::vector<double> outputDenormalizationOffset;    /*!< Vector containing denormalizaiton offsets *b* of the output for any linear denormlaization x = a*x_norm + b */

	};


	/**
	*  @struct AnnData
	*  @brief struct containing all information regarding the structure of a feedforward neural network
	*/
	struct AnnData : virtual public ModelData {
		AnnStructure structure;                                 /*!< struct containing the information about the networks structure (e.g. numbeer of layers, connections,...) */
		AnnWeights weights;                                     /*!< struct containing the networks weights (layers-, bias- and inputweights)  */
		std::shared_ptr<ScalerData> inputScalerData;			/*!< Object containing the data for the input scaling*/
		std::shared_ptr<ScalerData> outputScalerData;			/*!< Object containing the data for the output scaling*/
	};
}