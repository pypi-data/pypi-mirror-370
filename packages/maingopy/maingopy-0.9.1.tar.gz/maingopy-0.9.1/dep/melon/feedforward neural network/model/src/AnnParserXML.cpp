/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file AnnParserXML.cpp
*
* @brief File implementing the AnnParserXML class.
*
**********************************************************************************/

#include "AnnParser.h"

#include "tinyxml2.h"
#include "exceptions.h"

using namespace melon;


/////////////////////////////////////////////////////////////////////////
// Parsing function which is used to get the ANN data from a xml file
std::shared_ptr<ModelData> AnnParserXml::parse_model(const std::string modelPath, const std::string modelName) {

    // ---------------------------------------------------------------------------------
    // 0: Open the xml file
    // ---------------------------------------------------------------------------------

		std::string filePath = _format_file_path(modelPath, modelName, MODEL_FILE_TYPE::XML);

        // Load the xml file from given adress
        tinyxml2::XMLDocument xmlDoc;
        const char* charFilePath = (char*)filePath.data();
        tinyxml2::XMLError eResult = xmlDoc.LoadFile(charFilePath);
        if (eResult == 3) {
			throw MelonException("  Error while parsing model file : File \"" + filePath + "\" not found. \n  Please make sure that the model file is located in the correct directory.");
		}

        // Get root elements    
        tinyxml2::XMLNode * pRoot = xmlDoc.FirstChild();
		if (!pRoot) {
			throw MelonException("  Error while parsing network file (xml): Missing root node. Please use the training scripts provided with MeLOn to generate network files.");
		}

		tinyxml2::XMLElement * pElementValues = pRoot->FirstChildElement("Values");
		if (!pElementValues) {
			throw MelonException("  Error while parsing network file (xml): Missing element \"Values\" node. Please use the training scripts provided with MeLOn to generate network files.");
		}

        // Create aliases for data
		std::shared_ptr<AnnData> annData = std::make_shared<AnnData>();
		annData->inputScalerData = std::make_shared<ScalerData>();
		annData->outputScalerData = std::make_shared<ScalerData>();


        auto& structure = annData->structure;
        auto& weights = annData->weights;
		auto& inputScalerData = annData->inputScalerData;
		auto& outputScalerData = annData->outputScalerData;


    // ---------------------------------------------------------------------------------
    // 1: Obtain the structure of the ANN
    // ---------------------------------------------------------------------------------

        std::vector<std::vector<double>> inputWeightLight;
        std::vector<std::vector<std::vector<double>>> layerWeightLight;

		// Get the structure elements from xml
        tinyxml2::XMLElement * pElementArchitecture = pElementValues->FirstChildElement("Architecture");
		if (!pElementArchitecture) {
			throw MelonException("  Error while parsing network file (xml): Missing element \"Values->Architecture\". Please use the training scripts provided with MeLOn to generate network files.");
		}
        tinyxml2::XMLElement * pElementNumLayers = pElementArchitecture->FirstChildElement("NumberOfLayers");
		if (!pElementNumLayers) {
			throw MelonException("  Error while parsing network file (xml): Missing element \"Values->Architecture->NumberOfLayers\". Please use the training scripts provided with MeLOn to generate network files.");
		}
        tinyxml2::XMLElement * pElementNumInputs = pElementArchitecture->FirstChildElement("NumberOfInputs");
		if (!pElementNumInputs) {
			throw MelonException("  Error while parsing network file (xml): Missing element \"Values->Architecture->NumberOfInputs\". Please use the training scripts provided with MeLOn to generate network files.");
		}
        tinyxml2::XMLElement * pElementNumOutputs = pElementArchitecture->FirstChildElement("NumberOfOutputs");
		if (!pElementNumOutputs) {
			throw MelonException("  Error while parsing network file (xml): Missing element \"Values->Architecture->NumberOfOutputs\". Please use the training scripts provided with MeLOn to generate network files.");
		}
		tinyxml2::XMLElement * pElementLayerSizes = pElementArchitecture->FirstChildElement("LayerSizes");
		if (!pElementLayerSizes) {
			throw MelonException("  Error while parsing network file (xml): Missing element \"Values->Architecture->LayerSizes\". Please use the training scripts provided with MeLOn to generate network files.");
		}
		tinyxml2::XMLElement * pElementInputScaled = pElementValues->FirstChildElement("inputIsScaled")->FirstChildElement("inputIsScaled");
		if (!pElementArchitecture) {
			throw MelonException("  Error while parsing network file (xml): Missing element \"Values->inputIsScaled->inputIsScaled\". Please use the training scripts provided with MeLOn to generate network files.");
		}
		tinyxml2::XMLElement * pElementOutputNormalized = pElementValues->FirstChildElement("outputIsNormalized")->FirstChildElement("outputIsNormalized");
		if (!pElementArchitecture) {
			throw MelonException("  Error while parsing network file (xml): Missing element \"Values->outputIsNormalized->outputIsNormalized\". Please use the training scripts provided with MeLOn to generate network files.");
		}
    
        // Temporary variable
        int tmpOutputSize;

        // Get number of layers
        eResult = pElementNumLayers->QueryIntText(&(structure.numLayers));
		if (eResult != tinyxml2::XMLError::XML_SUCCESS) {
			throw MelonException("  Error while parsing network file (xml): Could not read element \"Values->Architecture->NumberOfLayers\". Please use the training scripts provided with MeLOn to generate network files.");
		}
        else if (structure.numLayers == 0) {
            throw MelonException("  Error while parsing network file (xml): Element \"Values->Architecture->NumberOfLayers\" has value 0, therefore no layers are defined for this network. Please use the training scripts provided with MeLOn to generate network files.");
        }

		// Get input size
        eResult = pElementNumInputs->QueryIntText(&(structure.inputSize));
		if (eResult != tinyxml2::XMLError::XML_SUCCESS) {
			throw MelonException("  Error while parsing network file (xml): Could not read element \"Values->Architecture->NumberOfInputs\". Please use the training scripts provided with MeLOn to generate network files.");
		}

		// Get sizes for each layer
        eResult = _parse_vector_int(pElementLayerSizes, "LayerSize", structure.layerSize);
		if (eResult != tinyxml2::XMLError::XML_SUCCESS) {
			throw MelonException("  Error while parsing network file (xml): Could not read sub elements of \"Values->Architecture->LayerSize\". Please use the training scripts provided with MeLOn to generate network files.");
		}
		eResult = pElementNumOutputs->QueryIntText(&tmpOutputSize);
		if (eResult != tinyxml2::XMLError::XML_SUCCESS) {
			throw MelonException("  Error while parsing network file (xml): Could not read element \"Values->Architecture->NumberOfOutputs\". Please use the training scripts provided with MeLOn to generate network files.");
		}
        structure.layerSize.push_back(tmpOutputSize);
		if (structure.layerSize.size() != structure.numLayers) {
			throw MelonException("  Error while parsing network file (xml): Incorect size of layer size vector. Please use the training scripts provided with MeLOn to generate network files.");
		}

        // All networks loaded from xml files have biases in every layer
        structure.biasConnect = std::vector<int>(structure.numLayers, 1);

        // In all networks loaded from xml files the input is only connected to the first layer
        structure.inputConnect = std::vector<int>(structure.numLayers, 0);
        structure.inputConnect.at(0) = 1;

        // In all networks loaded from xml files the layers are only connected to their previous layer
        structure.layerConnect = std::vector<std::vector<int>>(structure.numLayers, std::vector<int>(structure.numLayers, 0));
        for (int i = 1; i < structure.numLayers; ++i) {
            structure.layerConnect.at(i).at(i-1) = 1;
        }

		// Get flag values determinig wether in- or output normalization should be used
		int intScaledInput;
		eResult = pElementInputScaled->QueryIntText(&(intScaledInput));
		if (eResult != tinyxml2::XMLError::XML_SUCCESS) {
			throw MelonException("  Error while parsing network file (xml): Could not read element \"Values->inputIsScaled\". Please use the training scripts provided with MeLOn to generate network files.");
		}
		structure.scaledInput = bool(intScaledInput);

		int intNormalizedOutput;
		eResult = pElementOutputNormalized->QueryIntText(&(intNormalizedOutput));
		if (eResult != tinyxml2::XMLError::XML_SUCCESS) {
			throw MelonException("  Error while parsing network file (xml): Could not read element \"Values->outputIsNormalized\". Please use the training scripts provided with MeLOn to generate network files.");
		}
		structure.normalizedOutput = bool(intNormalizedOutput);

    // ---------------------------------------------------------------------------------
    // 2: Obtain the normalization parameters of the ANN
    // ---------------------------------------------------------------------------------
    
        // Get the bound/normalization parameter elements from xml 
        tinyxml2::XMLElement * pElementBounds = pElementValues->FirstChildElement("Bounds");
		if (!pElementBounds) {
			throw MelonException("  Error while parsing network file (xml): Missing element \"Values->Bounds\". Please use the training scripts provided with MeLOn to generate network files.");
		}
		tinyxml2::XMLElement * pElementStdofOutput;
		tinyxml2::XMLElement * pElementMeanofOutput;
		tinyxml2::XMLElement * pElementInputLowerBounds;
		tinyxml2::XMLElement * pElementInputUpperBounds;

		if (structure.normalizedOutput) {
			pElementStdofOutput = pElementValues->FirstChildElement("Stdofoutput");
			if (!pElementStdofOutput) {
				throw MelonException("  Error while parsing network file (xml): Missing element \"Values->Stdofoutput\". Please use the training scripts provided with MeLOn to generate network files.");
			}
			pElementMeanofOutput = pElementValues->FirstChildElement("Meanofoutput");
			if (!pElementMeanofOutput) {
				throw MelonException("  Error while parsing network file (xml): Missing element \"Values->Meanofoutput\". Please use the training scripts provided with MeLOn to generate network files.");
			}
		}
		if (structure.scaledInput) {
			pElementInputLowerBounds = pElementBounds->FirstChildElement("InputLowerBound");
			if (!pElementInputLowerBounds) {
				throw MelonException("  Error while parsing network file (xml): Missing element \"Values->Bounds->InputLowerBound\". Please use the training scripts provided with MeLOn to generate network files.");
			}
			pElementInputUpperBounds = pElementBounds->FirstChildElement("InputUpperBound");
			if (!pElementInputUpperBounds) {
				throw MelonException("  Error while parsing network file (xml): Missing element \"Values->Bounds->InputUpperBound\". Please use the training scripts provided with MeLOn to generate network files.");
			}
		}

        // Store values of normalization parameters
		if (structure.scaledInput) {

			// Set up input scaler
			inputScalerData->type = SCALER_TYPE::MINMAX;
			inputScalerData->parameters.emplace(SCALER_PARAMETER::LOWER_BOUNDS, std::vector<double>());
			inputScalerData->parameters.emplace(SCALER_PARAMETER::UPPER_BOUNDS, std::vector<double>());
			inputScalerData->parameters.emplace(SCALER_PARAMETER::SCALED_LOWER_BOUNDS, std::vector<double>(structure.inputSize, -1));
			inputScalerData->parameters.emplace(SCALER_PARAMETER::SCALED_UPPER_BOUNDS, std::vector<double>(structure.inputSize, 1));

			_parse_vector_double(pElementInputLowerBounds, "Bounds", inputScalerData->parameters.at(SCALER_PARAMETER::LOWER_BOUNDS));
			if (inputScalerData->parameters.at(SCALER_PARAMETER::LOWER_BOUNDS).size() != structure.inputSize) {
				throw MelonException("  Error while parsing network file (xml): Could not read sub elements of \"Values->Bounds->InputLowerBound\". Please use the training scripts provided with MeLOn to generate network files.");
			}

			_parse_vector_double(pElementInputUpperBounds, "Bounds", inputScalerData->parameters.at(SCALER_PARAMETER::UPPER_BOUNDS));
			if (inputScalerData->parameters.at(SCALER_PARAMETER::UPPER_BOUNDS).size() != structure.inputSize) {
				throw MelonException("  Error while parsing network file (xml): Could not read sub elements of \"Values->Bounds->InputUpperBound\". Please use the training scripts provided with MeLOn to generate network files.");
			}
		}

		if (structure.normalizedOutput) {

			// Set up output scaler
			outputScalerData->type = SCALER_TYPE::STANDARD;
			outputScalerData->parameters.emplace(SCALER_PARAMETER::MEAN, std::vector<double>());
			outputScalerData->parameters.emplace(SCALER_PARAMETER::STD_DEV, std::vector<double>());

			_parse_vector_double(pElementStdofOutput, "outputStd", outputScalerData->parameters.at(SCALER_PARAMETER::STD_DEV));
			if (outputScalerData->parameters.at(SCALER_PARAMETER::STD_DEV).size() != structure.layerSize.back()) {
				throw MelonException("  Error while parsing network file (xml): Could not read sub elements of \"Values->Stdofoutput\". Please use the training scripts provided with MeLOn to generate network files.");
			}

			_parse_vector_double(pElementMeanofOutput, "outputMean", outputScalerData->parameters.at(SCALER_PARAMETER::MEAN));
			if (outputScalerData->parameters.at(SCALER_PARAMETER::MEAN).size() != structure.layerSize.back()) {
				throw MelonException("  Error while parsing network file (xml): Could not read sub elements of \"Values->Meanofoutput\". Please use the training scripts provided with MeLOn to generate network files.");
			}
		}

    // ---------------------------------------------------------------------------------
    // 3: Obtain the weights of the ANN
    // ---------------------------------------------------------------------------------

        // Get the weight elements from xml 
        tinyxml2::XMLElement * pElementLayers = pElementValues->FirstChildElement("Layers");
		if (!pElementLayers) {
			throw MelonException("  Error while parsing network file (xml): Missing element \"Values->Layer\". Please use the training scripts provided with MeLOn to generate network files.");
		}

        // Iterate over layers
        for (int iLayer = 0; iLayer < structure.numLayers; ++iLayer)
        {
            // Set layer name
            std::string layerString = "Layer_" + std::to_string(iLayer);

            // Get the weight elements from xml for current layer
            tinyxml2::XMLElement * pElementLayerSingle = pElementLayers->FirstChildElement(layerString.c_str());
			if (!pElementLayerSingle) {
				throw MelonException("  Error while parsing network file (xml): Missing element \"Values->Layer->" + layerString + "\". Please use the training scripts provided with MeLOn to generate network files.");
			}
            tinyxml2::XMLElement * pElementBias = pElementLayerSingle->FirstChildElement("Bias");
			if (!pElementBias) {
				throw MelonException("  Error while parsing network file (xml): Missing element \"Values->Layer->" + layerString + "->Bias\". Please use the training scripts provided with MeLOn to generate network files.");
			}
            tinyxml2::XMLElement * pElementWeights = pElementLayerSingle->FirstChildElement("Weights");
			if (!pElementWeights) {
				throw MelonException("  Error while parsing network file (xml): Missing element \"Values->Layer->" + layerString + "->Weights\". Please use the training scripts provided with MeLOn to generate network files.");
			}
			tinyxml2::XMLElement * pElementActivationFunction = pElementLayerSingle->FirstChildElement("ActivationFunction");
			if (!pElementActivationFunction) {
				throw MelonException("  Error while parsing network file (xml): Missing element \"Values->Layer->" + layerString + "->ActivationFunction\". Please use the training scripts provided with MeLOn to generate network files.");
			}

            // 3.1: Obtain bias values ------------------------------------------------

            // Temporary variables
            std::vector<double> tmpLayerBias;

            // Store values of bias parameters
            _parse_vector_double(pElementBias, "Bias", tmpLayerBias);
            weights.biasWeight.push_back(tmpLayerBias);
			if (tmpLayerBias.size() != structure.layerSize.at(iLayer)) {
				throw MelonException("  Error while parsing network file (xml): Incorrect size of bias vector in element \"Values->Layer->" + layerString + "->Bias\". Please use the training scripts provided with MeLOn to generate network files.");
			}
			
            // 3.2: Obtain weight values ------------------------------------------------

            // helper variables for iteration over weights
            double tmpWeight;
            std::vector<double> weightsToIncidentNeuron;
            std::vector<std::vector<double>> layerWeightMatrix;
            int iNeuron = 0;

            // Iterate over a weight vector with the form (w_11, ..., w_1m, ..., w_n1, ..., w_nm) 
            // where the first index indicates the neurons of the previous layer and the second one the neurons of the current layer
            for (tinyxml2::XMLElement * pElementSingleWeight = pElementWeights->FirstChildElement("Weight"); pElementSingleWeight != NULL;
                pElementSingleWeight = pElementSingleWeight->NextSiblingElement("Weight"))
            {

                // Get weight value and store it to a vector 
                eResult = pElementSingleWeight->QueryDoubleText(&tmpWeight);
				if (eResult != tinyxml2::XMLError::XML_SUCCESS) {
					throw MelonException("  Error while parsing network file (xml): Could not read subelement of \"Values->" + layerString + "->Weights->InputLowerBound\". Please use the training scripts provided with MeLOn to generate network files.");
				}
                weightsToIncidentNeuron.push_back(tmpWeight);

                // Increase neuron index
                ++iNeuron;

                // When all weights corresponding to a neuron from the previous layer are stored, add the vector to the layers weightmatrix and clear it.
                if (iNeuron == structure.layerSize.at(iLayer)) {
                    layerWeightMatrix.push_back(weightsToIncidentNeuron);
                    weightsToIncidentNeuron.clear();
                    iNeuron = 0;
                }
            }
			
			// Check if all weights were parsed
			if ((iLayer == 0 && layerWeightMatrix.size() != structure.inputSize) || (iLayer > 0 && layerWeightMatrix.size() != structure.layerSize.at(iLayer - 1))) {
				throw MelonException("  Error while parsing network file (xml): Incorrect size of weight vector in element \"Values->Layer->" + layerString + "->Weights\". Please use the training scripts provided with MeLOn to generate network files.");
			}
		
            // Transpose weight matrix
            int nRows = layerWeightMatrix.size();
            int nCols = layerWeightMatrix.at(0).size();
            std::vector<std::vector<double>> layerWeightMatrixTransposed(nCols, std::vector<double>(nRows));
            for (int i = 0; i < nRows; i++) {
                for (int j = 0; j < nCols; j++) {
                    layerWeightMatrixTransposed[j][i] = layerWeightMatrix[i][j];
                }
            }

            // Store input layer weight matrix in seperate variable
            if (iLayer == 0) {
                inputWeightLight = layerWeightMatrixTransposed;
            }
            else {
                layerWeightLight.push_back(layerWeightMatrixTransposed);
            }


            // 3.2: Obtain activation function ------------------------------------------------

            ACTIVATION_FUNCTION singleActFct = _string_to_activation_function(pElementActivationFunction->GetText());

            structure.activationFunction.push_back(singleActFct);
		}

        // Embed the single weight matrices for each layer two for all (one for input weights and one for layer weights) 

        // In all networks loaded from xml files the input is only connected to the first layer
        weights.inputWeight = std::vector<std::vector<std::vector<double>>>(structure.numLayers, std::vector<std::vector<double>>());
        weights.inputWeight.at(0) = inputWeightLight;
    
        // In all networks loaded from xml files the layers are only connected to their previous layer
        weights.layerWeight = std::vector<std::vector<std::vector<std::vector<double>>>>(structure.numLayers, std::vector<std::vector<std::vector<double>>>(structure.numLayers, std::vector<std::vector<double>>()));
        for (int i = 0; i < structure.numLayers - 1; i++) {
            weights.layerWeight.at(i + 1).at(i) = layerWeightLight.at(i);
        }

		return annData;
}


