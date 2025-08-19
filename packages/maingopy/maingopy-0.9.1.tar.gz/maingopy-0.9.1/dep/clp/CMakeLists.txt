cmake_minimum_required(VERSION 3.15 FATAL_ERROR)

message("Checking files for CLP.")
project(clp C CXX)


if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
    option(BUILD_SHARED_LIBS "Build shared libraries" OFF)
    if (BUILD_SHARED_LIBS)
        set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR} CACHE PATH "Single output directory for all binaries.")
    endif()
endif()


set(CLP_SRCDIR ${CMAKE_CURRENT_SOURCE_DIR}/Clp-1.17.0/Clp/src)
set(CLP_COINDIR ${CMAKE_CURRENT_SOURCE_DIR}/Clp-1.17.0/CoinUtils/src)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/clpSourceFiles.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/coinutilsSourceFiles.cmake)


add_library(clp ${CLP_SOURCES} ${COINUTILS_SOURCES})
target_include_directories(clp
    PUBLIC
        ${CLP_SRCDIR}
        ${CLP_COINDIR}
    )

set_target_properties(clp PROPERTIES DEBUG_POSTFIX d)
if(BUILD_SHARED_LIBS)
    if(WIN32)
        set_target_properties(clp PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
    endif()
    if(MSVC)
        set_target_properties(clp PROPERTIES MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
    endif()
endif()
if(MSVC)
    target_compile_options(clp PRIVATE /MP)
else()
    target_compile_options(clp
        PRIVATE
            $<$<C_COMPILER_ID:Intel>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
            $<$<C_COMPILER_ID:GNU>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
            $<$<C_COMPILER_ID:AppleClang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
            $<$<C_COMPILER_ID:Clang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
        )
endif()
target_compile_options(clp
    PRIVATE
        $<$<C_COMPILER_ID:MSVC>: /wd4141;/wd4068;/wd4018;/wd4244;/wd4267;/wd4065;/wd4102;/wd4101;/wd4805>
        $<$<C_COMPILER_ID:Intel>: $<$<PLATFORM_ID:Windows>:/Qwd858> $<$<NOT:$<PLATFORM_ID:Windows>>:-wd858>>
        $<$<C_COMPILER_ID:GNU>: -Wno-stringop-overflow -Wno-format-overflow -Wno-register>
        $<$<C_COMPILER_ID:AppleClang>: -Wno-constant-logical-operand -Wno-deprecated-register -Wno-parentheses-equality -Wno-constant-conversion>
        $<$<C_COMPILER_ID:Clang>: -Wno-constant-logical-operand -Wno-deprecated-register -Wno-parentheses-equality -Wno-constant-conversion>
)
target_compile_definitions(clp
    PRIVATE
        __BYTE_ORDER
        HAVE_CONFIG_H
        CLP_BUILD
        COINUTILS_BUILD
        COIN_USE_MUMPS_MPI_H
        $<$<C_COMPILER_ID:MSVC>:_CRT_SECURE_NO_WARNINGS _SCL_SECURE_NO_WARNINGS>
)
if(WIN32)
    target_compile_definitions(clp
        PRIVATE
            NDEBUG # Since there is a portion of CLP code (which is compiled if NDEBUG is not defined) that uses usleep (which does not exist for windows), so we need to disable it
        )
endif()
target_link_libraries(clp
    PRIVATE
        mumps
        blas
        lapack
)

if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)

    # Add dependencies
    add_subdirectory(dep/blas)
    message("BLAS done.")
    add_subdirectory(dep/lapack)
    message("LAPACK done.")
    add_subdirectory(dep/mumps)
    message("MUMPS done.")

    # Test executables
    add_executable(clp-test
        ${PROJECT_SOURCE_DIR}/test/test.cpp
    )
    target_link_libraries(clp-test clp)
    target_compile_features(clp-test PRIVATE cxx_std_11)

endif()

# Determine Fortran-C name mangling
if((${MUMPS_usePrecompiledDll}) AND (${BLAS_usePrecompiledDll}) AND (${LAPACK_usePrecompiledDlls}))

    set(MANGLINGFILE "lapackNameMangling.h")
    set(MANGLINGMACRO FCLAPACK_GLOBAL)
    set(MANGLINGMACRO_ FCLAPACK_GLOBAL_)

else()

    set(MANGLINGFILE "lapackNameMangling.h")
    enable_language(Fortran)
    # Fortran-C Interface
    include(FortranCInterface)
    set(MANGLINGFILE "clpNameMangling.h")
    set(MANGLINGMACRO FCCLP_GLOBAL)
    set(MANGLINGMACRO_ FCCLP_GLOBAL_)
    FortranCInterface_HEADER(${CMAKE_CURRENT_BINARY_DIR}/clpNameMangling/${MANGLINGFILE} MACRO_NAMESPACE "FCCLP_")
    add_library(clpNameMangling INTERFACE)
    target_include_directories(clp PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/clpNameMangling)

endif()

# clpConfig.cmake needs MANGLINGFILE, therefore it is down here
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/clpConfig.cmake)
