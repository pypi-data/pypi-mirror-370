/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
*  @file ffNet.h
*
*  @brief File containing declaration of the FeedForwardNet class.
*
**********************************************************************************/

#pragma once

#include <vector>		// std::vector       a
#include <cmath>		// std::tanh
#include <algorithm>	// std::min, std::max, std::transform
#include <string>		// std::string, std::to_string
#include <utility>		// std::pair, std::make_pair
#include <memory>		// std::shared_ptr, std::make_shared

#include "vectorarithmetics.h"
#include "exceptions.h"
#include "MeLOn.h"
#include "AnnProperties.h"
#include "AnnParser.h"
#include "ffunc.hpp"

namespace melon {

    /**
    *  @enum TANH_REFORMULATION
    *  @brief Enum for representing the different reformulations for the tanh activation function
    */
    enum TANH_REFORMULATION {
        TANH_REF_0 = 0,     /*!< Standard tanh*/
        TANH_REF1,          /*!< tanh(x) = exp(x) - exp(-1 * x)) / (exp(x) + exp(-1 * x)*/
        TANH_REF2,          /*!< tanh(x) = (exp(2 * x) - 1) / (exp(2 * x) + 1)*/
        TANH_REF3,          /*!< tanh(x) = 1 - 2 / (1 + exp(2 * x))*/
        TANH_REF4           /*!< tanh(x) = (1 - exp(-2 * x)) / (1 + exp(-2 * x))*/
    };

    /**
    *  @enum SINGLE_NEURON_RELAXATION
    *  @brief Enum for representing the different relaxations for the tanh activation function in the multivariate case
    */
    enum SINGLE_NEURON_RELAXATION {
        TANH_MCCORMICK,                  /*!< Default tanh activation function */
        SINGLE_NEURON_MCCORMICK,         /*!< Default tanh activation function but called over intrinsic function of single_neuron*/
        SINGLE_NEURON_ENVELOPE,          /*!< Approach envelope */
        SINGLE_NEURON_MAX,               /*!< Approach maximum over different relaxations */
    };

    /**
    *  @class FeedForwardNet
    *  @brief This class represents a feed foward artificial network to be used in the MAiNGO solver.
    *
    * This class is used to enable the solution of optimization problems in MAiNGO containing feed foward ANNs. The trained ANNs can be loaded from csv/xml files created in matlab/keras.
    */
    template <typename T>
    class FeedForwardNet : public MelonModel<T> {
	private:

        std::shared_ptr<const AnnData> _annData;
		
		std::unique_ptr<Scaler<T>> _inputScaler;			/*!< Object for scaling input data*/
		std::unique_ptr<Scaler<T>> _outputScaler;			/*!< Object for scaling output data*/

        SINGLE_NEURON_RELAXATION single_neuron_type = TANH_MCCORMICK;

        T(*_tanh_formulation) (T) = &_tanh;                                                                                  /*!< pointer to the function used as formulation for the tanh */
		inline static T _tanh(T x) { using std::tanh;  return tanh(x); }
        inline static T _tanh_reformulation_1(T x) { return (exp(x) - exp(-1 * x)) / (exp(x) + exp(-1 * x)); }
        inline static T _tanh_reformulation_2(T x) { return (exp(2 * x) - 1) / (exp(2 * x) + 1); }
        inline static T _tanh_reformulation_3(T x) { return 1 - 2 / (1 + exp(2 * x)); }
        inline static T _tanh_reformulation_4(T x) { return (1 - exp(-2 * x)) / (1 + exp(-2 * x)); }
        
		inline static T _relu(T x) { using std::max; return max((T)0, x); }
        inline static T _relu6(T x) { using std::max; using std::min; return min((T)6, max((T)0, x)); }
      

        /**
        *  @brief Calculates the activations for a layer given its inputs
        *
        *  @param[in] v is a vector containing the summed inputs for each neuron in the layer
		*
        *  @param[in] activationFunction is an enum that determines which activation function should be applied to the layer
        *
        *  @return returns a vector containing the activation for each neuron in the layer
        */
        std::vector<T> _calculate_layer_activation(const std::vector<T>& v, const ACTIVATION_FUNCTION activationFunction);

        /**
        *  @brief Calculates the prediction of the feed forward net for a given point
        *
        *  @param[in] input is a vector containing input variables based on which the network is evaluated
        *
        *  @param[in] internalVariables is a vector containing values for the internal variables of the Network
        *
        *  @param[in] fullSpace indicates wether the network should be evaluated in fullspace mode (all internal variables are pre-set and given in variables and a vector of constraints is returned)
        *
        *  @param[out] constraints is a vector of constraints which are the difference of the given (in the vector variables) and calulated internal network variables.
        *
        *  @return returns a vector containing the network output values for the given input
        */
        std::vector<T> _calculate_prediction(const std::vector<T> input, const std::vector<T> internalVariables, const bool fullSpace, std::vector<T>& constraints);

