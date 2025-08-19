/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file AnnParserCSV.cpp
*
* @brief File implementing the AnnParserCSV class.
*
**********************************************************************************/

#include "AnnParser.h"

#include <vector>		// std::vector
#include <string>		// std::string, std::stoi, std::getline
#include <memory>		// std::make_shared
#include <iterator>		// std::distance, std::back_inserter
#include <fstream>		// std::ifstream
#include <sstream>		// std::stringstream
#include <algorithm>	// std::transform, std::mismatch

#include "exceptions.h"
#include "vectorarithmetics.h"

using namespace melon;

/////////////////////////////////////////////////////////////////////////
// Parsing function which is used to get the ANN data from a csv file
std::shared_ptr<ModelData> AnnParserCsv::parse_model(const std::string modelPath, const std::string modelName) {

    this->_modelName = modelName;
    this->_modelPath = modelPath;

	std::shared_ptr<AnnData> annData = std::make_shared<AnnData>();
    auto& structure = annData->structure;
    auto& weights = annData->weights;
	auto& inputScalerData = annData->inputScalerData;
	auto& outputScalerData = annData->outputScalerData;

	inputScalerData = std::make_shared<ScalerData>();
	outputScalerData = std::make_shared<ScalerData>();

    _parse_config_file(structure);
    _parse_scalers(inputScalerData, outputScalerData, structure);
    _parse_bias_weights(structure, weights);
    _parse_layer_weights(structure, weights);
    _parse_input_weights(structure, weights);

	return annData;
}


/////////////////////////////////////////////////////////////////////////
// Parses the configuration csv file
void AnnParserCsv::_parse_config_file(AnnStructure& structure) {

	// Read configurationa data from csv file
	std::vector<std::vector<std::string>> data = _csv_to_string_matrix(_modelName + "_config.csv");
	if (data.size() != 7) {
		throw MelonException("  Error while parsing configuration file (csv): Incorrect number of lines. Please use the training scripts provided with MeLOn to generate network files.");
	}

    // Define aliases
    auto& numLayersString = data.at(0);
    auto& inputConnectString = data.at(1);
    auto& biasConnectString = data.at(2);
    auto& layerConnectString = data.at(3);
    auto& inputSizeString = data.at(4);
    auto& layerSizeString = data.at(5);
    auto& activationFunctionString = data.at(6);

	// Define lambda function for converting string to int (enables using stoi in transform function)
    auto stoi = [](const std::string& s) { return std::stoi(s); };

	// Store amount of layers
	structure.numLayers = std::stoi(numLayersString.at(0));

	// Check if vector sizes are consistent
	if (inputConnectString.size() != structure.numLayers) {
		throw MelonException("  Error while parsing configuration file (csv): Incorrect size of inut connection vector. Please use the training scripts provided with MeLOn to generate network files.");
	}
	if (biasConnectString.size() != structure.numLayers) {
		throw MelonException("  Error while parsing configuration file (csv): Incorrect size of bias connection vector. Please use the training scripts provided with MeLOn to generate network files.");
	}
	if (layerConnectString.size() != structure.numLayers*structure.numLayers) {
		throw MelonException("  Error while parsing configuration file (csv): Incorrect size of layer connection vector. Please use the training scripts provided with MeLOn to generate network files.");
	}
	if (layerSizeString.size() != structure.numLayers) {
		throw MelonException("  Error while parsing configuration file (csv): Incorrect size of layer size vector. Please use the training scripts provided with MeLOn to generate network files.");
	}
	if (activationFunctionString.size() != structure.numLayers) {
		throw MelonException("  Error while parsing configuration file (csv): Incorrect size of activation function vector. Please use the training scripts provided with MeLOn to generate network files.");
	}

	// Store ann strucutral data in corresponding struct
    structure.inputConnect.reserve(inputConnectString.size());
    std::transform(inputConnectString.begin(), inputConnectString.end(), std::back_inserter(structure.inputConnect), stoi);
	
    structure.biasConnect.reserve(biasConnectString.size());
    std::transform(biasConnectString.begin(), biasConnectString.end(), std::back_inserter(structure.biasConnect), stoi);

	structure.layerConnect = std::vector<std::vector<int>>(structure.numLayers, std::vector<int>(structure.numLayers));
	for (int iRow = 0; iRow < structure.numLayers; ++iRow) {
		auto& row = structure.layerConnect.at(iRow);
		for (int iCol = 0; iCol < structure.numLayers; ++iCol) {
			row.at(iCol) = std::stoi(layerConnectString.at(iCol + iRow * structure.numLayers));
		}
	}

	structure.inputSize = std::stoi(inputSizeString.at(0));

    structure.layerSize.reserve(layerSizeString.size());
    std::transform(layerSizeString.begin(), layerSizeString.end(), std::back_inserter(structure.layerSize), stoi);

    structure.activationFunction.reserve(activationFunctionString.size());
    std::transform(activationFunctionString.begin(), activationFunctionString.end(), std::back_inserter(structure.activationFunction), [this](const std::string s) {return _string_to_activation_function(s); });

	// Networks generated in Matlab (csv) always uses in- and output normalization
	structure.scaledInput = true;
	structure.normalizedOutput = true;

};


