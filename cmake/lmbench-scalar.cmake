# Keep benchmark C source unchanged. This opt-in setting affects bw_mem.c,
# not just frd/fwr, and does not apply to the common timing library or tools.
set(LMBENCH_BW_MEM_SCALAR_FLAGS "")
if(LMBENCH_BW_MEM_SCALAR)
  if(CMAKE_CONFIGURATION_TYPES OR NOT CMAKE_BUILD_TYPE STREQUAL "O1")
    message(FATAL_ERROR "LMBENCH_BW_MEM_SCALAR requires a single-config O1 build")
  endif()
  if(NOT CMAKE_SYSTEM_PROCESSOR MATCHES "^(aarch64|arm64|ARM64)$")
    message(FATAL_ERROR "The scalar experiment is validated only for AArch64")
  endif()
  if(CMAKE_INTERPROCEDURAL_OPTIMIZATION OR CMAKE_INTERPROCEDURAL_OPTIMIZATION_O1)
    message(FATAL_ERROR "The scalar experiment does not support LTO")
  endif()
  if(CMAKE_C_COMPILER_ID MATCHES "Clang")
    set(LMBENCH_BW_MEM_SCALAR_FLAGS
      -mllvm -aarch64-enable-ldst-opt=false
      -mllvm -aarch64-enable-mcr=false
      -mllvm -combiner-store-merging=false)
  elseif(CMAKE_C_COMPILER_ID STREQUAL "GNU")
    set(LMBENCH_BW_MEM_SCALAR_FLAGS
      --param=aarch64-ldp-policy=never
      --param=aarch64-stp-policy=never)
  else()
    message(FATAL_ERROR "Unsupported scalar compiler: ${CMAKE_C_COMPILER_ID}")
  endif()
endif()