		/**
		*  @brief Sets data object containing model parameters.
		*
		*  @param[in] modelData is a ModelData object containing the data which defines the model
		*/
		void _set_data_object(std::shared_ptr<const ModelData> modelData) override;

    public:
		
        /**
        *  @brief Constructor for creating object with no model loaded.
        */
        FeedForwardNet() : MelonModel<T>(std::make_shared<AnnParserFactory>()) {};

        /**
        *  @brief Constructor for creating object from file with the modelName relative to the current working directory.
        *
        *  @param[in] modelName is the name of the network
        *
        *  @param[in] fileType specifies the data format of the network file
        */
        FeedForwardNet(std::string modelName, MODEL_FILE_TYPE fileType) : FeedForwardNet() { this->load_model(modelName, fileType); };

        /**
        *  @brief Constructor for creating object from file with the modelName being relative to modelPath.
        *
        *  @param[in] modelPath is the path to the directory in which the network is located
        *
        *  @param[in] modelName is the name of the network
        *
        *  @param[in] fileType specifies the data format of the network file
        */
        FeedForwardNet(std::string modelPath, std::string modelName, MODEL_FILE_TYPE fileType) : FeedForwardNet() { this->load_model(modelPath, modelName, fileType); };

        /**
        *  @brief Constructor for creating object from existing AnnData object.
        *
        *  @param[in] modelData is a AnnData object containing the data which defines the network
        */
        FeedForwardNet(std::shared_ptr<AnnData> modelData) : FeedForwardNet() { this->load_model(modelData); };

        /**
        *  @brief Default Destructor
        */
        ~FeedForwardNet() = default;

        /**
        *  @brief Calculates the prediction of the feed forward net for a given point in reduced space mode (only values network inputs are given)
        *
        *  @param[in] input is a vector containing input values for which the network is evaluated
        *
        *  @return returns a vector containing the network output values for the given input
        */
        std::vector<T> calculate_prediction_reduced_space(const std::vector<T> input);

        /**
        *  @brief Calculates the prediction of the feed forward net for a given point in full space mode (values for all internal variables are given and a set of constraints is returned)
        *
        *  @param[in] input is a vector containing input values for which the network is evaluated
        *
        *  @param[in] internalVariables is a vector containing values for the internal variables  of the Network
        *
        *  @param[out] constraints is a vector containing all intermediate variables
        *
        *  @return returns a vector containing the network output values for the given input
        */
        std::vector<T> calculate_prediction_full_space(const std::vector<T> input, const std::vector<T> internalVariables, std::vector<T>& constraints);

        /**
        *  @brief Changes the reformulation to be used for tanh evaluations. The reformulations are intended to be used when solvers do not support the tanh function. As reformulations change the tightness of the McCormick envelopes when used with MAiNGO it is  recommended to use the standard tanh whenever possible.
        *
        *  @param[in] reformulation enum representing the desired tanh reformulation
        */
        void set_tanh_formulation(const TANH_REFORMULATION& reformulation);

        /**
        *  @brief Changes the calculation of relaxations to be used for tanh activation functions with multivariate input space. As reformulations change the tightness of the relaxations when used with MAiNGO.
        *
        *  @param[in] relaxation_type enum representing the desired relaxation of single_neuron activation function
        */
        void set_neuron_relaxation_for_tanh(const SINGLE_NEURON_RELAXATION& relaxation_type);

        /**
        *  @brief Get the number of internal network variables
        *
        *  @return returns number of internal variables
        */
        unsigned int get_number_of_full_space_variables();

        /**
        *  @brief Returns the number and the names of the internal variables of the network
        *
        *  @param[out] variableNumber is the number of internal network variables
        *
        *  @param[out] variableNames is a vector containing the names of all internal network variables
        *
        *  @param[out] variableBounds is a vector of pairs containing the bounds of the internal variables
        */
        void get_full_space_variables(unsigned int& variableNumber, std::vector<std::string>& variableNames, std::vector<std::pair<double, double>>& variableBounds);

    };

