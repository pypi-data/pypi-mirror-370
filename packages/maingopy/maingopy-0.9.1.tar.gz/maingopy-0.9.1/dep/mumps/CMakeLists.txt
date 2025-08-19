cmake_minimum_required(VERSION 3.15 FATAL_ERROR)

message("Checking files for MUMPS.")
project(mumps C)


if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
    option(BUILD_SHARED_LIBS "Build shared libraries" OFF)
endif()


# For Visual Studio, we use pre-compiled version by default.
if(MSVC)

    option(MUMPS_usePrecompiledDll "Use precompiled MUMPS library" TRUE)

    # Set paths
    if(NOT "${CMAKE_SIZEOF_VOID_P}" STREQUAL "8")
        set(MUMPS_PRECOMPILED_DIR ${CMAKE_CURRENT_SOURCE_DIR}/precompiled/win32)
    else()
        set(MUMPS_PRECOMPILED_DIR ${CMAKE_CURRENT_SOURCE_DIR}/precompiled/win64)
    endif()

else()

    set(MUMPS_usePrecompiledDll FALSE CACHE INTERNAL "Use precompiled MUMPS library" FORCE)

endif()


if(MUMPS_usePrecompiledDll)

    message("Using pre-compiled MUMPS library.")

    # Find MUMPS libs
    find_library(MUMPS_LIB
        NAMES mumps
        HINTS ${MUMPS_PRECOMPILED_DIR}/lib
        NO_DEFAULT_PATH
    )
    message(STATUS "MUMPS Library: ${MUMPS_LIB}")
    find_library(MUMPS_LIBD
        NAMES mumpsd
        HINTS ${MUMPS_PRECOMPILED_DIR}/lib
        NO_DEFAULT_PATH
    )
    message(STATUS "MUMPS Library (Debug): ${MUMPS_LIBD}")

    # Prepare for copying dll
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Debug)
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/Release)
    add_custom_target(copyMumpsDll ALL COMMAND ${CMAKE_COMMAND} -E copy ${MUMPS_PRECOMPILED_DIR}/bin/$<$<CONFIG:Debug>:mumpsd.dll>$<$<NOT:$<CONFIG:Debug>>:mumps.dll>  $<$<CONFIG:Debug>:${CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG}/mumpsd.dll>$<$<NOT:$<CONFIG:Debug>>:${CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE}/mumps.dll>)

    # Create mumps target
    add_library(mumps STATIC IMPORTED GLOBAL)
    set(MUMPS_DIR ${CMAKE_CURRENT_SOURCE_DIR}/MUMPS_5.4.0)
    set_property(TARGET mumps APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES "${MUMPS_DIR}/include")
    set_property(TARGET mumps APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES "${MUMPS_DIR}/libseq")
    set_property(TARGET mumps APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES "${CMAKE_CURRENT_SOURCE_DIR}/inc")
    set_target_properties(mumps  PROPERTIES  IMPORTED_LOCATION_RELEASE ${MUMPS_LIB})
    set_target_properties(mumps  PROPERTIES  IMPORTED_LOCATION_DEBUG ${MUMPS_LIBD})
    add_dependencies(mumps copyMumpsDll blas lapack)