/////////////////////////////////////////////////////////////////////////
// Parses the input and output scalers
void AnnParserCsv::_parse_scalers(std::shared_ptr<ScalerData> inputScalerData, std::shared_ptr<ScalerData> outputScalerData, const AnnStructure& structure) {
	
	// Read bound data from csv file
	std::vector<std::vector<double>> data = _csv_to_double_matrix(_modelName + "_bounds.csv");
	if (data.size() != 4) {
		throw MelonException("  Error while parsing bound file (csv): Incorrect number of lines. Please use the training scripts provided with MeLOn to generate network files.");
	}

	// Define aliases for data
	auto& inputLbd = data.at(0);
	auto& inputUbd = data.at(1);
	auto& outputLbd = data.at(2);
	auto& outputUbd = data.at(3);

	// Check if vectors have correct sizes
	if (inputLbd.size() != structure.inputSize) {
		throw MelonException("  Error while parsing bound file (csv): Incorrect size of inut lower bound vector. Please use the training scripts provided with MeLOn to generate network files.");
	}
	if (inputUbd.size() != structure.inputSize) {
		throw MelonException("  Error while parsing bound file (csv): Incorrect size of inut upper bound vector. Please use the training scripts provided with MeLOn to generate network files.");
	}
	if (outputLbd.size() != structure.layerSize.back()) {
		throw MelonException("  Error while parsing bound file (csv): Incorrect size of output lower bound vector. Please use the training scripts provided with MeLOn to generate network files.");
	}
	if (outputUbd.size() != structure.layerSize.back()) {
		throw MelonException("  Error while parsing bound file (csv): Incorrect size of upper bound vector. Please use the training scripts provided with MeLOn to generate network files.");
	}

	// Set up input scaler
	inputScalerData->type = SCALER_TYPE::MINMAX;
	inputScalerData->parameters.emplace(SCALER_PARAMETER::SCALED_LOWER_BOUNDS, std::vector<double>(structure.inputSize, -1));
	inputScalerData->parameters.emplace(SCALER_PARAMETER::SCALED_UPPER_BOUNDS, std::vector<double>(structure.inputSize, 1));
	inputScalerData->parameters.emplace(SCALER_PARAMETER::LOWER_BOUNDS, inputLbd);
	inputScalerData->parameters.emplace(SCALER_PARAMETER::UPPER_BOUNDS, inputUbd);

	// Set up output scaler
	outputScalerData->type = SCALER_TYPE::MINMAX;
	outputScalerData->parameters.emplace(SCALER_PARAMETER::SCALED_LOWER_BOUNDS, std::vector<double>(structure.layerSize.back(), -1));
	outputScalerData->parameters.emplace(SCALER_PARAMETER::SCALED_UPPER_BOUNDS, std::vector<double>(structure.layerSize.back(), 1));
	outputScalerData->parameters.emplace(SCALER_PARAMETER::LOWER_BOUNDS, outputLbd);
	outputScalerData->parameters.emplace(SCALER_PARAMETER::UPPER_BOUNDS, outputUbd);
};


