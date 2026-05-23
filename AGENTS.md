# Agents index (GymnasiumAgents hub)

Open **`GymnasiumAgents.code-workspace`** from this repository. Do not use single-repo workspaces for routine work.

## Subagents

| Agent | File | Use for |
|-------|------|---------|
| **ai-rl-sme** | `.cursor/agents/ai-rl-sme.md` | Training, eval, metrics, checkpoints, experiment memory-bank |
| **dev** | `.cursor/agents/dev.md` | Python structure, `common/`, tooling, tests, refactors |

The parent agent delegates using `.cursor/rules/04-orchestration.mdc`.

## Context locations

| Scope | Path |
|-------|------|
| Hub (cross-repo) | `system-context/` |
| Registry | `registry/projects.yaml` |
| Gynasium experiments | `../Gynasium/memory-bank/` |
| GymnasiumTwo experiments | `../GymnasiumTwo/memory-bank/` |

## Skills

| Skill | Purpose |
|-------|---------|
| `verify-workspace` | Confirm required repos are on disk |
| `rl-train-eval` | Train/eval workflow + capture results |
| `update-memory-bank` | Tiered updates in code repos |

## Verify setup

```bash
python scripts/verify_workspace.py
```
