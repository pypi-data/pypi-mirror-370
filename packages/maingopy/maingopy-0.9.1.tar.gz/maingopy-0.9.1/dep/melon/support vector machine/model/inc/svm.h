/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
*  @file svm.h
*
*  @brief File containing declaration of the support vector machine class.
*
**********************************************************************************/

#include <vector>
#include <string>
#include <cmath>
#include <memory>

#include "MeLOn.h"
#include "exceptions.h"
#include "kernel.h"
#include "scaler.h"
#include "vectorarithmetics.h"
#include "svmData.h"
#include "svmParser.h"

namespace melon {

	/**
	*  @class SupportVectorMachine
	*  @brief Class defining support vector machine to be used in the MAiNGO solver.
	*/
	template<typename T>
	class SupportVectorMachine : public MelonModel<T> {
	protected:
		std::shared_ptr<const SvmData> _data;						/*!< object containing the data and parameters of the svm */
		std::unique_ptr<kernel::StationaryKernel<double, T>> _kernel;   /*!< kernel object*/

		std::unique_ptr<Scaler<T>> _inputScaler;						/*!< Object for scaling input data*/
		std::unique_ptr<Scaler<T>> _outputScaler;						/*!< Object for scaling output data*/
		
		/**
		*  @brief Sets data object containing model parameters.
		*
		*  @param[in] modelData is a ModelData object containing the data which defines the model
		*/
		void _set_data_object(std::shared_ptr<const ModelData> modelData) override;

		/**
		*  @brief Calculates prediction
		*
		*  @param[in] input is a vector of inputs for which the prediction will be evaluated
		*
		*  @param[in] internalVariables holds variables that are used in full space formulation and not in reduced space
		*
		*  @param[in] fullSpace decides if evaluation shall be done in full or reduced space
		*
		*  @param[out] constraints will be filled in case of fullSpace formulation
		*
		*  @return returns the result of the evaluation
		*/
		T _calculate_prediction(std::vector<T> input, std::vector<T> internalVariables, const bool fullSpace, std::vector<T>& constraints);

		/**
		*  @brief Loads kernel according to loaded internal parameters
		*/
		void _update_kernel();

		/**
		*  @brief Decision function used by the different types of svms
		*
		*  @param[in] kernelValues is a vector containing the kernel evaluations for the the support vectors with the input.
		*
		*  @return returns the result of the decision function 
		*/
		virtual T _decision_function(std::vector<T> kernelValues) = 0;

	public:

		/**
		*  @brief Default Constructor
		*/
		SupportVectorMachine() : MelonModel<T>(std::make_shared<SvmParserFactory>()) {};

		/**
		*  @brief Constructor
		*
		*  @param[in] modelName is the name of the svm
		*/
		SupportVectorMachine(std::string modelName) : SupportVectorMachine() { this->load_model(modelName, MODEL_FILE_TYPE::JSON); };

		/**
		*  @brief Constructor
		*
		*  @param[in] modelPath is the path to the directory in which the svm file is located
		*
		*  @param[in] modelName is the name of the svm
		*/
		SupportVectorMachine(std::string modelPath, std::string modelName) : SupportVectorMachine() { this->load_model(modelPath, modelName, MODEL_FILE_TYPE::JSON); };

		/**
		*  @brief Constructor
		*
		*  @param[in] modelData is a SvmData object containing the data which defines the svm
		*/
		SupportVectorMachine(std::shared_ptr<const SvmData> modelData) : SupportVectorMachine() { this->load_model(modelData); };

		/**
		*  @brief Creates variables for the full space formulation in MAiNGO.
		*
		*  @param[out] variableNumber is the number of variables created
		*
		*  @param[out] variableNames is a vetor of the corresponding variable names
		*
		*  @param[out] variableBounds is a pair vector of bounds for each variable
		*/
		void get_fullspace_variables(size_t& variableNumber, std::vector<std::string>& variableNames, std::vector<std::pair<double, double>>& variableBounds);

		/**
		*  @brief Calculates prediction based on inputs and set constraints for fullspace formulation
		*
		*  @param[in] input is a vector of inputs for which the constraint will be evaluated
		*
		*  @param[in] internalVariables holds variables that are used in full space formulation and not in reduced space
		*
		*  @param[out] constraints will be filled in case of fullSpace formulation (such that internal Variables are equal to internal evaluation)
		*
		*  @return returns the result of the calculation
		*/
		T calculate_prediction_full_space(std::vector<T> input, std::vector<T> internalVariables, std::vector<T>& constraints);

		/**
		*  @brief Calculates prediction based on inputs in reduced space
		*
		*  @param[in] input is a vector of inputs for which the constraint will be evaluated
		*
		*  @return returns the result of the calculation
		*/
		T calculate_prediction_reduced_space(std::vector<T> input);

