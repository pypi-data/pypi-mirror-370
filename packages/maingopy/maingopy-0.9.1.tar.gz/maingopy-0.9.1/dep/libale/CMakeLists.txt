# Uncomment the following line only if CMake has issued a corresponding error message.
# You can also specify a specific version, e.g., with set(CMAKE_SYSTEM_VERSION 10.0.20348.0)
# set(CMAKE_SYSTEM_VERSION 10.0)

project(ale)
cmake_minimum_required(VERSION 3.8 FATAL_ERROR)

set(CMAKE_DISABLE_IN_SOURCE_BUILD ON)
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)


##########
# libALE project
##########

message("Checking files for libALE.")


##########
# Library target
##########

add_library(ale STATIC
    ${PROJECT_SOURCE_DIR}/src/config.cpp
    ${PROJECT_SOURCE_DIR}/src/expression.cpp
    ${PROJECT_SOURCE_DIR}/src/helper.cpp
    ${PROJECT_SOURCE_DIR}/src/lexer.cpp
    ${PROJECT_SOURCE_DIR}/src/node.cpp
    ${PROJECT_SOURCE_DIR}/src/parser.cpp
    ${PROJECT_SOURCE_DIR}/src/symbol.cpp
    ${PROJECT_SOURCE_DIR}/src/symbol_printer.cpp
    ${PROJECT_SOURCE_DIR}/src/symbol_table.cpp
    ${PROJECT_SOURCE_DIR}/src/symbol_typer.cpp
    ${PROJECT_SOURCE_DIR}/src/tensor.cpp
    ${PROJECT_SOURCE_DIR}/src/token.cpp
    ${PROJECT_SOURCE_DIR}/src/token_buffer.cpp
    ${PROJECT_SOURCE_DIR}/src/value.cpp
    ${PROJECT_SOURCE_DIR}/src/util/evaluator.cpp
    ${PROJECT_SOURCE_DIR}/src/util/expression_differentiation.cpp
    ${PROJECT_SOURCE_DIR}/src/util/expression_to_string.cpp
    ${PROJECT_SOURCE_DIR}/src/util/expression_utils/expression_utils_get_shape.cpp
    ${PROJECT_SOURCE_DIR}/src/util/expression_utils/expression_utils_is_constant.cpp
    ${PROJECT_SOURCE_DIR}/src/util/expression_utils/expression_utils_replace_constant.cpp
    ${PROJECT_SOURCE_DIR}/src/util/expression_utils/expression_utils_replace_parameter.cpp
    #${PROJECT_SOURCE_DIR}/src/util/expression_utils.cpp
    ${PROJECT_SOURCE_DIR}/src/util/nrtl_subroutines.cpp
    ${PROJECT_SOURCE_DIR}/src/util/renaming_util.cpp
    ${PROJECT_SOURCE_DIR}/src/util/visitor_utils.cpp
    ${PROJECT_SOURCE_DIR}/src/util/var_bounds_consistency_checker.cpp
)
target_include_directories(ale
    PUBLIC ${PROJECT_SOURCE_DIR}/src
)
set_target_properties(ale
        PROPERTIES CXX_STANDARD 17
)
find_program(iwyu_path NAMES include-what-you-use iwyu)
if(iwyu_path)
    set(iwyu_path_and_options
    ${iwyu_path}
    -Xiwyu
    --cxx17ns
    -Xiwyu
    --update_comments
    -Xiwyu
    --max_line_length=160
    -Xiwyu
    --no_fwd_decls )
    message("Found iwyu")
    set_property(TARGET ale PROPERTY CMAKE_CXX_INCLUDE_WHAT_YOU_USE ${iwyu_path_and_options})
endif()

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)


