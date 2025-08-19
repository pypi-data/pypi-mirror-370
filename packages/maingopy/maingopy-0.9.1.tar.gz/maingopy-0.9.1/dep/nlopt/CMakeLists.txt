cmake_minimum_required (VERSION 3.15)

message("Checking files for NLOPT.")
project (nlopt C CXX)

set(NLOPT_DIR "nlopt-2.9.1")

#==============================================================================
# version
set (NLOPT_MAJOR_VERSION "2")
set (NLOPT_MINOR_VERSION "9")
set (NLOPT_BUGFIX_VERSION "1")
set (NLOPT_VERSION_STRING ${NLOPT_MAJOR_VERSION}.${NLOPT_MINOR_VERSION}.${NLOPT_BUGFIX_VERSION})
message (STATUS "NLopt version ${NLOPT_VERSION_STRING}")

# This is the ABI version number, which differes from the API version above
# (it indicates ABI compatibility), but they are typically incremented together.
set(SO_MAJOR 0)
set(SO_MINOR 13)
set(SO_PATCH 0)
#==============================================================================

list (APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)

option (NLOPT_CXX "enable cxx routines" ON)
option (NLOPT_FORTRAN "enable fortran" OFF)
option (BUILD_SHARED_LIBS "Build NLopt as a shared library" OFF)
option (NLOPT_PYTHON "build python bindings" OFF)
option (NLOPT_OCTAVE "build octave bindings" OFF)
option (NLOPT_MATLAB "build matlab bindings" OFF)
option (NLOPT_GUILE "build guile bindings" OFF)
option (NLOPT_SWIG "use SWIG to build bindings" OFF)
option (NLOPT_LUKSAN "enable LGPL Luksan solvers" ON)
option (NLOPT_TESTS "build unit tests" OFF)

