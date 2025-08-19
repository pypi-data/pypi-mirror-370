/**********************************************************************************
 * Copyright (c) 2021-2024 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#include "MAiNGOException.h"

#include <typeinfo>


using namespace maingo;



//////////////////////////////////////////////////////////////////////////
MAiNGOException::MAiNGOException(const std::string& errorMessage)
{
    _construct_complete_error_message(errorMessage, nullptr, nullptr);
}

//////////////////////////////////////////////////////////////////////////
MAiNGOException::MAiNGOException(const std::string& errorMessage, const babBase::BabNode& nodeThatErrorOccurredIn)
{
    _construct_complete_error_message(errorMessage, nullptr, &nodeThatErrorOccurredIn);
}

//////////////////////////////////////////////////////////////////////////
MAiNGOException::MAiNGOException(const std::string& errorMessage, const std::exception& originalException)
{
    _construct_complete_error_message(errorMessage, &originalException, nullptr);
}

//////////////////////////////////////////////////////////////////////////
MAiNGOException::MAiNGOException(const std::string& errorMessage, const std::exception& originalException, const babBase::BabNode& nodeThatErrorOccurredIn)
{
    _construct_complete_error_message(errorMessage, &originalException, &nodeThatErrorOccurredIn);
}

//////////////////////////////////////////////////////////////////////////
const char*
MAiNGOException::what() const noexcept
{
    return _errorMessage.c_str();
}


//////////////////////////////////////////////////////////////////////////
void
MAiNGOException::_construct_complete_error_message(const std::string& errorMessage, const std::exception* originalException, const babBase::BabNode* nodeThatErrorOccurredIn)
{
    std::ostringstream errorMessageStream;

    _append_original_exception_info_to_message(originalException, errorMessageStream);
    _append_current_error_message_to_message(errorMessage, errorMessageStream);
    _append_node_info_to_message(nodeThatErrorOccurredIn, errorMessageStream);

    _errorMessage = errorMessageStream.str();
}


//////////////////////////////////////////////////////////////////////////
void
MAiNGOException::_append_current_error_message_to_message(const std::string& currentErrorMessage, std::ostringstream& completeErrorMessage)
{
    completeErrorMessage << currentErrorMessage;
}


//////////////////////////////////////////////////////////////////////////
void
MAiNGOException::_append_original_exception_info_to_message(const std::exception* originalException, std::ostringstream& completeErrorMessage)
{
    if (originalException) {
        if (typeid(*originalException).name() != typeid(*this).name()) {
            completeErrorMessage << "  Original exception type: " << typeid(*originalException).name() << ": " << std::endl
                                 << "   ";
        }
        completeErrorMessage << originalException->what() << std::endl;
    }
}


//////////////////////////////////////////////////////////////////////////
void
MAiNGOException::_append_node_info_to_message(const babBase::BabNode* nodeThatErrorOccurredIn, std::ostringstream& completeErrorMessage)
{
    if (nodeThatErrorOccurredIn) {
        std::vector<double> lowerVarBounds(nodeThatErrorOccurredIn->get_lower_bounds()), upperVarBounds(nodeThatErrorOccurredIn->get_upper_bounds());
        completeErrorMessage << std::endl
                             << "  Exception was thrown while processing node no. " << nodeThatErrorOccurredIn->get_ID() << ":";
        for (size_t i = 0; i < lowerVarBounds.size(); i++) {
            completeErrorMessage << std::endl
                                 << "    x(" << i << "): " << std::setprecision(16) << lowerVarBounds[i] << ":" << upperVarBounds[i];
        }
    }
}