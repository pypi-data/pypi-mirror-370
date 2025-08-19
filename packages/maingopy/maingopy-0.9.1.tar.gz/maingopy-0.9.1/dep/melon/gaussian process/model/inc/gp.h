/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file gp.h
*
* @brief File containing declaration of the Gaussian process class.
*
**********************************************************************************/

#pragma once

#include <vector>		    // std::vector
#include <cmath>		    // std::tanh std::pow
#include <string>           // std::stoi 
#include <utility>		    // std::pair, std::make_pair
#include <memory>			// std::shared_ptr, std::unique_ptr, std::make_shared, std::make_unique, std::dynamic_pointer_cast
#include <algorithm>		// std::min_element, std::max_element, std::max

#include "vectorarithmetics.h"
#include "matern.h"
#include "exceptions.h"
#include "MeLOn.h"
#include "gpData.h"
#include "gpParser.h"

namespace melon {

    /**
    * @class GaussianProcess
    * @brief This class represents a Gaussian process, to be used in the MAiNGO solver.
    *
    * This class is used to enable the solution of optimization problems in MAiNGO containing Gaussian processes. The trained GPs can be loaded from json files created in matlab.
    */
	template<typename T>
	class GaussianProcess : public MelonModel<T> {
	private:

		std::shared_ptr<const GPData> _data;                            /*!< object containing the data and parameters of the Gaussian process */
		std::unique_ptr<kernel::StationaryKernel<double, T>> _kernel;   /*!< kernel object*/
		std::unique_ptr<Scaler<T>> _inputScaler;						/*!< Object for scaling input data*/
		std::unique_ptr<Scaler<T>> _predictionScaler;					/*!< Object for scaling output data*/
		std::unique_ptr<Scaler<double>> _parameterScaler;				/*!< Object for scaling double parameters*/

		/**
		*  @brief Sets data object containing model parameters.
		*
		*  @param[in] modelData is a ModelData object containing the data which defines the model
		*/
		void _set_data_object(std::shared_ptr<const ModelData> modelData) override;

		/**
		*  @brief Function for setting the kernel of the Gaussian process
		*
		*  @param[in] data is a pointer to a GPData object containing information about the kernel that should be set
		*/
		void _set_kernel(std::shared_ptr<const GPData> data);

		/**
		*  @brief Calculates the covariance vector of the Gaussian process for a given point
		*
		*  @param[in] input is a vector containing input point for which the covariance vector is calculated
		*
		*  @param[in] internalVariables is a iterator pointing to the beginning of the internal variables used in calculation of the covariance vector
		*
		*  @param[in] fullSpace indicates wether the Gaussian process should be evaluated in fullspace mode (all internal variables are pre-set and given in variables and a vector of constraints is returned)
		*
		*  @param[out] constraints is a vector of constraints which are the difference of the given (in the vector variables) and calulated internal Gaussian process variables.
		*
		*  @return returns the covariance vector
		*/
		template <typename RandomAccessIterator>
		std::vector<T> _calculate_covariance_vector(std::vector<T> input, RandomAccessIterator& internalVariables, const bool fullSpace, std::vector<T>& constraints) const;

		/**
		*  @brief Calculates the prediction of the Gaussian process for a given point
		*
		*  @param[in] covarianceVector is a vector based on which the prediction is calculated
		*
		*  @param[in] internalVariables is a iterator pointing to the beginning of the internal variables used in calculation of the prediction
		*
		*  @param[in] fullSpace indicates wether the Gaussian process should be evaluated in fullspace mode (all internal variables are pre-set and given in variables and a vector of constraints is returned)
		*
		*  @param[out] constraints is a vector of constraints which are the difference of the given (in the vector variables) and calulated internal Gaussian process variables.
		*
		*  @return returns the prediction
		*/
		template <typename RandomAccessIterator>
		T _calculate_prediction(std::vector<T> covarianceVector, RandomAccessIterator& internalVariables, const bool fullSpace, std::vector<T>& constraints) const;

