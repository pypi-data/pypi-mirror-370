cmake_minimum_required(VERSION 3.22.1 FATAL_ERROR)
project(subintervalArithmetic LANGUAGES CXX)

if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
	add_subdirectory(dep/dag)
    add_subdirectory(dep/babbase)
    add_subdirectory(dep/blas)
    add_subdirectory(dep/cpplapack)
    add_subdirectory(dep/fadbad)
    add_subdirectory(dep/filib)
    add_subdirectory(dep/lapack)
    add_subdirectory(dep/mcpp)
endif()

if(HAVE_CUDA_TOOLKIT)	
	add_library(subintervalArithmetic 
		src/subinterval_arithmetic_settings.cu 
	)
	set_target_properties(subintervalArithmetic 
	PROPERTIES 
		CUDA_SEPARABLE_COMPILATION ON
	)
	if(CMAKE_BUILD_TYPE STREQUAL "Debug")
		target_compile_options(subintervalArithmetic PRIVATE $<$<COMPILE_LANGUAGE:CUDA>: -g -G>)
	endif()
else()
	add_library(subintervalArithmetic 
	src/subinterval_arithmetic_settings.cpp 
	)
	if(CMAKE_BUILD_TYPE STREQUAL "Debug")
		target_compile_options(subintervalArithmetic PRIVATE $<$<COMPILE_LANGUAGE:CUDA>: -g>)
	endif()
endif()

target_include_directories(subintervalArithmetic PUBLIC ${PROJECT_SOURCE_DIR}/inc)
target_link_libraries(subintervalArithmetic PUBLIC dag)