	/////////////////////////////////////////////////////////////////////////
	// Set data object containing model parameters
	template<typename T>
	void FeedForwardNet<T>::_set_data_object(std::shared_ptr<const ModelData> modelData) {

		// Check if you can downcast the ModelData pointer to an AnnData pointer
		_annData = std::dynamic_pointer_cast<const AnnData>(modelData);
		if (_annData == nullptr) {
			throw(MelonException("  Error while loading feed forward network: Incorrect type of passed data object. The data object must be of type AnnData."));
		}

		_inputScaler = ScalerFactory<T>::create_scaler(_annData->inputScalerData);
		_outputScaler = ScalerFactory<T>::create_scaler(_annData->outputScalerData);
	}

    /////////////////////////////////////////////////////////////////////////
    // Calculates the prediction of the feed forward net for a given point in reduced space mode (only values network inputs are given)
    template <typename T>
    std::vector<T> FeedForwardNet<T>::calculate_prediction_reduced_space(std::vector<T> input) {
        std::vector<T> dummyConstraints;
        std::vector<T> dummyInternalVariables;
        try {
            return _calculate_prediction(input, dummyInternalVariables, false, dummyConstraints);
        }
        catch (const std::exception& e) {
            throw(MelonException("  Encountered a fatal error while evaluating feed forward network. Terminating.", e));
        }
        catch (...) {
            throw(MelonException("  Encountered a fatal error while evaluating feed forward network. Terminating."));
        }
    }


    /////////////////////////////////////////////////////////////////////////
    // Calculates the prediction of the feed forward net for a given point in full space mode (values for all internal variables are given and a set of constraints is returned)
    template <typename T>
    std::vector<T> FeedForwardNet<T>::calculate_prediction_full_space(const std::vector<T> input, const std::vector<T> internalVariables, std::vector<T>& constraints) {
        try {
            return _calculate_prediction(input, internalVariables, true, constraints);
        }
        catch (const std::exception& e) {
            throw(MelonException("  Encountered a fatal error while evaluating feed forward network. Terminating.", e));
        }
        catch (...) {
            throw(MelonException("  Encountered a fatal error while evaluating feed forward network. Terminating."));
        }
    }


    /////////////////////////////////////////////////////////////////////////
    // Changes the reformulation to be used for tanh evaluations.
    template <typename T>
    void FeedForwardNet<T>::set_tanh_formulation(const TANH_REFORMULATION& reformulation) {
        switch (reformulation) {
        case TANH_REFORMULATION::TANH_REF_0:
			this->_tanh_formulation = &_tanh;
            break;
        case TANH_REFORMULATION::TANH_REF1:
            this->_tanh_formulation = &_tanh_reformulation_1;
            break;
        case TANH_REFORMULATION::TANH_REF2:
            this->_tanh_formulation = &_tanh_reformulation_2;
            break;
        case TANH_REFORMULATION::TANH_REF3:
            this->_tanh_formulation = &_tanh_reformulation_3;
            break;
        case TANH_REFORMULATION::TANH_REF4:
            this->_tanh_formulation = &_tanh_reformulation_4;
            break;
        default:
            throw MelonException("  Error while setting tanh formulation: Unknown tanh formulation.");
        }
    }

    /////////////////////////////////////////////////////////////////////////
    // Changes the relaxations to be used for single_neuron activation function.
    template <typename T>
    void FeedForwardNet<T>::set_neuron_relaxation_for_tanh(const SINGLE_NEURON_RELAXATION& relaxation_type) {
		this->single_neuron_type = relaxation_type;
    }

    /////////////////////////////////////////////////////////////////////////
    // Get the number of internal network variables
    template <typename T>
    unsigned int FeedForwardNet<T>::get_number_of_full_space_variables() {
        if (!MelonModel<T>::_modelLoaded) {
            throw MelonException("  Error: No network loaded.");
        }

        unsigned int variableNumber;
        std::vector<std::string> dummyVariableNames;
        std::vector<std::pair<double, double>> dummyVariableBounds;

        get_full_space_variables(variableNumber, dummyVariableNames, dummyVariableBounds);

        return variableNumber;
    }