		/**
		*  @brief Calculates the variance of the Gaussian process for a given point
		*
		*  @param[in] covarianceVector is a vector based on which the variance is calculated
		*
		*  @param[in] internalVariables is a iterator pointing to the beginning of the internal variables used in calculation of the variance
		*
		*  @param[in] fullSpace indicates wether the Gaussian process should be evaluated in fullspace mode (all internal variables are pre-set and given in variables and a vector of constraints is returned)
		*
		*  @param[out] constraints is a vector of constraints which are the difference of the given (in the vector variables) and calulated internal Gaussian process variables.
		*
		*  @return returns the variance
		*/
		template <typename RandomAccessIterator>
		T _calculate_variance(std::vector<T> covarianceVector, RandomAccessIterator& internalVariables, const bool fullSpace, std::vector<T>& constraints) const;

	public:

        /**
        *  @brief Default Constructor
        */
        GaussianProcess() : MelonModel<T>(std::make_shared<GpParserFactory>()) {};

        /**
        *  @brief Constructor
        *
        *  @param[in] modelName is the name of the Gaussian process
        */
        GaussianProcess(std::string modelName) : GaussianProcess() { MelonModel<T>::load_model(modelName, MODEL_FILE_TYPE::JSON); };

        /**
        *  @brief Constructor
        *
        *  @param[in] modelPath is the path to the directory in which the Gaussian process file is located
        *
        *  @param[in] modelName is the name of the Gaussian process
        */
        GaussianProcess(std::string modelPath, std::string modelName) : GaussianProcess() { MelonModel<T>::load_model(modelPath, modelName, MODEL_FILE_TYPE::JSON); };

        /**
        *  @brief Constructor
        *
        *  @param[in] modelData is a GPData object containing the data which defines the Gaussian process
        */
		GaussianProcess(std::shared_ptr<const GPData> modelData) : GaussianProcess() { MelonModel<T>::load_model(modelData); };

        /**
        *  @brief Calculates the prediction of the Gaussian process at a given point in reduced space mode (only network inputs are given)
        *
        *  @param[in] input is a vector containing input point for which the prediction of the Gaussian process is calculated
        *
        *  @return returns the prediction of the gaussian process
        */
		T calculate_prediction_reduced_space(std::vector<T> input) const; 
		
        /**
        *  @brief Calculates the variance of the Gaussian process at a given point in reduced space mode (only network inputs are given)
        *
        *  @param[in] input is a vector containing input point for which the variance of the Gaussian process is calculated
        *
        *  @return returns the variance of the gaussian process
        */
		T calculate_variance_reduced_space(std::vector<T> input) const;

        /**
        *  @brief Calculates the prediction of the Gaussian process at a given point in full space mode (values for all internal variables are given and a set of constraints is returned)
        *
        *  @param[in] input is a vector containing input point for which the prediction of the Gaussian process is calculated
        *
        *  @param[in] internalVariables is a vector containing values for the internal variables of the Gaussian process prediction calculation
        *
        *  @param[out] constraints is vector containing the evaluation of the fullspace constraints regarding the internal variables
        *
        *  @return returns the prediction of the gaussian process
        */
		T calculate_prediction_full_space(std::vector<T> input, std::vector<T> internalVariables, std::vector<T>& constraints) const;

        /**
        *  @brief Calculates the variance of the Gaussian process at a given point in full space mode (values for all internal variables are given and a set of constraints is returned)
        *
        *  @param[in] input is a vector containing input point for which the variance of the Gaussian process is calculated
        *
        *  @param[in] internalVariables is a vector containing values for the internal variables of the Gaussian process variance calculation
        *
        *  @param[out] constraints is vector containing the evaluation of the fullspace constraints regarding the internal variables
        *
        *  @return returns the variance of the gaussian process
        */
		T calculate_variance_full_space(std::vector<T> input, std::vector<T> internalVariables, std::vector<T>& constraints) const;

        /**
        *  @brief Calculates the prediction and the variance of the Gaussian process at a given point in full space mode (values for all internal variables are given and a set of constraints is returned)
        *
        *  @param[in] input is a vector containing input point for which prediction and variance of the Gaussian process are calculated
        *
        *  @param[in] internalVariables is a vector containing values for the internal variables of the Gaussian process predcition and variance calculation
        *
        *  @param[out] constraints is vector containing the evaluation of the fullspace constraints regarding the internal variables
        *
        *  @return returns a pair contianing the prediction and variance value
        */
        std::pair<T, T> calculate_prediction_and_variance_full_space(std::vector<T> input, std::vector<T> internalVariables, std::vector<T>& constraints) const;
		
