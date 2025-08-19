/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file gpParser.cpp
*
* @brief File implementing the GpParser and the GpParserFactory classes.
*
**********************************************************************************/

#include "gpParser.h"

#include <memory>	// std::shared_ptr, std:_unique_ptr, std::make_shared, std::make_unique

#include "exceptions.h"
#include "gpData.h"

#include <nlohmann/json.hpp>
using json = nlohmann::json;

using namespace melon;

/*
* @brief Function for allowing to parse data from a json object directly to an GPData object
*
* @param[in] j jason object from which data is parsed
*
* @param[out] d GPData object in which parsed data is stored
*/
void from_json(const json & j, GPData & d) {
	j.at("nX").get_to(d.nX);
	j.at("DX").get_to(d.DX);
	j.at("DY").get_to(d.DY);
	j.at("matern").get_to(d.matern);
	j.at("meanfunction").get_to(d.meanfunction);
	j.at("stdOfOutput").get_to(d.stdOfOutput);

	j.at("X").get_to(d.X);
	j.at("Y").get_to(d.Y);
	j.at("K").get_to(d.K);
	j.at("invK").get_to(d.invK);

	d.inputScalerData = std::make_shared<ScalerData>();
	d.inputScalerData->type = SCALER_TYPE::MINMAX;
	d.inputScalerData->parameters.emplace(SCALER_PARAMETER::SCALED_LOWER_BOUNDS, std::vector<double>(d.DX, 0));
	d.inputScalerData->parameters.emplace(SCALER_PARAMETER::SCALED_UPPER_BOUNDS, std::vector<double>(d.DX, 1));
	d.inputScalerData->parameters.emplace(SCALER_PARAMETER::LOWER_BOUNDS, std::vector<double>());
	d.inputScalerData->parameters.emplace(SCALER_PARAMETER::UPPER_BOUNDS, std::vector<double>());
	j.at("problemLowerBound").get_to(d.inputScalerData->parameters.at(SCALER_PARAMETER::LOWER_BOUNDS));
	j.at("problemUpperBound").get_to(d.inputScalerData->parameters.at(SCALER_PARAMETER::UPPER_BOUNDS));

	d.predictionScalerData = std::make_shared<ScalerData>();
	d.predictionScalerData->type = SCALER_TYPE::STANDARD;
	d.predictionScalerData->parameters.emplace(SCALER_PARAMETER::MEAN, std::vector<double>());
	d.predictionScalerData->parameters.emplace(SCALER_PARAMETER::STD_DEV, std::vector<double>(1,d.stdOfOutput));
	d.predictionScalerData->parameters.at(SCALER_PARAMETER::MEAN) = { j.at("meanOfOutput").get<double>() };

	d.kernelData = std::make_shared<kernel::KernelData>();
	j.at("ell").get_to(d.kernelData->ell);
	j.at("sf2").get_to(d.kernelData->sf2);
	
	// TODO Remove (?)
	// j.at("inputLowerBound").get_to(d.inputLowerBound);
	// j.at("inputUpperBound").get_to(d.inputUpperBound);
};

/////////////////////////////////////////////////////////////////////////
// Factory function for creating a instance of an Gaussian process parser corresponding to the specified file type 
std::unique_ptr<ModelParser> GpParserFactory::create_model_parser(const MODEL_FILE_TYPE fileType) {

	switch (fileType) {
	case MODEL_FILE_TYPE::JSON:
		return std::make_unique<GpParser>();
	default:
		throw MelonException("  Error while creating file parser: Invalid file type.");
	}

}

std::shared_ptr<ModelData> GpParser::parse_model(const std::string modelPath, const std::string modelName) {

	std::string filePath = _format_file_path(modelPath, modelName, MODEL_FILE_TYPE::JSON);

	// Start parsing file
	std::ifstream ifs(filePath);
	if (!ifs.is_open()) {
		throw MelonException("  Error while parsing model file : File \"" + filePath + "\" not found. \n  Please make sure that the model file is located in the correct directory.");
	}

	json j;
	ifs >> j;
	std::shared_ptr<GPData> gpData = std::make_shared<GPData>(j.get<GPData>());

	return gpData;
}

