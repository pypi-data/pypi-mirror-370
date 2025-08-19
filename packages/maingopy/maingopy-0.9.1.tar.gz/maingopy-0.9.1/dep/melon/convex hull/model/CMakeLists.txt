cmake_minimum_required(VERSION 3.8 FATAL_ERROR)

message("Checking files for ConvexHull.")
project(convexhull CXX)

add_library(convexhull STATIC 
	${PROJECT_SOURCE_DIR}/src/convexhullParser.cpp
)
target_include_directories(convexhull PUBLIC ${PROJECT_SOURCE_DIR}/inc)
set_target_properties(convexhull PROPERTIES CXX_STANDARD 17)
target_link_libraries(convexhull PUBLIC meloncommon json)