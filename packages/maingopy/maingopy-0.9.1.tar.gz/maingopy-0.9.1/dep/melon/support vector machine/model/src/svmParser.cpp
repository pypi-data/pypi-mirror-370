/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file svmParser.cpp
*
* @brief File implementing the SvmParser and the SvmParserFactory classes.
*
**********************************************************************************/

#include "svmParser.h"

#include <fstream>	// std::ifstream

using namespace melon;

/*
* @brief Function for allowing to parse data from a json object directly to an SvmData object
*
* @param[in] j jason object from which data is parsed
*
* @param[out] d SvmData object in which parsed data is stored
* @param[out] d SvmData object in which parsed data is stored
*/
void from_json(const json & j, SvmData& d) {
	j.at("rho").get_to(d.rho);
	j.at("support_vectors").get_to(d.supportVectors);
	j.at("dual_coefficients").get_to(d.dualCoefficients);

	d.kernelFunction = SvmParser::string_to_kernel_function(j.at("kernel_function").get<std::string>());
	j.at("kernel_parameters").get_to(d.kernelParameters);

	try {
		d.inputScalerData = SvmParser::parse_scaler(j.at("scaling").at("input"));
	}
	catch (json::out_of_range&) {
		// Assign default ScalerData (default scaler type is identity)
		d.inputScalerData = std::make_unique<ScalerData>();
	}

	try {
		d.outputScalerData = SvmParser::parse_scaler(j.at("scaling").at("output"));
	}
	catch (json::out_of_range&) {
		// Assign default ScalerData (default scaler type is identity)
		d.outputScalerData = std::make_unique<ScalerData>();
	}
}


/////////////////////////////////////////////////////////////////////////
// Factory function for creating a instance of an svm parser corresponding to the specified file type 
std::unique_ptr<ModelParser> SvmParserFactory::create_model_parser(const MODEL_FILE_TYPE fileType) {

	switch (fileType) {
	    case MODEL_FILE_TYPE::JSON:
		    return std::make_unique<SvmParser>();
		default:
	    throw MelonException("  Error while creating file parser: Invalid file type.");
	}

}


/////////////////////////////////////////////////////////////////////////
// Function for parsing scaler data from json object.
std::shared_ptr<ScalerData> SvmParser::parse_scaler(json scalerJson) {

	std::shared_ptr<ScalerData> scalerData = std::make_shared<ScalerData>();

	// Read parameters and scaler type from parser
	for (json::iterator it = scalerJson.begin(); it != scalerJson.end(); ++it) {
		if (it.key() == "scaler") {
			std::string scalerType = it.value().get<std::string>();
			scalerData->type = _string_to_scaler_type(scalerType);
		}
		else
		{
			SCALER_PARAMETER parameterType = _string_to_scaler_parameter(it.key());
			scalerData->parameters.emplace(parameterType, it.value().get<std::vector<double>>());
		}
	}

	// Always scale to [-1,1] when using MinMax scaling TODO: write scaling interval to file in training script
	if (scalerData->type == SCALER_TYPE::MINMAX) {
		size_t inputSize = scalerData->parameters.at(SCALER_PARAMETER::LOWER_BOUNDS).size();
		scalerData->parameters.emplace(SCALER_PARAMETER::SCALED_LOWER_BOUNDS, std::vector<double>(inputSize, -1));
		scalerData->parameters.emplace(SCALER_PARAMETER::SCALED_UPPER_BOUNDS, std::vector<double>(inputSize, 1));
	}

	return scalerData;
}


/////////////////////////////////////////////////////////////////////////
// Turns string with kernel name into enum representation
KERNEL_FUNCTION SvmParser::string_to_kernel_function(const std::string& kernelName) {

	if (kernelName.compare("rbf") == 0) {
		return KERNEL_FUNCTION::RBF;
	}
	else
		throw MelonException("Error while parsing kernel: Invalid kernel string specifier. Must be 'rbf' ");
}


/////////////////////////////////////////////////////////////////////////
// Function for parsing the support vector machine data from a file.
std::shared_ptr<ModelData> SvmParser::parse_model(const std::string modelPath, const std::string modelName) {

	std::string filePath = _format_file_path(modelPath, modelName, MODEL_FILE_TYPE::JSON);

	// Start parsing file
	std::ifstream ifs(filePath);
	if (!ifs.is_open()) {
		throw MelonException("  Error while parsing model file : File \"" + filePath + "\" not found. \n  Please make sure that the model file is located in the correct directory.");
	}

	json j;
	ifs >> j;
	std::shared_ptr<SvmData> svmData = std::make_shared<SvmData>(j.get<SvmData>());

	return svmData;
}