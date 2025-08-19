cmake_minimum_required(VERSION 3.8 FATAL_ERROR)

project(meloncommon)

add_library(meloncommon STATIC
	${PROJECT_SOURCE_DIR}/src/modelParser.cpp
)
target_include_directories(meloncommon PUBLIC ${PROJECT_SOURCE_DIR}/inc)
set_target_properties(meloncommon PROPERTIES CXX_STANDARD 17)
target_link_libraries(meloncommon PUBLIC json tinyxml2 mcpp)

# Make sure we can use the filesystem library with older versions of GCC
if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")

    # until 9.1, need to link to the filesystem library explicitly
    if(CMAKE_CXX_COMPILER_VERSION VERSION_LESS 9.1)
        target_link_libraries(meloncommon PRIVATE stdc++fs)

        # until 8.1, it was additionally considered experimental
        if(CMAKE_CXX_COMPILER_VERSION VERSION_LESS 8.1)
            target_compile_definitions(meloncommon PRIVATE "GCC_FS_EXPERIMENTAL")
        endif()

    endif()

endif()
