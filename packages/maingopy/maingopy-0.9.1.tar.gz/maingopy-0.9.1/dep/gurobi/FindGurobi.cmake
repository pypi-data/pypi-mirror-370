# This module finds Gurobi.

if(WIN32)

    if(NOT MSVC)

        message("On Windows, Gurobi is currently only supported for Visual Studio.")

    else()

        # Get Visual Studio version
        string(REGEX REPLACE "/VC/bin/.*" "" VISUAL_STUDIO_PATH ${CMAKE_CXX_COMPILER})
        string(REGEX MATCH "Studio/[0-9]+/" GUROBI_WIN_VS_VERSION_TEMP ${VISUAL_STUDIO_PATH})
        string(REGEX REPLACE "Studio/" "" GUROBI_WIN_VS_VERSION_TEMP ${GUROBI_WIN_VS_VERSION_TEMP})
        string(REGEX REPLACE "/" "" GUROBI_WIN_VS_VERSION_TEMP ${GUROBI_WIN_VS_VERSION_TEMP})

        set(GUROBI_WIN_VS_VERSION ${GUROBI_WIN_VS_VERSION_TEMP} CACHE STRING "Visual Studio Version" FORCE)
        mark_as_advanced(GUROBI_WIN_VS_VERSION)
        message(STATUS "Visual Studio version: ${GUROBI_WIN_VS_VERSION}.")

        if(NOT((${GUROBI_WIN_VS_VERSION} STREQUAL "2022") OR (${GUROBI_WIN_VS_VERSION} STREQUAL "2019") OR (${GUROBI_WIN_VS_VERSION} STREQUAL "2017") OR (${GUROBI_WIN_VS_VERSION} STREQUAL "2015")))
            message(FATAL_ERROR "Gurobi: Visual Studio version at '${VISUAL_STUDIO_PATH}' is not equal to 2015, 2017, 2019, or 2022.")
        endif()
		
        # Attempt to locate Gurobi root directory from the environment variable GUROBI_HOME
        if(NOT(GUROBI_ROOT_DIR))
            set(GUROBI_ROOT_DIR_TEMP "$ENV{GUROBI_HOME}")
            if(GUROBI_ROOT_DIR_TEMP)
			    set(GUROBI_ROOT_DIR "${GUROBI_ROOT_DIR_TEMP}" CACHE PATH "Gurobi root directory.")
            else()
                message(STATUS "The environment variable 'GUROBI_HOME' is not set. You have to set it.")
            endif()
        endif()

        set(GUROBI_ROOT_DIR "" CACHE PATH "GUROBI root directory.")
        message(STATUS "Gurobi root directory: ${GUROBI_ROOT_DIR}.")

        # Set binary directory
        set(GUROBI_BIN_DIR "${GUROBI_ROOT_DIR}/bin" CACHE PATH "" FORCE)
        mark_as_advanced(GUROBI_BIN_DIR)

        # Get Gurobi version in the format "<main version><sub version>"
        # Iterate over the files in the root directory until a file matches "gurobi[1-9]?[0-9][0-9].dll"
		file(GLOB GUROBI_BIN_FILES "${GUROBI_BIN_DIR}/*")
		foreach(FILE ${GUROBI_BIN_FILES})
            get_filename_component(FILE ${FILE} NAME)
			if(FILE MATCHES "gurobi[1-9]*[0-9][0-9].dll")
                string(REGEX MATCH "[1-9]*[0-9][0-9]" GUROBI_VERSION_TEMP ${FILE})
                set(GUROBI_VERSION "${GUROBI_VERSION_TEMP}" CACHE STRING "Gurobi version (e.g., 81, 92, 103 or 110)" FORCE)
                break()
			endif()
		endforeach()

        set(GUROBI_VERSION "" CACHE STRING "Gurobi version (e.g., 81, 92, 103 or 110)")
        mark_as_advanced(GUROBI_VERSION)
        message(STATUS "Gurobi version: ${GUROBI_VERSION}.")

        # Set library names
        set(GUROBI_WIN_CXX_LIB_NAME "gurobi_c++md2019" "gurobi_c++md2017" "gurobi_c++md2015" CACHE STRING "Gurobi file name of C++ library")
        set(GUROBI_WIN_CXX_LIB_NAME_DEBUG "gurobi_c++mdd2019" "gurobi_c++mdd2017" "gurobi_c++mdd2015" CACHE STRING "Gurobi file name of C++ library (debug)")
        set(GUROBI_WIN_C_LIB_NAME "gurobi${GUROBI_VERSION}" CACHE STRING "Gurobi file name of C library")

        # Set inlcude directory
        set(GUROBI_INCLUDE_DIR "${GUROBI_ROOT_DIR}/include" CACHE PATH "")
        mark_as_advanced(GUROBI_INCLUDE_DIR)

        # Find static C++ & C libraries
        find_library(GUROBI_CXX_LIBRARY
            NAMES ${GUROBI_WIN_CXX_LIB_NAME}
            HINTS ${GUROBI_ROOT_DIR}/lib
            NO_DEFAULT_PATH
            )
        message(STATUS "Gurobi C++ library: ${GUROBI_CXX_LIBRARY}.")
 
        find_library(GUROBI_CXX_LIBRARY_D
            NAMES ${GUROBI_WIN_CXX_LIB_NAME_DEBUG}
            HINTS ${GUROBI_ROOT_DIR}/lib
            NO_DEFAULT_PATH
            )
        message(STATUS "Gurobi C++ library (Debug): ${GUROBI_CXX_LIBRARY_D}.")

        find_library(GUROBI_C_LIBRARY
            NAMES ${GUROBI_WIN_C_LIB_NAME} 
            HINTS ${GUROBI_ROOT_DIR}/lib
            NO_DEFAULT_PATH
            )
        message(STATUS "Gurobi C library: ${GUROBI_C_LIBRARY}.")

        include(FindPackageHandleStandardArgs)
        FIND_PACKAGE_HANDLE_STANDARD_ARGS(Gurobi DEFAULT_MSG
            GUROBI_CXX_LIBRARY GUROBI_CXX_LIBRARY_D GUROBI_C_LIBRARY GUROBI_INCLUDE_DIR GUROBI_BIN_DIR)
        mark_as_advanced(GUROBI_CXX_LIBRARY GUROBI_CXX_LIBRARY_D GUROBI_C_LIBRARY)

    endif()

