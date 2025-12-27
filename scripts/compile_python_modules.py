#!/usr/bin/env python3
"""
Compile the python_modules package without touching the tracked __pycache__ tree.

The script mirrors Python's default __pycache__ naming but writes the bytecode
into binary_artifacts/python_modules/, keeping the repository working tree clean.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import py_compile
import shutil
import sys
from pathlib import Path
from typing import Iterable, List


ROOT_DIR = Path(__file__).resolve().parents[1]
MODULES_DIR = ROOT_DIR / "python_modules"
ARTIFACT_ROOT = ROOT_DIR / "binary_artifacts" / "python_modules"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile python_modules into binary_artifacts without mutating tracked pyc files."
    )
    parser.add_argument(
        "--optimize",
        "-O",
        action="append",
        type=int,
        choices=(0, 1, 2),
        default=[0],
        help="Optimization levels to emit (default: 0). Specify multiple times for several levels.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete the binary_artifacts/python_modules tree before compiling.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild all .py files even if the artifact appears up-to-date.",
    )
    return parser.parse_args()


def _discover_sources(root: Path) -> List[Path]:
    return sorted(
        path
        for path in root.rglob("*.py")
        if "__pycache__" not in path.parts
    )


def _destination_for(source: Path, optimize: int) -> Path:
    rel_parent = source.parent.relative_to(MODULES_DIR)
    cache_dir = ARTIFACT_ROOT / rel_parent / "__pycache__"
    optimization = "" if optimize == 0 else str(optimize)
    cache_name = Path(importlib.util.cache_from_source(str(source), optimization=optimization)).name
    return cache_dir / cache_name


def _needs_rebuild(source: Path, dest: Path) -> bool:
    if not dest.exists():
        return True
    return source.stat().st_mtime_ns > dest.stat().st_mtime_ns


def _compile_file(source: Path, optimize: int, force: bool) -> bool:
    dest = _destination_for(source, optimize)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if not force and not _needs_rebuild(source, dest):
        return False

    py_compile.compile(
        file=str(source),
        cfile=str(dest),
        dfile=str(source.relative_to(ROOT_DIR)),
        optimize=optimize,
        invalidation_mode=None,
    )

    src_stats = source.stat()
    os.utime(dest, (src_stats.st_atime, src_stats.st_mtime))
    return True


def compile_python_modules(optimize_levels: Iterable[int], clean: bool, force: bool) -> int:
    if not MODULES_DIR.exists():
        raise FileNotFoundError(f"Expected python_modules at {MODULES_DIR}")

    if clean and ARTIFACT_ROOT.exists():
        shutil.rmtree(ARTIFACT_ROOT)

    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

    sources = _discover_sources(MODULES_DIR)
    if not sources:
        print("No python sources found under python_modules/")
        return 0

    compiled = 0
    for optimize in sorted(set(optimize_levels)):
        for source in sources:
            if _compile_file(source, optimize, force):
                compiled += 1

    return compiled


def main() -> None:
    args = _parse_args()
    compiled = compile_python_modules(args.optimize, args.clean, args.force)
    artifact_path = ARTIFACT_ROOT.relative_to(ROOT_DIR)

    print(
        f"{compiled} file(s) compiled into {artifact_path} "
        f"(optimize levels: {sorted(set(args.optimize))})."
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
