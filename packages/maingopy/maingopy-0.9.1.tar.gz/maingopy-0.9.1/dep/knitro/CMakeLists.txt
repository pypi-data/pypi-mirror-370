cmake_minimum_required(VERSION 3.8 FATAL_ERROR)

message("Checking files for KNITRO.")
project(knitro C CXX)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${PROJECT_SOURCE_DIR}")

find_package(KNITRO)


if(${KNITRO_FOUND})
	add_library(knitro SHARED IMPORTED GLOBAL)
	set_target_properties(knitro  PROPERTIES  INTERFACE_INCLUDE_DIRECTORIES "${KNITRO_INCLUDE_DIR};${KNITRO_CPP_INCLUDE_DIR}")
	set_target_properties(knitro  PROPERTIES  INTERFACE_COMPILE_DEFINITIONS HAVE_KNITRO)
	if(WIN32)
		set_target_properties(knitro  PROPERTIES  IMPORTED_IMPLIB_RELEASE ${KNITRO_LIBRARY})
		set_target_properties(knitro  PROPERTIES  IMPORTED_IMPLIB_GENERAL ${KNITRO_LIBRARY})
		set_target_properties(knitro  PROPERTIES  IMPORTED_IMPLIB_DEBUG ${KNITRO_LIBRARY})
	else()
		set_target_properties(knitro  PROPERTIES  IMPORTED_LOCATION ${KNITRO_LIBRARY})
	endif()
else()
	add_library(knitro INTERFACE)
	message("KNITRO could not be found. A dummy target will be used instead and the flag HAVE_KNITRO will not be defined.")
	message("This may be OK depending on the application (e.g., in MAiNGO), but you will not be able to actually use KNITRO.")

endif()
	
	
if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
	if(${KNITRO_FOUND})
		add_executable(knitro-test
			${PROJECT_SOURCE_DIR}/test/test.cpp
			${PROJECT_SOURCE_DIR}/test/knitroProblem.cpp
		)
		target_link_libraries(knitro-test knitro)
	else()
		message(FATAL_ERROR "KNITRO could not be found. Cannot build KNITRO test.")
	endif()
endif()