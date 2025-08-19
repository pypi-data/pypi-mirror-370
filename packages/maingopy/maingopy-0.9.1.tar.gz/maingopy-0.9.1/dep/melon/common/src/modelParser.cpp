/**********************************************************************************
* Copyright (c) 2019 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file melonParser.cpp
*
* @brief File implementing Functions of the abstract ModelParser class.
*
**********************************************************************************/

#include "modelParser.h"

#include <string>		// std::string
#ifdef GCC_FS_EXPERIMENTAL
#include <experimental/filesystem>	// std::experimetnal::filesystem::path, std::experimetnal::filesystem::absolute
#else
#include <filesystem>	// std::filesystem::path, std::filesystem::absolute
#endif


using namespace melon;

std::string ModelParser::_format_file_path(const std::string modelPath, const std::string modelName, const MODEL_FILE_TYPE fileType) {

#ifdef GCC_FS_EXPERIMENTAL
	std::experimental::filesystem::path filePath = modelPath;
	filePath /= modelName;
#else
	std::filesystem::path filePath = modelPath;
	filePath /= modelName;
	filePath = filePath.lexically_normal();
#endif

	std::string expectedExtension;
	switch (fileType) {
	case MODEL_FILE_TYPE::JSON:
		expectedExtension = ".json";
		break;
	case MODEL_FILE_TYPE::XML:
		expectedExtension = ".xml";
		break;
	case MODEL_FILE_TYPE::CSV:
		expectedExtension = ".csv";
		break;
	default:
		throw MelonException("  Error while formatting file path: Unkown file type.");
	}

	// Check if filename already contains file extension and append it otherwise
	if (filePath.has_extension()) {
		std::string extension = filePath.extension().string();

		// Check if file extension matches the expected extension
		if (expectedExtension != filePath.extension()) {
			throw MelonException("  Error while formatting file path: The file extension in modelName (\"" + modelName + "\") does not match the extension of the provided filetype (\"" + expectedExtension + "\").");
		}
	}
	else {
		filePath += expectedExtension;
	}

#ifdef GCC_FS_EXPERIMENTAL
	std::experimental::filesystem::path test = std::experimental::filesystem::current_path();
#else
	std::filesystem::path test = std::filesystem::current_path();
#endif

	// Convert filepath into absolut one in case it is relative
	if (filePath.is_relative()) {
#ifdef GCC_FS_EXPERIMENTAL
		filePath = std::experimental::filesystem::absolute(filePath);
	#else
		filePath = std::filesystem::absolute(filePath);
#endif
	}

	return filePath.string();
}


std::string ModelParser::_format_folder_path(const std::string modelPath)
{
#ifdef GCC_FS_EXPERIMENTAL
	std::experimental::filesystem::path filePath = modelPath;
	filePath /= modelName;
#else
	std::filesystem::path filePath = modelPath;
	filePath = filePath.lexically_normal();
#endif

#ifdef GCC_FS_EXPERIMENTAL
	bool isFolder = std::experimental::filesystem::is_directory(filePath);
#else
	bool isFolder = std::filesystem::is_directory(filePath);
#endif

	if (!isFolder) {
		throw MelonException("  Error while formatting folder path: modelPath is not a folder, it is " + filePath.string() + ".");
	}

#ifdef GCC_FS_EXPERIMENTAL
	std::experimental::filesystem::path test = std::experimental::filesystem::current_path();
#else
	std::filesystem::path test = std::filesystem::current_path();
#endif

	// Convert filepath into absolut one in case it is relative
	if (filePath.is_relative()) {
#ifdef GCC_FS_EXPERIMENTAL
		filePath = std::experimental::filesystem::absolute(filePath);
#else
		filePath = std::filesystem::absolute(filePath);
#endif
	}

	return filePath.string();
}

/////////////////////////////////////////////////////////////////////////
// Turns a string containing the name of an scaler type in the correct enum representation
SCALER_TYPE ModelParser::_string_to_scaler_type(const std::string scalerTypeName) {
	if (scalerTypeName == "Identity") {
		return SCALER_TYPE::IDENTITY;
	}
	else if (scalerTypeName == "MinMax") {
		return SCALER_TYPE::MINMAX;
	}
	else if (scalerTypeName == "Standard") {
		return SCALER_TYPE::STANDARD;
	}
	else {
		throw MelonException("  Error while parsing file: Unkown scaler type\"" + scalerTypeName + "\"");
	}
}


/////////////////////////////////////////////////////////////////////////
// Turns a string containing the name of an scaler type in the correct enum representation
SCALER_PARAMETER ModelParser::_string_to_scaler_parameter(const std::string scalerParameterName) {
	if (scalerParameterName == "min") {
		return SCALER_PARAMETER::LOWER_BOUNDS;
	}
	else if (scalerParameterName == "max") {
		return SCALER_PARAMETER::UPPER_BOUNDS;
	}
	else if (scalerParameterName == "mean") {
		return SCALER_PARAMETER::MEAN;
	}
	else if (scalerParameterName == "stddev") {
		return SCALER_PARAMETER::STD_DEV;
	}
	else {
		throw MelonException("  Error while parsing file: Unkown scaler parameter\"" + scalerParameterName + "\"");
	}
}