        /**
        *  @brief Get the dimesnion of the input
        *
        *  @return returns input dimension
        */
		int get_input_dimension() const;
		
		/**
        *  @brief Get the number of training data points
        *
        *  @return returns number of training data points
        */
		int get_number_of_training_data_points() const;

		/**
		*  @brief Get the minimum value of the training data outputs
		*
		*  @return returns the minimum value of the training data outputs
		*/
		double get_minimum_of_training_data_outputs() const;

		/**
		*  @brief Get the maximum value of the training data outputs
		*
		*  @return returns the maximum value of the training data outputs
		*/
		double get_maximum_of_training_data_outputs() const;

        /**
        *  @brief Get the number of internal variables used in the calculation of the prediction
        *
        *  @return returns number of internal variables
        */
		unsigned int get_number_of_full_space_variables_prediction() const;

        /**
        *  @brief Get the properties of internal variables used in the calculation of the prediction 
        *
        *  @param[out] variableNumber is the number of internal variables
        *
        *  @param[out] variableNames is a vector containing the names of the internal variables
        *
        *  @param[out] variableBounds is a vector of pairs containing the bounds of the internal variables
        *
        *  @return returns number of internal variables
        */
		void get_full_space_variables_prediction(unsigned int& variableNumber, std::vector<std::string>& variableNames, std::vector<std::pair<double, double>>& variableBounds) const;
		
        /**
        *  @brief Get the number of internal variables used in the calculation of the variance
        *
        *  @return returns number of internal variables
        */
        unsigned int get_number_of_full_space_variables_variance() const;

        /**
        *  @brief Get the properties of internal variables used in the calculation of the variance
        *
        *  @param[out] variableNumber is the number of internal variables
        *
        *  @param[out] variableNames is a vector containing the names of the internal variables
        *
        *  @param[out] variableBounds is a vector of pairs containing the bounds of the internal variables
        *
        *  @return returns number of internal variables
        */
		void get_full_space_variables_variance(unsigned int& variableNumber, std::vector<std::string>& variableNames, std::vector<std::pair<double, double>>& variableBounds) const;
        
        /**
        *  @brief Get the number of internal variables used in the calculation of prediction and variance
        *
        *  @return returns number of internal variables
        */
        unsigned int get_number_of_full_space_variables_prediction_and_variance() const;

        /**
        *  @brief Get the properties of internal variables used in the calculation of prediction and variance
        *
        *  @param[out] variableNumber is the number of internal variables
        *
        *  @param[out] variableNames is a vector containing the names of the internal variables
        *
        *  @param[out] variableBounds is a vector of pairs containing the bounds of the internal variables
        *
        *  @return returns number of internal variables
        */
        void get_full_space_variables_prediction_and_variance(unsigned int& variableNumber, std::vector<std::string>& variableNames, std::vector<std::pair<double, double>>& variableBounds) const;

        /**
        *  @brief Get the observations based on which the Gaussian process was trained and is evaluated
        *
        *  @return returns the Gaussian process' training observations
        */
        std::vector<double> get_observations() const;

        /**
        *  @brief Returns the the normalized values of the observations based on which the Gaussian process was trained and is evaluated
        *
        *  @return returns the normalized Gaussian process' training observations
        */
        std::vector<double> get_normalized_observations() const { return _data->Y; }

        /**
        * @brief Getter for member variable _data
        */
        const GPData& data() const { return *_data; };

        /**
        * @brief Getter for member variable _kernel
        */
        const kernel::StationaryKernel<double, T>& kernel() const { return *_kernel; };

        /**
        * @brief Getter for member variable _inputScaler
        */
        const Scaler<T>& inputScaler() const { return *_inputScaler; };

        /**
        * @brief Getter for member variable _predictionScaler
        */
        const Scaler<T>& predictionScaler() const { return *_predictionScaler; };

