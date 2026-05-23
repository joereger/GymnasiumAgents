---
name: verify-workspace
description: Verifies required code repos from registry/projects.yaml are present on disk. Use when opening the workspace, when a path is missing, or before cross-repo tasks.
---

# Verify workspace

## Quick check

From the **GymnasiumAgents** root:

```bash
python scripts/verify_workspace.py
```

Exit code `0` = all required projects found; non-zero = missing folder(s).

## If verification fails

1. Open **File → Open Workspace from File**
2. Choose `GymnasiumAgents/GymnasiumAgents.code-workspace` (not a single-repo workspace)
3. Ensure sibling folders exist: `../Gynasium`, `../GymnasiumTwo` relative to the hub
4. Re-run the script

## Agent behavior

When `registry/projects.yaml` lists a required project whose `relative_path` is not a directory, tell the user exactly which `folder_name` to add to the workspace file—do not proceed with paths outside the workspace.
