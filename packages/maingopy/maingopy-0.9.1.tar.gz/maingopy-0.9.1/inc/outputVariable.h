/**********************************************************************************
 * Copyright (c) 2019-2024 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#pragma once

#include "ffunc.hpp"

#include <string>


namespace maingo {


/**
	* @struct OutputVariable
	* @brief Struct for storing output variables
	*
	* Can be used to tag intermediate calculation results (i.e., FFVars) along with a descriptive string.
	*/
struct OutputVariable {

  public:
    OutputVariable() = default;
    OutputVariable(const std::string descriptionIn, const mc::FFVar valueIn);
    OutputVariable(const mc::FFVar valueIn, const std::string descriptionIn);
    OutputVariable(const std::tuple<mc::FFVar, std::string> tupleIn);
    OutputVariable(const std::tuple<std::string, mc::FFVar> tupleIn);

    OutputVariable(const OutputVariable& valueIn) = default;
    OutputVariable(OutputVariable&& valueIn) = default;
    ~OutputVariable() = default;

    OutputVariable& operator=(const OutputVariable& valueIn) = default;
    OutputVariable& operator=(OutputVariable&& valueIn) = default;

    inline bool operator==(const OutputVariable& other) const
    {
        return ((description == other.description) && (value == other.value));
    }

    mc::FFVar value         = {}; /*!< Variable object, allows access to value once evaluated*/
    std::string description = {}; /*!< Description, e.g. name of variable */
};


}    // end namespace maingo