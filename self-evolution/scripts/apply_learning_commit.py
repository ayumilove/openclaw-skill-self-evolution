#!/usr/bin/env python3
"""Persist a learning + optionally commit changes.

This script is intentionally conservative. It will:
- Append a learning record (JSONL) to memory/self-evolution.jsonl
- Optionally run a verification command
- Optionally create a git commit of **staged changes only** when you pass --allow-commit

Usage examples:
  # Just log
  ./apply_learning_commit.py --trigger "..." --fix "..."

  # Log + verify
  ./apply_learning_commit.py --trigger "..." --fix "..." --verify "openclaw channels status --probe --timeout 60000"

  # Log + verify + commit (staged changes only)
  ./apply_learning_commit.py --trigger "..." --fix "..." --verify "pytest" \
    --allow-commit --commit-message "fix: improve preflight" \
    --repo-root .

Notes:
- By default the script stages with `git add -A` (see --stage).
- For extra safety you can require a clean tree before staging with --require-clean.
- A simple secrets scan is performed on staged content by default; disable with --no-secrets-scan.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("OpenAI key", re.compile(r"\bsk-[A-Za-z0-9]{16,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z\-_]{20,}\b")),
    ("Private key header", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
]


def run(cmd: str, cwd: Path | None = None) -> int:
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, shell=True)
    return p.returncode


def capture(cmd: list[str], cwd: Path) -> str:
    out = subprocess.check_output(cmd, cwd=str(cwd))
    return out.decode("utf-8", errors="replace")


def git_show(repo: Path, spec: str) -> bytes:
    return subprocess.check_output(["git", "show", spec], cwd=str(repo))


def scan_staged_for_secrets(repo: Path, files: list[str]) -> list[str]:
    hits: list[str] = []
    for f in files:
        try:
            blob = git_show(repo, f":{f}")
        except Exception:
            # Removed files, binary files, or other edge cases.
            continue

        text = blob.decode("utf-8", errors="replace")
        for label, pat in SECRET_PATTERNS:
            if pat.search(text):
                hits.append(f"{label}: {f}")

    return hits


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
    ap.add_argument(
        "--require-clean",
        action="store_true",
        help="Require a clean working tree before staging (extra safety, optional)",
    )
    ap.add_argument(
        "--secrets-scan",
        action="store_true",
        default=True,
        help="Scan staged files for common secret patterns before committing (default: on)",
    )
    ap.add_argument(
        "--no-secrets-scan",
        action="store_false",
        dest="secrets_scan",
        help="Disable secrets scan (NOT recommended)",
    )

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

    if args.require_clean:
        dirty = capture(["git", "status", "--porcelain"], cwd=repo).strip()
        if dirty:
            print(
                "Refusing to commit: working tree not clean (required by --require-clean).\n"
                "Commit from a clean tree, or re-run without --require-clean."
            )
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

    if args.secrets_scan:
        staged_files = [p for p in diff_cached.splitlines() if p.strip()]
        hits = scan_staged_for_secrets(repo, staged_files)
        if hits:
            print("Potential secrets detected in staged content; refusing to commit:")
            for h in hits[:50]:
                print("-", h)
            print(
                "If this is a false positive, edit the file to remove/obfuscate, "
                "or re-run with --no-secrets-scan."
            )
            return 3

    subprocess.check_call(["git", "commit", "-m", args.commit_message], cwd=str(repo))
    print("Committed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
