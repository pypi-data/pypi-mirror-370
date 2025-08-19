/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file mulfilGp.h
*
* @brief File that contains the declaration of the multifidelity Gaussian process class
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
#include "modelParser.h"
#include "mulfilGpData.h"
#include "mulfilGpParser.h"
#include "gp.h"

namespace melon {

    /**
    * @class MulfilGp
    * @brief Class that represents a multifidelity Gaussian process, to be used in the MAiNGO solver
    *
    * Refer to 'DOI: 10.1615/Int.J.UncertaintyQuantification.2014006914' for more information.
    * Currently only two levels of fidelity (low and high fidelity), a constant rho and no noise are supported.
    * The input sets for low and high fidelity are expected to be nested.
    *
    *
    */
    template<typename T>
    class MulfilGp : public MelonModel<T> {

    private:

        std::shared_ptr<const MulfilGpData> _data{};                                            /*!< Object containing the data and parameters of the multifidelity Gaussian process */
        std::shared_ptr<GaussianProcess<T>> _lowGp{ std::make_shared<GaussianProcess<T>>() };   /*!< Low fidelity GP object*/
        std::shared_ptr<GaussianProcess<T>> _auxGp{ std::make_shared<GaussianProcess<T>>() };   /*!< Auxiliary GP object used for high fidelity GP predictions*/

        /**
        *  @brief Override function that sets the member variables according to a MulfilGpData object
        *
        *  @param[in] modelData Pointer of ModelData pointing to a MulfilGpData object
        */
        void _set_data_object(std::shared_ptr<const ModelData> modelData) override;

    public:

        /**
        *  @brief Default constructor
        */
        MulfilGp() : MelonModel<T>(std::make_shared<MulfilGpParserFactory>()) {};

        /**
        *  @brief Constructor
        *
        *  @param[in] modelName  Name of the folder with the data files lowGpData.json, highGpData.json, rho.json,
        *  which contain all information for creating a multifidelity Gaussian process
        */
        explicit MulfilGp(std::string modelName) : MulfilGp() { MelonModel<T>::load_model(modelName, MODEL_FILE_TYPE::JSON); };

        /**
        *  @brief Constructor
        *
        * @param[in] modelPath Path to the parent folder of the folder with the data files
        * 
        *  @param[in] modelName  Name of the folder with the data files lowGpData.json, highGpData.json, rho.json,
        *  which contain all information for creating a multifidelity Gaussian process
        */
        MulfilGp(std::string modelPath, std::string modelName) : MulfilGp() { MelonModel<T>::load_model(modelPath, modelName, MODEL_FILE_TYPE::JSON); };

        /**
        *  @brief Constructor
        *
        *  @param[in] modelData Contains the data and parameters of the multifidelity Gaussian process
        */
        explicit MulfilGp(std::shared_ptr<const MulfilGpData> modelData) : MulfilGp() { MelonModel<T>::load_model(modelData); };

        /**
        *  @brief Calculates the prediction of the low fidelity Gaussian process at a given point in reduced space mode
        *
        *  @param[in] input Vector that contains the input point for which the prediction is calculated
        *
        *  @return Prediction of the low fidelity Gaussian process
        */
        T calculate_low_prediction_reduced_space(std::vector<T>& input) const;

        /**
        *  @brief Calculates the variance of the low fidelity Gaussian process at a given point in reduced space mode
        *
        *  @param[in] input Vector that contains the input point for which the variance is calculated
        *
        *  @return Variance of the low fidelity Gaussian process
        */
        T calculate_low_variance_reduced_space(std::vector<T>& input) const;

        /**
        *  @brief Calculates the prediction of the high fidelity Gaussian process at a given point in reduced space mode
        *
        *  @param[in] input Vector that contains the input point for which the prediction is calculated
        *
        *  @return Prediction of the high fidelity Gaussian process
        */
        T calculate_high_prediction_reduced_space(std::vector<T>& input) const;

        /**
        *  @brief Calculates the variance of the high fidelity Gaussian process at a given point in reduced space mode
        *
        *  @param[in] input Vector that contains the input point for which the variance is calculated
        *
        *  @return Variance of the high fidelity Gaussian process
        */
        T calculate_high_variance_reduced_space(std::vector<T>& input) const;

        /**
        *  @brief Getter for member variable _data
        */
        const MulfilGpData& data() const { return *_data; };

        /**
        *  @brief Getter for member variable _lowGp
        */
        const GaussianProcess<T>& lowGp() const { return *_lowGp; };
        
        /**
        *  @brief Getter for member variable _auxGp
        */
        const GaussianProcess<T>& auxGp() const { return *_auxGp; };
    };