    /////////////////////////////////////////////////////////////////////////
    // Returns the number and the names of the internal variables of the network
    template <typename T>
    void FeedForwardNet<T>::get_full_space_variables(unsigned int& variableNumber, std::vector<std::string>& variableNames, std::vector<std::pair<double, double>>& variableBounds) {
        if (!MelonModel<T>::_modelLoaded) {
            throw MelonException("  Error: No network loaded.");
        }

        // Create aliases for data
        auto& structure = _annData->structure;
        auto& weights = _annData->weights;

        const double MAX_BOUND = 10e6;
        variableNumber = 0;
        variableNames.clear();
        variableBounds.clear();

		// Normalized input
		if (structure.scaledInput) {
			variableNumber += structure.inputSize;
			for (int i = 0; i < structure.inputSize; i++) {
				variableNames.push_back("input_normalized_" + std::to_string(i));
				variableBounds.push_back(std::make_pair(-1., 1.));
			}
		}

        for (int iLayer = 0; iLayer < structure.numLayers; iLayer++) {

            if( !(structure.activationFunction.at(iLayer) == 1 && (single_neuron_type == SINGLE_NEURON_MCCORMICK || single_neuron_type == SINGLE_NEURON_ENVELOPE || single_neuron_type == SINGLE_NEURON_MAX))){ // not needed for single_neuron relaxation approach
                // Accumulated layer inputs
                variableNumber += structure.layerSize.at(iLayer);
                for (int iNeuron = 0; iNeuron < structure.layerSize.at(iLayer); iNeuron++) {
                    variableNames.push_back("layer_" + std::to_string(iLayer) + "_neuron_" + std::to_string(iNeuron) + "_acummulated_input");
                    variableBounds.push_back(std::make_pair(-MAX_BOUND, MAX_BOUND));
                }
            } 

            // Layer outputs
            variableNumber += structure.layerSize.at(iLayer);
            for (int iNeuron = 0; iNeuron < structure.layerSize.at(iLayer); iNeuron++) {
                variableNames.push_back("layer_" + std::to_string(iLayer) + "_neuron_" + std::to_string(iNeuron) + "_output");
                variableBounds.push_back(std::make_pair(-MAX_BOUND, MAX_BOUND));
            }
        }
		
        // Denormalized ouput
		if (structure.normalizedOutput) {
			variableNumber += structure.layerSize.back();
			for (int i = 0; i < structure.layerSize.back(); i++) {
				variableNames.push_back("output_" + std::to_string(i));
				variableBounds.push_back(std::make_pair(-MAX_BOUND, MAX_BOUND));
			}
		}
    }


