---
name: rl-train-eval
description: Runs Gymnasium training and evaluation in Gynasium or GymnasiumTwo using the correct venv, captures metrics and artifact paths, and updates memory-bank. Use for train, eval, DQN, PPO, checkpoints, or data/ logs.
---

# RL train and eval

## Before running

1. Resolve project in `registry/projects.yaml` (`gynasium` | `gymnasium_two`).
2. Read env tier-1 memory-bank files if they exist.
3. `cd` to that repo root; activate its venv (see registry `venv`).

## Gynasium examples

```bash
cd ../Gynasium
source GymnasiumVENV/bin/activate
python bipedal_walker/bipedal_walker.py
```

## GymnasiumTwo examples

```bash
cd ../GymnasiumTwo
source .venv/bin/activate
python freeway/freeway_dqn.py --train
python freeway/freeway_dqn.py --eval --load-checkpoint
```

## After running

Record in memory-bank:

- Command(s) and main CLI flags
- Episode count, reward summary, checkpoint/plot paths under `data/`
- One-line comparison to prior runs if known
- 2–3 proposed next steps

Invoke skill **update-memory-bank** if many files need updates.
