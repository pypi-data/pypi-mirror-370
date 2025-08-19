/***********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file gpData.h
*
* @brief File containing declaration of a struct for storing Gaussian process data
*
**********************************************************************************/

#pragma once

#include <vector>		// std::vector

#include "matern.h"
#include "modelData.h"
#include "scaler.h"

namespace melon {

    /**
    * @struct GPData
    *
    * @brief struct containing all information regarding the Gaussian process
    */
    struct GPData : public ModelData {
        std::shared_ptr<kernel::KernelData> kernelData;     /*!< Data/Parameter for kernel used in Gaussian process */
                                                            
        int nX;                                             /*!< Number of training points */                                                        
        int DX;                                             /*!< Dimension of input */
        int DY;                                             /*!< Dimension of output */
        int matern;                                         /*!< Identifier of matern kernel that is used in Gaussian process */

		std::shared_ptr<ScalerData> inputScalerData;		/*!< Object containing the data for the input scaling*/
		std::shared_ptr<ScalerData> predictionScalerData;	/*!< Object containing the data for the output scaling*/
		
		//std::vector<double> inputLowerBound;                /*!< Vector containing lower bound for each input dimension */
        //std::vector<double> inputUpperBound;                /*!< Vector containing upper bound for each input dimension */
        //std::vector<double> problemLowerBound;              /*!< Vector containing lower bound for each output dimension */
        //std::vector<double> problemUpperBound;              /*!< Vector containing upper bound for each output dimesnion */

        std::vector<std::vector<double>> X;                 /*!< Vector containg training input points */
        std::vector<double> Y;                              /*!< Vector containg training observations */
        std::vector<std::vector<double>> K;                 /*!< Covariance matrix for training data */
        std::vector<std::vector<double>> invK;              /*!< Inverse of K */
                

        double stdOfOutput;									/*!< Mean of training ouput, required for sclaing variance*/
        // TODO: remove (?)
        double meanfunction;
        //double meanOfOutput;								
    };
}