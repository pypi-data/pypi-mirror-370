/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file convexhullparser.h
*
* @brief File containing declaration of the convex hull parser classes.
*
**********************************************************************************/

#pragma once

#include <string>	// std::string
#include <vector>	// std::vector
#include <memory>	// std::unique_ptr, std::shared_ptr

#include "modelParser.h"

namespace melon {

	/**
	* @class ConvexHullParser
	* @brief This class implements a convex hull file parser.
	*/
	class ConvexHullParser : public ModelParser {
	public:

		/**
		*  @brief Abstract function for defining the structure of the parsing function which is used to get the convex hull data from a file
		*
		*  @param[in] modelPath Path to the location of the convex hull file
		*
		*  @param[in] modelName name of the network (either foldername in which csv files are stored or name of an xml file, depending on the filetype)
		*
		*  @param[out] modeData struct containing the information defining the convex hull
		*/
		std::shared_ptr<ModelData> parse_model(const std::string modelPath, const std::string modelName) override;
	};

	/**
	* @class ConvexHullParserFactory
	* @brief This class is a factory class for creating child instances of ConvexHullParser.
	*/
	class ConvexHullParserFactory : public ModelParserFactory {
	public:

		/**
		*  @brief Factory function for creating a instance of an Gauusian process parser corresponding to the specified file type
		*
		*  @brief fileType type of the file in which convex hull is stored
		*
		*  @returns Pointer to an instance of a child class of ConvexHullParser
		*/
		std::unique_ptr<ModelParser> create_model_parser(const MODEL_FILE_TYPE fileType) override;
	};
}