		/**
		*  @brief Calculates the number of full space variables.
		*
		*  @return returns the number of full space variables
		*/
		size_t get_number_of_full_space_variables();
	};

	/**
	*  @class SupportVectorRegression
	*  @brief Class defining support vector machine for regression to be used in the MAiNGO solver.
	*/
	template<typename T>
	class SupportVectorRegression : public SupportVectorMachine<T> {
	private:

		/**
		*  @brief Decision function for support vector regression
		*
		*  @param[in] input is a vector containing the kernel evaluations for the the support vectors with the input.
		*
		*  @return returns the result of the decision function
		*/
		T _decision_function(std::vector<T> input) override;
	public:
		// Inherit SupportVectorMachine constructors
		using SupportVectorMachine<T>::SupportVectorMachine;
	};

	/**
	*  @class SupportVectorMachineOneClass
	*  @brief Class defining support vector machine for one class classification to be used in the MAiNGO solver.
	*/
	template<typename T>
	class SupportVectorMachineOneClass : public SupportVectorMachine<T> {
	private:

		/**
		*  @brief Decision function for one class support vector machine
		*
		*  @param[in] input is a vector containing the kernel evaluations for the the support vectors with the input.
		*
		*  @return returns the result of the decision function
		*/
		T _decision_function(std::vector<T> input) override;
	public:
		// Inherit SupportVectorMachine constructors
		using SupportVectorMachine<T>::SupportVectorMachine; }; 

	/////////////////////////////////////////////////////////////////////////
	// Sets data object containing model parameters.
	template<typename T>
	void SupportVectorMachine<T>::_set_data_object(std::shared_ptr<const ModelData> modelData) {
		// Downcast the ModelData pointer to a SvmData pointer
		_data = std::dynamic_pointer_cast<const SvmData>(modelData);
		if (_data == nullptr) {
			throw(MelonException("  Error while loading support vector machine: Incorrect type of passed data object. The data object must be of type SvmData."));
		}

		_inputScaler = ScalerFactory<T>::create_scaler(_data->inputScalerData);
		_outputScaler = ScalerFactory<T>::create_scaler(_data->outputScalerData);
		_update_kernel();
	}


	/////////////////////////////////////////////////////////////////////////
	// Loads kernel according to loaded internal parameters
	template<typename T>
	void SupportVectorMachine<T>::_update_kernel() {
		switch (_data->kernelFunction) {
		case KERNEL_FUNCTION::RBF:
			_kernel = std::unique_ptr<kernel::KernelRBF<double, T>>(new kernel::KernelRBF<double, T>(_data->kernelParameters.front()));
		}
	}

	
	/////////////////////////////////////////////////////////////////////////
	// Calculates prediction based on inputs and set constraints for fullspace formulation
	template<typename T>
	T SupportVectorMachine<T>::calculate_prediction_full_space(std::vector<T> input, std::vector<T> internalVariables, std::vector<T>& constraints) {
		try{
			return _calculate_prediction(input, internalVariables, true, constraints);
		}
		catch (const std::exception& e) {
			throw(MelonException("  Encountered a fatal error while evaluating support vector machine. Terminating.", e));
		}
		catch (...) {
			throw(MelonException("  Encountered a fatal error while evaluating support vector machine. Terminating."));
		}

	}


	/////////////////////////////////////////////////////////////////////////
	// Calculates prediction based on inputs in reduced space
	template<typename T>
	T SupportVectorMachine<T>::calculate_prediction_reduced_space(std::vector<T> input) {
		std::vector<T> dummyInternalVariables;
		std::vector<T> dummyConstraints;
		try{
			return _calculate_prediction(input, dummyInternalVariables, false, dummyConstraints);
		}
		catch (const std::exception& e) {
			throw(MelonException("  Encountered a fatal error while evaluating support vector machine. Terminating.", e));
		}
		catch (...) {
			throw(MelonException("  Encountered a fatal error while evaluating support vector machine. Terminating."));
		}
	}