        /**
        * @brief Getter for member variable _parameterScaler
        */
        const Scaler<T>& parameterScaler() const { return *_parameterScaler; };
	};


	/////////////////////////////////////////////////////////////////////////
	// Set data object containing model parameters
	template<typename T>
	void GaussianProcess<T>::_set_data_object(std::shared_ptr<const ModelData> modelData) {

		// Downcast the ModelData pointer to a GPData pointer
		_data = std::dynamic_pointer_cast<const GPData>(modelData);
		if(_data == nullptr){
			throw(MelonException("  Error while loading Gaussian process: Incorrect type of passed data object. The data object must be of type GPData."));
		}

		_set_kernel(_data);

		_inputScaler = ScalerFactory<T>::create_scaler(_data->inputScalerData);
		_predictionScaler = ScalerFactory<T>::create_scaler(_data->predictionScalerData);
		_parameterScaler =  ScalerFactory<double>::create_scaler(_data->predictionScalerData); // this scaler is used for double values only
	}


    /////////////////////////////////////////////////////////////////////////
	// Function for setting the kernel of the Gaussian process
    template<typename T>
	void GaussianProcess<T>::_set_kernel(std::shared_ptr<const GPData> data) {
        using namespace kernel;
        const int INF = 999;

		switch(_data->matern) {
			case 1:
				_kernel = std::make_unique<Matern12<double, T>>(_data->kernelData);
				break;
			case 3:
				_kernel = std::make_unique<Matern32<double, T>>(_data->kernelData);
				break;
			case 5:
				_kernel = std::make_unique<Matern52<double, T>>(_data->kernelData);
				break;
			case INF:
				_kernel = std::make_unique<MaternInf<double, T>>(_data->kernelData);
				break;
			default:
                throw(MelonException("  Encountered a fatal error while setting kernel: Unkown kernel."));
		}
	}


    /////////////////////////////////////////////////////////////////////////
    // Get the dimension of the input
	template<typename T>
	int GaussianProcess<T>::get_input_dimension() const {
        if (!MelonModel<T>::_modelLoaded) {
            throw MelonException("  Error: No Gaussian process loaded.");
        }

		return _data->DX;
	}


	/////////////////////////////////////////////////////////////////////////
	// Get the number of trainig data points
	template<typename T>
	int GaussianProcess<T>::get_number_of_training_data_points() const {
        if (!MelonModel<T>::_modelLoaded) {
            throw MelonException("  Error: No Gaussian process loaded.");
        }

		return _data->nX;
	}


	/////////////////////////////////////////////////////////////////////////
	// Get the minimum of trainig data outputs
	template<typename T>
	double GaussianProcess<T>::get_minimum_of_training_data_outputs() const {
        if (!MelonModel<T>::_modelLoaded) {
            throw MelonException("  Error: No Gaussian process loaded.");
        }

		using std::min_element;

		double minimum_scaled = *min_element(_data->Y.begin(), _data->Y.end());

		double result = _parameterScaler->descale({ minimum_scaled }).front();
		
		return  result;
	}

	/////////////////////////////////////////////////////////////////////////
	// Get the maximum of trainig data outputs
	template<typename T>
	double GaussianProcess<T>::get_maximum_of_training_data_outputs() const {
		if (!MelonModel<T>::_modelLoaded) {
			throw MelonException("  Error: No Gaussian process loaded.");
		}

		using std::max_element;

		double maximum_scaled = *max_element(_data->Y.begin(), _data->Y.end());

		double result = _parameterScaler->descale({maximum_scaled}).front();

		return result;
	}


    /////////////////////////////////////////////////////////////////////////
    // Get the observations based on which the Gaussian process was trained and is evaluated
	template<typename T>
	std::vector<double> GaussianProcess<T>::get_observations() const {
        if (!MelonModel<T>::_modelLoaded) {
            throw MelonException("  Error: No Gaussian process loaded.");
        }

		std::vector<double> _Y;
		for (auto y : _data->Y) {
			_Y.push_back(_parameterScaler->descale({ y }).front());
		}
		return _Y;
	}


