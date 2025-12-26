#!/usr/bin/env python3
"""Placeholder audit for AutonomousZenithOptimizer.

Goals:
- Scan only git-tracked files (avoids .venv/, build outputs, local configs).
- Report placeholders of the form ${NAME} where NAME is [A-Z0-9_]+ (runtime config placeholders).
- Separately report other ${...} usages (bash/powershell/github actions) as non-config templating.
- Validate that every runtime placeholder is present as a key in .env.example.

Usage:
  python scripts/placeholder_audit.py
  python scripts/placeholder_audit.py --json

Exit codes:
    0 = OK
    2 = Missing keys in .env.example
    3 = Runtime placeholders found (must be zero)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple


RUNTIME_PLACEHOLDER_RE = re.compile(r"\$\{([A-Z0-9_]+)\}")
ANY_DOLLAR_CURLY_RE = re.compile(r"\$\{[^}]+\}")
GITHUB_ACTIONS_RE = re.compile(r"\$\{\{[^}]+\}\}")


@dataclass(frozen=True)
class Finding:
    path: str
    placeholders: Tuple[str, ...]


def _run_git_ls_files(repo_root: Path) -> List[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=str(repo_root),
        text=True,
        capture_output=True,
        check=True,
    )
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _read_text(path: Path) -> str:
    # Be tolerant to odd encodings; we only need to find ASCII placeholder patterns.
    return path.read_text(encoding="utf-8", errors="ignore")


def _scan_files(
    repo_root: Path, files: Iterable[str]
) -> Tuple[List[Finding], Dict[str, List[str]]]:
    runtime_findings: List[Finding] = []
    non_runtime_by_path: Dict[str, List[str]] = {}

    for rel in files:
        p = repo_root / rel

        # Skip files that are likely binary/huge.
        try:
            if p.is_file() and p.stat().st_size > 2_000_000:
                continue
        except OSError:
            continue

        # Only scan text-ish files. (We still rely on error-tolerant read.)
        if p.suffix.lower() not in {
            ".json",
            ".py",
            ".md",
            ".txt",
            ".ps1",
            ".sh",
            ".yml",
            ".yaml",
        }:
            continue

        try:
            text = _read_text(p)
        except OSError:
            continue

        # Runtime placeholders are only taken from JSON config files.
        # Everything else is treated as non-runtime templating/example usage.
        runtime: List[str] = []
        if p.suffix.lower() == ".json":
            # Ignore GitHub Actions expressions; treat them as non-runtime templating.
            text_without_actions = GITHUB_ACTIONS_RE.sub("", text)
            runtime = sorted(set(RUNTIME_PLACEHOLDER_RE.findall(text_without_actions)))
            if runtime:
                runtime_findings.append(
                    Finding(
                        path=rel.replace("\\", "/"),
                        placeholders=tuple(runtime),
                    )
                )

        # Collect other ${...} usages (after removing runtime placeholders and gha expressions).
        non_runtime_candidates = set(ANY_DOLLAR_CURLY_RE.findall(text))
        for rp in runtime:
            non_runtime_candidates.discard(f"${{{rp}}}")
        # remove gha expressions from non-runtime list too
        non_runtime_candidates = {
            x for x in non_runtime_candidates if not GITHUB_ACTIONS_RE.fullmatch(x)
        }

        if non_runtime_candidates:
            non_runtime_by_path[rel.replace("\\", "/")] = sorted(non_runtime_candidates)

    return runtime_findings, non_runtime_by_path


def _parse_env_example_keys(env_example_path: Path) -> Set[str]:
    keys: Set[str] = set()
    if not env_example_path.exists():
        return keys

    for raw in env_example_path.read_text(
        encoding="utf-8", errors="ignore"
    ).splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        if key:
            keys.add(key)
    return keys


def _build_report(repo_root: Path) -> Dict[str, object]:
    tracked = _run_git_ls_files(repo_root)
    runtime_findings, non_runtime_by_path = _scan_files(repo_root, tracked)

    runtime_vars: Set[str] = set()
    by_var: Dict[str, List[str]] = {}
    for f in runtime_findings:
        for var in f.placeholders:
            runtime_vars.add(var)
            by_var.setdefault(var, []).append(f.path)

    env_example = repo_root / ".env.example"
    env_keys = _parse_env_example_keys(env_example)

    missing_in_env_example = sorted([v for v in runtime_vars if v not in env_keys])

    return {
        "runtime_placeholders": {
            "count": len(runtime_vars),
            "vars": sorted(runtime_vars),
            "locations": {k: sorted(v) for k, v in sorted(by_var.items())},
        },
        "non_runtime_dollar_curly": {
            "files_count": len(non_runtime_by_path),
            "by_file": non_runtime_by_path,
        },
        "env_example": {
            "path": str(env_example.relative_to(repo_root)).replace("\\", "/"),
            "keys_count": len(env_keys),
            "missing_keys_for_runtime_placeholders": missing_in_env_example,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    report = _build_report(repo_root)

    runtime_count = report["runtime_placeholders"]["count"]
    missing = report["env_example"]["missing_keys_for_runtime_placeholders"]

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        runtime = report["runtime_placeholders"]
        print("--- Placeholder Audit ---")
        print(f"Runtime placeholders: {runtime['count']}")
        for var in runtime["vars"]:
            locs = report["runtime_placeholders"]["locations"].get(var, [])
            print(f"  - {var}  ({len(locs)} files)")

        print("")
        print(f".env.example keys: {report['env_example']['keys_count']}")
        if missing:
            print("Missing in .env.example:")
            for k in missing:
                print(f"  - {k}")
        else:
            print("All runtime placeholders are covered by .env.example")

        if runtime_count:
            print("")
            print(
                "FAIL: Runtime placeholders were found in JSON configs. "
                "This repo expects zero ${NAME} placeholders in tracked JSON."
            )

        print("")
        print(
            "Note: Non-runtime ${...} (bash/powershell/github actions templating) "
            "is reported separately in --json mode."
        )

    if runtime_count:
        return 3
    return 2 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
