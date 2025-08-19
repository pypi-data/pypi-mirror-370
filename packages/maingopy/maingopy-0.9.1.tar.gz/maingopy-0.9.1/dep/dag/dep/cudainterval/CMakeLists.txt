cmake_minimum_required(VERSION 3.29.2)
project(cudaIntervalLibrary)

# Create interface libraries, storing the include path and pass it to the executable/other libraries.
add_library(cudainterval INTERFACE)
# Let CPP compiler know where cuda runtime library is.
find_package(CUDAToolkit REQUIRED)
target_link_libraries(cudainterval
    INTERFACE
        CUDA::cudart
)
target_include_directories(cudainterval 
    INTERFACE 
        ${PROJECT_SOURCE_DIR}/inc
)

add_library(helpers INTERFACE)
target_include_directories(helpers INTERFACE ${PROJECT_SOURCE_DIR}/helpers)