    /////////////////////////////////////////////////////////////////////////
	// Calculates the prediction of the Gaussian process at a given point in reduced space mode (only network inputs are given)
	template <typename T>
	T GaussianProcess<T>::calculate_prediction_reduced_space(std::vector<T> input) const {
		std::vector<T> dummyConstraints;
        typename std::vector<T>::iterator dummyIterator;
        try {
            if (!MelonModel<T>::_modelLoaded) {
                throw MelonException("  Error while calculating Gaussian process prediction: No model was loaded yet.");
            }

            std::vector<T> covarianceVector = _calculate_covariance_vector(input, dummyIterator, false, dummyConstraints);
            return _calculate_prediction(covarianceVector, dummyIterator, false, dummyConstraints);
		}
		catch (const std::exception& e) {
			throw(MelonException("  Encountered a fatal error while calculating Gaussian process prediction. Terminating.", e));
		}
		catch (...) {
			throw(MelonException("  Encountered a fatal error while calculating Gaussian process prediction. Terminating."));
		}
	}


    /////////////////////////////////////////////////////////////////////////
	// Calculates the variance of the Gaussian process at a given point in reduced space mode (only network inputs are given)
    template <typename T>
    T GaussianProcess<T>::calculate_variance_reduced_space(std::vector<T> input) const {
        std::vector<T> dummyConstraints;
        std::vector<T> dummInternalVariables;
        typename std::vector<T>::iterator dummyIterator;
        try {
            if (!MelonModel<T>::_modelLoaded) {
                throw MelonException("  Error while calculating Gaussian process variance: No model was loaded yet.");
            }

            std::vector<T> covarianceVector = _calculate_covariance_vector(input, dummyIterator, false, dummyConstraints);
            return _calculate_variance(covarianceVector, dummyIterator, false, dummyConstraints);
        }
        catch (const std::exception& e) {
            throw(MelonException("  Encountered a fatal error while calculating Gaussian process variance. Terminating.", e));
        }
        catch (...) {
            throw(MelonException("  Encountered a fatal error while calculating Gaussian process variance. Terminating."));
        }
    }



    /////////////////////////////////////////////////////////////////////////
	// Calculates the prediction of the Gaussian process at a given point in full space mode (values for all internal variables are given and a set of constraints is returned)
	template <typename T>
	T GaussianProcess<T>::calculate_prediction_full_space(std::vector<T> input, std::vector<T> internalVariables, std::vector<T>& constraints) const {
		try {
            if (!MelonModel<T>::_modelLoaded) {
                throw MelonException("  Error while calculating Gaussian process prediction: No model was loaded yet.");
            }

            auto internalVariablesIterator = internalVariables.begin();
            std::vector<T> covarianceVector = _calculate_covariance_vector(input, internalVariablesIterator, true, constraints);
			return _calculate_prediction(covarianceVector, internalVariablesIterator, true, constraints);
		}
		catch (const std::exception& e) {
			throw(MelonException("  Encountered a fatal error while calculating Gaussian process prediction. Terminating.", e));
		}
		catch (...) {
			throw(MelonException("  Encountered a fatal error while calculating Gaussian process prediction. Terminating."));
		}
	}


    /////////////////////////////////////////////////////////////////////////
	// Calculates the variance of the Gaussian process at a given point in full space mode (values for all internal variables are given and a set of constraints is returned)
	template <typename T>
	T GaussianProcess<T>::calculate_variance_full_space(std::vector<T> input, std::vector<T> internalVariables, std::vector<T>& constraints) const {
		try {
            if (!MelonModel<T>::_modelLoaded) {
                throw MelonException("  Error while calculating Gaussian process variance: No model was loaded yet.");
            }

            auto internalVariablesIterator = internalVariables.begin();
            std::vector<T> covarianceVector = _calculate_covariance_vector(input, internalVariablesIterator, true, constraints);
			return _calculate_variance(covarianceVector, internalVariablesIterator, true, constraints);
		}
		catch (const std::exception& e) {
			throw(MelonException("  Encountered a fatal error while calculating Gaussian process variance. Terminating.", e));
		}
		catch (...) {
			throw(MelonException("  Encountered a fatal error while calculating Gaussian process variance. Terminating."));
		}
	}


