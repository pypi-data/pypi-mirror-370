/***********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file mulfilGpData.h
*
* @brief File that contains the declaration of a struct for storing multifidelity Gaussian process data
*
**********************************************************************************/

#pragma once

#include "modelData.h"
#include "gpData.h"


namespace melon {

    /**
    * @struct MulFilGpData
    *
    * @brief Struct that contains all information for creating a multifidelity Gaussian process
    */
    struct MulfilGpData : public ModelData {

        GPData lowGpData; /*!< Data for low fidelity GP (_lowGp) */
        GPData highGpData; /*!< Data for a high fidelity GP. Together with the low fidelity GP it is used to create the member variable _auxGp */
        double rho; /*!< Scale factor between low and high fidelity model */

        /**
        * @brief Constructor
        */
        MulfilGpData(const GPData& lowGPData, const GPData& highGPData, double rho) :
            lowGpData{ lowGPData },
            highGpData{ highGPData },
            rho{ rho }
        {}
    };
}