file(GLOB ALL_ALE_src CONFIGURE_DEPENDS ${PROJECT_SOURCE_DIR}/src/**.cpp ${PROJECT_SOURCE_DIR}/src/**.hpp ${PROJECT_SOURCE_DIR}/src/**.h ${PROJECT_SOURCE_DIR}/src/**.tpp)

find_package(ClangFormat)
if(CLANG_FORMAT_FOUND)


    message("clang-format executable found: ${CLANG_FORMAT_EXECUTABLE}\n"
            "version:${CLANG_FORMAT_VERSION}"
    )
    if(MSVC)
        find_program(GIT_CLANG_FORMAT_EXE git-clang-format.py
                    HINTS ${clang_path_hint_1} ${clang_path_hint_2}
        )
    else()
        find_program(GIT_CLANG_FORMAT_EXE git-clang-format)
    endif()
    message("git-clang-format executable found: ${GIT_CLANG_FORMAT_EXE}\n"
            "version:${CLANG_FORMAT_VERSION}"
    )
    add_custom_target(
        format_ALE ALL
        COMMAND "${GIT_CLANG_FORMAT_EXE}" --commit "HEAD" -q --diff --style=file
                --binary=${CLANG_FORMAT_EXECUTABLE} "${ALL_ALE_src}" || (exit 0)
        COMMENT "ALE: Running formatting on diff from previous commit."
        VERBATIM COMMAND_EXPAND_LISTS
    )
    add_custom_target(
        doformat_ALE
        # ALL
        COMMAND "${GIT_CLANG_FORMAT_EXE}" --commit "HEAD" -q --force
                --style=file --binary=${CLANG_FORMAT_EXECUTABLE} "${ALL_ALE_src}" 
        COMMENT "ALE: Apply formatting on diff from previous commit."
        VERBATIM COMMAND_EXPAND_LISTS
    )
    add_custom_target(
        hardformat_ALE
        COMMAND "${CLANG_FORMAT_EXECUTABLE}" --dry-run "${ALL_ALE_src}" || (exit 0)
        COMMENT "ALE: Running formatting on diff from previous commit."
        VERBATIM COMMAND_EXPAND_LISTS
    )
    add_custom_target(
        dohardformat_ALE
        # ALL
        COMMAND "${CLANG_FORMAT_EXECUTABLE}" -i "${ALL_ALE_src}" 
        COMMENT "ALE: Running formatting without looking at diff."
        VERBATIM COMMAND_EXPAND_LISTS
    )
endif()


if(MSVC)
    message(STATUS "Detected MSVC: using compile flag /bigobj /MP /Qpar /Zc:preprocessor (or /experimental:preprocessor)")
    target_compile_options(ale
        PUBLIC /bigobj /MP /Qpar
    )
    if(MSVC_VERSION VERSION_GREATER_EQUAL  1925)
        message(STATUS "Detected MSVC version ${MSVC_VERSION}. Using /Zc:preprocessor flag."
        )
        target_compile_options(ale
            PUBLIC /Zc:preprocessor
        )
    elseif(MSVC_VERSION VERSION_GREATER_EQUAL  1915)
        message(STATUS "Detected MSVC version ${MSVC_VERSION}. Using /experimental:preprocessor flag."
        )
        target_compile_options(ale
            PUBLIC /experimental:preprocessor
        )
    else()
        message(FATAL_ERROR "Unsupported Visual Studio version ${MSVC_VERSION}.\n"
            "Visual Studio 2017 version 15.8 or later required for preprocessor conformance mode (/experimental:preprocessor) [depricated] or "
            "Visual Studio 2019 version 16.5 or later required for preprocessor conformance mode (/Zc:preprocessor). "
            "Preprocessor conformance mode is needed for the forward declarations.\n"
            ">>>>>>>>>>>>>>>>>>>>>>>>> POSSIBLE WORKAROUNDS <<<<<<<<<<<<<<<<<<<<<<<<<\n"
            "Install a newer Visual Studio version.\n"
        )
    endif()
    if(CMAKE_VS_WINDOWS_TARGET_PLATFORM_VERSION VERSION_LESS "10.0.20348.0")
        message(FATAL_ERROR
            "Using incompatible Windows SDK version ${CMAKE_VS_WINDOWS_TARGET_PLATFORM_VERSION}.\n"
            "The preprocessor conformance mode flag /Zc:preprocessor (or /experimental:preprocessor) [depricated]) requires Windows SDK 10.0.20348.0 (version 2104) or later. Preprocessor conformance mode is required for the forward declarations.\n"
            ">>>>>>>>>>>>>>>>>>>>>>>>> POSSIBLE WORKAROUNDS <<<<<<<<<<<<<<<<<<<<<<<<<\n"
            "1. Check whether a compatible Windows SDK version >= 10.0.20348.0 is installed; install compatible Windows SDK if necessary.\n"
            "2. If CMake selects a incompatible Windows SDK version, manually select a compatible Windows SDK version >= 10.0.20348.0 as described below.\n"
            "2.1. Uncomment or add the line: 'set(CMAKE_SYSTEM_VERSION 10.0)' in the CMakeLists.txt of the root directory. You can also select a specific Windows SDK version by replacing '10.0' with the desired version number. Note that this line must be inserted before the first use of the 'project' command.\n"
            "2.2. If you run cmake from the command line, you can pass the desired Windows SDK version with, e.g., '-D CMAKE_SYSTEM_VERSION=10.0.20348.0'.\n"
            "3. Delete cache, reconfigure, and regenerate cmake.\n"
            #"4. (only for developers) If the above doesn't work, define forward declarations manually."
        )
    else()
        message(STATUS "Using compatible Windows SDK version ${CMAKE_VS_WINDOWS_TARGET_PLATFORM_VERSION}")
    endif()

    message(STATUS "Detected MSVC: using compile definition _USE_MATH_DEFINES")
    target_compile_definitions(ale
        PUBLIC _USE_MATH_DEFINES
    )
    target_compile_options(ale
        PRIVATE /wd4267)    # ingoring compiler warning C4267: conversion from 'size_t' to 'type', possible loss of data
endif()

##########
# Demo target
##########

if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
    add_executable(ale_demo
        ${PROJECT_SOURCE_DIR}/demo/src/main.cpp
    )
    target_include_directories(ale_demo
        PRIVATE ${PROJECT_SOURCE_DIR}/demo/src
    )
    file(GLOB DEMO_INPUT_FILES "${PROJECT_SOURCE_DIR}/demo/input_files/*.txt")
    if (MSVC)
        file(COPY ${DEMO_INPUT_FILES} DESTINATION ${CMAKE_BINARY_DIR}/Release/)
        file(COPY ${DEMO_INPUT_FILES} DESTINATION ${CMAKE_BINARY_DIR}/Debug/)
    else()
        file(COPY ${DEMO_INPUT_FILES} DESTINATION ${CMAKE_BINARY_DIR}/)
    endif()
    set_target_properties(ale_demo
        PROPERTIES CXX_STANDARD 17
    )
    target_link_libraries(ale_demo ale)
endif()