/////////////////////////////////////////////////////////////////////////
// Parses the bias weights
void AnnParserCsv::_parse_bias_weights(const AnnStructure& structure, AnnWeights& weights) {
	
	// Read bias values from csv file
	std::vector<std::vector<double>> data = _csv_to_double_matrix(_modelName + "_BW.csv");
	
	// Initialze bias weight matrix
	weights.biasWeight = std::vector<std::vector<double>>(structure.numLayers, std::vector<double>());

	// Defining vector for logging parsed weights (required for checking correctness of data)
	std::vector<int> weightLayerLog(structure.biasConnect.size(), 0);

	for (std::vector<std::vector<double>>::iterator iRow = data.begin(); iRow != data.end(); ++iRow) { 
	
		// Get index of the layer for which the next row of bias weights is parsed
		int layerIndicator = (int)iRow->at(0);
		if (!_check_if_layer_indicator(layerIndicator)) {
			std::stringstream errmsg;
			errmsg << "  Error while parsing bias weight file (csv): Expected layer indicator at line " << std::distance(data.begin(), iRow) + 1  << ". Please use the training scripts provided with MeLOn to generate network files.";
			throw MelonException(errmsg.str());
		}								
		int iLayer = _get_layer_index_from_indicator(layerIndicator);

		// If the layer has any bias read it from the following line
		if (structure.biasConnect.at(iLayer) == 1) {
			++iRow;
			if (iRow->size() != structure.layerSize.at(iLayer)) {
				std::stringstream errmsg;
				errmsg << "  Error while parsing bias weight file (csv): Incorrect size of bias weight vector at line " << std::distance(data.begin(), iRow) + 1 << ". Please use the training scripts provided with MeLOn to generate network files.";
				throw MelonException(errmsg.str());
			}
			weights.biasWeight.at(iLayer) = *iRow;
			weightLayerLog.at(iLayer) = 1;
		}
	}

	// Check if bias weights were parsed for all layers with 
	if (weightLayerLog != structure.biasConnect) {
		std::stringstream errmsg;
		errmsg << "  Error while parsing bias weight file (csv): Missing input weights for layers: ";

		// Find missmatching layers by comparing the log to the bias connection vector
		auto misspair = std::mismatch(weightLayerLog.begin(), weightLayerLog.end(), structure.biasConnect.begin());
		while (true) {
			errmsg << std::distance(weightLayerLog.begin(), misspair.first);
			misspair = std::mismatch(++misspair.first, weightLayerLog.end(), ++misspair.second);
		
			if (misspair.first != weightLayerLog.end()) {
				errmsg << ", ";
			}
			else {
				break;
			}
		}
		errmsg << ". Please use the training scripts provided with MeLOn to generate network files.";

		throw MelonException(errmsg.str());
	}
};


