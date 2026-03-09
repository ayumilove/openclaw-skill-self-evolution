#!/usr/bin/env python3
"""Append a learning record as JSONL under memory/self-evolution.jsonl.

Usage:
  log_learning.py --trigger "..." --fix "..." [--root-cause "..."] [--verify "..."]
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--trigger", required=True)
    p.add_argument("--symptom", default="")
    p.add_argument("--root-cause", default="")
    p.add_argument("--fix", required=True)
    p.add_argument("--prevention", default="")
    p.add_argument("--verify", default="")
    p.add_argument("--tags", default="")
    args = p.parse_args()

    ts = datetime.now(timezone.utc).isoformat()
    rec = {
        "ts": ts,
        "trigger": args.trigger,
        "symptom": args.symptom,
        "rootCause": args.root_cause,
        "fix": args.fix,
        "prevention": args.prevention,
        "verify": args.verify,
        "tags": [t for t in (args.tags.split(",") if args.tags else []) if t.strip()],
        "cwd": os.getcwd(),
    }

    mem_dir = Path("memory")
    mem_dir.mkdir(parents=True, exist_ok=True)
    out = mem_dir / "self-evolution.jsonl"
    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
