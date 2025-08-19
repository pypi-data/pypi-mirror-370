cmake_minimum_required(VERSION 3.8 FATAL_ERROR)

MESSAGE("Checking files for FILIB++.")
project(filib CXX)


set(FILIB_DIR ${PROJECT_SOURCE_DIR}/filib-3.0.2)
# Note: not allowing filib as shared library since this causes trouble on Windows b/c of static data members...
add_library(filib STATIC
	${FILIB_DIR}/fp_traits/fp_traits_base_double_setup.cpp
	${FILIB_DIR}/fp_traits/fp_traits_base_float_setup.cpp
	${FILIB_DIR}/fp_traits/fp_traits_double_setup.cpp
	${FILIB_DIR}/fp_traits/fp_traits_float_setup.cpp
	${FILIB_DIR}/fp_traits/fp_traits_sse_const.cpp
	${FILIB_DIR}/fp_traits/fp_traits_x87_const.cpp
	${FILIB_DIR}/ieee/primitive.cpp
	${FILIB_DIR}/interval/stdfun/filib_consts.cpp
)
configure_file(${FILIB_DIR}/rounding_control/rounding_control_config.hpp.in rounding_control/rounding_control_config.hpp)
configure_file(${FILIB_DIR}/config.h.in config.h)
target_include_directories(filib
	PUBLIC
		${FILIB_DIR}
		${CMAKE_CURRENT_BINARY_DIR}
)
target_compile_options(filib
	PRIVATE
        $<$<CXX_COMPILER_ID:MSVC>:-fp:strict>
        $<$<CXX_COMPILER_ID:Intel>: $<$<PLATFORM_ID:Windows>:/fp:strict> $<$<NOT:$<PLATFORM_ID:Windows>>:-fp-model:strict>>
)
target_compile_options(filib
	PUBLIC
        $<$<CXX_COMPILER_ID:MSVC>:/wd4996;/wd4244>
        $<$<CXX_COMPILER_ID:Intel>: $<$<PLATFORM_ID:Windows>:/Qwd161;/Qwd3346> $<$<NOT:$<PLATFORM_ID:Windows>>:-wd161 -wd3346>>
        $<$<CXX_COMPILER_ID:GNU>:-Wno-deprecated>
        $<$<CXX_COMPILER_ID:AppleClang>:-Wno-logical-op-parentheses -Wno-dangling-else -Wno-undefined-var-template>
        $<$<CXX_COMPILER_ID:Clang>:-Wno-logical-op-parentheses -Wno-dangling-else -Wno-undefined-var-template -Wno-unknown-pragmas>
)
set_target_properties(filib PROPERTIES DEBUG_POSTFIX d)
if(MSVC)
    target_compile_options(filib PRIVATE /MP;/Qpar)
else()
	target_compile_options(filib
		PRIVATE
			$<$<CXX_COMPILER_ID:Intel>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
			$<$<CXX_COMPILER_ID:GNU>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
			$<$<CXX_COMPILER_ID:AppleClang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
			$<$<CXX_COMPILER_ID:Clang>: $<$<NOT:$<CONFIG:DEBUG>>:-O3> $<$<CONFIG:DEBUG>:-O0>>
	)
endif()

if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
	add_executable(filib-test
		${PROJECT_SOURCE_DIR}/test/test.cpp
	)
	target_link_libraries(filib-test PRIVATE filib)
endif()