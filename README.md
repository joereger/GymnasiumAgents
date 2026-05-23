# GymnasiumAgents

Central **Cursor hub** for multi-repo Gymnasium reinforcement-learning work. Code lives in sibling repos; agents, rules, and workspace orchestration live here.

## Quick start

1. Clone/check out sibling repos next to this folder:
   - `../Gynasium`
   - `../GymnasiumTwo`
2. In Cursor: **File → Open Workspace from File** → `GymnasiumAgents.code-workspace`
3. Verify:

```bash
cd GymnasiumAgents
pip install -r requirements.txt   # optional, for verify script
python scripts/verify_workspace.py
```

**Freeway duel dashboard** (runs demo-eval in both code repos; needs trained checkpoints):

```bash
pip install -r requirements.txt
python scripts/freeway_duel_dashboard.py
```

Use `--no-gui` for headless polling; `--episodes`, `--fps`, and `--max-steps-per-episode` adjust the run.

## Layout

```
GymnasiumAgents/
├── GymnasiumAgents.code-workspace   # ← open this
├── registry/projects.yaml           # required repos, paths, layouts
├── system-context/                  # hub narrative (not memory-bank)
│   ├── architecture.md
│   ├── activeContext.md
│   └── progress.md
├── .cursor/
│   ├── rules/                       # always-on hub rules
│   ├── agents/                      # ai-rl-sme, dev
│   └── skills/
├── scripts/verify_workspace.py
└── AGENTS.md
```

## Code repos

| Repo | Role | Context in repo |
|------|------|-----------------|
| [Gynasium](../Gynasium) | Broad Gymnasium envs, per-env self-contained layout | `memory-bank/` |
| [GymnasiumTwo](../GymnasiumTwo) | Atari DQN, shared `common/` | `memory-bank/` (seed as needed) |

See **`system-context/architecture.md`** for directory diagrams and venv notes.

## Adding another repo (work pattern)

1. Add entry to `registry/projects.yaml`
2. Add folder to `GymnasiumAgents.code-workspace`
3. Document in `system-context/architecture.md`
4. Run `python scripts/verify_workspace.py`
