cmake_minimum_required(VERSION 3.8 FATAL_ERROR)

message("Checking files for MultifideltyGP.")
project(multifidelityGP CXX)

add_library(multifidelityGP STATIC ${PROJECT_SOURCE_DIR}/src/mulfilGpParser.cpp)

target_include_directories(multifidelityGP PUBLIC ${PROJECT_SOURCE_DIR}/inc)

set_target_properties(multifidelityGP PROPERTIES CXX_STANDARD 17)
target_link_libraries(multifidelityGP PUBLIC meloncommon gp json)