set(CMAKE_SYSTEM_VERSION 10.0)
cmake_minimum_required(VERSION 3.15)

include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/MAiNGOversion.cmake)
project(MAiNGO
    VERSION ${MAiNGO_VERSION}
    LANGUAGES CXX)


#--------------------------- Settings --------------------------------
set(MAiNGO_use_melon TRUE CACHE BOOL "Build MAiNGO executable with the MeLOn toolbox.")
set(MAiNGO_use_cplex TRUE CACHE BOOL "Use CPLEX if it is available on the system.")
set(MAiNGO_use_gurobi TRUE CACHE BOOL "Use Gurobi if it is available on the system.")
set(MAiNGO_use_knitro TRUE CACHE BOOL "Use KNITRO if it is available on the system.")
set(MAiNGO_use_mpi FALSE CACHE BOOL "Build parallel version of MAiNGO.")
set(MAiNGO_use_growing_datasets FALSE CACHE BOOL "Build MAiNGO with growing datasets for solving parameter estimation problems.")
set(MAiNGO_use_openmp FALSE CACHE BOOL "Use OpenMP for parallelelization of embarassingly parallel loops.")
set(MAiNGO_build_python_interface FALSE CACHE BOOL "Build the Python package 'maingopy' that allows to call MAiNGO from Python.")
set(MAiNGO_build_standalone FALSE CACHE BOOL "Build MAiNGOcpp executable as standalone solver with problem.h.")
set(MAiNGO_build_shared_c_api FALSE CACHE BOOL "Build library version of MAiNGO with parser callable from C.")
set(MAiNGO_use_gcov FALSE CACHE BOOL "Instrument the code for code coverage with gcov (only for compatible compilers)")
set(MAiNGO_use_CUDA FALSE CACHE BOOL "Enable CUDA.")
if(MAiNGO_use_CUDA)
    include(CheckLanguage)
    check_language(CUDA)
    if(CMAKE_CUDA_COMPILER)
        enable_language(CUDA)
        set(HAVE_CUDA_TOOLKIT TRUE) 
        message(STATUS "CUDA compiler was found! Build GPU parallel subdomain lowerbounding solver.")
    else()
        message(STATUS "CUDA compiler was not found! Build CPU serial subdomain lowerbounding solver.")
    endif()    
endif()
if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
    set(MAiNGO_build_parser TRUE CACHE BOOL "Build MAiNGO executable with parser.")
    set(MAiNGO_build_test TRUE CACHE BOOL "Build MAiNGO test cases.")
else()
    set(MAiNGO_build_parser FALSE CACHE BOOL "Build MAiNGO executable with parser.")
    set(MAiNGO_build_test FALSE CACHE BOOL "Build MAiNGO test cases.")
endif()


#------------------------ Adjust settings when building with scikit-build -----------------------------
if(SKBUILD)
    message(STATUS "The project is built using scikit-build, also building Python interface.")
    # Enforce use of Python interface
    set(MAiNGO_build_python_interface TRUE CACHE INTERNAL "" FORCE)
    # Default: disable use of CPLEX and KNITRO
    message(STATUS "Not using CPLEX, Gurobi, and KNITRO even if they are available. If you still want to use them, you need to explicitly enable the corresponding CMake options.")
    set(MAiNGO_use_cplex FALSE CACHE BOOL "Use CPLEX if it is available on the system." FORCE)
    set(MAiNGO_use_gurobi FALSE CACHE BOOL "Use Gurobi if it is available on the system." FORCE)
    set(MAiNGO_use_knitro FALSE CACHE BOOL "Use KNITRO if it is available on the system." FORCE)
    # Disable stuff that is not compatible with the Python package to be installed
    set(MAiNGO_use_mpi FALSE CACHE INTERNAL "" FORCE)
    set(MAiNGO_use_growing_datasets FALSE CACHE INTERNAL "" FORCE)
    set(MAiNGO_build_standalone FALSE CACHE INTERNAL "" FORCE)
    set(MAiNGO_build_parser FALSE CACHE INTERNAL "" FORCE)
    set(MAiNGO_build_test FALSE CACHE INTERNAL "" FORCE)
    set(BLAS_usePrecompiledDll FALSE CACHE INTERNAL "" FORCE)
    set(LAPACK_usePrecompiledDlls FALSE CACHE INTERNAL "" FORCE)
    set(MUMPS_usePrecompiledDll FALSE CACHE INTERNAL "" FORCE)
    # Force required settings
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
    set(BUILD_SHARED_LIBS FALSE CACHE INTERNAL "" FORCE)
