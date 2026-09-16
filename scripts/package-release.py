#!/usr/bin/env python3
"""Package staged platform installations into the O1 and O2 release assets."""

import argparse
import hashlib
import io
from pathlib import Path
import re
import tarfile


PLATFORMS = ("android", "linux-aarch64", "macos", "ohos")
VARIANTS = {"O1": "O1", "O2": "RelWithDebInfo"}


def digest(path):
    with path.open("rb") as stream:
        result = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
        return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.version):
        parser.error("version must be a filename-safe release identifier")

    # Validate both variants before writing either archive.
    revisions = set()
    for variant, config in VARIANTS.items():
        for platform in PLATFORMS:
            root = args.stage / variant / platform
            for required in ("bin/bw_mem", "bin/bw_mem64", "bin/hello",
                             "share/lmbench/BUILD-INFO.txt", "share/lmbench/COPYING"):
                if not (root / required).is_file():
                    parser.error(f"missing {root / required}")
            info = (root / "share/lmbench/BUILD-INFO.txt").read_text()
            if f"Configuration: {config}\n" not in info:
                parser.error(f"wrong build configuration in {root}")
            expected_flags = "-O -g" if variant == "O1" else "-O2 -g -DNDEBUG"
            if f"Configuration C flags: {expected_flags}\n" not in info:
                parser.error(f"wrong optimization/debug flags in {root}")
            if "Source revision: unknown\n" in info:
                parser.error(f"source revision is not recorded in {root}")
            revisions.update(line for line in info.splitlines() if line.startswith("Source revision:"))
            for binary in (root / "bin").iterdir():
                symbols = (root / "symbols" / f"{binary.name}.dSYM" / "Contents" /
                           "Resources" / "DWARF" / binary.name) if platform == "macos" else (
                               root / "symbols" / f"{binary.name}.debug")
                if not symbols.is_file():
                    parser.error(f"missing separate symbols for {binary}: {symbols}")
        archive = args.output / f"lmbench-{args.version}-{variant}.tar.gz"
        if archive.exists():
            parser.error(f"refusing to overwrite {archive}")
    if (args.output / "SHA256SUMS").exists():
        parser.error("output SHA256SUMS already exists; use a fresh output directory")
    if len(revisions) != 1:
        parser.error("all platform variants must use the same source revision")

    args.output.mkdir(parents=True, exist_ok=True)
    archive_hashes = []
    for variant in VARIANTS:
        name = f"lmbench-{args.version}-{variant}"
        archive = args.output / f"{name}.tar.gz"
        root = args.stage / variant
        members = sorted(path for platform in PLATFORMS
                         for path in (root / platform).rglob("*") if path.is_file())
        manifest = "".join(f"{digest(path)}  {path.relative_to(root).as_posix()}\n"
                           for path in members)
        with tarfile.open(archive, "w:gz") as tar:
            for path in members:
                tar.add(path, arcname=f"{name}/{path.relative_to(root).as_posix()}")
            content = manifest.encode()
            entry = tarfile.TarInfo(f"{name}/SHA256SUMS")
            entry.size = len(content)
            entry.mode = 0o644
            tar.addfile(entry, io.BytesIO(content))
        archive_hashes.append(f"{digest(archive)}  {archive.name}\n")
        print(archive)
    (args.output / "SHA256SUMS").write_text("".join(archive_hashes))


if __name__ == "__main__":
    main()
