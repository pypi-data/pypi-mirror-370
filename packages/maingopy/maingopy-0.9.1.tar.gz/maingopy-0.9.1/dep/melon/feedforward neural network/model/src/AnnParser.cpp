/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file AnnParser.cpp
*
* @brief File implementing the AnnParser and the AnnParserFactory classes.
*
**********************************************************************************/

#include <memory>	// std::unique_ptr, std::make_unique

#include "exceptions.h"
#include "AnnParser.h"

using namespace melon;

/////////////////////////////////////////////////////////////////////////
// Turns a string containing the name of an activation function in the correct enum representation 
std::unique_ptr<ModelParser> AnnParserFactory::create_model_parser(const MODEL_FILE_TYPE fileType) {

    switch (fileType) {
    case MODEL_FILE_TYPE::CSV:
        return std::make_unique<AnnParserCsv>();
    case MODEL_FILE_TYPE::XML:
        return std::make_unique<AnnParserXml>();
    default:
        throw MelonException("  Error while creating file parser: Invalid file type.");
    }

}


/////////////////////////////////////////////////////////////////////////
// Factory function for creating a instance of an ann parser corresponding to the specified file type
ACTIVATION_FUNCTION AnnParser::_string_to_activation_function(const std::string& activationFunctionName) {

    if (activationFunctionName.compare("purelin") == 0) {
        return ACTIVATION_FUNCTION::PURE_LIN;
    }
    else if (activationFunctionName.compare("linear") == 0) {
        return ACTIVATION_FUNCTION::PURE_LIN;
    }
	else if (activationFunctionName.compare("tanh") == 0) {
		return ACTIVATION_FUNCTION::TANH;
	}
    else if (activationFunctionName.compare("tansig") == 0) {
        return ACTIVATION_FUNCTION::TANH;
    }
    else if (activationFunctionName.compare("relu") == 0) {
        return ACTIVATION_FUNCTION::RELU;
    }
    else if (activationFunctionName.compare("relu6") == 0) {
        return ACTIVATION_FUNCTION::RELU6;
    }
    else {
        throw MelonException("  Error while parsing file: Unkown activation function \"" + activationFunctionName + "\"");
    }
}