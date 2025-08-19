cmake_minimum_required(VERSION 3.15)

message("Checking files for BLAS.")
project(blas C)


if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
    option(BUILD_SHARED_LIBS "Build shared libraries" OFF)
endif()


# For Visual Studio, we use the pre-compiled version by default.
if(MSVC)

	option(BLAS_usePrecompiledDll "Use precompiled BLAS library" TRUE)

	# Set paths
	set(BLAS_PRECOMPILED_INC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/precompiled/inc)
	if(NOT "${CMAKE_SIZEOF_VOID_P}" STREQUAL "8")
		set(BLAS_PRECOMPILED_DIR ${CMAKE_CURRENT_SOURCE_DIR}/precompiled/win32)
	else()
		set(BLAS_PRECOMPILED_DIR ${CMAKE_CURRENT_SOURCE_DIR}/precompiled/win64)
	endif()

else()

	set(BLAS_usePrecompiledDll FALSE CACHE INTERNAL "Use precompiled BLAS library" FORCE)

endif()


if(BLAS_usePrecompiledDll)

	message("Using pre-compiled BLAS library.")

	# Find BLAS libs
	find_library(BLAS_LIB
		NAMES blas
		HINTS ${BLAS_PRECOMPILED_DIR}/lib
		NO_DEFAULT_PATH
        )
	message(STATUS "BLAS Library: ${BLAS_LIB}")
	find_library(BLAS_LIBD
		NAMES blasd
		HINTS ${BLAS_PRECOMPILED_DIR}/lib
		NO_DEFAULT_PATH
        )
	message(STATUS "BLAS Library (Debug): ${BLAS_LIBD}")

	# Prepare for copying dll
	set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
	set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Debug)
	set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Release)
	add_custom_target(copyBlasDll ALL COMMAND ${CMAKE_COMMAND} -E copy ${BLAS_PRECOMPILED_DIR}/bin/$<$<CONFIG:Debug>:blasd.dll>$<$<NOT:$<CONFIG:Debug>>:blas.dll>  $<$<CONFIG:Debug>:${CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG}/blasd.dll>$<$<NOT:$<CONFIG:Debug>>:${CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE}/blas.dll>)

	# Create blas target
	add_library(blas STATIC IMPORTED GLOBAL)
	set_target_properties(blas  PROPERTIES  INTERFACE_INCLUDE_DIRECTORIES ${BLAS_PRECOMPILED_INC_DIR})
	set_target_properties(blas  PROPERTIES  IMPORTED_LOCATION_RELEASE ${BLAS_LIB})
	set_target_properties(blas  PROPERTIES  IMPORTED_LOCATION_DEBUG ${BLAS_LIBD})
	add_dependencies(blas copyBlasDll)

else()

	enable_language(Fortran)

    # Fortran-C Interface
    include(FortranCInterface)
    FortranCInterface_HEADER(${CMAKE_CURRENT_BINARY_DIR}/blasNameMangling/blasNameMangling.h MACRO_NAMESPACE "FCBLAS_")
    add_library(blasNameMangling INTERFACE)
    target_include_directories(blasNameMangling INTERFACE ${CMAKE_CURRENT_BINARY_DIR}/blasNameMangling)

	# Blas library
	include(${CMAKE_CURRENT_SOURCE_DIR}/blasSourceFiles.cmake)
    add_library(blas ${BLAS_SOURCES})

    set_target_properties(blas PROPERTIES DEBUG_POSTFIX d)
    if(WIN32 AND BUILD_SHARED_LIBS)
		set_target_properties(blas PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
    endif()
    if(MSVC)
        if(BUILD_SHARED_LIBS)
            set_target_properties(blas PROPERTIES MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
        endif()
        target_compile_options(blas PRIVATE /MP)
    else()
        target_compile_options(blas
            PRIVATE
                $<$<Fortran_COMPILER_ID:Intel>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<Fortran_COMPILER_ID:GNU>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
            )
    endif()
    target_link_libraries(blas PUBLIC blasNameMangling)


endif()


if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)

	enable_language(CXX)

	# Test executable
	add_executable(blas-test
		${PROJECT_SOURCE_DIR}/test/test.cpp
	)
	target_link_libraries(blas-test blas)

endif()