else()

    set(GUROBI_ROOT_DIR "/opt/gurobi/linux64" CACHE PATH "GUROBI root directory.")
    set(GUROBI_ROOT_DIR2 "/usr/local/gurobi/linux64")
    set(GUROBI_ROOT_DIR3 "~/gurobi/linux64")
    set(GUROBI_ROOT_DIR4 "//Library/gurobi/mac64")
    file(GLOB GUROBI_ROOT_DIR5 "/opt/gurobi[1-9]?[0-9][0-9]*/linux64")
    file(GLOB GUROBI_ROOT_DIR6 "/usr/local/gurobi[1-9]?[0-9][0-9]*]/linux64")
    file(GLOB GUROBI_ROOT_DIR7 "~/gurobi[1-9]?[0-9][0-9]*/linux64")
    file(GLOB GUROBI_ROOT_DIR8 "//Library/gurobi[1-9]?[0-9][0-9]*/mac64")

    # Reverse order of lists to ensure later versions are found first
    list(REVERSE GUROBI_ROOT_DIR5)
    list(REVERSE GUROBI_ROOT_DIR6)
    list(REVERSE GUROBI_ROOT_DIR7)
    list(REVERSE GUROBI_ROOT_DIR8)

    set(GUROBI_ROOT_DIR_GUESSES
        ${GUROBI_ROOT_DIR}
        ${GUROBI_ROOT_DIR2}
        ${GUROBI_ROOT_DIR3}
        ${GUROBI_ROOT_DIR4}
        ${GUROBI_ROOT_DIR5}
        ${GUROBI_ROOT_DIR6}
        ${GUROBI_ROOT_DIR7}
        ${GUROBI_ROOT_DIR8}
        ${GUROBI_HOME}
        $ENV{GUROBI_HOME}
        )

    # Find inlcude directory
    find_path(GUROBI_INCLUDE_DIR
        gurobi_c++.h
        HINTS ${GUROBI_ROOT_DIR_GUESSES}
        NO_DEFAULT_PATH
        PATH_SUFFIXES include
        )

    # Find C++ library
    # First, select allowable g++ versions.
    # For now supporting all g++ versions (as of 09/2021) with full C++11 support
    # Gurobi also ships / used to be shipped with older versions not compatible with C++11
    set(GUROBI_ALLOWABLE_CXX_VERSIONS
        gurobi_g++11.3 gurobi_g++11.2 gurobi_g++11.1
        gurobi_g++10.3 gurobi_g++10.2 gurobi_g++10.1
        gurobi_g++9.3 gurobi_g++9.2 gurobi_g++9.1
        gurobi_g++8.5 gurobi_g++8.4 gurobi_g++8.3 gurobi_g++8.2 gurobi_g++8.1
        gurobi_g++7.5 gurobi_g++7.4 gurobi_g++7.3 gurobi_g++7.2 gurobi_g++7.1
        gurobi_g++6.5 gurobi_g++6.4 gurobi_g++6.3 gurobi_g++6.2 gurobi_g++6.1
        gurobi_g++5.5 gurobi_g++5.4 gurobi_g++5.3 gurobi_g++5.2 gurobi_g++5.1
        gurobi_g++4.9 gurobi_g++4.8
        )
    if (CMAKE_SYSTEM_NAME STREQUAL "Darwin")
        # On MacOS (=Darwin), only the version compiled with g++4.2 appears to be shipped.
        # For some reason, this seems to work (unlike on Linux, where a more recent version with C++ 11 support is required...)
        set(GUROBI_ALLOWABLE_CXX_VERSIONS ${GUROBI_ALLOWABLE_CXX_VERSIONS} gurobi_g++4.2)
    endif()
    find_library(GUROBI_CXX_LIBRARY
        NAMES ${GUROBI_ALLOWABLE_CXX_VERSIONS}
        HINTS ${GUROBI_ROOT_DIR_GUESSES}
        NO_DEFAULT_PATH
        PATH_SUFFIXES lib
        )
    message(STATUS "Gurobi C++ library: ${GUROBI_CXX_LIBRARY}")

    # Find C library
    find_library(GUROBI_C_LIBRARY
        NAMES gurobi120  gurobi110 gurobi100 gurobi95 gurobi92 gurobi91 gurobi90 gurobi81 gurobi80
        HINTS ${GUROBI_ROOT_DIR_GUESSES}
        NO_DEFAULT_PATH
        PATH_SUFFIXES lib
        )
    message(STATUS "Gurobi C library: ${GUROBI_C_LIBRARY}")

    include(FindPackageHandleStandardArgs)
    FIND_PACKAGE_HANDLE_STANDARD_ARGS(Gurobi DEFAULT_MSG
        GUROBI_CXX_LIBRARY GUROBI_C_LIBRARY GUROBI_INCLUDE_DIR)
    mark_as_advanced(GUROBI_CXX_LIBRARY GUROBI_C_LIBRARY GUROBI_INCLUDE_DIR)

endif()
