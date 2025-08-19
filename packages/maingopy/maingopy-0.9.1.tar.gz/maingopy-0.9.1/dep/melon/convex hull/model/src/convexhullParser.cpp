/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file convexhullParser.cpp
*
* @brief File implementing the ConvexHullParser and the ConvexHullParserFactory classes.
*
**********************************************************************************/

#include "convexhullParser.h"

#include <memory>	// std::shared_ptr, std:_unique_ptr, std::make_shared, std::make_unique
#include <fstream>	// std::ifs

#include "exceptions.h"
#include "convexhullData.h"

#include <nlohmann/json.hpp>
using json = nlohmann::json;

using namespace melon;

/*
	* @brief Function for allowing to parse data from a json object directly to an ConvexHullData object
	*
	* @param[in] j jason object from which data is parsed
	*
	* @param[out] d ConvexHullData object in which parsed data is stored
	*/
void from_json(const json & j, ConvexHullData & d) {
	j.at("A").get_to(d.A);
	j.at("b").get_to(d.b);
};

/////////////////////////////////////////////////////////////////////////
// Factory function for creating a instance of an Gaussian process parser corresponding to the specified file type 
std::unique_ptr<ModelParser> ConvexHullParserFactory::create_model_parser(const MODEL_FILE_TYPE fileType) {

    switch (fileType) {
        case MODEL_FILE_TYPE::JSON:
            return std::make_unique<ConvexHullParser>();
        default:
            throw MelonException("  Error while creating file parser: Invalid file type.");
    }

}

std::shared_ptr<ModelData> ConvexHullParser::parse_model(const std::string modelPath, const std::string modelName) {

	std::string filePath = _format_file_path(modelPath, modelName, MODEL_FILE_TYPE::JSON);

	// Start parsing file
	std::ifstream ifs(filePath);
	if (!ifs.is_open()) {
		throw MelonException("  Error while parsing model file : File \"" + filePath + "\" not found. \n  Please make sure that the model file is located in the correct directory.");
	}

	json j;
	ifs >> j;
	std::shared_ptr<ConvexHullData> convexHullData = std::make_shared<ConvexHullData>(j.get<ConvexHullData>());

	return convexHullData;
}

