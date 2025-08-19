/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file mulfilGpParser.cpp
*
* @brief File implementing the MulfilGpParser and the MulfilGpParserFactory classes.
*
**********************************************************************************/

#include "mulfilGpParser.h"
#include "gpParser.h"

#include <nlohmann/json.hpp>
using json = nlohmann::json;

#ifdef GCC_FS_EXPERIMENTAL
#include <experimental/filesystem>
#else
#include <filesystem>
#endif

using namespace melon;


std::unique_ptr<ModelParser> MulfilGpParserFactory::create_model_parser(const MODEL_FILE_TYPE fileType) {

	switch (fileType) {
	case MODEL_FILE_TYPE::JSON:
		return std::make_unique<MulfilGpParser>();
	default:
		throw MelonException("Error while creating file parser: Invalid file type.");
	}
}


std::shared_ptr<ModelData> MulfilGpParser::parse_model(const std::string modelPath, const std::string modelName) {

	GpParser gpParser{};

	std::string formattedModelPath{
		modelPath.empty() ?
		_format_folder_path(modelName) :
		_format_folder_path(modelPath + "/" + modelName) };

	// low and high fidelity GP data
	std::shared_ptr<GPData> lowGpData = std::dynamic_pointer_cast<GPData>(gpParser.parse_model(formattedModelPath, "lowGpData.json"));
	std::shared_ptr<GPData> highGpData = std::dynamic_pointer_cast<GPData>(gpParser.parse_model(formattedModelPath, "highGpData.json"));

	// rho
#ifdef GCC_FS_EXPERIMENTAL
	std::experimental::filesystem::path rhoPath{ std::experimental::filesystem::path{ formattedModelPath } / "rho.json" };
#else
	std::filesystem::path rhoPath{ std::filesystem::path{ formattedModelPath } / "rho.json" };
#endif

	std::ifstream ifs(rhoPath);
	if (!ifs.is_open()) {
		throw MelonException("  Error while parsing model files : File \"" + rhoPath.string() + "\" not found. \n  Please make sure that the model files are located in the correct directory and named correctly.");
	}

	json j;
	ifs >> j;
	double rho{ j["rho"].get<double>() };
	
	std::shared_ptr<MulfilGpData> data = std::make_shared<MulfilGpData>(*lowGpData, *highGpData, rho);
	return data;
}
