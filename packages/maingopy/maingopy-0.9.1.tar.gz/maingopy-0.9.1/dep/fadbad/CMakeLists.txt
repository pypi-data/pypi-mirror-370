cmake_minimum_required(VERSION 3.8 FATAL_ERROR)

project(fadbad CXX)
MESSAGE("Checking files for FADBAD++.")

add_library(fadbad INTERFACE)

set(FADBADDIR ${PROJECT_SOURCE_DIR}/fadbad-2.1)
target_include_directories(fadbad
	INTERFACE ${FADBADDIR}
)


if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
	add_executable(test-fadbad
		${PROJECT_SOURCE_DIR}/test/test.cpp
	)
	target_link_libraries(test-fadbad fadbad)
endif()