if (CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
  option (NLOPT_TESTS "build unit tests" ON)
else ()
  option (NLOPT_TESTS "build unit tests" OFF)
endif ()


if(POLICY CMP0042)
  # Set MACOSX_RPATH to ON
  cmake_policy(SET CMP0042 NEW)
endif()

if (POLICY CMP0086)
  # UseSWIG honors SWIG_MODULE_NAME via -module flag
  cmake_policy(SET CMP0086 NEW)
endif ()

include (CheckIncludeFiles)
include (CheckFunctionExists)
include (CheckTypeSize)
include (CheckCCompilerFlag)
include (CheckCXXSymbolExists)
include (CheckCSourceCompiles)
include (CheckCXXCompilerFlag)
include (CheckLibraryExists)

#==============================================================================
# COMPILATION CHECKINGS and CONFIGURATION GENERATION
#==============================================================================
check_include_file (getopt.h HAVE_GETOPT_H)
check_include_file (unistd.h HAVE_UNISTD_H)
check_include_file (stdint.h HAVE_STDINT_H)
check_include_file (time.h HAVE_TIME_H)
check_include_file (sys/time.h HAVE_SYS_TIME_H)
if (HAVE_TIME_H AND HAVE_SYS_TIME_H)
  set (TIME_WITH_SYS_TIME TRUE)
endif ()
check_function_exists (getpid HAVE_GETPID)
check_function_exists (syscall HAVE_GETTID_SYSCALL)
check_function_exists (isinf HAVE_ISINF)
check_function_exists (isnan HAVE_ISNAN)
check_function_exists (gettimeofday HAVE_GETTIMEOFDAY)
check_function_exists (qsort_r HAVE_QSORT_R)
check_function_exists (time HAVE_TIME)
check_function_exists (copysign HAVE_COPYSIGN)
check_function_exists (getopt HAVE_GETOPT)
check_type_size ("uint32_t" SIZEOF_UINT32_T)
set (HAVE_UINT32_T ${SIZEOF_UINT32_T})
check_type_size ("unsigned int" SIZEOF_UNSIGNED_INT)
check_type_size ("unsigned long" SIZEOF_UNSIGNED_LONG)

check_library_exists ("m" sqrt "" HAVE_LIBM)
if (HAVE_LIBM)
  set (M_LIBRARY m)
  set (LIBS_PRIVATE "-l${M_LIBRARY}")
endif()

if (NOT DEFINED HAVE_FPCLASSIFY)
  message(STATUS "Looking for fpclassify")
  file (WRITE ${PROJECT_BINARY_DIR}/fpclassify.c "#include <math.h>\n")
  file (APPEND ${PROJECT_BINARY_DIR}/fpclassify.c "int main(void) {\n")
  file (APPEND ${PROJECT_BINARY_DIR}/fpclassify.c "if (!fpclassify(3.14159)) fpclassify(2.7183);\n")
  file (APPEND ${PROJECT_BINARY_DIR}/fpclassify.c "  return 0; }\n")
  try_compile (HAVE_FPCLASSIFY
  ${PROJECT_BINARY_DIR}/build_fpclassify
  ${PROJECT_BINARY_DIR}/fpclassify.c
  CMAKE_FLAGS -DLINK_LIBRARIES=m)
  message(STATUS "Looking for fpclassify - ${HAVE_FPCLASSIFY}")
endif ()

option (WITH_THREADLOCAL "check thread local keyword" ON)
if (WITH_THREADLOCAL AND NOT DEFINED THREADLOCAL)
  foreach (_THREADLOCAL_KEY "__thread" "__declspec(thread)")
    unset (HAVE_THREAD_LOCAL_STORAGE CACHE)
    check_c_source_compiles("
    ${_THREADLOCAL_KEY} int tls;

    int main(void) {
        return 0;
    }" HAVE_THREAD_LOCAL_STORAGE)
    if (HAVE_THREAD_LOCAL_STORAGE)
      set (THREADLOCAL ${_THREADLOCAL_KEY} CACHE STRING "Thread local keyword")
    endif ()
  endforeach()
endif ()


if (NLOPT_CXX OR NLOPT_PYTHON OR NLOPT_GUILE OR NLOPT_OCTAVE)
  check_cxx_symbol_exists (__cplusplus ciso646 SYSTEM_HAS_CXX)
  if (SYSTEM_HAS_CXX)
    set (CMAKE_CXX_STANDARD 11) # set the standard to C++11 but do not require it

    if (NLOPT_CXX)
      set (CMAKE_CXX_STANDARD_REQUIRED ON) # if we build C++ API, we do need C++11
    endif ()
  else()
    message (FATAL_ERROR "The compiler doesn't support CXX.")
  endif ()
endif ()

#==============================================================================
# CREATE nlopt_config.h
#==============================================================================

configure_file (${CMAKE_CURRENT_SOURCE_DIR}/${NLOPT_DIR}/nlopt_config.h.in ${CMAKE_CURRENT_BINARY_DIR}/nlopt_config.h IMMEDIATE)

#==============================================================================
# nlopt LIBRARY TARGET (SHARED OR STATIC)
#==============================================================================

set (NLOPT_HEADERS
  ${NLOPT_DIR}/src/api/nlopt.h ${PROJECT_BINARY_DIR}/nlopt.hpp
)

add_custom_command (OUTPUT nlopt.hpp
  COMMAND ${CMAKE_COMMAND} -DAPI_SOURCE_DIR=${PROJECT_SOURCE_DIR}/${NLOPT_DIR}/src/api -P ${PROJECT_SOURCE_DIR}/${NLOPT_DIR}/cmake/generate-cpp.cmake
  MAIN_DEPENDENCY ${NLOPT_DIR}/src/api/nlopt-in.hpp)
add_custom_target (generate-cpp ALL DEPENDS nlopt.hpp)

if (NLOPT_FORTRAN)
  add_custom_command (OUTPUT nlopt.f
    COMMAND ${CMAKE_COMMAND} -DAPI_SOURCE_DIR=${PROJECT_SOURCE_DIR}/${NLOPT_DIR}/src/api -P ${PROJECT_SOURCE_DIR}/${NLOPT_DIR}/cmake/generate-fortran.cmake
    MAIN_DEPENDENCY ${NLOPT_DIR}/src/api/nlopt.h)
  add_custom_target (generate-fortran ALL DEPENDS nlopt.f)
  list (APPEND NLOPT_HEADERS ${PROJECT_BINARY_DIR}/nlopt.f)
endif()

set (NLOPT_SOURCES
  ${NLOPT_DIR}/src/algs/direct/DIRect.c ${NLOPT_DIR}/src/algs/direct/direct_wrap.c ${NLOPT_DIR}/src/algs/direct/DIRserial.c ${NLOPT_DIR}/src/algs/direct/DIRsubrout.c ${NLOPT_DIR}/src/algs/direct/direct-internal.h ${NLOPT_DIR}/src/algs/direct/direct.h
  ${NLOPT_DIR}/src/algs/cdirect/cdirect.c ${NLOPT_DIR}/src/algs/cdirect/hybrid.c ${NLOPT_DIR}/src/algs/cdirect/cdirect.h
  ${NLOPT_DIR}/src/algs/praxis/praxis.c ${NLOPT_DIR}/src/algs/praxis/praxis.h
  ${NLOPT_DIR}/src/algs/crs/crs.c ${NLOPT_DIR}/src/algs/crs/crs.h
  ${NLOPT_DIR}/src/algs/mlsl/mlsl.c ${NLOPT_DIR}/src/algs/mlsl/mlsl.h
  ${NLOPT_DIR}/src/algs/mma/mma.c ${NLOPT_DIR}/src/algs/mma/mma.h ${NLOPT_DIR}/src/algs/mma/ccsa_quadratic.c
  ${NLOPT_DIR}/src/algs/cobyla/cobyla.c ${NLOPT_DIR}/src/algs/cobyla/cobyla.h
  ${NLOPT_DIR}/src/algs/newuoa/newuoa.c ${NLOPT_DIR}/src/algs/newuoa/newuoa.h
  ${NLOPT_DIR}/src/algs/neldermead/nldrmd.c ${NLOPT_DIR}/src/algs/neldermead/neldermead.h ${NLOPT_DIR}/src/algs/neldermead/sbplx.c
  ${NLOPT_DIR}/src/algs/auglag/auglag.c ${NLOPT_DIR}/src/algs/auglag/auglag.h
  ${NLOPT_DIR}/src/algs/bobyqa/bobyqa.c ${NLOPT_DIR}/src/algs/bobyqa/bobyqa.h
  ${NLOPT_DIR}/src/algs/isres/isres.c ${NLOPT_DIR}/src/algs/isres/isres.h
  ${NLOPT_DIR}/src/algs/slsqp/slsqp.c ${NLOPT_DIR}/src/algs/slsqp/slsqp.h
  ${NLOPT_DIR}/src/algs/esch/esch.c ${NLOPT_DIR}/src/algs/esch/esch.h
  ${NLOPT_DIR}/src/api/general.c ${NLOPT_DIR}/src/api/options.c ${NLOPT_DIR}/src/api/optimize.c ${NLOPT_DIR}/src/api/deprecated.c ${NLOPT_DIR}/src/api/nlopt-internal.h ${NLOPT_DIR}/src/api/nlopt.h ${NLOPT_DIR}/src/api/f77api.c ${NLOPT_DIR}/src/api/f77funcs.h ${NLOPT_DIR}/src/api/f77funcs_.h ${PROJECT_BINARY_DIR}/nlopt.hpp
  ${NLOPT_DIR}/src/util/mt19937ar.c ${NLOPT_DIR}/src/util/sobolseq.c ${NLOPT_DIR}/src/util/soboldata.h ${NLOPT_DIR}/src/util/timer.c ${NLOPT_DIR}/src/util/stop.c ${NLOPT_DIR}/src/util/nlopt-util.h ${NLOPT_DIR}/src/util/redblack.c ${NLOPT_DIR}/src/util/redblack.h ${NLOPT_DIR}/src/util/qsort_r.c ${NLOPT_DIR}/src/util/rescale.c
)

if(NLOPT_LUKSAN)
  list(APPEND NLOPT_SOURCES
    ${NLOPT_DIR}/src/algs/luksan/plis.c ${NLOPT_DIR}/src/algs/luksan/plip.c ${NLOPT_DIR}/src/algs/luksan/pnet.c ${NLOPT_DIR}/src/algs/luksan/mssubs.c ${NLOPT_DIR}/src/algs/luksan/pssubs.c ${NLOPT_DIR}/src/algs/luksan/luksan.h)
endif()


set_property(SOURCE ${NLOPT_DIR}/src/algs/bobyqa/bobyqa.c ${NLOPT_DIR}/src/algs/cdirect/hybrid.c ${NLOPT_DIR}/src/algs/mma/ccsa_quadratic.c ${NLOPT_DIR}/src/algs/cobyla/cobyla.c
                    ${NLOPT_DIR}/src/util/redblack.c ${NLOPT_DIR}/src/algs/neldermead/nldrmd.c ${NLOPT_DIR}/src/algs/newuoa/newuoa.c ${NLOPT_DIR}/src/util/qsort_r.c src/util/mt19937ar.c
             PROPERTY SKIP_UNITY_BUILD_INCLUSION ON)

# workaround for false positive in newuoa
if (CMAKE_C_COMPILER_ID MATCHES "GNU" AND CMAKE_C_COMPILER_VERSION VERSION_GREATER_EQUAL 12)
  set_source_files_properties(${NLOPT_DIR}/src/algs/newuoa/newuoa.c PROPERTIES COMPILE_FLAGS -U_FORTIFY_SOURCE)
endif ()

if (NLOPT_CXX)
  list (APPEND NLOPT_SOURCES
    ${NLOPT_DIR}/src/algs/stogo/global.cc
    ${NLOPT_DIR}/src/algs/stogo/linalg.cc
    ${NLOPT_DIR}/src/algs/stogo/local.cc
    ${NLOPT_DIR}/src/algs/stogo/stogo.cc
    ${NLOPT_DIR}/src/algs/stogo/tools.cc
    ${NLOPT_DIR}/src/algs/stogo/global.h
    ${NLOPT_DIR}/src/algs/stogo/linalg.h
    ${NLOPT_DIR}/src/algs/stogo/local.h
    ${NLOPT_DIR}/src/algs/stogo/stogo_config.h
    ${NLOPT_DIR}/src/algs/stogo/stogo.h
    ${NLOPT_DIR}/src/algs/stogo/tools.h
    ${NLOPT_DIR}/src/algs/ags/data_types.hpp
    ${NLOPT_DIR}/src/algs/ags/evolvent.hpp
    ${NLOPT_DIR}/src/algs/ags/evolvent.cc
    ${NLOPT_DIR}/src/algs/ags/solver.hpp
    ${NLOPT_DIR}/src/algs/ags/solver.cc
    ${NLOPT_DIR}/src/algs/ags/local_optimizer.hpp
    ${NLOPT_DIR}/src/algs/ags/local_optimizer.cc
    ${NLOPT_DIR}/src/algs/ags/ags.h
    ${NLOPT_DIR}/src/algs/ags/ags.cc)

set_property(SOURCE ${NLOPT_DIR}/src/algs/ags/solver.cc ${NLOPT_DIR}/src/algs/ags/local_optimizer.cc ${NLOPT_DIR}/src/algs/ags/ags.cc ${NLOPT_DIR}/src/algs/slsqp/slsqp.c
             PROPERTY SKIP_UNITY_BUILD_INCLUSION ON)
endif ()

#install (FILES ${NLOPT_HEADERS} DESTINATION ${NLOPT_INSTALL_INCLUDEDIR})

set (nlopt_lib nlopt)
add_library (${nlopt_lib} ${NLOPT_SOURCES})
add_dependencies(${nlopt_lib} generate-cpp)
if (NLOPT_LUKSAN)
  target_include_directories(${nlopt_lib} PRIVATE ${NLOPT_DIR}/src/algs/luksan)
  target_compile_definitions (${nlopt_lib} PRIVATE NLOPT_LUKSAN)
endif ()
target_link_libraries (${nlopt_lib} ${M_LIBRARY})
set_target_properties (${nlopt_lib} PROPERTIES SOVERSION ${SO_MAJOR})
set_target_properties (${nlopt_lib} PROPERTIES VERSION "${SO_MAJOR}.${SO_MINOR}.${SO_PATCH}")

#==============================================================================
# INCLUDE DIRECTORIES
#==============================================================================
target_include_directories (${nlopt_lib} PRIVATE
  ${PROJECT_BINARY_DIR}
  ${NLOPT_DIR}/src/algs/stogo
  ${NLOPT_DIR}/src/algs/ags
  ${NLOPT_DIR}/src/util
  ${NLOPT_DIR}/src/algs/direct
  ${NLOPT_DIR}/src/algs/cdirect
  ${NLOPT_DIR}/src/algs/praxis
  ${NLOPT_DIR}/src/algs/crs
  ${NLOPT_DIR}/src/algs/mlsl
  ${NLOPT_DIR}/src/algs/mma
  ${NLOPT_DIR}/src/algs/cobyla
  ${NLOPT_DIR}/src/algs/newuoa
  ${NLOPT_DIR}/src/algs/neldermead
  ${NLOPT_DIR}/src/algs/auglag
  ${NLOPT_DIR}/src/algs/bobyqa
  ${NLOPT_DIR}/src/algs/isres
  ${NLOPT_DIR}/src/algs/slsqp
  ${NLOPT_DIR}/src/algs/esch
  ${NLOPT_DIR}/src/api)

get_target_property (NLOPT_PRIVATE_INCLUDE_DIRS ${nlopt_lib} INCLUDE_DIRECTORIES)
#"$<INSTALL_INTERFACE:$<INSTALL_PREFIX>/${CMAKE_INSTALL_INCLUDEDIR}>"
target_include_directories (${nlopt_lib} INTERFACE "$<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/${NLOPT_DIR}/src/api;${PROJECT_BINARY_DIR}>")

if (BUILD_SHARED_LIBS)
  target_compile_definitions (${nlopt_lib} PUBLIC NLOPT_DLL)

  if (WIN32)
    # needed to switch between dllexport/dllimport
    target_compile_definitions (${nlopt_lib} PRIVATE NLOPT_DLL_EXPORT)
  endif ()
endif ()

# needed for the language plugins
set_target_properties (${nlopt_lib} PROPERTIES POSITION_INDEPENDENT_CODE ON)

# for consistent floating-point operations across architectures
option (DISABLE_FP_CONTRACT "Disable floating-point contractions" ON)
if (DISABLE_FP_CONTRACT AND CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
  set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -ffp-contract=off")
endif ()

# Compile nlopt as a static library
set(BUILD_SHARED_LIBS OFF CACHE INTERNAL "" FORCE)


# Enable tests only when building nlopt by itself
if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
	set(NLOPT_TESTS ON CACHE BOOL "" FORCE)
	add_executable(nlopt-test
		${PROJECT_SOURCE_DIR}/test/test.cpp
	)
	target_link_libraries(nlopt-test nlopt)
endif()


# Disable annoying warnings and enable parallel compilation
target_compile_options(nlopt 
	PRIVATE
		$<$<C_COMPILER_ID:MSVC>:/wd4244;/wd4267;/wd4146;/MP;/Qpar>
		$<$<C_COMPILER_ID:Intel>: $<$<PLATFORM_ID:Windwos>:/Qwd1478> $<$<NOT:$<PLATFORM_ID:Windows>>:-wd1478> >
		$<$<C_COMPILER_ID:GNU>:-Wno-deprecated-declarations -Wstringop-overflow=0>
		$<$<C_COMPILER_ID:AppleClang>:-Wno-deprecated-declarations>
		$<$<C_COMPILER_ID:Clang>:-Wno-deprecated-declarations>
)
if(NOT(MSVC))
	target_compile_options(nlopt
		PRIVATE
			$<$<CXX_COMPILER_ID:Intel>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
			$<$<CXX_COMPILER_ID:GNU>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
			$<$<CXX_COMPILER_ID:AppleClang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
			$<$<CXX_COMPILER_ID:Clang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
	)
endif()
if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
	target_compile_options(nlopt-test 
	PUBLIC
		$<$<C_COMPILER_ID:MSVC>:/wd4267>
	)
endif()