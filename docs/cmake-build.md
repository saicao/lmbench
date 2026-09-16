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

The default CMake build type is `O1`, matching the historical Makefile's
`CFLAGS=-O` optimization level. Its configuration flags are `-O -g`: GCC and
Clang treat `-O` as `-O1`, and `-g` retains debug information for profiling.
Platform/toolchain compatibility flags still apply.
This applies both to a fresh plain CMake build and the platform presets.
Existing build directories keep their cached build type; reconfigure with a
platform preset or `-DCMAKE_BUILD_TYPE=O1` to select the new default explicitly.

Each platform also has an O2 preset (`linux-o2`, `macos-o2`, `android-o2`,
`ohos-o2`) using `RelWithDebInfo` (`-O2 -g -DNDEBUG`) and a separate build
directory. For example:

```sh
cmake --preset android-o2
cmake --build build.android-o2
cmake --install build.android-o2
```

Standard `Debug`, `Release`, and `RelWithDebInfo` configurations retain CMake's
normal behavior. Explicit flags such as `-DCMAKE_C_FLAGS_O1=...` remain supported.
O1 does not guarantee scalar-only instructions: compilers may still combine
adjacent accesses into `LDP`/`STP`. The benchmark sources are unchanged.

Each installation records its compiler, target, configuration, C flags, and
source revision in `share/lmbench/BUILD-INFO.txt`. Release builds set
`LMBENCH_SOURCE_REVISION` to the full Git commit and `LMBENCH_VERSION` to the
release-specific version string.

## Release packaging

Every release provides exactly two binary download archives, O1 and O2. Each
archive contains all four platform installations (`android`, `linux-aarch64`,
`macos`, `ohos`), including the complete supported tool set, documentation,
licenses, and build metadata. Both variants compile with debug information.
Release archives contain stripped executables in each platform's `bin/` and
separate matching symbols in `symbols/`: ELF `.debug` files for Android, Linux,
and OHOS, and `.dSYM` bundles for macOS. Extract the symbols before stripping;
retain the original local build artifacts for disassembly and debugging.
GitHub also displays its automatic source archives.

Use clean build directories for all eight builds. Stage each installation under
`<stage>/<O1|O2>/<platform>` using `cmake --install <build> --prefix <path>`, then:

```sh
python3 scripts/package-release.py --version 20260916 --stage /path/to/stage --output /path/to/assets
```

The script checks all platform installations, embeds a per-file `SHA256SUMS`,
and produces `lmbench-20260916-O1.tar.gz` and `lmbench-20260916-O2.tar.gz`.
It also writes the archive checksums to a local `SHA256SUMS` file: include these
in the release description and upload only the two `.tar.gz` binary assets.
Record any SDK or toolchain changes in the release description as well.

If local SDK paths differ from the presets, override the toolchain explicitly
with `--toolchain /path/to/toolchain.cmake` when configuring. Use the same
compiler and SDK for both optimization variants of a platform.

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
