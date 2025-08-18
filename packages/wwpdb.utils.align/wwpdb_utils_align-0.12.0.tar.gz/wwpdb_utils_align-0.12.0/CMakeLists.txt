cmake_minimum_required(VERSION 3.15...4.0)
project(alignlib)
#
# File: CMakeLists.txt -
# Date: 13-Oct-2018
#
# Updates:
#
# C++ wrappers using alignment utilities
#
if (POLICY CMP0148)
  # cmake warns cmake > 3.12 still using FindPythonInterp
  cmake_policy(SET CMP0148 OLD)
endif()
#
#
find_package(PythonInterp)
find_package(PythonLibs)
include_directories(${PYTHON_INCLUDE_DIRS})
message(STATUS "Python include path set to " ${PYTHON_INCLUDE_DIRS})
#
#  -- Build a wrapper library  --
#
add_subdirectory("modules/pybind11")
#
#
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

IF(NOT DEFINED ENV{RUN_FROM_DISUTILS})
    set(CMAKE_VERBOSE_MAKEFILE ON)
ENDIF()
#
#
if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    # require at least gcc 4.8
    if (CMAKE_CXX_COMPILER_VERSION VERSION_LESS 4.8)
        message(FATAL_ERROR "GCC version must be at least 4.8!")
    endif()
    set(warnings " -Wall -Wno-unused-variable -Wno-unused-value -Wno-unused-but-set-variable -Wno-deprecated-declarations")
    # set(WRAPPER_DIR_EXT "Linux")
elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
     if (CMAKE_CXX_COMPILER_VERSION VERSION_LESS 8.1)
        message(FATAL_ERROR "Clang version must be at least 8.1!")
    endif()
    #set(warnings "-Wall -Wextra -Werror")
    set(warnings " -Wall -Wno-unused-variable -Wno-deprecated-declarations -Wno-register")
    #set(WRAPPER_DIR_EXT "Darwin")
elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "MSVC")
    message(FATAL_ERROR "No current support for MSVC!")
    set(warnings "/W4 /WX /EHsc")
endif()
#
set(mydefines " -DBIG_ENDIAN_PLATFORM  -DHAVE_STRCASECMP -DINCL_TEMPLATE_SRC -DHAVE_PLACEMENT_NEW  ")
if (NOT CONFIGURED_ONCE)
    #set(CMAKE_CXX_FLAGS "${warnings} ${mydefines}  -fno-common -fvisibility=hidden -fvisibility-inlines-hidden -std=c++14  -flto "
    #    CACHE STRING "Flags used by the compiler during all build types." FORCE)
    #
    set(CMAKE_CXX_FLAGS "${warnings} ${mydefines}  -fno-common -fvisibility=hidden -fvisibility-inlines-hidden -std=c++11  -flto "
        CACHE STRING "Flags used by the compiler during all build types." FORCE)
    #
    set(CMAKE_C_FLAGS   "${warnings} ${mydefines}  -fPIC"
        CACHE STRING "Flags used by the compiler during all build types." FORCE)
    #
    if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
        SET(CMAKE_AR  "gcc-ar")
        SET(CMAKE_CXX_ARCHIVE_CREATE "<CMAKE_AR> qcs <TARGET> <LINK_FLAGS> <OBJECTS>")
        SET(CMAKE_CXX_ARCHIVE_FINISH   true)
    endif()

endif()

message(STATUS "Compiler flags " ${CMAKE_CXX_FLAGS})

#
# ---------------------------------------------------------------
#   WHERE AM I RUNNING
#
message(STATUS "---CMAKE MODULE PATH - " ${CMAKE_MODULE_PATH})
message(STATUS "---CMAKE SOURCE DIR  - " ${CMAKE_SOURCE_DIR})
message(STATUS "---CMAKE PROJECT DIR - " ${PROJECT_SOURCE_DIR})
# ---------------------------------------------------------------
#
set(BUILD_SOURCE_DIR "${CMAKE_CURRENT_BINARY_DIR}/src")
set(BUILD_INCLUDE_DIR "${CMAKE_CURRENT_BINARY_DIR}/include")
set(BUILD_BINARY_DIR "${CMAKE_CURRENT_BINARY_DIR}/bin")
set(BUILD_LIBRARY_DIR "${CMAKE_CURRENT_BINARY_DIR}/lib")
#
#  Set the source module paths ---
#