else()

    enable_language(Fortran)

    # Mumps library
    set(MUMPS_DIR ${CMAKE_CURRENT_SOURCE_DIR}/MUMPS_5.4.0)
    include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/mumpsCSourceFiles.cmake)
    include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/mumpsFortranSourceFiles.cmake)
    include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/mumpsCLibseqFiles.cmake)
    include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/mumpsFortranLibseqFiles.cmake)


    # For Visual Studio, create separate targets for the C and Fortran parts
    if(MSVC)

        # Fortran part of MUMPS:
        add_library(mumps-f STATIC ${MUMPS_FORTRAN_SOURCES} ${MUMPS_FORTRAN_SOURCES_SEQ})
        target_include_directories(mumps-f
            PRIVATE
                ${MUMPS_DIR}/include
                ${MUMPS_DIR}/libseq
            )
        if(BUILD_SHARED_LIBS)
            set_target_properties(mumps-f PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
            set_target_properties(mumps-f PROPERTIES POSITION_INDEPENDENT_CODE ON)
            set_target_properties(mumps-f PROPERTIES MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
        endif()
        set_target_properties(mumps-f PROPERTIES DEBUG_POSTFIX d)
        target_compile_options(mumps-f PRIVATE /MP;$<$<Fortran_COMPILER_ID:Intel>:/Qdiag-disable:6380;/Qdiag-disable:6379>)

        # C part of MUMPS:
        add_library(mumps ${MUMPS_C_SOURCES} ${MUMPS_C_SOURCES_SEQ})
        if(BUILD_SHARED_LIBS)
            set_target_properties(mumps PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
            set_target_properties(mumps PROPERTIES POSITION_INDEPENDENT_CODE ON)
            set_target_properties(mumps PROPERTIES MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
        endif()
        set_target_properties(mumps PROPERTIES DEBUG_POSTFIX d)
        target_compile_options(mumps PRIVATE /MP;/wd4005;/wd4101;/wd4267;/wd4996)
        target_link_libraries(mumps PRIVATE mumps-f)

    else()


        add_library(mumps
                ${MUMPS_FORTRAN_SOURCES}
                ${MUMPS_FORTRAN_SOURCES_SEQ}
                ${MUMPS_C_SOURCES}
                ${MUMPS_C_SOURCES_SEQ}
                )
        if(BUILD_SHARED_LIBS)
            set_target_properties(mumps PROPERTIES POSITION_INDEPENDENT_CODE ON)
        endif()
        set_target_properties(mumps PROPERTIES DEBUG_POSTFIX d)
        target_compile_options(mumps
            PRIVATE
                $<$<C_COMPILER_ID:Intel>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<C_COMPILER_ID:GNU>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<C_COMPILER_ID:Clang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<C_COMPILER_ID:AppleClang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
            )
        if(CMAKE_Fortran_COMPILER_ID STREQUAL "GNU")
            if(CMAKE_Fortran_COMPILER_VERSION VERSION_GREATER 10)
                set_property(SOURCE ${MUMPS_FORTRAN_SOURCES} ${MUMPS_FORTRAN_SOURCES_SEQ} PROPERTY COMPILE_OPTIONS -fallow-argument-mismatch -w)
	    else()
                set_property(SOURCE ${MUMPS_FORTRAN_SOURCES} ${MUMPS_FORTRAN_SOURCES_SEQ} PROPERTY COMPILE_OPTIONS -w)
            endif()
        endif()

    endif()

    if(WIN32)
        target_compile_definitions(mumps PRIVATE DMUMPS_WIN32)
    endif()

    set_property(SOURCE ${MUMPS_C_SOURCES} ${MUMPS_C_SOURCES_SEQ} PROPERTY COMPILE_DEFINITIONS
         MUMPS_BUILD Add_ WITHOUT_PTHREAD=1 ALLOW_NON_INIT MUMPS_ARITH=MUMPS_ARITH_d)

    target_include_directories(mumps
        PUBLIC
            ${MUMPS_DIR}/include
            ${MUMPS_DIR}/libseq
            ${CMAKE_CURRENT_SOURCE_DIR}/inc
        )
    target_link_libraries(mumps
        PRIVATE
            blas
            lapack
        )

endif()


if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)

    # Add dependencies
    add_subdirectory(dep/blas)
    message("BLAS OK.")
    add_subdirectory(dep/lapack)
    message("LAPACK OK.")

    # Test executable
    add_executable(mumps-test
        ${CMAKE_CURRENT_SOURCE_DIR}/MUMPS_5.4.0/examples/c_example.c
    )
    target_link_libraries(mumps-test mumps)

endif()
