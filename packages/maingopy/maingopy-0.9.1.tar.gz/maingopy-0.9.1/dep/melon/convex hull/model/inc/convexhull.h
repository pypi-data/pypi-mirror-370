/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file convexhull.h
*
* @brief File containing declaration of the convex hull class.
*
**********************************************************************************/

#pragma once

#include <vector>		    // std::vector
#include <string>           // std::stoi 

#include "exceptions.h"
#include "MeLOn.h"
#include "convexhullParser.h"
#include "convexhullData.h"
#include "vectorarithmetics.h"

namespace melon {

	/**
	* @class GaussianProcess
	* @brief This class represents a convex hull, to be used in the MAiNGO solver.
	*
	* This class is used to enable the solution of optimization problems in MAiNGO containing convex hull. The trained GPs can be loaded from json files created in matlab.
	*/
	template<typename T>
	class ConvexHull : public MelonModel<T> {
	private:
		std::shared_ptr<const ConvexHullData> _data;					/*!< object containing the data and parameters of the convex hull */

		/*
		*  @brief Sets data object containing model parameters.
		*
		*  @param[in] modelData is a ModelData object containing the data which defines the model
		*/
		void _set_data_object(std::shared_ptr<const ModelData> modelData) override;

	public:

		/*
		*  @brief Default Constructor
		*/
		ConvexHull() : MelonModel<T>(std::make_shared<ConvexHullParserFactory>()) {};

		/*
		*  @brief Constructor
		*
		*  @param[in] modelName is the name of the convex hull
		*/
		ConvexHull(std::string modelName) : ConvexHull() { this->load_model(modelName, MODEL_FILE_TYPE::JSON); };

		/*
		*  @brief Constructor
		*
		*  @param[in] modelPath is the path to the directory in which the convex hull file is located
		*
		*  @param[in] modelName is the name of the convex hull
		*/
		ConvexHull(std::string modelPath, std::string modelName) : ConvexHull() { this->load_model(modelPath, modelName, MODEL_FILE_TYPE::JSON); };

		/*
		*  @brief Constructor
		*
		*  @param[in] modelData is a ConvexHullData object containing the data which defines the convex hull
		*/
		ConvexHull(std::shared_ptr<const ConvexHullData> modelData) : ConvexHull() { this->load_model(modelData, MODEL_FILE_TYPE::JSON); };

		/*
		*  @brief Generates convex hull constraints
		*
		*  @param[in] input is a vector containing an input point for which is checked wether it lays within the convex hull 
		*
		*  @return returns convex hull constraints
		*/
		std::vector<T> generate_constraints(std::vector<T> input);

		/*
		*  @brief Get the dimesnion of the input
		*
		*  @return returns input dimension
		*/
		int get_input_dimension();

		/*
		*  @brief Get the number of generated constraints
		*
		*  @return returns constraint dimension
		*/
		int get_constraint_dimension();
	};

	/////////////////////////////////////////////////////////////////////////
	// Set data object containing model parameters
	template<typename T>
	void ConvexHull<T>::_set_data_object(std::shared_ptr<const ModelData> modelData) {

		// Downcast the ModelData pointer to a GPData pointer
		_data = std::dynamic_pointer_cast<const ConvexHullData>(modelData);
		if (_data == nullptr) {
			throw(MelonException("  Error while loading convex hull: Incorrect type of passed data object. The data object must be of type ConvexHullData."));
		}
	}


	/////////////////////////////////////////////////////////////////////////
	// Generates convex hull constraints
	template<typename T>
	std::vector<T> ConvexHull<T>::generate_constraints(std::vector<T> input) {
		try {
			if (!MelonModel<T>::_modelLoaded) {
				throw MelonException("  Error: No model loaded. Terminating.");
			}
			return _data->A*input + _data->b;
		}
		catch (const std::exception& e) {
			throw(MelonException("  Encountered a fatal error while generating convex hull constraints. Terminating.", e));
		}
		catch (...) {
			throw(MelonException("  Encountered a fatal error while generating convex hull constraints. Terminating."));
		}
	}


	/////////////////////////////////////////////////////////////////////////
	// Get the dimesnion of the input
	template<typename T>
	int ConvexHull<T>::get_input_dimension() {
			if (!MelonModel<T>::_modelLoaded) {
				throw MelonException("  Encountered a fatal error while obtaining convex hull input dimension: No model loaded. Terminating.");
			}
			return _data->A.front().size();
	}


	/////////////////////////////////////////////////////////////////////////
	// Get the number of generated constraints
	template<typename T>
	int ConvexHull<T>::get_constraint_dimension() {
		if (!MelonModel<T>::_modelLoaded) {
			throw MelonException("  Encountered a fatal error while obtaining convex hull constraint dimension: No model loaded. Terminating.");
		}
		return _data->A.size();
	}
}


   
