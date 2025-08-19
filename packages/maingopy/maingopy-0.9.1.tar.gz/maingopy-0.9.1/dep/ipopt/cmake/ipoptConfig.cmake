cmake_minimum_required(VERSION 3.8)

#project(IpoptConfig C CXX)


#include(FortranCInterface)

include(CheckIncludeFile)
include(CheckIncludeFileCXX)
include(CheckFunctionExists)
include(CheckSymbolExists)




#Fortran Name mangling in separate header
#FortranCInterface_HEADER(${CMAKE_CURRENT_SOURCE_DIR}/CFortranNameMangling.h)

check_include_file_CXX(cassert HAVE_CASSERT)
check_include_file_CXX(cctype HAVE_CCTYPE)
check_include_file_CXX(cfloat HAVE_CFLOAT)
check_include_file_CXX(cieeefp HAVE_CIEEEFP)
check_include_file_CXX(cmath HAVE_CMATH)
check_include_file_CXX(cstdarg HAVE_CSTDARG)
check_include_file_CXX(cstdio HAVE_CSTDIO)
check_include_file_CXX(cstdlib HAVE_CSTDLIB)
check_include_file_CXX(cstring HAVE_CSTRING)
check_include_file_CXX(ctime HAVE_CTIME)
check_include_file_CXX(cstddef HAVE_CSTDDEF)

check_include_file(stdlib.h HAVE_STDLIB_H)
check_include_file(stdint.h HAVE_STDINT_H)
check_include_file(stdio.h HAVE_STDIO_H)
check_include_file(stddef.h HAVE_STDDEF_H)
check_include_file(stdarg.h HAVE_STDARG_H)
check_include_file(strings.h HAVE_STRINGS_H)
check_include_file(string.h  HAVE_STRING_H)
check_include_file(time.h  HAVE_TIME_H)
check_include_file(sys/stat.h HAVE_SYS_STAT_H)
check_include_file(sys/types.h HAVE_SYS_TYPES_H)


check_include_file(dlfcn.h HAVE_DLFCN_H)
check_include_file(inttypes.h HAVE_INTTYPES_H)
check_include_file(windows.h HAVE_WINDOWS_H)
check_include_file(unistd.h HAVE_UNISTD_H)
check_include_file(float.h HAVE_FLOAT_H)
check_include_file(ieeefp.h HAVE_IEEEFP_H)

check_include_file(memory.h HAVE_MEMORY_H)


#check functions
check_function_exists(finite HAVE_FINITE)
check_function_exists(_finite HAVE_UNDERSCORE_FINITE)
check_function_exists(drand48 HAVE_DRAND48)
check_function_exists(std::rand HAVE_STD__RAND)
check_function_exists(rand HAVE_RAND)
check_function_exists(va_copy HAVE_VA_COPY)
check_symbol_exists(snprintf stdio.h HAVE_SNPRINTF)
check_function_exists(vsnprintf HAVE_VSNPRINTF)
check_function_exists(_snprintf HAVE__SNPRINTF)
check_function_exists(_vsnprintf HAVE__VSNPRINTF)


set(IPOPT_CONFIG_INCLUDE ${CMAKE_CURRENT_BINARY_DIR}/IpoptConfig/include/)
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/config.h.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/IpoptConfig/include/config.h.cmake
)
# compare with the real version file
execute_process(
    COMMAND
			${CMAKE_COMMAND} -E compare_files
			${CMAKE_CURRENT_BINARY_DIR}/IpoptConfig/include/config.h.cmake
			${CMAKE_CURRENT_BINARY_DIR}/IpoptConfig/include/config.h
    RESULT_VARIABLE
        VERSION_NEEDS_UPDATING
    OUTPUT_QUIET
    ERROR_QUIET
)
# update the real version file if necessary
if(VERSION_NEEDS_UPDATING)
    execute_process(
        COMMAND
            ${CMAKE_COMMAND} -E copy
			${CMAKE_CURRENT_BINARY_DIR}/IpoptConfig/include/config.h.cmake
			${CMAKE_CURRENT_BINARY_DIR}/IpoptConfig/include/config.h
    )
endif()

configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/config_ipopt.h.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/IpoptConfig/include/config_ipopt.h.cmake
)
# compare with the real version file
execute_process(
    COMMAND
			${CMAKE_COMMAND} -E compare_files
			${CMAKE_CURRENT_BINARY_DIR}/IpoptConfig/include/config_ipopt.h.cmake
			${CMAKE_CURRENT_BINARY_DIR}/IpoptConfig/include/config_ipopt.h
    RESULT_VARIABLE
        VERSION_NEEDS_UPDATING
    OUTPUT_QUIET
    ERROR_QUIET
)
# update the real version file if necessary
if(VERSION_NEEDS_UPDATING)
    execute_process(
        COMMAND
            ${CMAKE_COMMAND} -E copy
			${CMAKE_CURRENT_BINARY_DIR}/IpoptConfig/include/config_ipopt.h.cmake
			${CMAKE_CURRENT_BINARY_DIR}/IpoptConfig/include/config_ipopt.h
    )
endif()
