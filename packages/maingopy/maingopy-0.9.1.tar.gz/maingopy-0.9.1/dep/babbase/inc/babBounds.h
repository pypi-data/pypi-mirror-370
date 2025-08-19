/**********************************************************************************
 * Copyright (c) 2019 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#pragma once

#include <iostream>


/**
*   @namespace babBase
*   @brief namespace holding all essentials of the babBase submodule
*/
namespace babBase {


/**
    * @struct Bounds
    * @brief Auxiliary struct for representing bounds on an optimization variable.
    */
struct Bounds {

  public:
    /**
        * @brief Constructor
        *
        * @param[in] lowerIn is the specified lower bound on the optimization variable
        * @param[in] upperIn is the specified upper bound on the optimization variable
        */
    Bounds(const double lowerIn, const double upperIn):
        lower(lowerIn), upper(upperIn) {}

    /**
        * @brief Function for querying whether the lower bound is less than or equal to the upper bound
        */
    bool are_consistent() const
    {
        return (lower <= upper);
    }

    double lower; /*!< Lower bound on the optimization variable */
    double upper; /*!< Upper bound on the optimization variable */
};


/**
    * @brief Overloaded outstream operator for nicer output
    *
    * @param[out] os is the outstream to be written to
    * @param[in] b are the bounds to be written
    */
inline std::ostream &
operator<<(std::ostream &os, const Bounds &b)
{
    os << "Lower:" << b.lower << " , Upper:" << b.upper;
    return os;
};


/**
    * @brief Equality operator for checking if two bound objects are equal
    *
    * @param[in] b1 is the first bound object
    * @param[in] b2 is the second bound object
    */
inline bool
operator==(const Bounds &b1, const Bounds &b2)
{
    return ((b1.lower == b2.lower) && (b1.upper == b2.upper));
};


/**
    * @brief Inequality operator for checking if two bound objects differ from each other
    *
    * @param[in] b1 is the first bound object
    * @param[in] b2 is the second bound object
    */
inline bool
operator!=(const Bounds &b1, const Bounds &b2)
{
    return ((b1.lower != b2.lower) || (b1.upper != b2.upper));
};


}    // namespace babBase