endif()
if(MAiNGO_build_python_interface OR MAiNGO_build_shared_c_api)
    # if building the python interface, the generated module needs PIC, even if building static libraries
    set(CMAKE_POSITION_INDEPENDENT_CODE ON)
endif()


#------------------------ MAiNGO library -----------------------------
include(${PROJECT_SOURCE_DIR}/cmake/MAiNGOsourceFiles.cmake)
add_library(maingo-core ${MAiNGO_SRC})
if(WIN32 AND BUILD_SHARED_LIBS)
    set_target_properties(maingo-core PRIVATE WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

configure_file(${PROJECT_SOURCE_DIR}/inc/version.h.in maingo-core/version.h)
target_include_directories(maingo-core
    PUBLIC
        ${PROJECT_SOURCE_DIR}/inc
    PRIVATE
        ${CMAKE_CURRENT_BINARY_DIR}/maingo-core
    )

target_compile_features(maingo-core PRIVATE cxx_std_14)
if(MSVC)
    target_compile_options(maingo-core PRIVATE /MP;/Qpar)
else()
    target_compile_options(maingo-core
        PRIVATE
            $<$<CXX_COMPILER_ID:Intel>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
            $<$<CXX_COMPILER_ID:GNU>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
            $<$<CXX_COMPILER_ID:AppleClang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
            $<$<CXX_COMPILER_ID:Clang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
        )
endif()

if(MAiNGO_use_cplex)
    # cplex has to be linked first, since on Linux/MacOS, it comes as a static library that contains BLAS etc.
    # if linking it after our blas, this will result in multiply defined symbols
    target_link_libraries(maingo-core PUBLIC cplex)
endif()
target_link_libraries(maingo-core
    PUBLIC
        babbase
        mcpp
    PRIVATE
        filib
        mumps
        nlopt
        ipopt
        clp
    )
if(HAVE_CUDA_TOOLKIT)   
    if(NOT DEFINED CMAKE_CUDA_ARCHITECTURES)
        set(CMAKE_CUDA_ARCHITECTURES native)
    endif()    
    set_target_properties(maingo-core
        PROPERTIES 
            CUDA_ARCHITECTURES ${CMAKE_CUDA_ARCHITECTURES}
            CUDA_SEPARABLE_COMPILATION ON
    )
    target_compile_definitions(maingo-core PUBLIC CUDA_INSTALLED)
    target_link_libraries(maingo-core PRIVATE cuSubintervalArithmetic)
else()
    # If CUDA is not available, the CPU-serival version of the Subdomain Lower Bounding solver will be compiled.
    target_link_libraries(maingo-core PRIVATE 
        dag
        subintervalArithmetic
    )
endif()

if(MAiNGO_build_parser OR MAiNGO_build_shared_c_api)
    add_library(parser STATIC ${PARSER_SRC})
    target_include_directories(parser PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/inc)
    target_link_libraries(parser PUBLIC ale babbase mcpp)
    target_compile_features(parser PRIVATE cxx_std_17)
    target_link_libraries(maingo-core PUBLIC parser)
    target_compile_definitions(maingo-core PUBLIC HAVE_MAiNGO_PARSER)
endif()
if(MAiNGO_use_melon)
    target_link_libraries(maingo-core PUBLIC melon)
endif()
if(MAiNGO_use_gurobi)
    target_link_libraries(maingo-core PRIVATE gurobi)
endif()
if(MAiNGO_use_knitro)
    # knitro always needs to be linked after all other math-related libraries because of incompatibility with several math routines
    target_link_libraries(maingo-core PUBLIC knitro)
endif()
if(MAiNGO_use_mpi)
    find_package(MPI REQUIRED QUIET)
    message("Found MPI. Run MAiNGO with MPI like this: ${MPIEXEC} ${MPIEXEC_NUMPROC_FLAG} ${MPIEXEC_MAX_NUMPROCS} ${MPIEXEC_PREFLAGS} <yourMAiNGOexecutable> ${MPIEXEC_POSTFLAGS} <yourCommandLineArguments>")
    target_compile_definitions(maingo-core PUBLIC HAVE_MAiNGO_MPI) # Define pre-processor variable HAVE_MAiNGO_MPI
    target_link_libraries(maingo-core PUBLIC MPI::MPI_CXX)
endif()
if(MAiNGO_use_growing_datasets)
    message("Growing datasets will be used. See documentation for changes in model setup.")
    target_compile_definitions(maingo-core PUBLIC HAVE_GROWING_DATASETS) # Define pre-processor variable HAVE_GROWING_DATASETS
endif()
if(MAiNGO_use_gcov)
    # Enable coverage report with gcov only for compilers that support it
    target_compile_options(maingo-core PRIVATE
                            $<$<CXX_COMPILER_ID:GNU>:--coverage>
                            $<$<CXX_COMPILER_ID:AppleClang>:--coverage>
                            $<$<CXX_COMPILER_ID:Clang>:--coverage>
                           )
    target_link_options(maingo-core PUBLIC
                            $<$<CXX_COMPILER_ID:GNU>:--coverage>
                            $<$<CXX_COMPILER_ID:AppleClang>:--coverage>
                            $<$<CXX_COMPILER_ID:Clang>:--coverage>
                       )
endif()
if(MAiNGO_use_openmp)
    if(APPLE)
        if(CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang")
            # AppleClang Version 15.0.0 may be required!
            # AppleClang does not support OpenMP out of the box.
            # We tested with the libomp, provided by brew.
            set(OpenMP_CXX "${CMAKE_CXX_COMPILER}" CACHE STRING "" FORCE)
            set(OpenMP_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Xpreprocessor -fopenmp")
            set(OpenMP_CXX_LIB_NAMES "omp")
            set(OpenMP_omp_LIBRARY omp)
        endif()
    endif()
    find_package(OpenMP REQUIRED QUIET)
    message("Found OpenMP. Will parallelize embarrassingly parrallel for loops.")
    target_link_libraries(maingo-core PUBLIC OpenMP::OpenMP_CXX)
endif()

#----------------- If this is the top level, include dependencies  --------------------
if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)

    # --------------- Dependencies ---------------------------
    message("=================================================================")
    message("=================================================================")
    message("Configure dependencies...")
    message("=================================================================")
    include(${PROJECT_SOURCE_DIR}/cmake/addDependency.cmake)
    add_dependency_subdir(babbase)
    if(MAiNGO_use_growing_datasets)
        target_compile_definitions(babbase PUBLIC BABBASE_HAVE_GROWING_DATASETS) # Pass pre-processor variable to babbase
    endif()
    add_dependency_subdir(fadbad)
    add_dependency_subdir(blas)
    add_dependency_subdir(lapack)
    add_dependency_subdir(cpplapack)
    add_dependency_subdir(mcpp)
    add_dependency_subdir(mumps)
    add_dependency_subdir(ipopt)
    add_dependency_subdir(nlopt)
    add_dependency_subdir(clp)
    add_dependency_subdir(filib)
    if(MAiNGO_build_parser OR MAiNGO_build_shared_c_api)
        add_dependency_subdir(libale)
    endif()
    if(HAVE_CUDA_TOOLKIT)
        # If use CUDA, then add cuSubintervalArithmetic to the library
        add_dependency_subdir(cuSubintervalArithmetic)
        # The dependencies of cuSubintervalArithmetic library
        add_dependency_subdir(cuinterval)
        add_dependency_subdir(cutangent)
    else()
        # Otherwise add the SVT_Dag and subintervalArithmetic libraries
        add_dependency_subdir(dag)    
        add_dependency_subdir(subintervalArithmetic)
    endif()
    if(MAiNGO_use_cplex)
        add_dependency_subdir(cplex)
    endif()
    if(MAiNGO_use_gurobi)
        add_dependency_subdir(gurobi)
    endif()
    if(MAiNGO_use_knitro)
        add_dependency_subdir(knitro)
    endif()
    if(MAiNGO_build_python_interface)
        set(PYBIND11_FINDPYTHON FALSE CACHE BOOL "Whether to have pybind11 use FindPython")
        if(SKBUILD)
            set(Python_EXECUTABLE ${PYTHON_EXECUTABLE})
            set(Python_VERSION ${PYTHON_VERSION_STRING})
            set(Python_INCLUDE_DIRS ${PYTHON_INCLUDE_DIR})
            set(Python_LIBRARIES ${PYTHON_LIBRARY})
        endif()
        add_dependency_subdir(pybind11)
    endif()
    if(MAiNGO_use_melon) # Melon needs to go after pybind11, since it's CMakeLists.txt need pybind11_add_module if using the Python interface of MeLOn
        if(MAiNGO_build_python_interface)
            set(MeLOn_build_python_interface TRUE CACHE BOOL "" FORCE)
        endif()
        add_dependency_subdir(melon)
        add_dependency_subdir(json)
        add_dependency_subdir(tinyxml2)
    endif()
    if(MAiNGO_build_test)
        set(INSTALL_GTEST FALSE CACHE INTERNAL "")
        set(BUILD_GMOCK FALSE CACHE INTERNAL "")
        set(gmock_build_tests FALSE CACHE INTERNAL "")
        add_dependency_subdir(googletest)
    endif()
    message("Done configuring dependencies.")
    message("=================================================================")
    message("=================================================================")

    if( (NOT BLAS_usePrecompiledDll) OR (NOT LAPACK_usePrecompiledDlls) OR (NOT MUMPS_usePrecompiledDll) )
        enable_language(Fortran)
    endif()

    # --------- Setup the Executable/.dll output Directory -------------
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR} CACHE PATH "Single Directory for all Executables.")

