/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file svmParser.h
*
* @brief File containing declaration of the support vector machine parser classes.
*
**********************************************************************************/

#pragma once

#include <string>	// std::string
#include <vector>	// std::vector
#include <memory>	// std::unique_ptr, std::shared_ptr

#include "modelParser.h"
#include "svmData.h"
#include "exceptions.h"
#include "scaler.h"

#include <nlohmann/json.hpp>
using json = nlohmann::json;

namespace melon {

	/**
	* @class SvmParser
	* @brief This class implements a support vector machine file parser.
	*/
	class SvmParser : public ModelParser {
	public:

		/**
		*  @brief Function for parsing the support vector machine data from a file.
		*
		*  @param[in] modelPath Path to the location of the support vector machine file
		*
		*  @param[in] modelName name of the model
		*
		*  @return returns modelData struct containing the information defining the support vector machine
		*/
		std::shared_ptr<ModelData> parse_model(const std::string modelPath, const std::string modelName) override;

		/**
		* @brief Turns string with kernel name into enum representation
		*
		* @param[in] kernelName is a std::string with the kernel name
		*
		* @return returns the enum representation of file type
		*/
		static KERNEL_FUNCTION string_to_kernel_function(const std::string& kernelName);

		/**
		*  @brief Function for parsing scaler data from json object.
		*
		*  @param[in] scalerJson json object containing the scaler specifications
		*
		*  @return returns a scaler data object containing the data rewuired to create the specified scaler.
		*/
		static std::shared_ptr<ScalerData> parse_scaler(json scalerJson);
	};


	/**
	* @class SvmParserFactory
	* @brief This class is a factory class for creating child instances of SvmParser.
	*/
	class SvmParserFactory : public ModelParserFactory {
	public:

		/**
		*  @brief Factory function for creating a instance of a support vector machine parser corresponding to the specified file type
		*
		*  @brief fileType type of the file in which support vector machine is stored
		*
		*  @returns Pointer to an instance of a child class of SvmParser
		*/
		std::unique_ptr<ModelParser> create_model_parser(const MODEL_FILE_TYPE fileType) override;
	};
}