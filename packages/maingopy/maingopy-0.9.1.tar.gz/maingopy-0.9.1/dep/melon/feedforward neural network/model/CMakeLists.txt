cmake_minimum_required(VERSION 3.8 FATAL_ERROR)

message("Checking files for ffNet.")
project(ffNet CXX)

add_library(ffnet STATIC 
    ${PROJECT_SOURCE_DIR}/src/AnnParser.cpp
    ${PROJECT_SOURCE_DIR}/src/AnnParserCSV.cpp
    ${PROJECT_SOURCE_DIR}/src/AnnParserXML.cpp
)
target_include_directories(ffnet PUBLIC ${PROJECT_SOURCE_DIR}/inc)
set_target_properties(ffnet PROPERTIES CXX_STANDARD 17)

target_link_libraries(ffnet meloncommon tinyxml2)

