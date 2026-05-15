cmake_minimum_required(VERSION 3.25)

project(lmbench VERSION 3.0 LANGUAGES C)

include(GNUInstallDirs)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE "RelWithDebInfo" CACHE STRING "Build type" FORCE)
endif()

option(LMBENCH_BUILD_OPTIONAL "Build optional lmbench tools" ON)
option(LMBENCH_ENABLE_RPC "Build RPC benchmarks when the platform provides ONC RPC" OFF)
option(LMBENCH_STRICT_WARNINGS "Build lmbench with strict compiler warnings" OFF)
option(LMBENCH_INSTALL_SCRIPTS "Install lmbench scripts and generated driver" ON)

set(LMBENCH_VERSION "3.0-a9" CACHE STRING "Version string embedded in the lmbench driver")

if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
  set(CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}/install"
    CACHE PATH "Install path prefix" FORCE)
endif()

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_BINDIR}")

include(cmake/lmbench-platform.cmake)

add_subdirectory(src)

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
