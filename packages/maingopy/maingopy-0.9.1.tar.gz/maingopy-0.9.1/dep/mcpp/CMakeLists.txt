cmake_minimum_required(VERSION 3.15 FATAL_ERROR)

message("Checking files for MC++.")
project(mcpp CXX)

add_library(mcpp INTERFACE)
target_include_directories(mcpp
	INTERFACE ${PROJECT_SOURCE_DIR}/src/mc
)
target_link_libraries(mcpp INTERFACE cpplapack fadbad filib)
target_compile_features(mcpp INTERFACE cxx_std_14)
target_compile_options(mcpp
	INTERFACE
		$<$<CXX_COMPILER_ID:Intel>: $<$<PLATFORM_ID:Windows>:/Qwd381;/Qwd858> $<$<NOT:$<PLATFORM_ID:Windows>>:-wd381,858> >
	)


if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)

	add_subdirectory(dep/filib)
	message("FILIB++ OK.")
	add_subdirectory(dep/fadbad)
	message("FADBAD++ OK.")
	add_subdirectory(dep/blas)
	message("BLAS OK.")
	add_subdirectory(dep/lapack)
	message("LAPACK OK.")
	add_subdirectory(dep/cpplapack)
	message("CPPLAPACK OK.")
	
	add_executable(mcpp-test
		${PROJECT_SOURCE_DIR}/test/test.cpp
	)
	target_link_libraries(mcpp-test mcpp)
	
	add_executable(mc-1d
		${PROJECT_SOURCE_DIR}/examples/MC-1D/main.cpp
	)
	target_link_libraries(mc-1d mcpp)
	
	add_executable(mc-2d
		${PROJECT_SOURCE_DIR}/examples/MC-2D/main.cpp
	)
	target_link_libraries(mc-2d mcpp)

endif()


