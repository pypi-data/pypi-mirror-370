cmake_minimum_required(VERSION 3.8 FATAL_ERROR)

message("Checking files for GP.")
project(gp CXX)

add_library(gp STATIC 
	${PROJECT_SOURCE_DIR}/src/gpParser.cpp
)
target_include_directories(gp PUBLIC ${PROJECT_SOURCE_DIR}/inc)
set_target_properties(gp PROPERTIES CXX_STANDARD 17)
target_link_libraries(gp PUBLIC meloncommon json)