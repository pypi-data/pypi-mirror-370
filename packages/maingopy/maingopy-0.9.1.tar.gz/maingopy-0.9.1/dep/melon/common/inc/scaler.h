/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file scaler.h
*
* @brief File containing declaration of the scaler classes.
*
**********************************************************************************/

#pragma once

#include <vector>		// std::vector
#include <string>		// std::string
#include <memory>		// std::unique_ptr, std::make_unique
#include <unordered_map>	// std::unordered_map

#include "exceptions.h"

namespace melon {

	/**
	* @enum SCALER_TYPE
	* @brief Enum for representing the available types of scalers
	*/
	enum SCALER_TYPE {
		IDENTITY = 0,			/*!< identity scaler*/
		MINMAX,					/*!< MinMax scaler */
		STANDARD,               /*!< standard scaler */
	};

	/**
	* @enum ACTIVATION_FUNCTION
	* @brief Enum for representing the available types of scaler parameters
	*/
	enum SCALER_PARAMETER {
		LOWER_BOUNDS = 0,		/*!< lower bounds of training data*/
		UPPER_BOUNDS,           /*!< upper bounds of training data*/
		STD_DEV,				/*!< standard derivation of training data */
		MEAN,					/*!< mean of training data*/
		SCALED_LOWER_BOUNDS,	/*!< lower bound of scaled data*/
		SCALED_UPPER_BOUNDS		/*!< upper bound of scaled data*/
	};

	/**
	* @struct ScalerData
	* @brief Base struct from which data structs of different scalers can be derived.
	*/
	struct ScalerData {
		ScalerData(): type(SCALER_TYPE::IDENTITY) {};
		SCALER_TYPE type;														/*!< Type of scaler*/
		std::unordered_map<SCALER_PARAMETER, std::vector<double>> parameters;	/*!< Unordered map containing the different scaler parameters*/
	};

	/**
	* @class Scaler
	* @brief Abstract class defining scaling algorithm.
	*/
	template<typename T>
	class Scaler {
	public:
		/**
		* @brief Scales input values.
		*
		* @param[in] input is a vector of values that shoud get scaled.
		*
		* @return returns a vector of scaled values
		*/
		virtual std::vector<T> scale(const std::vector<T>& input) const = 0;

		/**
		* @brief Descales input values.
		*
		* @param[in] input is a vector of scaled values that shoud get descaled.
		*
		* @return returns a vector of descaled values
		*/
		virtual std::vector<T> descale(const std::vector<T>& input) const = 0;
		
		/**
		*  @brief Virtual desctructor to enable inheritance
		*
		*/
		virtual ~Scaler() = default;
	};

	/**
	* @class ScalerFactory
	* @brief This class is a factory class for creating child instances of Scaler.
	*/
	template<typename T>
	class ScalerFactory {
	public:

		/**
		*  @brief Factory function for creating a instance of a scaler object.
		*
		*  @param[in] scalerData struct containing the information and parameters of the scaler to be created.
		*
		*  @returns Pointer to an instance of a derived scaler class.
		*/
		static std::unique_ptr<Scaler<T>> create_scaler(const std::shared_ptr<const ScalerData> scalerData);
	};

	/**
	* @class IdentityScaler
	* @brief Class implementing an identity scaling algorithm.
	*/
	template<typename T>
	class IdentityScaler : public Scaler<T> {
	public:
		IdentityScaler() = default;
		~IdentityScaler() = default;

		/**
		* @brief Scales input value using the identity (= no scaling).
		*
		* @param[in] input is a vector of values that shoud get scaled.
		*
		* @return returns a vector of scaled values
		*/
		std::vector<T> scale(const std::vector<T>& input) const override { return input; };

		/**
		* @brief Scales input values (= no scaling).
		*
		* @param[in] input is a vector of values that shoud get scaled.
		*
		* @return returns a vector of scaled values
		*/
		std::vector<T> descale(const std::vector<T>& input) const override { return input; };
	};

	/**
	* @class MinMaxScaler
	* @brief Class implementing a MinMax-Scaling algorithm.
	*/
	template<typename T>
	class MinMaxScaler : public Scaler<T> {
	private:
		std::vector<double> _lowerBounds;
		std::vector<double> _upperBounds;

		std::vector<double> _scaledLowerBounds;
		std::vector<double> _scaledUpperBounds;

	public:
		MinMaxScaler(const std::vector<double>& lowerBounds, const std::vector<double>& upperBounds, const std::vector<double>& scaledLowerBounds, const std::vector<double>& scaledUpperBounds) : _lowerBounds(lowerBounds), _upperBounds(upperBounds), _scaledLowerBounds(scaledLowerBounds), _scaledUpperBounds(scaledUpperBounds) {};

