# self-evolution (OpenClaw Skill)

A lightweight skill that helps an OpenClaw agent **learn from corrections and failures** and make improvements that persist (memory updates, skill updates, small scripts), with clear safety boundaries.

## What it does

This skill provides a repeatable workflow:

1. Capture the signal (user correction / repeated failure / recurring request)
2. Reproduce and find the root cause
3. Pick the smallest durable fix
4. Persist the learning (daily log / curated memory / skill or scripts)
5. Verify
6. Commit

## Safety boundaries

- Do **not** modify system prompts, tool policies, auth, or security posture unless the user explicitly asks.
- Do **not** store secrets in memory files.
- If an improvement changes user-visible behavior, explicitly say what will change.

## Repo layout

```
self-evolution/
  SKILL.md
  references/
    rules.md
  scripts/
    log_learning.py
    quick_validate_skill.py
    apply_learning_commit.py
```

## Installing into OpenClaw

Option A (copy into the OpenClaw skills directory):

```bash
# adjust path if your OpenClaw state dir differs
mkdir -p ~/.openclaw/skills
cp -a ./self-evolution ~/.openclaw/skills/
```

Option B (use your own skills path):

- Keep this repo somewhere stable and configure OpenClaw to include that skills directory.

## Validate the skill

```bash
python3 self-evolution/scripts/quick_validate_skill.py
```

## Record a learning entry (JSONL)

From a workspace that has a `memory/` folder (or it will be created):

```bash
python3 self-evolution/scripts/log_learning.py \
  --trigger "channels status timed out" \
  --symptom "Request timed out before a response was generated" \
  --root-cause "CLI timeout too low" \
  --fix "Re-run with --timeout 60000" \
  --verify "openclaw channels status --probe --timeout 60000"
```

Output file:
- `memory/self-evolution.jsonl`

## Apply a learning and commit safely (optional)

This helper can log the learning, run an optional verify command, then create a git commit **only from staged changes**.

```bash
python3 self-evolution/scripts/apply_learning_commit.py \
  --trigger "Fix validator portability" \
  --fix "Make validator path portable" \
  --verify "python3 self-evolution/scripts/quick_validate_skill.py" \
  --allow-commit \
  --repo-root . \
  --commit-message "fix: portable validator"
```

It also runs a basic **secrets scan** on staged content by default.

## License

MIT