endif()


# --------------- MAiNGO executable (using ALE parser) ---------------------------
if (MAiNGO_build_parser)

    add_executable(MAiNGO ${PROJECT_SOURCE_DIR}/examples/mainAleParser.cpp)
    target_link_libraries(MAiNGO PRIVATE maingo-core)
    target_compile_features(MAiNGO PRIVATE cxx_std_17)
    if(MSVC)
        target_compile_options(MAiNGO PRIVATE /MP;/Qpar)
        set_target_properties(MAiNGO PROPERTIES LINK_FLAGS /ignore:4099) #/ignore:4099 disables annoying linker warning because cplex does not provide debugging information
    else()
        target_compile_options(MAiNGO
            PRIVATE
                $<$<CXX_COMPILER_ID:Intel>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<CXX_COMPILER_ID:GNU>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<CXX_COMPILER_ID:AppleClang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<CXX_COMPILER_ID:Clang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
            )
    endif()

endif()


# --------------- Standalone MAiNGO executable (for C++ API) ---------------------------
if (MAiNGO_build_standalone)

    add_executable(MAiNGOcpp ${PROJECT_SOURCE_DIR}/examples/mainCppApi.cpp)
    target_link_libraries(MAiNGOcpp PRIVATE maingo-core)
    target_compile_features(MAiNGOcpp PRIVATE cxx_std_14)
    if(MSVC)
        target_compile_options(MAiNGOcpp PRIVATE /MP;/Qpar)
        set_target_properties(MAiNGOcpp PROPERTIES LINK_FLAGS /ignore:4099) #/ignore:4099 disables annoying linker warning because cplex does not provide debugging information
    else()
        target_compile_options(MAiNGOcpp
            PRIVATE
                $<$<CXX_COMPILER_ID:Intel>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<CXX_COMPILER_ID:GNU>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<CXX_COMPILER_ID:AppleClang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<CXX_COMPILER_ID:Clang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
            )
    endif()