/////////////////////////////////////////////////////////////////////////
// Parses child elements of an xml element into an vector of int
tinyxml2::XMLError AnnParserXml::_parse_vector_int(tinyxml2::XMLElement *parentElement, const std::string vectorName, std::vector<int>& vector) {
    
	tinyxml2::XMLError eResult = tinyxml2::XMLError::XML_SUCCESS;

    for (tinyxml2::XMLElement * pElement = parentElement->FirstChildElement(vectorName.c_str()); pElement != NULL;
        pElement = pElement->NextSiblingElement(vectorName.c_str()))
    {
        int tmpValue;
        eResult = pElement->QueryIntText(&tmpValue);
		if (eResult != tinyxml2::XMLError::XML_SUCCESS) {
			break;
		}
        vector.push_back(tmpValue);
    }

	return eResult;
}


/////////////////////////////////////////////////////////////////////////
// Parses child elements of an xml element into an vector of double
tinyxml2::XMLError AnnParserXml::_parse_vector_double(tinyxml2::XMLElement *parentElement, const std::string vectorName, std::vector<double>& vector) {

	tinyxml2::XMLError eResult = tinyxml2::XMLError::XML_SUCCESS;

    for (tinyxml2::XMLElement * pElement = parentElement->FirstChildElement(vectorName.c_str()); pElement != NULL;
        pElement = pElement->NextSiblingElement(vectorName.c_str()))
    {
        double tmpValue;
        eResult = pElement->QueryDoubleText(&tmpValue);
		if (eResult != tinyxml2::XMLError::XML_SUCCESS) {
			break;
		}
        vector.push_back(tmpValue);
    }

	return eResult;
}