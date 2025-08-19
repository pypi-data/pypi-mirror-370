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

#if defined(_WIN32)

#define NOMINMAX    // The header windows.h has macros for min and max which interfer with our overloads of min and max
#include <windows.h>

#elif defined(__linux__) || (defined(__APPLE__) && defined(__MACH__))

#include <cstddef>
#include <sys/resource.h>
#include <sys/time.h>

#else

#error "No routines for measuring CPU and wall-clock time are available for your system."

#endif

#include "getTime.h"
#include "MAiNGOException.h"


using namespace maingo;


/////////////////////////////////////////////////////////////////////////////////////////////
// function for querying CPU time of the process
double
maingo::get_cpu_time()
{

#if defined(_WIN32)
    {
        FILETIME creation;
        FILETIME exit;
        FILETIME kernel;
        FILETIME user;
        if (GetProcessTimes(GetCurrentProcess(), &creation, &exit, &kernel, &user) != -1) {
            SYSTEMTIME theTime;
            if (FileTimeToSystemTime(&user, &theTime) != -1) {
                return (double)theTime.wDay * 86400 + (double)theTime.wHour * 3600. + (double)theTime.wMinute * 60. + (double)theTime.wSecond + (double)theTime.wMilliseconds / 1000.;
            }
        }
    }

#elif defined(__linux__) || (defined(__APPLE__) && defined(__MACH__))
    {
        struct rusage rusage;
        if (getrusage(RUSAGE_SELF, &rusage) != -1) {
            return (double)rusage.ru_utime.tv_sec + (double)rusage.ru_utime.tv_usec / 1000000.;
        }
    }

#endif

    throw MAiNGOException("Error querying CPU time."); // GCOVR_EXCL_LINE

}


/////////////////////////////////////////////////////////////////////////////////////////////
// function for querying wall clock time of the process
double
maingo::get_wall_time()
{

#if defined(_WIN32)
    {
        FILETIME creation;
        GetSystemTimeAsFileTime(&creation);
        ULONGLONG t = ((ULONGLONG)creation.dwHighDateTime << 32) | (ULONGLONG)creation.dwLowDateTime;
        return (double)t / 10000000.;
    }


#elif defined(__linux__) || (defined(__APPLE__) && defined(__MACH__))
    {
        struct timeval timeVal;
        gettimeofday(&timeVal, NULL);
        return (double)(timeVal.tv_sec + timeVal.tv_usec / 1000000.);
    }

#endif

    throw MAiNGOException("Error querying wall-clock time."); // GCOVR_EXCL_LINE

}