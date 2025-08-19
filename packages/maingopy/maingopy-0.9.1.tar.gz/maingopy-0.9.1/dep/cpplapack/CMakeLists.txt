cmake_minimum_required(VERSION 3.8 FATAL_ERROR)

message("Checking files for CPPLAPACK.")
project(cpplapack CXX)


add_library(cpplapack INTERFACE)
target_include_directories(cpplapack
	INTERFACE ${PROJECT_SOURCE_DIR}/cpplapack-r198/include
    )
target_compile_options(cpplapack
	INTERFACE
        $<$<CXX_COMPILER_ID:Intel>:-wd1478>
        $<$<CXX_COMPILER_ID:MSVC>:/wd4267;/wd4244;/wd4190>
        $<$<CXX_COMPILER_ID:AppleClang>:-Wno-return-type-c-linkage>
        $<$<CXX_COMPILER_ID:Clang>:-Wno-return-type-c-linkage>
    )

target_link_libraries(cpplapack INTERFACE blas lapack)


if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)

	# Include dependencies
	add_subdirectory(dep/blas)
	message("BLAS OK.")
	add_subdirectory(dep/lapack)
	message("LAPACK OK.")

	# Test executables
	add_executable(cpplapack-test
		${PROJECT_SOURCE_DIR}/cpplapack-r198/test/double/main.cpp
	)
	target_link_libraries(cpplapack-test cpplapack)

endif()