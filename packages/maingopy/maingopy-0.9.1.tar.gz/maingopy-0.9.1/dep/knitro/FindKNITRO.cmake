# This module finds knitro.
#
# User can give KNITRO_ROOT_DIR as a hint stored in the cmake cache.


if(WIN32)
  execute_process(COMMAND cmd /C set KNITRODIR OUTPUT_VARIABLE KNITRO_ROOT_DIR ERROR_QUIET OUTPUT_STRIP_TRAILING_WHITESPACE)
  if(NOT KNITRO_ROOT_DIR)
    message(STATUS "Unable to find KNITRO: environment variable KNITRODIR not set.")
  else() 
	  # We want to use version 11.0.1 only  
	  set(KNITRO_VERSION "Knitro 11.0.1")
	  STRING(REGEX REPLACE "KNITRODIR=" "" KNITRO_ROOT_DIR ${KNITRO_ROOT_DIR})
	  STRING(REGEX REPLACE "\n.*" "" KNITRO_ROOT_DIR ${KNITRO_ROOT_DIR})
	  file(TO_CMAKE_PATH "${KNITRO_ROOT_DIR}" KNITRO_ROOT_DIR_GUESS) 
	  set(KNITRO_ROOT_DIR "${KNITRO_ROOT_DIR_GUESS}")
	  
	  message(STATUS "Found KNITRO version ${KNITRO_VERSION} at '${KNITRO_ROOT_DIR}'")
	  
  endif()
else()

 	set(KNITRO_ROOT_DIR "/opt/knitro")	
	message("Looking for KNITRO at " ${KNITRO_ROOT_DIR})
  
endif(WIN32)

set(KNITRO_LIB_PATH "${KNITRO_ROOT_DIR}/lib")
set(KNITRO_INCLUDE_PATH "${KNITRO_ROOT_DIR}/include")
set(KNITRO_CPP_PATH "${KNITRO_ROOT_DIR}/examples/C++/include")


find_path(KNITRO_INCLUDE_DIR
  knitro.h
  HINTS ${KNITRO_INCLUDE_PATH}
  )

message(STATUS "KNITRO Include: ${KNITRO_INCLUDE_DIR}")
find_path(KNITRO_CPP_INCLUDE_DIR
  KTRProblem.h
  HINTS ${KNITRO_CPP_PATH}
  )
message(STATUS "KNITRO Include CPP: ${KNITRO_CPP_INCLUDE_DIR}")
  
find_library(KNITRO_LIBRARY
  NAMES knitro1101 knitro 
  HINTS  ${KNITRO_LIB_PATH} #windows  
  )
message(STATUS "KNITRO Library: ${KNITRO_LIBRARY}")

#Debug
find_library(KNITRO_LIBRARY_D
  NAMES knitro1101 knitro
  HINTS  ${KNITRO_LIB_PATH} #windows  
  )
message(STATUS "KNITRO Library (Debug): ${KNITRO_LIBRARY_D}")

if(WIN32)
	find_path(KNITRO_BIN_DIR
	  knitro1101.dll 
          HINTS ${KNITRO_LIB_PATH} #windows
	  )
endif(WIN32)

include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(KNITRO DEFAULT_MSG 
 KNITRO_LIBRARY KNITRO_LIBRARY_D KNITRO_INCLUDE_DIR KNITRO_CPP_INCLUDE_DIR )

 
if(KNITRO_FOUND)
	SET(KNITRO_INCLUDE_DIRS ${KNITRO_INCLUDE_DIR} ${KNITRO_CPP_INCLUDE_DIR})
endif(KNITRO_FOUND)


mark_as_advanced(KNITRO_LIBRARY KNITRO_LIBRARY_D KNITRO_INCLUDE_DIRS)