cmake_minimum_required(VERSION 3.25)

project(lmbench VERSION 3.0 LANGUAGES C)

include(GNUInstallDirs)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE "O1" CACHE STRING "Build type" FORCE)
endif()

# Match the historical Makefile's CFLAGS=-O without changing CMake's standard
# Debug/Release/RelWithDebInfo profiles. Explicit user flags remain overridable.
set(CMAKE_C_FLAGS_O1 "-O -g" CACHE STRING "C flags for Makefile-aligned O1 builds with symbols")
mark_as_advanced(CMAKE_C_FLAGS_O1)
if(CMAKE_CONFIGURATION_TYPES)
  list(APPEND CMAKE_CONFIGURATION_TYPES O1)
  list(REMOVE_DUPLICATES CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_CONFIGURATION_TYPES "${CMAKE_CONFIGURATION_TYPES}" CACHE STRING "Build types" FORCE)
else()
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS O1 Debug Release RelWithDebInfo MinSizeRel)
endif()

option(LMBENCH_BUILD_OPTIONAL "Build optional lmbench tools" ON)
option(LMBENCH_ENABLE_RPC "Build RPC benchmarks when the platform provides ONC RPC" OFF)
option(LMBENCH_STRICT_WARNINGS "Build lmbench with strict compiler warnings" OFF)
option(LMBENCH_INSTALL_SCRIPTS "Install lmbench scripts and generated driver" ON)

set(LMBENCH_VERSION "3.0-a9" CACHE STRING "Version string embedded in the lmbench driver")
set(LMBENCH_SOURCE_REVISION "unknown" CACHE STRING "Source commit recorded in build metadata")

if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
  set(CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}/install"
    CACHE PATH "Install path prefix" FORCE)
endif()

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_BINDIR}")

include(cmake/lmbench-platform.cmake)

add_subdirectory(src)

set(LMBENCH_CONFIG_FLAGS "")
foreach(config IN ITEMS O1 Debug Release RelWithDebInfo MinSizeRel)
  string(TOUPPER "${config}" config_upper)
  string(APPEND LMBENCH_CONFIG_FLAGS "$<$<CONFIG:${config}>:${CMAKE_C_FLAGS_${config_upper}}>")
endforeach()
configure_file(cmake/build-info.txt.in "${CMAKE_BINARY_DIR}/build-info.txt.in" @ONLY)
file(GENERATE OUTPUT "${CMAKE_BINARY_DIR}/metadata/$<CONFIG>/BUILD-INFO.txt"
  INPUT "${CMAKE_BINARY_DIR}/build-info.txt.in")
install(FILES "${CMAKE_BINARY_DIR}/metadata/$<CONFIG>/BUILD-INFO.txt" COPYING COPYING-2
  DESTINATION "${CMAKE_INSTALL_DATADIR}/lmbench")

install(
  DIRECTORY doc/
  DESTINATION "${CMAKE_INSTALL_DATADIR}/lmbench/doc"
)
install(
  FILES docs/cmake-build.md
  DESTINATION "${CMAKE_INSTALL_DATADIR}/lmbench/doc"
)

if(LMBENCH_INSTALL_SCRIPTS)
  set(LMBENCH_GENERATED_DIR "${CMAKE_BINARY_DIR}/generated")
  file(MAKE_DIRECTORY "${LMBENCH_GENERATED_DIR}")
  file(READ "${CMAKE_CURRENT_SOURCE_DIR}/scripts/lmbench" LMBENCH_DRIVER_CONTENT)
  string(REPLACE "<version>" "${LMBENCH_VERSION}" LMBENCH_DRIVER_CONTENT "${LMBENCH_DRIVER_CONTENT}")
  file(WRITE "${LMBENCH_GENERATED_DIR}/lmbench" "${LMBENCH_DRIVER_CONTENT}")

  install(
    DIRECTORY scripts/
    DESTINATION "${CMAKE_INSTALL_DATADIR}/lmbench/scripts"
    USE_SOURCE_PERMISSIONS
    PATTERN "lmbench" EXCLUDE
  )
  install(
    PROGRAMS "${LMBENCH_GENERATED_DIR}/lmbench"
    DESTINATION "${CMAKE_INSTALL_DATADIR}/lmbench/scripts"
  )
endif()
