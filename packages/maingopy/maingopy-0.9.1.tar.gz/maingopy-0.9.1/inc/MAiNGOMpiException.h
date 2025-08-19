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

#ifdef HAVE_MAiNGO_MPI
#pragma once

#include "MAiNGOException.h"
#include "babNode.h"


namespace maingo {


/**
* @class MAiNGOMpiException
* @brief This class defines the exceptions thrown by MAiNGO when using MPI
*
* In addition to the MAiNGOException class, it contains an enum to distinguish which process the exception came from.
* At the point where an exception becomes relevant to the MPI communication scheme (i.e., a process needs to inform 
* another process that something went wrong - or a process receives a message from another process stating that something
* went wrong - these MAiNGOMpiExceptions are used. Such an exception can be newly created or converted from a MAiNGOException.
*/
class MAiNGOMpiException: public MAiNGOException {

  public:
    MAiNGOMpiException()                                     = delete;
    MAiNGOMpiException(const MAiNGOMpiException&)            = default;
    MAiNGOMpiException(MAiNGOMpiException&&)                 = default;
    MAiNGOMpiException& operator=(const MAiNGOMpiException&) = default;
    MAiNGOMpiException& operator=(MAiNGOMpiException&&)      = default;
    ~MAiNGOMpiException()                                    = default;

    enum ORIGIN {
        ORIGIN_ME = 1, /*!< An exception (not necessarily this one) was originally thrown by the current process */
        ORIGIN_OTHER   /*!< An exception was thrown by another process and the present exception was thrown in responce to a corresponding MPI message */
    };

    MAiNGOMpiException(const std::string& errorMessage, const ORIGIN origin):
        MAiNGOException(errorMessage), _origin(origin)
    {
    }

    MAiNGOMpiException(const std::string& errorMessage, const babBase::BabNode& nodeThatProblemOccurredIn, const ORIGIN origin):
        MAiNGOException(errorMessage, nodeThatProblemOccurredIn), _origin(origin)
    {
    }

    MAiNGOMpiException(const std::string& errorMessage, const std::exception& originalException, const ORIGIN origin):
        MAiNGOException(errorMessage, originalException), _origin(origin)
    {
    }

    MAiNGOMpiException(const std::string& errorMessage, const std::exception& originalException, const babBase::BabNode& nodeThatProblemOccurredIn, const ORIGIN origin):
        MAiNGOException(errorMessage, originalException, nodeThatProblemOccurredIn), _origin(origin)
    {
    }

    MAiNGOMpiException(MAiNGOException& originalException, ORIGIN origin):
        MAiNGOException(originalException), _origin(origin)
    {
    }

    ORIGIN origin() const noexcept { return _origin; }

  private:
    ORIGIN _origin;
};


}    // end namespace maingo
#endif