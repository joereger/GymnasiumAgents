#!/usr/bin/env python3
"""Verify multi-root workspace folders match registry/projects.yaml."""

from __future__ import annotations

import sys
from pathlib import Path

HUB_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = HUB_ROOT / "registry" / "projects.yaml"


def _load_projects() -> list[dict]:
    text = REGISTRY.read_text(encoding="utf-8")
    try:
        import yaml

        data = yaml.safe_load(text)
        return data.get("projects") or []
    except ImportError:
        return _parse_projects_minimal(text)


def _parse_projects_minimal(text: str) -> list[dict]:
    """Parse projects.yaml without PyYAML (list entries only)."""
    projects: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            if current:
                projects.append(current)
            current = {"id": stripped.split(":", 1)[1].strip()}
        elif current is not None and ":" in stripped:
            key, _, val = stripped.partition(":")
            key, val = key.strip(), val.strip()
            if key == "required":
                current[key] = val.lower() == "true"
            elif key in ("id", "folder_name", "relative_path", "name"):
                current[key] = val
    if current:
        projects.append(current)
    return projects


def main() -> int:
    if not REGISTRY.is_file():
        print(f"Missing registry: {REGISTRY}", file=sys.stderr)
        return 1

    projects = _load_projects()
    missing_required: list[str] = []
    present: list[str] = []
    optional_missing: list[str] = []

    for proj in projects:
        pid = proj.get("id", "?")
        rel = proj.get("relative_path", "")
        required = proj.get("required", True)
        path = (HUB_ROOT / rel).resolve()

        if path.is_dir():
            present.append(f"  OK  {pid}: {path}")
        elif required:
            missing_required.append(
                f"  MISSING (required) {pid}: {path}\n"
                f"         Add folder to GymnasiumAgents.code-workspace "
                f"(name: {proj.get('folder_name', pid)})"
            )
        else:
            optional_missing.append(f"  optional absent {pid}: {path}")

    print("GymnasiumAgents workspace verification\n")
    for line in present:
        print(line)

    if optional_missing:
        print()
        for line in optional_missing:
            print(line)

    if missing_required:
        print("\nRequired projects not found:", file=sys.stderr)
        for line in missing_required:
            print(line, file=sys.stderr)
        print(
            "\nFix: File → Open Workspace from File → "
            "GymnasiumAgents/GymnasiumAgents.code-workspace",
            file=sys.stderr,
        )
        return 1

    print("\nAll required projects present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
