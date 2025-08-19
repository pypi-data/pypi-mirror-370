cmake_minimum_required(VERSION 3.15 FATAL_ERROR)

message("Checking files for Gurobi.")
project(gurobi CXX)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${PROJECT_SOURCE_DIR}")

find_package(Gurobi)


if(${Gurobi_FOUND})

    add_library(gurobi INTERFACE)
    set_target_properties(gurobi  PROPERTIES  INTERFACE_INCLUDE_DIRECTORIES ${GUROBI_INCLUDE_DIR})
    set_target_properties(gurobi  PROPERTIES  INTERFACE_COMPILE_DEFINITIONS HAVE_GUROBI)

    add_library(gurobi-cxx STATIC IMPORTED)
    set_target_properties(gurobi-cxx  PROPERTIES  IMPORTED_LOCATION ${GUROBI_CXX_LIBRARY})

    if(WIN32)

        add_library(gurobi-cxx-d STATIC IMPORTED)
        set_target_properties(gurobi-cxx-d  PROPERTIES  IMPORTED_LOCATION ${GUROBI_CXX_LIBRARY_D})
        target_link_libraries(gurobi INTERFACE debug gurobi-cxx-d)
        target_link_libraries(gurobi INTERFACE optimized gurobi-cxx)

    else()

        target_link_libraries(gurobi INTERFACE gurobi-cxx)

    endif()

    add_library(gurobi-c IMPORTED STATIC)
    set_target_properties(gurobi-c  PROPERTIES  IMPORTED_LOCATION ${GUROBI_C_LIBRARY})
    add_library(gurobi-available INTERFACE)
    set_target_properties(gurobi-available  PROPERTIES  INTERFACE_COMPILE_DEFINITIONS HAVE_GUROBI)

    target_link_libraries(gurobi INTERFACE gurobi-c gurobi-available)

else()

    add_library(gurobi-available INTERFACE)
    add_library(gurobi INTERFACE)
    message("No supported version of Gurobi could be found. A dummy target will be used instead and the flag HAVE_GUROBI will not be defined.")
    message("This may be OK depending on the application (e.g., in MAiNGO), but you will not be able to actually use Gurobi.")

endif()


if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)

    if(${Gurobi_FOUND})

        add_executable(gurobi-test
            ${PROJECT_SOURCE_DIR}/test/test.cpp
            )

        target_link_libraries(gurobi-test
            gurobi
            gtest_main
            )

        option(BUILD_GMOCK "" OFF)
        option(INSTALL_GTEST "" OFF)
        option(gtest_force_shared_crt "" ON)
        add_subdirectory(dep/googletest)

    else()

        message(FATAL_ERROR "Gurobi could not be found. Cannot build Gurobi test.")

    endif()

endif()
