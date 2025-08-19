cmake_minimum_required(VERSION 3.10)

message("Checking files for JSON.")
project(json CXX)

add_library(json INTERFACE)
target_include_directories(json
    INTERFACE
    ${PROJECT_SOURCE_DIR}/json-3.7.3/single_include/
)
target_compile_features(json INTERFACE cxx_std_11)