/////////////////////////////////////////////////////////////////////////
// Parses the input weights
void AnnParserCsv::_parse_input_weights(const AnnStructure& structure, AnnWeights& weights) {
    
	// Read input weights from csv file
	std::vector<std::vector<double>> data = _csv_to_double_matrix(_modelName + "_IW.csv");

    // Initialize input weight matrix
    weights.inputWeight = std::vector<std::vector<std::vector<double>>>(structure.numLayers, std::vector<std::vector<double>>());

	// Defining vector for logging parsed weights (required for checking correctness of data)
	std::vector<int> weightLayerLog(structure.inputConnect.size(), 0);

	for (std::vector<std::vector<double>>::iterator iRow = data.begin(); iRow != data.end(); ++iRow) {
		
		// Get index of layer
		int layerIndicatorSource = (int)iRow->at(0);
		int layerIndicatorTarget = (int)iRow->at(1);
		if (!(_check_if_layer_indicator(layerIndicatorSource) && _check_if_layer_indicator(layerIndicatorTarget))) {
			std::stringstream errmsg;
			errmsg << "  Error while parsing input weight file (csv): Expected layer indicators at line " << std::distance(data.begin(), iRow) + 1 << ". Please use the training scripts provided with MeLOn to generate network files.";
			throw MelonException(errmsg.str());
		}
		int iLayer = _get_layer_index_from_indicator(layerIndicatorSource);

		// If layer is connected to the input, store the weight
		if (structure.inputConnect.at(iLayer) == 1) {

			// Define alias for layers weights
			auto& inputWeightLayer = weights.inputWeight.at(iLayer);

			// Store the weight vectors for each neuron in the layer (each row contains weights for one neuron)
			inputWeightLayer.resize(structure.layerSize.at(iLayer));
			for (int iNeuron = 0; iNeuron < structure.layerSize.at(iLayer); iNeuron++) {
				++iRow;
				if (iRow->size() != structure.inputSize) {
					std::stringstream errmsg;
					errmsg << "  Error while parsing bias weight file (csv): Incorrect size of input weight vector at line " << std::distance(data.begin(), iRow) + 1 << ". Please use the training scripts provided with MeLOn to generate network files.";
					throw MelonException(errmsg.str());
				}
				inputWeightLayer.at(iNeuron) = *iRow;
			}
			weightLayerLog.at(iLayer) = 1;
		}
	}

	// Check if input weights were parsed for all layers with incident input
	if (weightLayerLog != structure.inputConnect) {
		std::stringstream errmsg;
		errmsg << "  Error while parsing bias weight file (csv): Missing input weights for layers: ";

		// Find missmatching layers by comparing the log to the input connection vector
		auto misspair = std::mismatch(weightLayerLog.begin(), weightLayerLog.end(), structure.biasConnect.begin());
		while (true) {
			errmsg << std::distance(weightLayerLog.begin(), misspair.first);
			misspair = std::mismatch(++misspair.first, weightLayerLog.end(), ++misspair.second);
			if (misspair.first != weightLayerLog.end()) {
				errmsg << ", ";
			}
			else {
				break;
			}
		}
		errmsg << ". Please use the training scripts provided with MeLOn to generate network files.";

		throw MelonException(errmsg.str());
	}
};


/////////////////////////////////////////////////////////////////////////
// Parses the layer weights
void AnnParserCsv::_parse_layer_weights(const AnnStructure& structure, AnnWeights& weights) {
	
	// Read layer weighst from csv file
	std::vector<std::vector<double>> data = _csv_to_double_matrix(_modelName + "_LW.csv");
	
	// Initialize layer weight matrix
    weights.layerWeight = std::vector < std::vector<std::vector<std::vector<double>>>>(structure.numLayers, std::vector<std::vector<std::vector<double>>>(structure.numLayers, std::vector<std::vector<double>>()));

	// Defining vector for logging parsed weights (required for checking correctness of data)
	std::vector<std::vector<int>> weightLayerLog(structure.layerConnect.size(), std::vector<int>(structure.layerConnect.at(0).size(),0));

	for (std::vector<std::vector<double>>::iterator iRow = data.begin(); iRow != data.end(); ++iRow) {

		// Get index of source and target layer
		int layerIndicatorTarget = (int)iRow->at(0);
		int layerIndicatorSource = (int)iRow->at(1);
		if(!(_check_if_layer_indicator(layerIndicatorSource) && _check_if_layer_indicator(layerIndicatorTarget))){
			std::stringstream errmsg;
			errmsg << "  Error while parsing layer weight file (csv): Expected layer indicators at line " << std::distance(data.begin(), iRow) + 1 << ". Please use the training scripts provided with MeLOn to generate network files.";
			throw MelonException(errmsg.str());
		}
		int iLayerSource = _get_layer_index_from_indicator(layerIndicatorSource);
		int iLayerTarget = _get_layer_index_from_indicator(layerIndicatorTarget);

		if (structure.layerConnect.at(iLayerTarget).at(iLayerSource) == 1) {
			
			// Define alias for weights between source and target layer
			auto& incidentLayerWeights = weights.layerWeight.at(iLayerTarget).at(iLayerSource);

			// Store the weight vectors for each neuron in the target layer (each row contains weights for one neuron)
			incidentLayerWeights.resize(structure.layerSize.at(iLayerTarget));
			for (int iNeuron = 0; iNeuron < structure.layerSize.at(iLayerTarget); iNeuron++) {
				++iRow;
				if (iRow->size() != structure.layerSize.at(iLayerSource)) {
					std::stringstream errmsg;
					errmsg << "  Error while parsing layer weight file (csv): Incorrect size of layer weight vector at line " << std::distance(data.begin(), iRow) + 1 << ". Please use the training scripts provided with MeLOn to generate network files.";
					throw MelonException(errmsg.str());
				}
				incidentLayerWeights.at(iNeuron) = *iRow;
			}

			weightLayerLog.at(iLayerTarget).at(iLayerSource) = 1;
		}
	}

	// Check if input weights were parsed for all layers with incident input
	if (weightLayerLog != structure.layerConnect) {
		std::stringstream errmsg;
		errmsg << "  Error while parsing layer weight file (csv): Missing input weights for layer pairs (target, source): ";

		// Find missmatching layers by comparing the log to the layer connection vector
		for (size_t iLayer = 0; iLayer < weightLayerLog.size(); ++iLayer) {
			auto& layer = weightLayerLog.at(iLayer);
			auto misspair = std::mismatch(layer.begin(), layer.end(), structure.biasConnect.begin());
			while (true) {
				errmsg << "(" << iLayer << std::distance(layer.begin(), misspair.first) << ")";
				misspair = std::mismatch(++misspair.first, layer.end(), ++misspair.second);

				if (misspair.first != layer.end() || iLayer < weightLayerLog.size() - 1) {
					errmsg << ", ";
				}
				if (misspair.first == layer.end()){
					break;
				}
			}
		}
		errmsg << ". Please use the training scripts provided with MeLOn to generate network files.";

		throw MelonException(errmsg.str());
	}
};


