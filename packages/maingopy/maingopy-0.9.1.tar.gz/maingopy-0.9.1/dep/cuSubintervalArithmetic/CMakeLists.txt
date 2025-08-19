cmake_minimum_required(VERSION 3.22.1)

project(
    cuSubintervalArithmetic
    VERSION 0.0.1
    DESCRIPTION "Use CUDA graph to evaluate interval arithmetics"
    LANGUAGES CXX CUDA
)


if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
    add_subdirectory(dep/babbase)
    add_subdirectory(dep/blas)
    add_subdirectory(dep/mcpp)
    add_subdirectory(dep/cuinterval)
    add_subdirectory(dep/cutangent)
    add_subdirectory(dep/cpplapack)
    add_subdirectory(dep/lapack)
    add_subdirectory(dep/fadbad)
    add_subdirectory(dep/filib)
endif()

add_library(cuSubintervalArithmetic
    src/dagConversion.cpp
    src/subinterval_arithmetic_settings.cu
)

set_target_properties(cuSubintervalArithmetic
    PROPERTIES 
        CUDA_SEPARABLE_COMPILATION ON
)

target_include_directories(cuSubintervalArithmetic
    PUBLIC ${PROJECT_SOURCE_DIR}/inc
)

target_link_libraries(cuSubintervalArithmetic 
    PUBLIC
        cuinterval
        cutangent
    PRIVATE
        babbase
        mcpp
        filib
)

if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_options(cuSubintervalArithmetic PUBLIC $<$<COMPILE_LANGUAGE:CUDA>: -g -G>)
endif()