    /////////////////////////////////////////////////////////////////////////
    // Calculates the prediction of the feed forward net for a given point
    template <typename T>
    std::vector<T> FeedForwardNet<T>::_calculate_prediction(const std::vector<T> input, const std::vector<T> internalVariables, const bool fullSpace, std::vector<T>& constraints) {
        if (MelonModel<T>::_modelLoaded) {
            // ---------------------------------------------------------------------------------
            // 0: Initialization
            // ---------------------------------------------------------------------------------

            // Create aliases for data
            auto& structure = _annData->structure;
            auto& weights = _annData->weights;

            // Check if variables vector has correct size
            if (input.size() != structure.inputSize) {
                throw MelonException("  Error while evaluating network: Incorrect number of variables. In reduced space mode evaluation the number of variables must be equal to the number of network inputs.");
            }
            if (fullSpace) {
                unsigned int variablesSize = get_number_of_full_space_variables();
                if (internalVariables.size() != variablesSize) {
                    throw MelonException("  Error while evaluating network: Incorrect number of variables. In full space mode evaluation the number of variables must be equal to the number of internal network variables.");
                }
            }

            std::vector<std::vector<T>> networkValues(structure.numLayers);

            auto variableIterator = internalVariables.begin();

            // ---------------------------------------------------------------------------------
            // 1: Normalize the input
            // ---------------------------------------------------------------------------------
			std::vector<T> normalizedInput = input;
			if (structure.scaledInput) {
				normalizedInput = _inputScaler->scale(input);
				if (fullSpace) {
					this->_set_constraints(constraints, normalizedInput, variableIterator);
				}
			}


            // ---------------------------------------------------------------------------------
            // 2: Evaluate each layer in the network
            // ---------------------------------------------------------------------------------
            for (size_t iLayer = 0; iLayer < networkValues.size(); iLayer++) {

                // Create aliases for better code readability
                auto& layerInputWeights = weights.inputWeight.at(iLayer);
                auto& layerBiasWeights = weights.biasWeight.at(iLayer);
                auto& layerIncidentLayerWeights = weights.layerWeight.at(iLayer);
                auto& layerConnections = structure.layerConnect.at(iLayer);
                auto& layerSize = structure.layerSize.at(iLayer);

                if (structure.activationFunction.at(iLayer) == 1 && single_neuron_type != TANH_MCCORMICK) { // using relaxation for a whole single_neuron (see intrinisic function single_neuron in MAiNGO)

                    //Matrix containing all the weights between layer iLayer and iLayer-1
                    std::vector<std::vector<double>> weightMatrix;
                    if (structure.inputConnect.at(iLayer) == 1)
                    {
                        weightMatrix = layerInputWeights;
                    } else
                    {
                        weightMatrix = layerIncidentLayerWeights.at(iLayer-1);
                    }

                    // Calculate the layer output by evaluating the activation function on the weighted sum at every neuron 
                    std::vector<T> layerOutput (layerSize);

                    int type; 
                    switch (single_neuron_type) {
                    case SINGLE_NEURON_RELAXATION::SINGLE_NEURON_MCCORMICK:
						type = 0;
						break;
                    case SINGLE_NEURON_RELAXATION::SINGLE_NEURON_ENVELOPE:
			            type = 1;
                        break;
                    case SINGLE_NEURON_RELAXATION::SINGLE_NEURON_MAX:
			            type = 2;
                        break;
                    }

                    for (size_t jNeuron = 0; jNeuron < layerSize; jNeuron++) {
                        if (structure.inputConnect.at(iLayer) == 1)
                        {
                            layerOutput.at(jNeuron) = mc::single_neuron(normalizedInput, weightMatrix[jNeuron], layerBiasWeights.at(jNeuron), type);
                        } else
                        {
                            layerOutput.at(jNeuron) = mc::single_neuron(networkValues.at(iLayer-1), weightMatrix[jNeuron], layerBiasWeights.at(jNeuron), type);
                        }
                    }
                    
                    if (fullSpace) {
                        this->_set_constraints(constraints, layerOutput, variableIterator);
                    }

                    networkValues.at(iLayer) = layerOutput;
                } else { // default case
                    // 1a Calculate weighted sum
                    std::vector<T> accumulatedLayerInputs(structure.layerSize.at(iLayer), 0);

                    // - input variables incident to the current layer
                    if (structure.inputConnect.at(iLayer) == 1) {
                        accumulatedLayerInputs = accumulatedLayerInputs + layerInputWeights * normalizedInput;
                    }

                    // - bias for the current layer
                    if (structure.biasConnect.at(iLayer) == 1) {
                        accumulatedLayerInputs = accumulatedLayerInputs + layerBiasWeights;
                    }

                    // - values from previous layers that are incident to the current layer
                    for (size_t iIncidentLayer = 0; iIncidentLayer < layerConnections.size(); iIncidentLayer++) {
                        if (layerConnections.at(iIncidentLayer) == 1) {
                            accumulatedLayerInputs = accumulatedLayerInputs + layerIncidentLayerWeights.at(iIncidentLayer)*networkValues.at(iIncidentLayer);
                        }
                    }

                    if (fullSpace) {
                        this->_set_constraints(constraints, accumulatedLayerInputs, variableIterator);
                    }

                    // 2b Calculate the layer output by evaluating the activation function on the weighted sum 
                    std::vector<T> layerOutput = _calculate_layer_activation(accumulatedLayerInputs, structure.activationFunction.at(iLayer));

                    if (fullSpace) {
                        this->_set_constraints(constraints, layerOutput, variableIterator);
                    }

                    networkValues.at(iLayer) = layerOutput;
                }
            }

            // ---------------------------------------------------------------------------------
            // 2: Denormalize network output
            // ---------------------------------------------------------------------------------
            std::vector<T> output = networkValues.back();
			if (structure.normalizedOutput) {
				output = _outputScaler->descale(networkValues.back());
				if (fullSpace) {
					this->_set_constraints(constraints, output, variableIterator);
				}
			}
            
            return output;
        }
        else {
            throw MelonException("  Error while evaluating network: No network loaded.");
        }
    };


    /////////////////////////////////////////////////////////////////////////
    // Calculates the activations for a layer given its inputs.
    template <typename T>
    std::vector<T> FeedForwardNet<T>::_calculate_layer_activation(const std::vector<T> &v, const ACTIVATION_FUNCTION activationFunction) {

        std::vector<T> layerActivation(v);

        // Select correct activation function
        T(*activation_function) (T);
        switch (activationFunction) {
        case ACTIVATION_FUNCTION::PURE_LIN:
            return layerActivation;
        case ACTIVATION_FUNCTION::TANH:
            activation_function = this->_tanh_formulation;
            break;
        case ACTIVATION_FUNCTION::RELU:
            activation_function = &_relu;
            break;
        case ACTIVATION_FUNCTION::RELU6:
            activation_function = &_relu6;
            break;
        }

        //  Apply activation function to all entries in v (layer neurons) and write the results to layerActivation
        std::transform(v.begin(), v.end(), layerActivation.begin(), activation_function);

        return layerActivation;
    };
}