/////////////////////////////////////////////////////////////////////////
// Parses the content of an csv file into a double matrix
std::vector<std::vector<double>> AnnParserCsv::_csv_to_double_matrix(std::string fileName) {
	
    // Open file
	std::string filePath = _format_file_path(_modelPath, _modelName + "/" + fileName, MODEL_FILE_TYPE::CSV);
    
	std::ifstream file(filePath);
    if (!file.is_open()) {
		throw MelonException("  Error while parsing model file : File \"" + filePath + "\" not found. \n  Please make sure that the model file is located in the correct directory.");
	}

    // Load lines from file to vector
    std::string line;
    std::vector<std::string> lines;
    while (file >> line) {
        lines.push_back(line);
    }

	// Convert string vector to double vector
	std::vector<std::vector<double>> data(lines.size());

    // Seperate strings at ','
    for (size_t iLine = 0; iLine != lines.size(); iLine++) {
        std::stringstream lineStream(lines.at(iLine));
        std::string datapoint;

        while (std::getline(lineStream, datapoint, ',')) {
            data.at(iLine).push_back(std::stod(datapoint));
        }
    }
	return data;
}


/////////////////////////////////////////////////////////////////////////
// Parses the content of an csv file into a string matrix
std::vector<std::vector<std::string>> AnnParserCsv::_csv_to_string_matrix(std::string fileName) {
	
    // Open file
	std::string filePath = _format_file_path(_modelPath, _modelName + "/" + fileName, MODEL_FILE_TYPE::CSV);
	
	std::ifstream file(filePath);
	if (!file.is_open()) {
		throw MelonException("  Error while parsing model file : File \"" + filePath + "\" not found. \n  Please make sure that the model file is located in the correct directory.");
	}

    // Load lines from file to vector
	std::string line;
	std::vector<std::string> lines;
	while (file >> line) {
        lines.push_back(line);
	}

    std::vector<std::vector<std::string>> data(lines.size());
	
    // Seperate strings at ','
	for (size_t iLine = 0; iLine != lines.size(); iLine++) {
		std::stringstream lineStream(lines.at(iLine));
		std::string datapoint;

		while (std::getline(lineStream, datapoint, ',')) {
			data.at(iLine).push_back(datapoint);
		}
	}

	return data;
}


/////////////////////////////////////////////////////////////////////////
// Checks if passed number is a layer indicator
bool AnnParserCsv::_check_if_layer_indicator(int number) {
	return (number - number % 100) == LAYER_INDICATOR_BASE;
};


/////////////////////////////////////////////////////////////////////////
// Extracts layer index from a layer indicator
int AnnParserCsv::_get_layer_index_from_indicator(int indicator) {
	return (indicator % LAYER_INDICATOR_BASE) - 1;
}
