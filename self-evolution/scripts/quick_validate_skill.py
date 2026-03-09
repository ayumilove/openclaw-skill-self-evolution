#!/usr/bin/env python3
"""Quick-validate this skill folder using OpenClaw's validator.

Usage:
  quick_validate_skill.py [--skill-dir /path/to/skill]

Default skill dir: directory containing this script/..
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--skill-dir", default=None)
    args = p.parse_args()

    if args.skill_dir:
        skill_dir = Path(args.skill_dir)
    else:
        skill_dir = Path(__file__).resolve().parent.parent

    validator = Path("/root/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/skills/skill-creator/scripts/quick_validate.py")
    cmd = ["python3", str(validator), str(skill_dir)]
    print("Running:", " ".join(cmd))
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
