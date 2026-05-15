# CMake build

This tree keeps the original Makefile build intact and adds a separate CMake
path for modern host and cross builds. The CMake build produces the traditional
lmbench command-line executables, not the xcbench/sbench shared-library wrapper.

## Presets

```sh
cmake --preset macos
cmake --build build.macos
cmake --install build.macos
```

Available presets:

| Preset | Build dir | Notes |
| --- | --- | --- |
| `linux` | `build.linux` | Native Linux build. |
| `macos` | `build.macos` | Native macOS build. |
| `android` | `build.android` | Uses the local Android NDK CMake toolchain and `arm64-v8a`. |
| `ohos` | `build.ohos` | Uses the local OpenHarmony native CMake toolchain. |

The default install prefix is `<build-dir>/install`. Executables are installed
to `bin`, documentation to `share/lmbench/doc`, and scripts to
`share/lmbench/scripts`.

The default CMake build type is `RelWithDebInfo`, matching the presets. On
GCC/Clang-like compilers this normally means `-O2 -g -DNDEBUG`. This differs
from the historical Makefile's `CFLAGS=-O`; use `-DCMAKE_BUILD_TYPE=Release`,
`Debug`, or another CMake build type if a different optimization/debug profile
is needed.

## Options

| Option | Default | Meaning |
| --- | --- | --- |
| `LMBENCH_BUILD_OPTIONAL` | `ON` | Also build optional tools such as `cache`, `lat_rand`, `lat_cmd`, and `bw_udp`. |
| `LMBENCH_ENABLE_RPC` | `OFF` | Try to build `lat_rpc` when ONC RPC headers are available. |
| `LMBENCH_STRICT_WARNINGS` | `OFF` | Keep old C compatibility warnings non-fatal. |
| `LMBENCH_INSTALL_SCRIPTS` | `ON` | Install original scripts and a generated driver with the configured version string. |

## Platform isolation

Some original lmbench programs depend on APIs that are absent or inconsistent on
modern targets. CMake skips those programs instead of failing the whole build.

| Target | Default behavior |
| --- | --- |
| `lat_rpc` | Skipped unless `LMBENCH_ENABLE_RPC=ON` and RPC headers are found. |
| `lat_sem` | Skipped on Android and OHOS; enabled only when `sys/sem.h` is available. |
| `lat_usleep` | Enabled on Linux, Android, and OHOS; skipped on macOS because the realtime scheduler path is not available. |
| `bw_mem64a` | Enabled only when the active compiler accepts its inline assembly for the current architecture. |
| `busy`, `seek`, `clock`, `rhttp` | Not part of the default CMake build; they are old standalone helpers outside the regular suite. |

`valloc` is provided by a small compatibility shim only on platforms where the
libc symbol is missing.

## Smoke checks

Native macOS example:

```sh
cmake --preset macos
cmake --build build.macos
build.macos/bin/hello
build.macos/bin/enough
build.macos/bin/mhz
cmake --install build.macos
```

Cross-build examples:

```sh
cmake --preset android
cmake --build build.android

cmake --preset ohos
cmake --build build.ohos
```

For Linux, run the same native flow with `cmake --preset linux` on a Linux host.
