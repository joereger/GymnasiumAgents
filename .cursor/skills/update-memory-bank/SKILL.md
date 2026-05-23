---
name: update-memory-bank
description: Updates tiered memory-bank markdown in Gynasium or GymnasiumTwo after experiments or code changes. Use when the user says update memory bank or after substantive RL or architecture work in a code repo.
---

# Update memory-bank (code repos)

Applies to **Gynasium** and **GymnasiumTwo** only—not hub `system-context/`.

## Checklist

1. Identify repo and environment from `registry/projects.yaml`.
2. Read current `memory-bank/activeContext.md` and `progress.md` (and env copies if applicable).
3. Update:
   - **Always:** `activeContext.md`, `progress.md` (repo + env if relevant)
   - **After experiments:** env `approaches.md` (what ran, outcome, next hypothesis)
   - **After structural change:** `systemPatterns.md`, `techContext.md`
4. On first structured work in GymnasiumTwo, create missing top-level memory-bank files if needed.

## Hub vs code repo

| Location | When to update |
|----------|----------------|
| `<repo>/memory-bank/` | Experiment and env state |
| `GymnasiumAgents/system-context/` | Registry, workspace, cross-repo milestones only |

Use direct file edits in the repository.
