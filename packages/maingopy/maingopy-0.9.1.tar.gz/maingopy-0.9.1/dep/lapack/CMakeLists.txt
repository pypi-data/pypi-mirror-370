cmake_minimum_required(VERSION 3.15 FATAL_ERROR)

message("Checking files for LAPACK.")
project(lapack C)


if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
    option(BUILD_SHARED_LIBS "Build shared libraries" OFF)
    if (BUILD_SHARED_LIBS)
        set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR} CACHE PATH "Single output directory for all binaries.")
    endif()
endif()


# For Visual Studio, we use pre-compiled version by default.
if(MSVC)

    option(LAPACK_usePrecompiledDlls "Use precompiled LAPACK library" TRUE)

	# Set paths
	set(LAPACK_PRECOMPILED_INC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/precompiled/inc)
	if(NOT "${CMAKE_SIZEOF_VOID_P}" STREQUAL "8")
		set(LAPACK_PRECOMPILED_DIR ${CMAKE_CURRENT_SOURCE_DIR}/precompiled/win32)
	else()
		set(LAPACK_PRECOMPILED_DIR ${CMAKE_CURRENT_SOURCE_DIR}/precompiled/win64)
	endif()

else()

	set(LAPACK_usePrecompiledDlls FALSE CACHE INTERNAL "Use precompiled LAPACK library" FORCE)

endif()


if(LAPACK_usePrecompiledDlls)

	message("Using pre-compiled LAPACK library.")

	# Find LAPACK libs
	find_library(LAPACK_LIB
		NAMES lapack
		HINTS ${LAPACK_PRECOMPILED_DIR}/lib
		NO_DEFAULT_PATH
        )
	message(STATUS "LAPACK Library: ${LAPACK_LIB}")
	find_library(LAPACK_LIBD
		NAMES lapackd
		HINTS ${LAPACK_PRECOMPILED_DIR}/lib
		NO_DEFAULT_PATH
        )
	message(STATUS "LAPACK Library (Debug): ${LAPACK_LIBD}")

	# Prepare for copying dll
	set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
	set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Debug)
	set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Release)
	add_custom_target(copyLapackDll ALL COMMAND ${CMAKE_COMMAND} -E copy ${LAPACK_PRECOMPILED_DIR}/bin/$<$<CONFIG:Debug>:lapackd.dll>$<$<NOT:$<CONFIG:Debug>>:lapack.dll>  $<$<CONFIG:Debug>:${CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG}/lapackd.dll>$<$<NOT:$<CONFIG:Debug>>:${CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE}/lapack.dll>)

	# Create lapack target
	add_library(lapack STATIC IMPORTED GLOBAL)
	set_target_properties(lapack  PROPERTIES  INTERFACE_INCLUDE_DIRECTORIES ${LAPACK_PRECOMPILED_INC_DIR})
	set_target_properties(lapack  PROPERTIES  IMPORTED_LOCATION_RELEASE ${LAPACK_LIB})
	set_target_properties(lapack  PROPERTIES  IMPORTED_LOCATION_DEBUG ${LAPACK_LIBD})
	add_dependencies(lapack copyLapackDll blas)

else()

	enable_language(Fortran)

	# Lapack library
	include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/lapackSourceFiles.cmake)
	add_library(lapack ${LAPACK_SOURCE_FILES})

	set_target_properties(lapack PROPERTIES DEBUG_POSTFIX d)
    if(WIN32 AND BUILD_SHARED_LIBS)
		set_target_properties(lapack PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
    endif()
    if(MSVC)
        if(BUILD_SHARED_LIBS)
            set_target_properties(lapack PROPERTIES MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
        endif()
        target_compile_options(lapack PRIVATE /MP)
    else()
        target_compile_options(lapack
            PRIVATE
                $<$<Fortran_COMPILER_ID:Intel>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<Fortran_COMPILER_ID:GNU>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
            )
    endif()

	# Get the correct time functions
    if (NOT TIME_FUNC)
        include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/checkTimeFunction.cmake)
        set(TIME_FUNC NONE ${TIME_FUNC})
        check_time_function(NONE TIME_FUNC)
        check_time_function(INT_CPU_TIME TIME_FUNC)
        check_time_function(EXT_ETIME TIME_FUNC)
        check_time_function(EXT_ETIME_ TIME_FUNC)
        check_time_function(INT_ETIME TIME_FUNC)
        message(STATUS "--> Will use second_${TIME_FUNC}.f and dsecnd_${TIME_FUNC}.f as timing function.")
        set(SECOND_SRC second_${TIME_FUNC}.f)
        set(DSECOND_SRC dsecnd_${TIME_FUNC}.f)
    endif()

	# Fortran-C Interface
	include(FortranCInterface)
	FortranCInterface_HEADER(${CMAKE_CURRENT_BINARY_DIR}/lapackNameMangling/lapackNameMangling.h MACRO_NAMESPACE "FCLAPACK_")
	add_library(lapackNameMangling INTERFACE)
	target_include_directories(lapackNameMangling INTERFACE ${CMAKE_CURRENT_BINARY_DIR}/lapackNameMangling)
	target_link_libraries(lapack
        PUBLIC
            lapackNameMangling
        PRIVATE
            blas
        )

endif()


if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)

	add_subdirectory(dep/blas)
	message("BLAS OK.")

	enable_language(CXX)

	# Test executable
	add_executable(lapack-test
		${PROJECT_SOURCE_DIR}/test/test.cpp
        )
	target_link_libraries(lapack-test lapack)

endif()