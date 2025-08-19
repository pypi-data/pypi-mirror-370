cmake_minimum_required(VERSION 3.15 FATAL_ERROR)

project(melon CXX)

set(MeLOn_build_python_interface FALSE CACHE BOOL "Build the Python extension module 'melonpy' that allows to call MeLOn from Python.")
if(MeLOn_build_python_interface)
	set(CMAKE_POSITION_INDEPENDENT_CODE ON)
endif()

add_library(melon INTERFACE)
target_link_libraries(melon INTERFACE gp multifidelityGP ffnet svm convexhull)

add_subdirectory("feedforward neural network/model")
message("ffNet done.")
add_subdirectory("gaussian process/model")
message("GP done.")
add_subdirectory("multifidelity gaussian process/model")
message("MultifidelityGP done.")
add_subdirectory("support vector machine/model")
message("SVM done.")
add_subdirectory("convex hull/model")
message("ConvexHull done.")

add_subdirectory("common")

set(JSON_BuildTests OFF CACHE INTERNAL "")


if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)

	# Get further dependencies - needed for exchanging data (json) and for constructing relaxations (the rest)
	function(add_dependency_subdir DEPENDENCY)
		if(EXISTS ${PROJECT_SOURCE_DIR}/dep/${DEPENDENCY}/CMakeLists.txt)
			add_subdirectory(${PROJECT_SOURCE_DIR}/dep/${DEPENDENCY})
			message("${DEPENDENCY} done.")
		else()
			message(FATAL_ERROR "Error: Could not find CMakeLists.txt at ${PROJECT_SOURCE_DIR}/dep/${DEPENDENCY}. Did you initialize and update all submodules (cf. Readme.md)?")
		endif()
	endfunction(add_dependency_subdir DEPENDENCY)
	add_dependency_subdir(json)
	add_dependency_subdir(tinyxml2)
	add_dependency_subdir(mcpp)
	add_dependency_subdir(filib)
	add_dependency_subdir(fadbad)
	add_dependency_subdir(blas)
	add_dependency_subdir(lapack)
	add_dependency_subdir(cpplapack)

	# Add python interface
	if(MeLOn_build_python_interface)
        set(PYBIND11_FINDPYTHON FALSE CACHE BOOL "Whether to have pybind11 use FindPython")
        if(SKBUILD)
            set(Python_EXECUTABLE ${PYTHON_EXECUTABLE})
            set(Python_VERSION ${PYTHON_VERSION_STRING})
            set(Python_INCLUDE_DIRS ${PYTHON_INCLUDE_DIR})
            set(Python_LIBRARIES ${PYTHON_LIBRARY})
        endif()
		add_dependency_subdir(pybind11)
	endif()

	# Test executable using doubles for GPs
	add_executable(gp-test
		"${PROJECT_SOURCE_DIR}/gaussian process/model/test/test.cpp"
	)
	target_link_libraries(gp-test gp)
	set_target_properties(gp-test PROPERTIES CXX_STANDARD 17)

	# Test executable for multifidelity Gaussian processes
	add_executable(multifidelityGP-test
		"${PROJECT_SOURCE_DIR}/multifidelity gaussian process/model/test/test.cpp"
	)
	target_link_libraries(multifidelityGP-test multifidelityGP)
	set_target_properties(multifidelityGP-test PROPERTIES CXX_STANDARD 17)

	# Test executable for ANNs
	add_executable(feedforwardnet-test
		"${PROJECT_SOURCE_DIR}/feedforward neural network/model/test/test.cpp"
	)
	target_link_libraries(feedforwardnet-test ffnet)
	set_target_properties(feedforwardnet-test PROPERTIES CXX_STANDARD 17)

	# Test executable for ConvexHull
	add_executable(convexhull-test
		"${PROJECT_SOURCE_DIR}/convex hull/model/test/test.cpp"
	)
	target_link_libraries(convexhull-test convexhull)
	set_target_properties(convexhull-test PROPERTIES CXX_STANDARD 17)

	# Test executable for SVM
	add_executable(svm-test
		"${PROJECT_SOURCE_DIR}/support vector machine/model/test/test.cpp"
	)
	target_link_libraries(svm-test svm)
	set_target_properties(svm-test PROPERTIES CXX_STANDARD 17)

	# TODO: Copy network to build folder (following solution not quite working)
	#add_custom_target(copyNetworks ALL COMMAND ${CMAKE_COMMAND} -E copy_directory "${PROJECT_SOURCE_DIR}/feedforward neural network/model/test/networks/"  $<$<CONFIG:Debug>:${CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG}/networks/>$<$<NOT:$<CONFIG:Debug>>:${CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE}/networks/>)
	#add_dependencies(feedforwardnet-test copyNetworks)

endif()


# --------------- Python interface ---------------------------
if(MeLOn_build_python_interface)

    # Create target for melonpy extension module
    pybind11_add_module(melonpy common/src/melonpy.cpp)
    target_compile_features(melonpy PRIVATE cxx_std_14)
    target_link_libraries(melonpy PRIVATE melon mcpp)
    target_compile_options(melonpy PRIVATE $<$<CXX_COMPILER_ID:AppleClang>: -fvisibility=default>)

endif()
