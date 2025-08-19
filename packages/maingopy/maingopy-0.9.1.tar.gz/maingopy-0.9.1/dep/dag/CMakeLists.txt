cmake_minimum_required(VERSION 3.22.1)
project(SVTDag VERSION 1.0 LANGUAGES CXX)

if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
    add_subdirectory(dep/babbase)
    add_subdirectory(dep/blas)
    add_subdirectory(dep/cpplapack)
    add_subdirectory(dep/fadbad)
    add_subdirectory(dep/filib)
    add_subdirectory(dep/lapack)
    add_subdirectory(dep/mcpp)
endif()

if(HAVE_CUDA_TOOLKIT)
    add_subdirectory(dep/cudainterval)

    add_library(dag
        src/dag.cpp 
        src/operations.cpp
        src/modeloperations.cpp  
        src/dagprinting.cpp 
        src/modelvar.cpp
        src/derivativeinformation.cpp
        src/dagconversion.cpp	
        src/operations.cu
    )
    target_compile_definitions(dag PUBLIC CUDA_INSTALLED)
    set_target_properties(dag 
        PROPERTIES
        # For each static library being consumed by a shared library or executable, 
        # CUDA_SEPARABLE_COMPLIATION must be set as ON. Get this set only in the target 
        # of the shared library or executable will not work properly (template functions/polymophism).
        CUDA_SEPARABLE_COMPILATION ON
    )
    target_include_directories(dag 
        PUBLIC ${PROJECT_SOURCE_DIR}/inc
    )
    target_link_libraries(dag 
        PUBLIC 
            cudainterval
            filib
            mcpp
            babbase
    )

    if(CMAKE_BUILD_TYPE STREQUAL "Debug")
        target_compile_options(dag PRIVATE $<$<COMPILE_LANGUAGE:CUDA>:-g -G>)
    endif()

    if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
        include(CheckLanguage)
        check_language(CUDA)
        if(CMAKE_CUDA_COMPILER)
            message(STATUS "CUDA compiler was found!")
            enable_language(CUDA) 

            if(NOT DEFINED CMAKE_CUDA_ARCHITECTURES)
                set(CMAKE_CUDA_ARCHITECTURES native)
            endif() 

            add_executable(DagTest test/main.cu)
            if(CMAKE_BUILD_TYPE STREQUAL "Debug")
                target_compile_options(DagTest PRIVATE $<$<COMPILE_LANGUAGE:CUDA>:-g -G>)
            endif()

            set_target_properties(dag 
                PROPERTIES 
                CUDA_SEPARABLE_COMPILATION ON
                CUDA_ARCHITECTURES ${CMAKE_CUDA_ARCHITECTURES}
            )

            set_target_properties(DagTest 
                PROPERTIES 
                CUDA_SEPARABLE_COMPILATION ON
                CUDA_ARCHITECTURES ${CMAKE_CUDA_ARCHITECTURES}
            )
            target_link_libraries(DagTest 
                PRIVATE dag
            )

            add_executable(cudaIntervalNewtonTest dep/cudainterval/interval_newton.cu)
            if(CMAKE_BUILD_TYPE STREQUAL "Debug")
                target_compile_options(cudaIntervalNewtonTest PRIVATE $<$<COMPILE_LANGUAGE:CUDA>:-g -G>)
            endif()
            set_target_properties(cudaIntervalNewtonTest 
                PROPERTIES 
                CUDA_SEPARABLE_COMPILATION ON
                CUDA_ARCHITECTURES ${CMAKE_CUDA_ARCHITECTURES}
            )
            target_link_libraries(cudaIntervalNewtonTest 
                PRIVATE helpers
                PRIVATE dag
            )
        else()
            message(STATUS "No CUDA compiler found! The DagTest and cudaIntervalNewtonTest will not built.")
        endif()
    endif()
else()
    add_library(dag 
        src/dag.cpp
        src/dagprinting.cpp  
        src/modeloperations.cpp
        src/modelvar.cpp 
        src/derivativeinformation.cpp
        src/operations.cpp 
        src/dagconversion.cpp
    )
    target_include_directories(dag
        PUBLIC ${PROJECT_SOURCE_DIR}/inc 
    )
    target_link_libraries(dag 
        PUBLIC
            filib
            mcpp
            babbase
    )

    if(CMAKE_BUILD_TYPE STREQUAL "Debug")
        target_compile_options(dag PRIVATE $<$<COMPILE_LANGUAGE:CUDA>:-g>)
    endif()

    if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
        add_executable(CPUDagTest test/main.cpp)
        target_link_libraries(CPUDagTest PRIVATE dag)
    endif()
endif()