endif()


# --------------- Shared library for MAiNGO including parser callable from C ---------------------------
if (MAiNGO_build_shared_c_api)
    # To build shared libraries in Windows, we set CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS to TRUE.
    # See https://cmake.org/cmake/help/v3.4/variable/CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS.html
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
    add_library(maingo-c-api SHARED
        ${PROJECT_SOURCE_DIR}/src/cApi.cpp
    )
    target_link_libraries(maingo-c-api maingo-core parser)
    set_target_properties(maingo-c-api PROPERTIES CXX_STANDARD 17)
    set_target_properties(maingo-c-api PROPERTIES POSITION_INDEPENDENT_CODE ON)
    set_target_properties(maingo-c-api PROPERTIES PUBLIC_HEADER ${PROJECT_SOURCE_DIR}/inc/cApi.h)

    if(NOT(MSVC))
        target_compile_options(maingo-c-api
            PRIVATE
                $<$<CXX_COMPILER_ID:Intel>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<CXX_COMPILER_ID:GNU>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<CXX_COMPILER_ID:AppleClang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<CXX_COMPILER_ID:Clang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
        )
    else()
        set_target_properties(maingo-c-api PROPERTIES LINK_FLAGS /ignore:4099) #/ignore:4099 disables annoying linker warning because cplex does not provide debugging information
    endif()

