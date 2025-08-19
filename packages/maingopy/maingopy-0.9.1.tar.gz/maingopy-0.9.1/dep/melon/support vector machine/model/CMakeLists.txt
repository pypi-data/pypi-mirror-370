cmake_minimum_required(VERSION 3.8 FATAL_ERROR)

message("Checking files for SVM.")
project(svm CXX)

add_library(svm STATIC 
	${PROJECT_SOURCE_DIR}/src/svmParser.cpp
)
target_include_directories(svm PUBLIC ${PROJECT_SOURCE_DIR}/inc)
set_target_properties(svm PROPERTIES CXX_STANDARD 17)
target_link_libraries(svm PUBLIC meloncommon json)