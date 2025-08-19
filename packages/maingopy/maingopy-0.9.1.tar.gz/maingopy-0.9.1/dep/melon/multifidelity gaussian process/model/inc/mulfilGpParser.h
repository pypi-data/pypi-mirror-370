/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file mulfilGpParser.h
*
* @brief File that contains the declaration of the multifidelity Gaussian process parser classes.
*
**********************************************************************************/

#pragma once

#include <string>	// std::string
#include <vector>	// std::vector
#include <memory>	// std::unique_ptr, std::shared_ptr

#include "modelParser.h"
#include "mulfilGpData.h"

namespace melon {

	/**
	* @class MulfilGpParser
	* @brief Class that implements a multifidelity Gaussian process file parser.
	*/
	class MulfilGpParser : public ModelParser {
	public:

		/**
		*  @brief Override function that gets the multifidelty Gaussian process data from a folder
		* 
		*  The folder has to contain the data files lowGpData.json, highGpData.json, rho.json.
		* 
		*  @param[in] modelPath Path to the parent folder of the folder with the data files
        * 
        *  @param[in] modelName  Name of the folder with the data files
		*
		*  @returns Pointer of ModelData pointing to a MulfilGpData object
		*/
		std::shared_ptr<ModelData> parse_model(const std::string modelPath, const std::string modelName) override;
	};

	/**
	* @class MulfilGpParserFactory
	* @brief Class that implements a factory for creating child instances of MulfilGpParser.
	*/
	class MulfilGpParserFactory : public ModelParserFactory {
	public:

		/**
		*  @brief Override function that creates an instance of a MulfilGpParser
		*
		*  @param[in] fileType Type of the files in which multifidelity Gaussian process data is stored
		*  (in the case of MulfilGpParserFactory not used within the function)
		*
		*  @returns Pointer of ModelParser pointing to a MulfilGpParser object 
		*/
		std::unique_ptr<ModelParser> create_model_parser(const MODEL_FILE_TYPE fileType = MODEL_FILE_TYPE::JSON) override;
	};
}
