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

#include "babNode.h"

#include <exception>
#include <sstream>
#include <typeinfo>


namespace babBase {


/**
* @class BranchAndBoundBaseException
* @brief This class defines the exceptions thrown by BranchAndBoundBase
*
* The class contains different constructors. The first parameter is always the error message.
* For debugging, the error message will also contain the file name and line number
* Additionally, the constructor can take an exception as second argument.
* If done so, the type of the exception object and its what() will be saved in the error message as well.
*
*/
class BranchAndBoundBaseException: public std::exception {

  protected:
    std::string _msg{""}; /*!< string holding the exception message */
    BranchAndBoundBaseException();

  public:
    /**
        * @brief Constructor used for forwarding
        *
        * @param[in] arg is a string holding an error message
        */
    explicit BranchAndBoundBaseException(const std::string& arg):
        BranchAndBoundBaseException(arg, nullptr, nullptr)
    {
    }

    /**
        * @brief Constructor used for forwarding
        *
        * @param[in] arg is a string holding an error message
        * @param[in] node holds the current BabNode
        */
    BranchAndBoundBaseException(const std::string& arg, const babBase::BabNode& node):
        BranchAndBoundBaseException(arg, nullptr, &node)
    {
    }

    /**
        * @brief Constructor used for forwarding
        *
        * @param[in] arg is a string holding an error message
        * @param[in] e holds the exception
        */
    BranchAndBoundBaseException(const std::string& arg, const std::exception& e):
        BranchAndBoundBaseException(arg, &e, nullptr)
    {
    }

    /**
        * @brief Constructor used for forwarding
        *
        * @param[in] arg is a string holding an error message
        * @param[in] e holds the exception
        * @param[in] node holds the current BabNode
        */
    BranchAndBoundBaseException(const std::string& arg, const std::exception& e, const babBase::BabNode& node):
        BranchAndBoundBaseException(arg, &e, &node)
    {
    }

    /**
        * @brief Constructor used printing a BranchAndBoundBase Exception
        *
        * @param[in] arg is a string holding an error message
        * @param[in] e holds the exception
        * @param[in] node holds the current BabNode
        */
    BranchAndBoundBaseException(const std::string& arg, const std::exception* e, const babBase::BabNode* node)
    {
        std::ostringstream message;
        message << arg;
        if (e) {
            if (typeid(*e).name() != typeid(*this).name()) {
                message << "Original std::exception: " << typeid(*e).name() << ": " << std::endl
                        << "   ";
            }
            message << e->what();
        }
        if (node) {
            std::vector<double> lowerVarBounds(node->get_lower_bounds()), upperVarBounds(node->get_upper_bounds());
            message << std::endl
                    << "Exception was thrown while processing node no. " << node->get_ID() << ":" << std::endl;
            for (unsigned int i = 0; i < lowerVarBounds.size(); i++) {
                message << "   x(" << i << "): " << std::setprecision(16) << lowerVarBounds[i] << ":" << upperVarBounds[i] << std::endl;
            }
        }
        _msg = message.str();
    }


    /**
         * @brief Function to return the error message
         *
         * @return Error message.
         */
    const char* what() const noexcept
    {
        return _msg.c_str();
    }
};


}    // namespace babBase