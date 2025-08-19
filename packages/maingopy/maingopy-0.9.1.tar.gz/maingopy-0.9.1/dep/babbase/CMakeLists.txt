cmake_minimum_required(VERSION 3.8 FATAL_ERROR)
cmake_policy(SET CMP0074 NEW)
message("Checking files for babBase.")
project(babbase CXX)

if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
    option(BUILD_SHARED_LIBS "Build shared libraries" OFF)
endif()


# Babbase library
add_library(babbase
	${PROJECT_SOURCE_DIR}/src/babTree.cpp
	${PROJECT_SOURCE_DIR}/src/babBrancher.cpp
	${PROJECT_SOURCE_DIR}/src/babOptVar.cpp
)
target_include_directories(babbase PUBLIC ${PROJECT_SOURCE_DIR}/inc)
target_compile_features(babbase PUBLIC cxx_std_11)
set_target_properties(babbase PROPERTIES DEBUG_POSTFIX d)
if(WIN32 AND BUILD_SHARED_LIBS)
    set_target_properties(babbase PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()
if(MSVC)
       target_compile_options(babbase PRIVATE /MP;/Qpar)
else()
    target_compile_options(babbase
        PRIVATE
            $<$<CXX_COMPILER_ID:Intel>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
            $<$<CXX_COMPILER_ID:GNU>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
            $<$<CXX_COMPILER_ID:Clang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
            $<$<CXX_COMPILER_ID:AppleClang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
        )
endif()    


if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
	# Simple test executable (without boost)
	enable_language(CXX)
	add_executable(babbase-test
		${PROJECT_SOURCE_DIR}/test/test.cpp
	)
	target_link_libraries(babbase-test babbase)
	target_compile_features(babbase-test PRIVATE cxx_std_11)
endif()


# Tests with boost / rapidcheck
option(BABBASE_build_boost_tests "Build tests for BabBase using Boost." OFF)
if(BABBASE_build_boost_tests)
	include(test/boostTest.cmake)
endif()