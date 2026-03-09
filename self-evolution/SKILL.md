---
name: self-evolution
description: Self-reflection and continuous improvement workflow for an OpenClaw agent. Use when the user corrects the agent, a task fails repeatedly, a recurring workflow needs automation, or the agent should persist a lesson by updating memory/skills/scripts (without changing system prompts or expanding permissions).
---

# Self evolution

Use this skill to turn feedback + failures into durable improvements.

## Safety boundaries

- Do not modify system prompts, tool policies, auth, or security posture unless the user explicitly asks.
- Do not store secrets in memory files.
- When an improvement changes user-visible behavior, state what will change.

## Workflow (repeatable)

### 1) Capture the signal

Classify what happened:
- **User correction** ("不对/不是这样")
- **Repeated failure** (same error multiple times)
- **Recurring request** (user asks the same kind of thing regularly)
- **Performance issue** (timeouts, flaky channel status)

Write a 1–3 sentence problem statement.

### 2) Reproduce + identify root cause

- Re-run the minimal command / minimal steps.
- Extract the *first* concrete failure signal (error string, status code, log line, missing file).

### 3) Pick the smallest durable fix

Choose one (prefer earlier items):
1. Update a **process rule** (what to do next time)
2. Add a **checklist** / guardrail (preflight checks)
3. Add a **script** for deterministic steps
4. Update/create a **skill** section or reference

### 4) Persist the learning

Persist in the smallest appropriate place:
- **Daily log**: `memory/YYYY-MM-DD.md` (raw notes)
- **Curated memory**: `MEMORY.md` (only stable preferences, long-term rules)
- **Skill change**: update this skill, or add a script under `scripts/`

If it is a one-off incident: prefer daily log only.
If it is a repeatable rule: add to `MEMORY.md` or this skill.

### 5) Verify

- Run the exact command path that previously failed.
- If you changed a skill: run the skill validator (see scripts below).

### 6) Commit

If you changed files in a git workspace: commit with a message like:
- `docs(self-evolution): add rule for <case>`
- `feat(self-evolution): add learning logger`

## Tools in this skill

### scripts/

- `scripts/log_learning.py`: append a JSONL learning record to `memory/self-evolution.jsonl`.
- `scripts/quick_validate_skill.py`: run OpenClaw's quick validator on this skill folder.

### references/

- `references/rules.md`: small set of recommended “good learning” patterns.