set(WRAP_DIR_1 "modules/cpp-alignlib-wrapper/src")


set(SOURCE_DIR_1 "modules/PairwiseAlign/src")
set(INCLUDE_DIR_1 "modules/PairwiseAlign/include")
#

set(SOURCE_TEST_DIR  "modules/PairwiseAlign/test")
#
# ---------------------------------------------------------------
#
file(GLOB INC_1 "${INCLUDE_DIR_1}/*.h")
file(COPY ${INC_1} DESTINATION include)
#
file(MAKE_DIRECTORY ${BUILD_SOURCE_DIR})
file(MAKE_DIRECTORY ${BUILD_INCLUDE_DIR})
file(MAKE_DIRECTORY ${BUILD_BINARY_DIR})
file(MAKE_DIRECTORY ${BUILD_LIBRARY_DIR})
#
IF(NOT DEFINED ENV{RUN_FROM_DISUTILS})
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY  ${BUILD_LIBRARY_DIR})
ENDIF()
#
#set(LIBRARY_OUTPUT_DIRECTORY        ${BUILD_LIBRARY_DIR})
#set(ARCHIVE_OUTPUT_DIRECTORY        ${BUILD_LIBRARY_DIR})
#
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY  ${BUILD_LIBRARY_DIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY  ${BUILD_BINARY_DIR})
#
# ---------------------------------------------------------------
install(DIRECTORY ${INCLUDE_DIR_1} DESTINATION include FILES_MATCHING PATTERN "*.h")
#
#  Build 'common' library
set(SOURCES_1
         "${SOURCE_DIR_1}/AlignUtil.C"
         "${SOURCE_DIR_1}/PairwiseAlign.C"
         "${SOURCE_DIR_1}/PseudoMultiAlign.C")

add_library("align" OBJECT ${SOURCES_1})
target_include_directories("align" PUBLIC ${BUILD_INCLUDE_DIR})


#
# Combine the all object into consolidated library  'mmciflib-all'
#
add_library("align-all" STATIC
            "$<TARGET_OBJECTS:align>"
            )

#
#  -- Build a test application binary to verify the completeness of the library--
#
add_executable("align_test_1" "${SOURCE_TEST_DIR}/testPairwiseAlign.C")
target_link_libraries("align_test_1" "align-all")
target_include_directories("align_test_1" PUBLIC ${BUILD_INCLUDE_DIR})
#
add_executable("align_test_2" "${SOURCE_TEST_DIR}/testPairwiseAlignZF.C")
target_link_libraries("align_test_2" "align-all")
target_include_directories("align_test_2" PUBLIC ${BUILD_INCLUDE_DIR})
#
add_executable("align_test_3" "${SOURCE_TEST_DIR}/testPseudoMultiAlign.C")
target_link_libraries("align_test_3" "align-all")
target_include_directories("align_test_3" PUBLIC ${BUILD_INCLUDE_DIR})
#
add_executable("align_test_4" "${SOURCE_TEST_DIR}/testRefSeqAlign.C")
target_link_libraries("align_test_4" "align-all")
target_include_directories("align_test_4" PUBLIC ${BUILD_INCLUDE_DIR})
#
#  -- Build a wrapper library  --
#
file(GLOB_RECURSE WRAP_SRC_FILES "${WRAP_DIR_1}/*.cpp")
#
pybind11_add_module("alignlib" ${WRAP_SRC_FILES})
target_include_directories("alignlib" PUBLIC ${BUILD_INCLUDE_DIR} )
target_link_libraries("alignlib" PUBLIC "align-all")
#
IF(NOT DEFINED ENV{RUN_FROM_DISUTILS})
    message(STATUS "Source directory 1 " ${SOURCE_DIR_1})
    message(STATUS "Include directory 1 " ${INCLUDE_DIR_1})
    message(STATUS "SOURCE_1 LIST " ${SOURCES_1})
    message(STATUS, "---WRAPPER SOURCE ${WRAP_DIR_1} INITIAL FILE LIST " ${WRAP_SRC_FILES})
    message(STATUS, "---EXCLUDING FILE " ${EXC_FILES})
    message(STATUS, "---WRAPPER SOURCE FINAL FILE LIST " ${WRAP_SRC_FILES})
ENDIF()
#
message(STATUS, "---ALL DONE WITH CMAKE")
#
