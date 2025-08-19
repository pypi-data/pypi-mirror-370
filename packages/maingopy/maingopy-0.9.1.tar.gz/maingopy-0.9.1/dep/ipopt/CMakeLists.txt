cmake_minimum_required(VERSION 3.15 FATAL_ERROR)

message("Checking files for IPOPT.")
project(ipopt C CXX)


set(IPOPT_SRCDIR ${CMAKE_CURRENT_SOURCE_DIR}/Ipopt-3.12.12/Ipopt/src)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/ipoptConfig.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/ipoptCommonCSources.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/ipoptInterfacesCSources.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/ipoptLinAlgCSources.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/ipoptContribCSources.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/ipoptAlgorithmCSources.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/ipoptAlgorithmInexactCSources.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/ipoptAlgorithmLinSolvCSources.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/ipoptAlgorithmLinSolvFSources.cmake)
set(IPOPT_C_SOURCES
    ${IPOPT_COMMON_C_SOURCES}
    ${IPOPT_INTERFACES_C_SOURCES}
    ${IPOPT_LINALG_C_SOURCES}
    ${IPOPT_CONTRIB_C_SOURCES}
    ${IPOPT_ALGORITHM_C_SOURCES}
    ${IPOPT_ALGORITHM_INEXACT_C_SOURCES}
    ${IPOPT_ALGORITHM_LINSOLV_C_SOURCES}
    )
set(IPOPT_C_HEADER
    ${IPOPT_COMMON_C_HEADER}
    ${IPOPT_INTERFACES_C_HEADER}
    ${IPOPT_LINALG_C_HEADER}
    ${IPOPT_CONTRIB_C_HEADER}
    ${IPOPT_ALGORITHM_C_HEADER}
    ${IPOPT_ALGORITHM_INEXACT_C_HEADER}
    ${IPOPT_ALGORITHM_LINSOLV_C_HEADER}
    )
set(IPOPT_DIR_LIST  ${IPOPT_SRCDIR}/Algorithm
                    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers
                    ${IPOPT_SRCDIR}/Algorithm/Inexact
                    ${IPOPT_SRCDIR}/contrib/CGPenalty
                    ${IPOPT_SRCDIR}/contrib/LinearSolverLoader
                    ${IPOPT_SRCDIR}/Interfaces
                    ${IPOPT_SRCDIR}/Common
                    ${IPOPT_SRCDIR}/LinAlg
                    ${IPOPT_SRCDIR}/Apps/AmplSolver
                    ${IPOPT_SRCDIR}/LinAlg/TMatrices
                    ${IPOPT_SRCDIR}/Config
    )

add_library(ipopt STATIC ${IPOPT_C_SOURCES})
if(BUILD_SHARED_LIBS)
    set_target_properties(ipopt PROPERTIES POSITION_INDEPENDENT_CODE ON)
endif()
target_include_directories(ipopt PUBLIC ${IPOPT_DIR_LIST} ${IPOPT_CONFIG_INCLUDE})
# Turn off warnings and turn on optimization and parallel compilation
target_compile_options(ipopt 
	PUBLIC
		$<$<C_COMPILER_ID:MSVC>: /wd4996>
		$<$<C_COMPILER_ID:AppleClang>: -Wno-deprecated-declarations>
    )
if(MSVC)
    target_compile_options(ipopt 
        PRIVATE
            $<$<C_COMPILER_ID:MSVC>: /MP;/Qpar>
        )
else()
	target_compile_options(ipopt 
		PRIVATE
			$<$<CXX_COMPILER_ID:Intel>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
			$<$<CXX_COMPILER_ID:GNU>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
			$<$<CXX_COMPILER_ID:AppleClang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
	)
endif()
target_compile_definitions(ipopt
    PRIVATE 
        HAVE_CONFIG_H
        IPOPT_BUILD
        COIN_USE_MUMPS_MPI_H
        $<$<C_COMPILER_ID:MSVC>:_CRT_SECURE_NO_WARNINGS>
    )
target_link_libraries(ipopt  
	PRIVATE
		mumps
		blas
		lapack
    )

if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)

	# Add dependencies
	add_subdirectory(dep/blas)
	message("BLAS OK.")
	add_subdirectory(dep/lapack)
	message("LAPACK OK.")
	add_subdirectory(dep/mumps)
	message("MUMPS OK.")

    if( (NOT BLAS_usePrecompiledDll) OR (NOT LAPACK_usePrecompiledDlls) OR (NOT MUMPS_usePrecompiledDll) )
        enable_language(Fortran)
    endif()

	# Test executables, the test ist an example problem from the Ipopt-3.12.12
	add_executable(ipopt-test
		${PROJECT_SOURCE_DIR}/test/hs071_main.cpp
		${PROJECT_SOURCE_DIR}/test/hs071_nlp.cpp
	)
	target_link_libraries(ipopt-test ipopt)
	
endif()