    template<typename T>
    void MulfilGp<T>::_set_data_object(std::shared_ptr<const ModelData> modelData) {

        // Cast the ModelData pointer to a MulfilGpData pointer
        _data = std::dynamic_pointer_cast<const MulfilGpData>(modelData);
        if (_data == nullptr) {
            throw(MelonException("  Error while loading multifidelity Gaussian process: Incorrect type of passed data object. The data object must be of type MulfilGpData."));
        }

        // Low fidelity GP
        _lowGp->MelonModel<T>::load_model(std::make_shared<const GPData>(_data->lowGpData));

        // Auxiliary GP
        // The data of the auxiliary GP (auxData) can be derived from _data->highGpData and from _lowGp.calculate_prediction_reduced_space()

        auto inputScaler{ ScalerFactory<double>::create_scaler(_data->highGpData.inputScalerData) };
        auto highPredictionScaler{ ScalerFactory<double>::create_scaler(_data->highGpData.predictionScalerData) };
        GaussianProcess<double> lowGpDouble{ std::make_shared<const GPData>(_data->lowGpData) };
        
        std::vector<std::vector<double>> XHighDescaled(_data->highGpData.nX, std::vector<double>(_data->highGpData.DX));
        for (std::size_t i{ 0 }; i < _data->highGpData.nX; ++i)
        {
            XHighDescaled[i] = inputScaler->descale({ _data->highGpData.X[i] });
        }
        
        std::vector<double> lowPredictionsForHighInputsWithRho(_data->highGpData.nX);
        std::vector<double> yHighDescaled(_data->highGpData.nX);
        for (std::size_t i{ 0 }; i < _data->highGpData.nX; ++i)
        {
            lowPredictionsForHighInputsWithRho[i] = _data->rho * lowGpDouble.calculate_prediction_reduced_space(XHighDescaled[i]);
            yHighDescaled[i] = highPredictionScaler->descale({ _data->highGpData.Y[i] }).front();
        }
        std::vector<double> yAuxDescaled{ yHighDescaled - lowPredictionsForHighInputsWithRho };

        double yAuxMean{ 0.0 };
        for (std::size_t i{ 0 }; i < _data->highGpData.nX; ++i)
        {
            yAuxMean = yAuxMean + yAuxDescaled[i];
        }
        yAuxMean = yAuxMean / _data->highGpData.nX;

        double yAuxStd{ 0.0 };
        for (std::size_t i{ 0 }; i < _data->highGpData.nX; ++i)
        {
            yAuxStd = yAuxStd + pow(yAuxDescaled[i] - yAuxMean, 2);
        }
        yAuxStd = sqrt(yAuxStd / _data->highGpData.nX);

        StandardScaler<double> auxPredictionScaler{ {yAuxMean}, {yAuxStd} };
        std::vector<double> yAuxScaled(_data->highGpData.nX);
        for (std::size_t i{ 0 }; i < _data->highGpData.nX; ++i)
        {
            yAuxScaled[i] = auxPredictionScaler.scale({ yAuxDescaled[i] }).front();
        }

        GPData auxData{ _data->highGpData };
        auxData.Y = yAuxScaled;
        auxData.predictionScalerData->parameters.at(SCALER_PARAMETER::MEAN) = { yAuxMean };
        auxData.predictionScalerData->parameters.at(SCALER_PARAMETER::STD_DEV) = { yAuxStd };
        auxData.stdOfOutput = yAuxStd;
        auxData.meanfunction = auxPredictionScaler.scale(highPredictionScaler->descale({ _data->highGpData.meanfunction })).front();
        const double factor{ pow(_data->highGpData.stdOfOutput, 2) / pow(yAuxStd, 2) };
        auxData.kernelData->sf2 = factor * _data->highGpData.kernelData->sf2;
        for (std::size_t i{ 0 }; i < auxData.K.size(); ++i)
        {
            auxData.K[i] = factor * _data->highGpData.K[i];
            auxData.invK[i] = _data->highGpData.invK[i] / factor;
        }

        _auxGp->MelonModel<T>::load_model(std::make_shared<const GPData>(auxData));
    }

    template<typename T>
    T MulfilGp<T>::calculate_low_prediction_reduced_space(std::vector<T>& input) const {
        
        return _lowGp->calculate_prediction_reduced_space(input);
    }
    
    template<typename T>
    T MulfilGp<T>::calculate_low_variance_reduced_space(std::vector<T>& input) const {
    
        return _lowGp->calculate_variance_reduced_space(input);
    }

    template<typename T>
    T MulfilGp<T>::calculate_high_prediction_reduced_space(std::vector<T>& input) const {

        T auxPrediction{ _auxGp->calculate_prediction_reduced_space(input) };
        T lowPrediction{ _lowGp->calculate_prediction_reduced_space(input) };
        return auxPrediction + _data->rho * lowPrediction;
    }

    template<typename T>
    T MulfilGp<T>::calculate_high_variance_reduced_space(std::vector<T>& input) const {

        T auxVariance{ _auxGp->calculate_variance_reduced_space(input) };
        T lowVariance{ _lowGp->calculate_variance_reduced_space(input) };
        return auxVariance + _data->rho * _data->rho * lowVariance;
    }
}