    /////////////////////////////////////////////////////////////////////////
    // Calculates the prediction and the variance of the Gaussian process at a given point in full space mode (values for all internal variables are given and a set of constraints is returned)
    template <typename T>
    std::pair<T,T> GaussianProcess<T>::calculate_prediction_and_variance_full_space(std::vector<T> input, std::vector<T> internalVariables, std::vector<T>& constraints) const {
        try {
            if (!MelonModel<T>::_modelLoaded) {
                throw MelonException("  Error while calculating Gaussian process prediction and variance: No model was loaded yet.");
            } 

            auto internalVariablesIterator = internalVariables.begin();
            std::vector<T> covarianceVector = _calculate_covariance_vector(input, internalVariablesIterator, true, constraints);
            T prediction = _calculate_prediction(covarianceVector, internalVariablesIterator, true, constraints);
            T variance = _calculate_variance(covarianceVector, internalVariablesIterator, true, constraints);
            return std::make_pair(prediction, variance);
        }
        catch (const std::exception& e) {
            throw(MelonException("  Encountered a fatal error while calculating Gaussian process prediction and variance. Terminating.", e));
        }
        catch (...) {
            throw(MelonException("  Encountered a fatal error while calculating Gaussian process prediction and variance. Terminating."));
        }
    }


    /////////////////////////////////////////////////////////////////////////
    // Calculates the covariance vector of the Gaussian process for a given point
    template <typename T>
    template <typename RandomAccessIterator>
    std::vector<T> GaussianProcess<T>::_calculate_covariance_vector(std::vector<T> input, RandomAccessIterator& internalVariables, const bool fullSpace, std::vector<T>& constraints) const {
        
        // ---------------------------------------------------------------------------------
        // 0: Check input dimensions
        // ---------------------------------------------------------------------------------

        if (input.size() != _data->DX) {
            throw MelonException("  Error while calculating covariance vector: Incorrect input dimension. In reduced space mode evaluation the size of the variables vector must be equal to the input dimension of the gaussian process.");
        }
                
        // ---------------------------------------------------------------------------------
        // 1: Normalize inputs
        // ---------------------------------------------------------------------------------

        std::vector<T> normalizedInput = _inputScaler->scale(input);
        if (fullSpace) {
            MelonModel<T>::_set_constraints(constraints, normalizedInput, internalVariables);
        }

        // ---------------------------------------------------------------------------------
        // 2: Calculate covariance vector
        // ---------------------------------------------------------------------------------

        std::vector<T> covarianceVector(_data->nX, 0);
        for (std::vector<int>::size_type h = 0; h != _data->nX; h++) {         // h the row of X, column of the covariance function between X and X_test
            T distance = _kernel->calculate_distance(_data->X[h], normalizedInput);
            if (fullSpace) {
                MelonModel<T>::_set_constraints(constraints, distance, internalVariables);
            }

            covarianceVector.at(h) = _kernel->evaluate_kernel(distance);
            if (fullSpace) {
                MelonModel<T>::_set_constraints(constraints, covarianceVector.at(h), internalVariables);
            }
        }

        return covarianceVector;
    }


    /////////////////////////////////////////////////////////////////////////
	// Calculates the prediction of the Gaussian process for a given point
	template <typename T>
    template <typename RandomAccessIterator>
	T GaussianProcess<T>::_calculate_prediction(std::vector<T> covarianceVector, RandomAccessIterator& internalVariables, const bool fullSpace, std::vector<T>& constraints) const {
		
		// result_scaled = meanfunction + k_x_x * invK * (Y - meanfunction);
		std::vector<double> result_scaled;
        std::vector<double> observationDeviations = _data->Y - _data->meanfunction;
		result_scaled = _data->invK * observationDeviations;
		T predictionDeviation = dot_product(covarianceVector, result_scaled);
		
        T result_scaled_t = predictionDeviation + _data->meanfunction;
		if (fullSpace) {
			MelonModel<T>::_set_constraints(constraints, result_scaled_t, internalVariables);
		}

		// denormalization: result = MeanOfOutput + stdOfOutput * reslut_scaled
		T result = _predictionScaler->descale({ result_scaled_t }).front();
		if (fullSpace) {
			MelonModel<T>::_set_constraints(constraints, result, internalVariables);
		}

		return result;
	};