		/**
		* @brief Scales input values using MinMax-Scaling.
		*
		* @param[in] input is a vector of values that shoud get scaled.
		*
		* @return returns a vector of scaled values
		*/
		std::vector<T> scale(const std::vector<T>& input) const override;

		/**
		* @brief Descales input values using MinMax-Scaling.
		*
		* @param[in] input is a vector of values that shoud get descaled.
		*
		* @return returns a vector of descaled values
		*/
		std::vector<T> descale(const std::vector<T>& input) const override;
	};

	/**
	* @class StandardScaler
	* @brief Class implementing a Standard-Scaling algorithm.
	*/
	template<typename T>
	class StandardScaler : public Scaler<T> {
	private:
		std::vector<double> _mean;
		std::vector<double> _stdDev;
	public:
		StandardScaler(const std::vector<double>& mean, const std::vector<double>& stdDev) : _mean(mean), _stdDev(stdDev) {};

		/**
		* @brief Scales input values using Standard-Scaling.
		*
		* @param[in] input is a vector of values that shoud get scaled.
		*
		* @return returns a vector of scaled values
		*/
		std::vector<T> scale(const std::vector<T>& input) const override;

		/**
		* @brief Descales input values using Standard-Scaling.
		*
		* @param[in] input is a vector of values that shoud get descaled.
		*
		* @return returns a vector of descaled values
		*/
		std::vector<T> descale(const std::vector<T>& input) const override;
	};

	/////////////////////////////////////////////////////////////////////////
	// Factory function for creating a instance of a scaler object.
	template<typename T>
	std::unique_ptr<Scaler<T>> ScalerFactory<T>::create_scaler(const std::shared_ptr<const ScalerData> scalerData) {
		try {
			switch (scalerData->type) {
			case SCALER_TYPE::IDENTITY:
				return std::make_unique<IdentityScaler<T>>();
			case SCALER_TYPE::MINMAX:
				return std::make_unique<MinMaxScaler<T>>(scalerData->parameters.at(SCALER_PARAMETER::LOWER_BOUNDS), scalerData->parameters.at(SCALER_PARAMETER::UPPER_BOUNDS), scalerData->parameters.at(SCALER_PARAMETER::SCALED_LOWER_BOUNDS), scalerData->parameters.at(SCALER_PARAMETER::SCALED_UPPER_BOUNDS));
			case SCALER_TYPE::STANDARD:
				return std::make_unique<StandardScaler<T>>(scalerData->parameters.at(SCALER_PARAMETER::MEAN), scalerData->parameters.at(SCALER_PARAMETER::STD_DEV));
			default:
				throw MelonException("  Error while creating sclaler: Invalid scaler type.");
			}
		}
		catch (const std::out_of_range& e) {
			throw MelonException("  Error while creating scaler: Scaler data object is missing a parameter.", e);
		}
	}


	/////////////////////////////////////////////////////////////////////////
	// Scales input values using MinMax-Scaling.
	template<typename T>
	std::vector<T> MinMaxScaler<T>::scale(const std::vector<T>& input) const {
		std::vector<T> output(input.size());
		for (size_t i = 0; i < input.size(); ++i) {
			output.at(i) = _scaledLowerBounds.at(i) + (input.at(i) - _lowerBounds.at(i)) / (_upperBounds.at(i) - _lowerBounds.at(i)) * (_scaledUpperBounds.at(i) - _scaledLowerBounds.at(i));
		}

		return output;
	}


	/////////////////////////////////////////////////////////////////////////
	// Decales input values using MinMax-Scaling.
	template<typename T>
	std::vector<T> MinMaxScaler<T>::descale(const std::vector<T>& input) const {
		std::vector<T> output(input.size());
		for (size_t i = 0; i < input.size(); ++i) {
			output.at(i) = _lowerBounds.at(i) + (input.at(i) - _scaledLowerBounds.at(i)) / (_scaledUpperBounds.at(i) - _scaledLowerBounds.at(i)) * (_upperBounds.at(i) - _lowerBounds.at(i));
		}
		
		return output;
	}


	/////////////////////////////////////////////////////////////////////////
	// Scales input values using Standard-Scaling.
	template<typename T>
	std::vector<T> StandardScaler<T>::scale(const std::vector<T>& input) const {
		std::vector<T> output(input.size());
		for (size_t i = 0; i < input.size(); ++i) {
			output.at(i) = (input.at(i) - _mean.at(i)) / _stdDev.at(i);
		}

		return output;
	}


	/////////////////////////////////////////////////////////////////////////
	// Descales input values using Standard-Scaling.


	template<typename T>
	std::vector<T> StandardScaler<T>::descale(const std::vector<T>& input) const {
		std::vector<T> output(input.size());
		for (size_t i = 0; i < input.size(); ++i) {
			output.at(i) = _stdDev.at(i)*input.at(i) + _mean.at(i);
		}

		return output;
	}
}