	/////////////////////////////////////////////////////////////////////////
	// Calculates prediction
	template<typename T>
	T  SupportVectorMachine<T>::_calculate_prediction(std::vector<T> input, std::vector<T> internalVariables, const bool fullSpace, std::vector<T>& constraints) {

		// ---------------------------------------------------------------------------------
		// 0: Check input dimensions
		// ---------------------------------------------------------------------------------

		if (input.size() != _data->supportVectors.at(0).size()) {
			throw MelonException("  Error while calculating svm prediction: Incorrect input dimension. In reduced space mode evaluation the size of the variables vector must be equal to the input dimension of the svm.");
		}
		if (fullSpace) {
			size_t variablesSize = get_number_of_full_space_variables();
			if (internalVariables.size() != variablesSize) {
				throw MelonException("  Error while calculating svm prediction: Incorrect input dimension. In full space mode evaluation the size of the variables vector be equal to the number of internal variables.");
			}
		}

		auto variableIterator = internalVariables.begin();
		if (this->_modelLoaded) {

			// ---------------------------------------------------------------------------------
			// 1: Scale inputs
			// ---------------------------------------------------------------------------------
		
			std::vector<T> scaledInput = _inputScaler->scale(input);
			if (fullSpace) {
				this->_set_constraints(constraints, scaledInput, variableIterator);
			}
		
			// ---------------------------------------------------------------------------------
			// 2: Evaluate kernel for support vectors and input
			// ---------------------------------------------------------------------------------

			std::vector<T> kernelValues;
			kernelValues.reserve(_data->supportVectors.size());
			for (auto& iSupportVector: _data->supportVectors) {
				T distance = _kernel->calculate_distance(iSupportVector, scaledInput);
				if (fullSpace) {
					this->_set_constraints(constraints, distance, variableIterator);
				}

				T kernelValue = _kernel->evaluate_kernel(distance);
				if (fullSpace) {
					this->_set_constraints(constraints, kernelValue, variableIterator);
				}

				kernelValues.push_back(kernelValue);
			}

			// ---------------------------------------------------------------------------------
			// 3: Evaluate decision function
			// ---------------------------------------------------------------------------------

			T result = _decision_function(kernelValues);
			if (fullSpace) {
				this->_set_constraints(constraints, result, variableIterator);
			}

			// ---------------------------------------------------------------------------------
			// 4: Descale ouput
			// ---------------------------------------------------------------------------------

			T output = _outputScaler->descale({ result }).front();
			if (fullSpace) {
				this->_set_constraints(constraints, output, variableIterator);
			}

			return  output;
		}
		else {
			throw MelonException{ "  Error while calculating support vector machine prediction: No model was loaded yet." };
		}
	}


	/////////////////////////////////////////////////////////////////////////
	// Decision function for support vector regression.
	template<typename T>
	T SupportVectorRegression<T>::_decision_function(std::vector<T> input) {
		return dot_product(this->_data->dualCoefficients, input) + this->_data->rho;
	}


	/////////////////////////////////////////////////////////////////////////
	// Decision function for one class support vector machine.
	template<typename T>
	T SupportVectorMachineOneClass<T>::_decision_function(std::vector<T> input) {
		return dot_product(this->_data->dualCoefficients, input) + this->_data->rho;
	}

	
	/////////////////////////////////////////////////////////////////////////
	// Calculates the number of full space variables.
	template<typename T>
	size_t SupportVectorMachine<T>::get_number_of_full_space_variables() {
		size_t variableNumber;
		std::vector<std::string> variableNames;
		std::vector<std::pair<double, double>> variableBounds;
		get_fullspace_variables(variableNumber, variableNames, variableBounds);
		return variableNumber;
	}


	/////////////////////////////////////////////////////////////////////////
	// Creates variables for the full space formulation in MAiNGO.
	template<typename T>
	void SupportVectorMachine<T>::get_fullspace_variables(size_t& variableNumber, std::vector<std::string>& variableNames, std::vector<std::pair<double, double>>& variableBounds) {

		variableNumber = 0;
		variableNames.clear();
		variableBounds.clear();


		// get max squared distance between support vectors
		auto n = this->_data->supportVectors.at(0).size();
		auto lbs = std::vector<double>(n, 1e6);
		auto ubs = std::vector<double>(n, -1e6);
		for (auto iSupportVector : this->_data->supportVectors) {
			for (int i = 0; i < iSupportVector.size(); i++) {
				auto xi = iSupportVector[i];
				if (xi < lbs[i]) lbs[i] = xi;
				if (xi > ubs[i]) ubs[i] = xi;
			}
		}
		double maxSquaredDistance = 0;
		for (size_t i = 0; i < lbs.size(); i++) {
			maxSquaredDistance = maxSquaredDistance + (ubs[i] - lbs[i])*(ubs[i] - lbs[i]);
		}

		//std::cout << "Hint: Using max squared distance = " << maxSquaredDistance << "\n\n\n";

		variableNumber += 2 * _data->dualCoefficients.size();
		for (int i = 0; i < _data->dualCoefficients.size(); i++) {
			variableNames.push_back("squared_distance_" + std::to_string(i));
			variableNames.push_back("kernel_value_" + std::to_string(i));
			variableBounds.push_back(std::make_pair(0., maxSquaredDistance));
			variableBounds.push_back(std::make_pair(0., 1.0));
		}

		double sum_alpha = 0;
		for (auto alpha : this->_data->dualCoefficients) {
			sum_alpha = sum_alpha + alpha;
		}

		variableNames.push_back("prediction");
		if (this->_data->kernelFunction == RBF) {
			variableBounds.push_back(std::make_pair(0, (sum_alpha - this->_data->rho)));
		}
		else {
			variableBounds.push_back(std::make_pair(-1e6, 1e6));

		}
		variableNumber++;
	}
}
