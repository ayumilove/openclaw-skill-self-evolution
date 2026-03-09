#!/usr/bin/env python3
"""Quick-validate this skill folder using OpenClaw's quick validator.

This script intentionally avoids hard-coded install paths.

Resolution order for the validator script:
1) $OPENCLAW_SKILL_VALIDATOR (explicit override)
2) `node -p "require.resolve('openclaw/package.json')"` + known relative path
3) `npm root -g` + known relative path (best-effort)

Usage:
  quick_validate_skill.py [--skill-dir /path/to/skill] [--validator /path/to/quick_validate.py]

Default skill dir: directory containing this script/..
"""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


def _try(cmd: list[str]) -> str | None:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        s = out.decode("utf-8", errors="replace").strip()
        return s or None
    except Exception:
        return None


def resolve_validator(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"--validator not found: {p}")
        return p

    env = os.environ.get("OPENCLAW_SKILL_VALIDATOR")
    if env:
        p = Path(env).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"OPENCLAW_SKILL_VALIDATOR not found: {p}")
        return p

    # Try to locate the OpenClaw npm package root via node resolution.
    pkg_json = _try(["node", "-p", "require.resolve('openclaw/package.json')"])
    if pkg_json:
        root = Path(pkg_json).resolve().parent
        candidate = root / "skills" / "skill-creator" / "scripts" / "quick_validate.py"
        if candidate.exists():
            return candidate

    # Best-effort fallback via npm root -g
    npm_root = _try(["npm", "root", "-g"])
    if npm_root:
        candidate = Path(npm_root).resolve() / "openclaw" / "skills" / "skill-creator" / "scripts" / "quick_validate.py"
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "Could not locate OpenClaw quick_validate.py. "
        "Pass --validator /path/to/quick_validate.py or set OPENCLAW_SKILL_VALIDATOR."
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--skill-dir", default=None)
    p.add_argument("--validator", default=None)
    args = p.parse_args()

    skill_dir = Path(args.skill_dir).expanduser().resolve() if args.skill_dir else Path(__file__).resolve().parent.parent

    validator = resolve_validator(args.validator)
    cmd = ["python3", str(validator), str(skill_dir)]
    print("Running:", " ".join(cmd))
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
