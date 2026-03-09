#!/usr/bin/env python3
"""Persist a learning + optionally commit changes.

This script is intentionally conservative. It will:
- Append a learning record (JSONL) to memory/self-evolution.jsonl
- Optionally run a verification command
- Optionally git-commit *only if* the repo is clean and you pass --allow-commit

Usage examples:
  # Just log
  ./apply_learning_commit.py --trigger "..." --fix "..."

  # Log + verify
  ./apply_learning_commit.py --trigger "..." --fix "..." --verify "openclaw channels status --probe --timeout 60000"

  # Log + verify + commit
  ./apply_learning_commit.py --trigger "..." --fix "..." --verify "pytest" \
    --allow-commit --commit-message "fix: improve preflight" \
    --repo-root .
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def run(cmd: str, cwd: Path | None = None) -> int:
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, shell=True)
    return p.returncode


def capture(cmd: list[str], cwd: Path) -> str:
    out = subprocess.check_output(cmd, cwd=str(cwd))
    return out.decode("utf-8", errors="replace")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trigger", required=True)
    ap.add_argument("--symptom", default="")
    ap.add_argument("--root-cause", default="")
    ap.add_argument("--fix", required=True)
    ap.add_argument("--prevention", default="")
    ap.add_argument("--verify", default="")
    ap.add_argument("--tags", default="")

    ap.add_argument("--repo-root", default=None, help="Path to git repo root (optional)")
    ap.add_argument("--allow-commit", action="store_true", help="Actually create a git commit")
    ap.add_argument("--commit-message", default="chore: record learning")
    ap.add_argument("--stage", default="-A", help="What to stage before commit (default: -A)")

    args = ap.parse_args()

    # 1) Write learning record
    ts = datetime.now(timezone.utc).isoformat()
    rec = {
        "ts": ts,
        "trigger": args.trigger,
        "symptom": args.symptom,
        "rootCause": args.root_cause,
        "fix": args.fix,
        "prevention": args.prevention,
        "verify": args.verify,
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
        "cwd": os.getcwd(),
    }

    mem_dir = Path("memory")
    mem_dir.mkdir(parents=True, exist_ok=True)
    out = mem_dir / "self-evolution.jsonl"
    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Wrote: {out}")

    # 2) Verify
    if args.verify:
        print(f"Running verify: {args.verify}")
        rc = run(args.verify)
        if rc != 0:
            print(f"Verify failed with exit code {rc}; skipping commit.")
            return rc

    # 3) Commit (optional)
    if not args.allow_commit:
        return 0

    if not args.repo_root:
        print("--allow-commit set but --repo-root missing; refusing to commit.")
        return 2

    repo = Path(args.repo_root).resolve()
    if not (repo / ".git").exists():
        print(f"Not a git repo: {repo}")
        return 2

    dirty = capture(["git", "status", "--porcelain"], cwd=repo).strip()
    if dirty:
        # It's OK to be dirty (we're about to commit), but require the caller to start from clean.
        # This prevents accidental commits of unrelated changes.
        print("Refusing to commit: working tree not clean BEFORE staging.\n"
              "Start from a clean tree, then re-run.")
        return 2

    # Stage
    stage_args = shlex.split(args.stage)
    stage_cmd = ["git", "add", *stage_args]
    subprocess.check_call(stage_cmd, cwd=str(repo))

    # Ensure we actually have something to commit
    diff_cached = capture(["git", "diff", "--cached", "--name-only"], cwd=repo).strip()
    if not diff_cached:
        print("Nothing staged; no commit created.")
        return 0

    subprocess.check_call(["git", "commit", "-m", args.commit_message], cwd=str(repo))
    print("Committed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
