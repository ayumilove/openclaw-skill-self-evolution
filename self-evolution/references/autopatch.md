# Autopatch & self-improvement protocol (reference)

Use this reference when a learning requires **changing files** (skills, scripts, configs, docs).

## Core idea

Turn “I learned X” into a *minimal, testable diff* that fixes the root cause and prevents recurrence.

## Safety rules

- Never change system prompts, tool policies, auth, or security posture unless explicitly requested by the user.
- Never commit secrets (API keys, tokens, cookies). If unsure, stop and ask.
- Prefer the smallest diff that solves the problem.

## Autopatch steps

1) **Select target**
- Skill text / reference doc / script / config.

2) **Make the minimal edit**
- Keep changes local and reversible.

3) **Run verification**
- Re-run the command that failed.
- If editing a skill: run the skill validator.

4) **Commit with intent**
- Use a message that explains *why*:
  - `fix(self-evolution): ...`
  - `docs(self-evolution): ...`
  - `feat(self-evolution): ...`

5) **Push only if appropriate**
- If the repo is public or shared, confirm there are no sensitive changes.

## Suggested preflight checks

- `git status --porcelain` must be clean before starting.
- `rg -n "sk-" -S .` / `rg -n "token" -S .` to sanity-check secrets before push.
