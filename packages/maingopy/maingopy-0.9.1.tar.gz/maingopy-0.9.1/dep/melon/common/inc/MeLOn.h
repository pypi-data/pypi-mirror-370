/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file MeLOn.h
*
* @brief File containing declaration of the MelonModel class.
*
**********************************************************************************/

#pragma once

#include <memory>	// std::shared_ptr, std::unique_ptr
#include <vector>	// std::vector

#include "modelParser.h"
#include "modelData.h"
#include "exceptions.h"

namespace melon {

    /*
    * @class MelonModel
    * @brief This class is a abstract parent class for models implemented in the MeLOn library
    */
    template<typename T>
    class MelonModel {
	public:
		/**
		*  @brief Default destructor
		*/
		virtual ~MelonModel() = default;

		/**
		*  @brief Loads new model from file
		*
		*  @param[in] modelName is the name of the model
		*
		*  @param[in] fileType specifies the file type of the model file
		*/
		void load_model(std::string modelName, MODEL_FILE_TYPE fileType);

		/**
		*  @brief Loads new model from file
		*
		*  @param[in] modelPath is the path to the directory in which the network is located
		*
		*  @param[in] modelName is the name of the model
		*
		*  @param[in] fileType specifies the file type of the model file
		*/
		void load_model(std::string modelPath, std::string modelName, MODEL_FILE_TYPE fileType);

		/**
		*  @brief Loads new model from file
		*
		*  @param[in] modelData is a ModelData object containing the data which defines the model
		*/
		void load_model(std::shared_ptr<const ModelData> modelData);

    protected:

		bool _modelLoaded { false };							/*!< Flag which indicates wether a model is currently loaded or not*/
		std::shared_ptr<ModelParserFactory> _parserFactory;		/*!< Pointer to a parser factory class which creates instances of parser objects fitting the type of model and file*/

		/**
	    *  @brief Constructor
		*
		*  @param[in] parserFactory is a pointer to an parser factory derived from ModelParserFactory wich creates compatible parsers for the model derived from this class
		*/
		MelonModel(std::shared_ptr<ModelParserFactory> parserFactory) : _parserFactory(parserFactory) {};

		/**
		*  @brief Sets data object containing model parameters.
		*
		*  @param[in] modelData is a ModelData object containing the data which defines the model
		*/
		virtual void _set_data_object(std::shared_ptr<const ModelData> modelData) = 0;
        
        /**
        *  @brief Sets constraints required for fullspace opimization
        *
        *  @param[out] constraints vector containing the constraints for the given variables (difference between values given by optimizer and values calulated by model)
        *
        *  @param[in,out] constraintEvaluation vector containing the values which were calculated by the model, returned is the vector containing the values which were given by the optimizer
        *
        *  @param[in] constraintValue is an iterator which points to the beginning of the variables, for which the constraints should be set, in the vector of variables given by the optimizer
        */
        template <typename RandomAccessIterator>
        void _set_constraints(std::vector<T>& constraints, std::vector<T>& constraintEvaluation, RandomAccessIterator& constraintValue) const;

        /**
        *  @brief Sets constraints required for fullspace opimization
        *
        *  @param[out] constraints vector containing the constraints for the given variables (difference between values given by optimizer and values calulated by model)
        *
        *  @param[in,out] constraintEvaluation is the values which was calculated by the model, returned is the vector containing the values which were given by the optimizer
        *
        *  @param[in] constraintValue is an iterator which points to the beginning of the variables, for which the constraints should be set, in the vector of variables given by the optimizer
        */
        template <typename RandomAccessIterator>
        void _set_constraints(std::vector<T>& constraints, T& constraintEvaluation, RandomAccessIterator& constraintValue) const;
    };


	/////////////////////////////////////////////////////////////////////////
	// Function wich loads model from file modelName
	template <typename T>
	void MelonModel<T>::load_model(std::string modelName, MODEL_FILE_TYPE fileType) {
		load_model("", modelName, fileType);
	}


	/////////////////////////////////////////////////////////////////////////
	// Constructor which loads model from file "modelName" located in "filePat"h
	template <typename T>
	void MelonModel<T>::load_model(std::string modelPath, std::string modelName, MODEL_FILE_TYPE fileType) {

		std::shared_ptr<ModelData> modelData;

		try {
			std::unique_ptr<ModelParser> parser = _parserFactory->create_model_parser(fileType);
			modelData = parser->parse_model(modelPath, modelName);
			_set_data_object(modelData);
		}
		catch (const std::exception& e) {
			throw(MelonException("  Encountered a fatal error while loading model from file. Terminating.", e));
		}
		catch (...) {
			throw(MelonException("  Encountered a fatal error while loading model from file. Terminating."));
		}

		_modelLoaded = true;

	}


	/////////////////////////////////////////////////////////////////////////
	// Constructor which loads model from ModelData object
	template <typename T>
	void MelonModel<T>::load_model(std::shared_ptr<const ModelData> modelData) {
		
		try {
			_set_data_object(modelData);
		}
		catch (std::exception &e) {
			throw(MelonException("  Encountered a fatal error while loading model from data object. Terminating.", e));
		}
		catch (...) {
			throw(MelonException("  Encountered a fatal error while loading model from data object. Terminating."));
		}

		_modelLoaded = true;
	}

	/////////////////////////////////////////////////////////////////////////
	// Sets constraints required for fullspace opimization
	template <typename T>
	template <typename RandomAccessIterator>
	void MelonModel<T>::_set_constraints(std::vector<T>& constraints, std::vector<T>& constraintEvaluation, RandomAccessIterator& constraintValue) const {
		for (auto& i : constraintEvaluation) {
			_set_constraints(constraints, i, constraintValue);
		}
	}


	/////////////////////////////////////////////////////////////////////////
	// Sets constraints required for fullspace opimization
	template <typename T>
	template <typename RandomAccessIterator>
	void MelonModel<T>::_set_constraints(std::vector<T>& constraints, T& constraintEvaluation, RandomAccessIterator& constraintValue) const {
		T cv = *constraintValue;
		T constraint = constraintEvaluation - cv;
		constraints.push_back(constraint);

		// Set normalized Input to the value provided by the solver for further calculations
		constraintEvaluation = *constraintValue;
		constraintValue++;
	}

}