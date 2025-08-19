/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file modelParser.h
*
* @brief File containing declaration of the ModelParser class.
*
**********************************************************************************/

#pragma once

#include <string>			// std::string

#include "exceptions.h"
#include "modelData.h"
#include "scaler.h"

namespace melon {

	/**
	* @enum MODEL_FILE_TYPE
	* @brief Enum for representing the parsable filetypes
	*/
	enum MODEL_FILE_TYPE {
		CSV = 0,
		XML,
		JSON
	};

	/**
	* @class ModelParser
	* @brief This class is a abstract parent class for model parser implemented in the MeLOn library.
	*/
	class ModelParser {
	public:
		/**
		*  @brief Abstract function for defining the structure of the parsing function which is used to get the model data from a file
		*
		*  @param[in] modelPath Path to the location of the model file
		*
		*  @param[in] modelName name of the model
		*
		*  @return returns pointer to data object 
		*/
		virtual std::shared_ptr<ModelData> parse_model(const std::string modelPath, const std::string modelName = "") = 0;

		/**
		*  @brief Virtual desctructor to enable inheritance
		*
		*/
		virtual ~ModelParser() = default;

	protected:
		std::string _modelPath;         /*!< Path to the location of the ANN file */
		std::string _modelName;         /*!< Name of the network */

		/**
		* @brief Applies the correct format to the path given by the user
		*
		* @param[in] modelPath Path to the location of the model file
		*
		* @param[in] modelName name of the model
		*
		* @param[in] fileType type of the file
		*
		* @return returns string with correctly formatted filepath
		*/
		std::string _format_file_path(const std::string modelPath, const std::string modelName, const MODEL_FILE_TYPE fileType);

		/**
		* @brief Applies the correct format to the path given by the user
		*
		* @param[in] modelPath Path to the location of the model folder
		*
		* @return returns string with correctly formatted filepath
		*/
		std::string _format_folder_path(const std::string modelPath);

		/**
		*  @brief Turns a string containing the name of an scaler type in the correct enum representation
		*
		*  @param[in] scalerTypeName is a string containing the name of the scaler type
		*
		*  @return returns the enum representation of the input
		*/
		static SCALER_TYPE _string_to_scaler_type(const std::string scalerTypeName);

		/**
		*  @brief Turns a string containing the name of an scaler type in the correct enum representation
		*
		*  @param[in] scalerParameterName is a string containing the name of the scaler parameter
		*
		*  @return returns the enum representation of the input
		*/
		static SCALER_PARAMETER _string_to_scaler_parameter(const std::string scalerParameterName);
	};

	/**
	* @class ModelParserFactory
	* @brief This class is a abstract parent class for model parser factories implemented in the MeLOn library.
	*/
	class ModelParserFactory {
	public:

		/**
		*  @brief Abstract factory function for creating a instance of an model parser corresponding to the specified file type.
		*
		*  @brief fileType type of the file in which model is stored
		*
		*  @returns Pointer to an instance of a derived class of ModelParse
		*/
		virtual std::unique_ptr<ModelParser> create_model_parser(const MODEL_FILE_TYPE fileType = MODEL_FILE_TYPE::CSV) = 0;
	};
}