endif()


# --------------- Python interface ---------------------------
if(MAiNGO_build_python_interface)

    # Get output directories right
    if(MSVC)
        set(RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_BINARY_DIR}/Debug)
        set(RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR}/Release)
    else()
        set(RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_BINARY_DIR})
        set(RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR})
    endif()

    # Create target for _maingopy extension module
    pybind11_add_module(_maingopy maingopy/_maingopy.cpp)
    target_compile_features(_maingopy PRIVATE cxx_std_14)
    target_link_libraries(_maingopy PRIVATE maingo-core)
    target_compile_options(_maingopy PRIVATE $<$<CXX_COMPILER_ID:AppleClang>: -fvisibility=default>)

    # Create target for maingopy package
    if(SKBUILD)
        install(TARGETS maingo-core DESTINATION . )
        install(TARGETS _maingopy DESTINATION .)
        if(MAiNGO_use_melon AND MeLOn_build_python_interface)
            install(TARGETS melonpy DESTINATION .)
            install(FILES ${PROJECT_SOURCE_DIR}/maingopy/__init__maingopy_and_melonpy.py.in DESTINATION . RENAME __init__.py)
        else()
        endif()
    else()
        set_target_properties(_maingopy PROPERTIES
            LIBRARY_OUTPUT_DIRECTORY $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}>/maingopy
            ARCHIVE_OUTPUT_DIRECTORY $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}>/maingopy
            )
        if(MAiNGO_use_melon AND MeLOn_build_python_interface)
            set_target_properties(melonpy PROPERTIES
                LIBRARY_OUTPUT_DIRECTORY $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}>/maingopy
                ARCHIVE_OUTPUT_DIRECTORY $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}>/maingopy
                )
            add_custom_target(maingopy ALL
                COMMAND ${CMAKE_COMMAND} -E make_directory
                    $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}>/maingopy
                COMMAND ${CMAKE_COMMAND} -E copy
                    ${PROJECT_SOURCE_DIR}/maingopy/__init__maingopy_and_melonpy.py.in
                    $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}>/maingopy/__init__.py
                )
            add_dependencies(melonpy maingopy)
            add_dependencies(_maingopy maingopy)
        else()
            add_custom_target(maingopy ALL
                COMMAND ${CMAKE_COMMAND} -E make_directory
                    $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}>/maingopy
                COMMAND ${CMAKE_COMMAND} -E copy
                    ${PROJECT_SOURCE_DIR}/maingopy/__init__only_maingopy.py.in
                    $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}>/maingopy/__init__.py
                )
            add_dependencies(_maingopy maingopy)
        endif()
        if(BLAS_usePrecompiledDll)
            add_custom_target(copyBlasDllmaingopy ALL
                COMMAND ${CMAKE_COMMAND} -E copy
                    $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}/blasd.dll>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}/blas.dll>
                    $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}/maingopy/blasd.dll>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}/maingopy/blas.dll>)
            add_dependencies(copyBlasDllmaingopy copyBlasDll)
            if(MAiNGO_use_melon)
                add_dependencies(copyBlasDllmaingopy melonpy)
            endif()
        endif()
        if(LAPACK_usePrecompiledDlls)
            add_custom_target(copyLapackDllmaingopy ALL
                COMMAND ${CMAKE_COMMAND} -E copy
                    $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}/lapackd.dll>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}/lapack.dll>
                    $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}/maingopy/lapackd.dll>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}/maingopy/lapack.dll>)
            add_dependencies(copyLapackDllmaingopy copyLapackDll)
            if(MAiNGO_use_melon)
                add_dependencies(copyLapackDllmaingopy melonpy)
            endif()
        endif()
        if(MUMPS_usePrecompiledDll)
            add_custom_target(copyMumpsDllmaingopy ALL
                COMMAND ${CMAKE_COMMAND} -E copy
                    $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}/mumpsd.dll>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}/mumps.dll>
                    $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}/maingopy/mumpsd.dll>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}/maingopy/mumps.dll>)
            add_dependencies(copyMumpsDllmaingopy copyMumpsDll)
            if(MAiNGO_use_melon)
                add_dependencies(copyMumpsDllmaingopy melonpy)
            endif()
        endif()
    endif()