    /////////////////////////////////////////////////////////////////////////
	// Calculates the variance of the Gaussian process for a given point
    template <typename T>
    template <typename RandomAccessIterator>
    T GaussianProcess<T>::_calculate_variance(std::vector<T> covarianceVector, RandomAccessIterator& internalVariables, const bool fullSpace, std::vector<T>& constraints) const {

        // transpose the covariance function between X and X_test
        std::vector<T> ki_v = _data->invK * covarianceVector;
        T ki = dot_product(covarianceVector, ki_v);
        T normalizedResult = _data->kernelData->sf2 - ki;
        if (fullSpace) {
            MelonModel<T>::_set_constraints(constraints, normalizedResult, internalVariables);
        }

        T result = normalizedResult * pow(_data->stdOfOutput, 2); // scaling variance     
        using std::max;
        result = max(result, 1e-16); // Variance is always nonnegative. However, due to numerical issues in GP training (e.g., poor coditioning of K and inverse of K), we need max operator here.
        if (fullSpace) {
            MelonModel<T>::_set_constraints(constraints, result, internalVariables);
        }

        return result;
    }

	/////////////////////////////////////////////////////////////////////////
	// Get the number of internal variables used in the calculation of the prediction
	template <typename T>
	unsigned int GaussianProcess<T>::get_number_of_full_space_variables_prediction() const {
        if (!MelonModel<T>::_modelLoaded) {
            throw MelonException("  Error: No Gaussian process loaded.");
        }

		unsigned int variableNumber;
		std::vector<std::string> dummyVariableNames;
		std::vector<std::pair<double, double>> dummyVariableBounds;

		get_full_space_variables_prediction(variableNumber, dummyVariableNames, dummyVariableBounds);

		return variableNumber;
	}


    /////////////////////////////////////////////////////////////////////////
	// Get the properties of internal variables used in the calculation of the prediction 
	template <typename T>
	void GaussianProcess<T>::get_full_space_variables_prediction(unsigned int& variableNumber, std::vector<std::string>& variableNames, std::vector<std::pair<double,double>>& variableBounds) const {
        if (!MelonModel<T>::_modelLoaded) {
            throw MelonException("  Error: No Gaussian process loaded.");
        }

		const double MAX_BOUND = 10e6;
		variableNumber = 0;
		variableNames.clear();
		variableBounds.clear();

		variableNumber += _data->DX;
		for (size_t i = 0; i < _data->DX; i++) {
			variableNames.push_back("normalized_input_" + std::to_string(i));
			variableBounds.push_back(std::make_pair(-1, 1));
		}

		variableNumber += 2*_data->nX;
		for (size_t i = 0; i < _data->nX; i++) {
			variableNames.push_back("squared_distance_" + std::to_string(i));
			variableBounds.push_back(std::make_pair(0., MAX_BOUND));

            variableNames.push_back("covariance_" + std::to_string(i));
            variableBounds.push_back(std::make_pair(0., MAX_BOUND));
		}

		variableNumber += 1;
		variableNames.push_back("normalized_prediction");
		variableBounds.push_back(std::make_pair(-MAX_BOUND, MAX_BOUND));

		variableNumber += 1;
		variableNames.push_back("prediction");
		variableBounds.push_back(std::make_pair(-MAX_BOUND, MAX_BOUND));
	}


	/////////////////////////////////////////////////////////////////////////
	// Get the number of internal variables used in the calculation of the variance
	template <typename T>
	unsigned int GaussianProcess<T>::get_number_of_full_space_variables_variance() const {
        if (!MelonModel<T>::_modelLoaded) {
            throw MelonException("  Error: No Gaussian process loaded.");
        }

		unsigned int variableNumber;
		std::vector<std::string> dummyVariableNames;
		std::vector<std::pair<double, double>> dummyVariableBounds;

		get_full_space_variables_variance(variableNumber, dummyVariableNames, dummyVariableBounds);

		return variableNumber;
	}


