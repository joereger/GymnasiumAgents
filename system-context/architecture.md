# Architecture: Gymnasium multi-repo workspace

This document describes how the **hub** (`GymnasiumAgents`) relates to the **code repos** (`Gynasium`, `GymnasiumTwo`). Open **`GymnasiumAgents.code-workspace`** from this folder as the single entry point for Cursor.

## Roles

| Location | Purpose |
|----------|---------|
| **GymnasiumAgents/** | Agent personas, Cursor rules/skills, project registry, **system-context/** (hub-level narrative only) |
| **Gynasium/** | Python Gymnasium experiments — older, broad env coverage |
| **GymnasiumTwo/** | Python Gymnasium experiments — focused Atari stack with shared `common/` |

Experiment progress, hyperparameters, and per-environment notes live in each code repo under **`memory-bank/`**, not in the hub.

## Gynasium (per-environment self-containment)

```
Gynasium/
├── GymnasiumVENV/          # project virtualenv
├── memory-bank/            # Cline-style context (project + environments/*)
├── data/<env_name>/        # models, logs per environment
├── bipedal_walker/         # code + local utils
├── cart_pole/
├── lunar_lander/
├── mountain_car/
├── pong/                   # (also present in GymnasiumTwo)
└── freeway/                # (also present in GymnasiumTwo)
```

**Layout:** `per_env_self_contained` — each environment folder holds its scripts and helpers; artifacts go to `data/<env_name>/`. Document env-specific work in `memory-bank/environments/<env_name>/`.

## GymnasiumTwo (shared common module)

```
GymnasiumTwo/
├── .venv/                  # local virtualenv (separate from Gynasium)
├── memory-bank/            # add as experiments mature
├── common/                 # atari_env.py, dqn.py — shared by games
├── data/<game>/            # checkpoints, plots
├── pong/
└── freeway/
```

**Layout:** `shared_common` — game folders import from `common/`; do not duplicate preprocessing across `pong/` and `freeway/` unless intentionally forking.

## Virtual environments

| Repo | Interpreter (from repo root) |
|------|------------------------------|
| Gynasium | `GymnasiumVENV/bin/python` |
| GymnasiumTwo | `.venv/bin/python` |

Never assume one venv for both repos.

## Registry

Machine-readable paths and layout flags: **`registry/projects.yaml`**.

Run **`python scripts/verify_workspace.py`** from the hub to confirm all required workspace folders are present.

## Scaling to more repos (work pattern)

Add a `projects.yaml` entry, add a folder to `GymnasiumAgents.code-workspace`, and extend this file with a short subsection. Optional repos can set `required: false` in the registry.
