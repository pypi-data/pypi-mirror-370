/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file gpParser.h
*
* @brief File containing declaration of the Gaussian process parser classes.
*
**********************************************************************************/

#pragma once

#include <string>	// std::string
#include <vector>	// std::vector
#include <memory>	// std::unique_ptr, std::shared_ptr

#include "modelParser.h"
#include "gpData.h"

namespace melon {

	/**
	* @class GpParser
	* @brief This class implements a Gaussian process file parser.
	*/
	class GpParser : public ModelParser {
	public:

		/**
		*  @brief Abstract function for defining the structure of the parsing function which is used to get the Gaussian process data from a file
		*
		*  @param[in] modelPath Path to the location of the Gaussian process file
		*
		*  @param[in] modelName name of the network (either foldername in which csv files are stored or name of an xml file, depending on the filetype)
		*
		*  @returns pointer to modelData struct containing the information defining the Gaussian process
		*/
		std::shared_ptr<ModelData> parse_model(const std::string modelPath, const std::string modelName) override;
	};

	/**
	* @class GpParserFactory
	* @brief This class is a factory class for creating child instances of GpParser.
	*/
	class GpParserFactory : public ModelParserFactory {
	public:

		/**
		*  @brief Factory function for creating a instance of an Gauusian process parser corresponding to the specified file type
		*
		*  @brief fileType type of the file in which Gaussian process is stored
		*
		*  @returns Pointer to an instance of a child class of GpParser
		*/
		std::unique_ptr<ModelParser> create_model_parser(const MODEL_FILE_TYPE fileType) override;
	};
}