endif()


# --------------- MAiNGO Tests ---------------------------
if(MAiNGO_build_test)

    # Test MAiNGO by solving a number of test problems
    add_executable(maingo-test-problems ${PROJECT_SOURCE_DIR}/tests/testProblems/main.cpp)
    target_link_libraries(maingo-test-problems PRIVATE maingo-core)
    target_compile_features(maingo-test-problems PRIVATE cxx_std_17)
    if(MSVC)
        target_compile_options(maingo-test-problems PRIVATE /MP;/Qpar)
        set_target_properties(maingo-test-problems PROPERTIES LINK_FLAGS /ignore:4099) #/ignore:4099 disables annoying linker warning because cplex does not provide debugging information
    else()
        target_compile_options(maingo-test-problems
            PRIVATE
                $<$<CXX_COMPILER_ID:Intel>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<CXX_COMPILER_ID:GNU>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<CXX_COMPILER_ID:AppleClang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<CXX_COMPILER_ID:Clang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
            )
    endif()
    if(MAiNGO_use_cplex)
        # Additionally linking cplex-available (part of the cplex target). This is merely to provide information whether the current MAiNGO build actually has CPLEX.
        # This is required since some test problems are only run if a dedicated MILP or QP solver is available.
        target_link_libraries(maingo-test-problems PRIVATE cplex-available)
    elseif(MAiNGO_use_gurobi)
        # Gurobi may also be used as an alternative to CPLEX.
        target_link_libraries(maingo-test-problems PRIVATE gurobi-available)
    endif()
    # Unit tests of MAiNGO
    add_executable(unit-test-maingo ${MAiNGO_UNIT_TEST_SRC})
    target_include_directories(unit-test-maingo PRIVATE ${PROJECT_SOURCE_DIR}/tests/unitTests)
    target_link_libraries(unit-test-maingo PRIVATE maingo-core gtest_main)
    target_compile_features(unit-test-maingo PRIVATE cxx_std_17)
    target_compile_definitions(unit-test-maingo PRIVATE HAVE_GTEST)
    if(MSVC)
        target_compile_options(unit-test-maingo PRIVATE /MP;/Qpar)
        set_target_properties(unit-test-maingo PROPERTIES LINK_FLAGS /ignore:4099) #/ignore:4099 disables annoying linker warning because cplex does not provide debugging information
    else()
        target_compile_options(unit-test-maingo
            PRIVATE
                $<$<CXX_COMPILER_ID:Intel>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<CXX_COMPILER_ID:GNU>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<CXX_COMPILER_ID:AppleClang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                $<$<CXX_COMPILER_ID:Clang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
            )
    endif()
    if(MAiNGO_use_cplex)
        # Additionally linking cplex-available (part of the cplex target). This is merely to provide information whether the current MAiNGO build actually has CPLEX.
        # This is required since the behavior of the unit test for setting the LBS solver depends on its availability.
        target_link_libraries(unit-test-maingo PRIVATE cplex-available)
    endif()
    if(MAiNGO_use_gurobi)
        # Additionally linking gurobi-available (part of the gurobi target). This is merely to provide information whether the current MAiNGO build actually has Gurobi.
        # This is required since the behavior of the unit test for setting the LBS solver depends on its availability.
        target_link_libraries(unit-test-maingo PRIVATE gurobi-available)
    endif()

    # Test the C API of MAiNGO
    if (MAiNGO_build_shared_c_api)
        set(C_API_TEST_DIR ${PROJECT_SOURCE_DIR}/tests/cApi)
        add_executable(test-c-api-maingo ${C_API_TEST_DIR}/main.cpp)
        add_dependencies(test-c-api-maingo maingo-c-api)
        target_link_libraries(test-c-api-maingo PUBLIC maingo-c-api)
        target_compile_features(test-c-api-maingo PRIVATE cxx_std_17)
        if(MSVC)
            target_compile_options(test-c-api-maingo PRIVATE /MP;/Qpar)
            set_target_properties(test-c-api-maingo PROPERTIES LINK_FLAGS /ignore:4099) #/ignore:4099 disables annoying linker warning because cplex does not provide debugging information
        else()
            target_compile_options(test-c-api-maingo
                PRIVATE
                    $<$<CXX_COMPILER_ID:Intel>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                    $<$<CXX_COMPILER_ID:GNU>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                    $<$<CXX_COMPILER_ID:AppleClang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                    $<$<CXX_COMPILER_ID:Clang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
                )
        endif()
    endif()

    # Test Python interface of MAiNGO
    if (MAiNGO_build_python_interface)
        set(PYTHON_TEST_DIR ${PROJECT_SOURCE_DIR}/maingopy/tests)
        add_custom_target(test-maingopy ALL
            COMMAND ${CMAKE_COMMAND} -E copy
                ${PYTHON_TEST_DIR}/testMaingopy.py
                $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}>
            COMMAND ${CMAKE_COMMAND} -E make_directory
                $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}>/individualPythonTests
            COMMAND ${CMAKE_COMMAND} -E copy
                ${PYTHON_TEST_DIR}/individualPythonTests/testErrorHandling.py
                ${PYTHON_TEST_DIR}/individualPythonTests/testEvaluationContainer.py
                ${PYTHON_TEST_DIR}/individualPythonTests/testIntrinsicFunctions.py
                ${PYTHON_TEST_DIR}/individualPythonTests/testMAiNGOmodel.py
                ${PYTHON_TEST_DIR}/individualPythonTests/testOptimizationVariables.py
                ${PYTHON_TEST_DIR}/individualPythonTests/testSolver.py
                ${PYTHON_TEST_DIR}/individualPythonTests/__init__.py
                $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}>/individualPythonTests
            COMMAND ${CMAKE_COMMAND} -E copy
                ${PROJECT_SOURCE_DIR}/examples/MAiNGOSettings.txt
                $<$<CONFIG:Debug>:${RUNTIME_OUTPUT_DIRECTORY_DEBUG}>$<$<NOT:$<CONFIG:Debug>>:${RUNTIME_OUTPUT_DIRECTORY_RELEASE}>/individualPythonTests
            )
    endif()

endif()