    /////////////////////////////////////////////////////////////////////////
    // Get the properties of internal variables used in the calculation of the variance
    template <typename T>
    void GaussianProcess<T>::get_full_space_variables_variance(unsigned int& variableNumber, std::vector<std::string>& variableNames, std::vector<std::pair<double, double>>& variableBounds) const {
        if (!MelonModel<T>::_modelLoaded) {
            throw MelonException("  Error: No Gaussian process loaded.");
        }

        const double MAX_BOUND = 10e6;
        variableNumber = 0;
        variableNames.clear();
        variableBounds.clear();

        variableNumber += _data->DX;
        for (size_t i = 0; i < _data->DX; i++) {
            variableNames.push_back("normalized_input_" + std::to_string(i));
            variableBounds.push_back(std::make_pair(-1, 1));
        }

        variableNumber += 2 * _data->nX;
        for (size_t i = 0; i < _data->nX; i++) {
            variableNames.push_back("squared_distance_" + std::to_string(i));
            variableBounds.push_back(std::make_pair(0., MAX_BOUND));

            variableNames.push_back("covariance_" + std::to_string(i));
            variableBounds.push_back(std::make_pair(0., MAX_BOUND));
        }

        variableNumber += 1;
        variableNames.push_back("normalized_variance");
        variableBounds.push_back(std::make_pair(0.0, MAX_BOUND));

        variableNumber += 1;
        variableNames.push_back("variance");
        variableBounds.push_back(std::make_pair(1e-16, MAX_BOUND));
    }


    /////////////////////////////////////////////////////////////////////////
    // Get the number of internal variables used in the calculation of the prediction
    template <typename T>
    unsigned int GaussianProcess<T>::get_number_of_full_space_variables_prediction_and_variance() const {
        if (!MelonModel<T>::_modelLoaded) {
            throw MelonException("  Error: No Gaussian process loaded.");
        }

        unsigned int variableNumber;
        std::vector<std::string> dummyVariableNames;
        std::vector<std::pair<double, double>> dummyVariableBounds;

        get_full_space_variables_prediction_and_variance(variableNumber, dummyVariableNames, dummyVariableBounds);

        return variableNumber;
    }


    /////////////////////////////////////////////////////////////////////////
    // Get the properties of internal variables used in the calculation of prediction and variance
    template <typename T>
    void GaussianProcess<T>::get_full_space_variables_prediction_and_variance(unsigned int& variableNumber, std::vector<std::string>& variableNames, std::vector<std::pair<double, double>>& variableBounds) const {
        if (!MelonModel<T>::_modelLoaded) {
            throw MelonException("  Error: No Gaussian process loaded."); }

        const double MAX_BOUND = 10e6;
        variableNumber = 0;
        variableNames.clear();
        variableBounds.clear();

        variableNumber += _data->DX;
        for (size_t i = 0; i < _data->DX; i++) {
            variableNames.push_back("normalized_input_" + std::to_string(i));
            variableBounds.push_back(std::make_pair(-1, 1));
        }

        variableNumber += 2 * _data->nX;
        for (size_t i = 0; i < _data->nX; i++) {
            variableNames.push_back("squared_distance_" + std::to_string(i));
            variableBounds.push_back(std::make_pair(0., MAX_BOUND));

            variableNames.push_back("covariance_" + std::to_string(i));
            variableBounds.push_back(std::make_pair(0., MAX_BOUND));
        }

        variableNumber += 1;
        variableNames.push_back("normalized_prediction");
        variableBounds.push_back(std::make_pair(-MAX_BOUND, MAX_BOUND));

        variableNumber += 1;
        variableNames.push_back("prediction");
        variableBounds.push_back(std::make_pair(-MAX_BOUND, MAX_BOUND));

        variableNumber += 1;
        variableNames.push_back("normalized_variance");
        variableBounds.push_back(std::make_pair(0.0, MAX_BOUND));

        variableNumber += 1;
        variableNames.push_back("variance");
        variableBounds.push_back(std::make_pair(1e-16, MAX_BOUND));
    }
}

