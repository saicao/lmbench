find_package(Threads REQUIRED)

set(LMBENCH_BUILT_TARGETS)
set(LMBENCH_SKIPPED_TARGETS)

function(lmbench_apply_target_defaults target_name)
  target_include_directories(${target_name} PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")

  if(CMAKE_C_COMPILER_ID MATCHES "Clang|GNU")
    target_compile_options(${target_name} PRIVATE -std=gnu89)
    if(CMAKE_SYSTEM_NAME STREQUAL "OHOS")
      target_compile_options(${target_name} PRIVATE -Wno-unused-command-line-argument)
    endif()
    if(NOT LMBENCH_STRICT_WARNINGS)
      target_compile_options(${target_name} PRIVATE
        -Wno-implicit-int
        -Wno-implicit-function-declaration
        -Wno-deprecated-non-prototype
        -Wno-incompatible-pointer-types
        -Wno-int-conversion
        -Wno-pointer-sign
        -Wno-return-type
        -Wno-format-security
        -Wno-unused-value
      )
    endif()
  endif()

  if(LMBENCH_MAP_ANONYMOUS_DEFINITION)
    target_compile_definitions(${target_name} PRIVATE ${LMBENCH_MAP_ANONYMOUS_DEFINITION})
  endif()
endfunction()

function(lmbench_add_executable target_name)
  set(options)
  set(one_value_keywords)
  set(multi_value_keywords SOURCES LIBS DEFINITIONS)
  cmake_parse_arguments(PARSE_ARGV 1 arg
    "${options}" "${one_value_keywords}" "${multi_value_keywords}"
  )

  if(arg_SOURCES)
    set(sources ${arg_SOURCES})
  else()
    set(sources ${target_name}.c)
  endif()

  add_executable(${target_name} ${sources})
  lmbench_apply_target_defaults(${target_name})
  target_link_libraries(${target_name} PRIVATE lmbench_common ${arg_LIBS})
  if(arg_DEFINITIONS)
    target_compile_definitions(${target_name} PRIVATE ${arg_DEFINITIONS})
  endif()
  install(TARGETS ${target_name} RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}")

  set(LMBENCH_BUILT_TARGETS ${LMBENCH_BUILT_TARGETS} ${target_name} PARENT_SCOPE)
endfunction()

function(lmbench_skip_target target_name reason)
  message(STATUS "Skipping ${target_name}: ${reason}")
  set(LMBENCH_SKIPPED_TARGETS
    ${LMBENCH_SKIPPED_TARGETS}
    "${target_name}: ${reason}"
    PARENT_SCOPE
  )
endfunction()

set(LMBENCH_COMMON_SOURCES
  lib_tcp.c
  lib_udp.c
  lib_unix.c
  lib_timing.c
  lib_mem.c
  lib_stats.c
  lib_debug.c
  getopt.c
  lib_sched.c
)

add_library(lmbench_common STATIC ${LMBENCH_COMMON_SOURCES})
lmbench_apply_target_defaults(lmbench_common)
target_link_libraries(lmbench_common PUBLIC m)

if(LMBENCH_NEED_VALLOC)
  target_compile_definitions(lmbench_common PUBLIC LMBENCH_NEED_VALLOC=1)
endif()

set(LMBENCH_DEFAULT_TARGETS
  bw_file_rd
  bw_mem
  bw_mem64
  bw_mmap_rd
  bw_pipe
  bw_tcp
  bw_unix
  hello
  lat_select
  lat_pipe
  lat_syscall
  lat_tcp
  lat_udp
  lat_mmap
  mhz
  lat_proc
  lat_pagefault
  lat_connect
  lat_fs
  lat_sig
  lat_mem_rd
  lat_ctx
  memsize
  lat_unix
  lmdd
  timing_o
  enough
  msleep
  loop_o
  lat_fifo
  lmhttp
  lat_http
  lat_fcntl
  disk
  lat_unix_connect
  flushdisk
  lat_ops
  line
  tlb
  par_mem
  par_ops
  stream
  lat_mem_pingpong
  bw_mem64p
  bw_mem64d
)

foreach(bench IN LISTS LMBENCH_DEFAULT_TARGETS)
  if(bench STREQUAL "mhz")
    lmbench_add_executable(${bench} LIBS m)
  elseif(bench STREQUAL "flushdisk")
    lmbench_add_executable(${bench} DEFINITIONS MAIN)
  elseif(bench STREQUAL "lat_mem_pingpong" AND NOT CMAKE_SYSTEM_NAME MATCHES "^(Android|OHOS)$")
    lmbench_add_executable(${bench} LIBS Threads::Threads)
  else()
    lmbench_add_executable(${bench})
  endif()
endforeach()

if(LMBENCH_CAN_BUILD_BW_MEM64A)
  lmbench_add_executable(bw_mem64a)
else()
  lmbench_skip_target(bw_mem64a "current compiler/architecture rejects its inline assembly")
endif()

if(LMBENCH_HAVE_SYSV_SEM)
  lmbench_add_executable(lat_sem)
else()
  lmbench_skip_target(lat_sem "SysV semaphores are unavailable or disabled on this platform")
endif()

if(LMBENCH_HAVE_REALTIME_SLEEP)
  lmbench_add_executable(lat_usleep DEFINITIONS TRUE=1 FALSE=0)
else()
  lmbench_skip_target(lat_usleep "real-time scheduler API is not available in this build")
endif()

if(LMBENCH_ENABLE_RPC AND LMBENCH_CAN_BUILD_LAT_RPC)
  lmbench_add_executable(lat_rpc DEFINITIONS LMBENCH_ENABLE_RPC=1)
else()
  lmbench_skip_target(lat_rpc "ONC RPC support is disabled or unavailable")
endif()

if(LMBENCH_BUILD_OPTIONAL)
  foreach(optional_bench IN ITEMS cache lat_dram_page lat_pmake lat_rand lat_cmd bw_udp)
    lmbench_add_executable(${optional_bench})
  endforeach()
endif()

message(STATUS "lmbench targets: ${LMBENCH_BUILT_TARGETS}")
if(LMBENCH_SKIPPED_TARGETS)
  message(STATUS "lmbench skipped targets: ${LMBENCH_SKIPPED_TARGETS}")
endif()
