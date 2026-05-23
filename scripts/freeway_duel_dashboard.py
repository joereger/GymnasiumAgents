#!/usr/bin/env python3
"""Side-by-side Freeway duel dashboard (Gynasium vs GymnasiumTwo)."""

from __future__ import annotations

import argparse
import json
import signal
import subprocess
import sys
import time
from pathlib import Path

HUB_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = HUB_ROOT / "registry" / "projects.yaml"
SUMMARY_DIR = HUB_ROOT / "data" / "freeway_duel"
SUMMARY_PATH = SUMMARY_DIR / "summary.png"

DUEL_SUBDIR = Path("data") / "freeway" / "duel"
GYNASIUM_SCRIPT = Path("freeway") / "freeway.py"
GYMNASIUM_TWO_SCRIPT = Path("freeway") / "freeway_dqn.py"


def _load_projects() -> list[dict]:
    text = REGISTRY.read_text(encoding="utf-8")
    try:
        import yaml

        data = yaml.safe_load(text)
        return data.get("projects") or []
    except ImportError:
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
                if key in ("id", "relative_path", "venv"):
                    current[key] = val
        if current:
            projects.append(current)
        return projects


def _project_by_id(projects: list[dict], pid: str) -> dict:
    for proj in projects:
        if proj.get("id") == pid:
            return proj
    raise KeyError(f"Unknown project id: {pid}")


def _repo_root(proj: dict) -> Path:
    return (HUB_ROOT / proj["relative_path"]).resolve()


def _python(proj: dict) -> Path:
    return _repo_root(proj) / proj["venv"]


def _read_status(duel_dir: Path) -> dict | None:
    path = duel_dir / "live_status.json"
    if not path.is_file():
        return None
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _read_frame(duel_dir: Path):
    path = duel_dir / "latest_frame.png"
    if not path.is_file():
        return None
    try:
        from PIL import Image
        import numpy as np

        img = Image.open(path).convert("RGB")
        return np.asarray(img)
    except OSError:
        return None


def _spawn_demo(
    proj: dict,
    *,
    episodes: int,
    max_steps: int,
    duel_dir: Path,
) -> subprocess.Popen:
    root = _repo_root(proj)
    script = GYNASIUM_SCRIPT if proj["id"] == "gynasium" else GYMNASIUM_TWO_SCRIPT
    py = _python(proj)
    cmd = [
        str(py),
        str(script),
        "--dashboard-mode",
        "--episodes",
        str(episodes),
        "--max-steps-per-episode",
        str(max_steps),
        "--duel-dir",
        str(duel_dir),
    ]
    return subprocess.Popen(
        cmd,
        cwd=str(root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def _format_status(label: str, status: dict | None) -> str:
    if not status:
        return f"{label}\n(waiting…)"
    state = status.get("state", "?")
    ep = status.get("episode", 0)
    total = status.get("episodes_total", 0)
    step = status.get("step", 0)
    rew = status.get("episode_reward", 0.0)
    mean_k = status.get("mean_reward_last_k")
    mean_s = f"{mean_k:.2f}" if mean_k is not None else "—"
    err = status.get("error")
    lines = [
        label,
        f"state: {state}",
        f"episode: {ep}/{total}  step: {step}",
        f"episode_reward: {rew:.2f}  mean_last_k: {mean_s}",
        f"epsilon: {status.get('epsilon', 0):.4f}",
        f"checkpoint: {status.get('checkpoint', '')}",
    ]
    if err:
        lines.append(f"error: {err}")
    return "\n".join(lines)


def _both_finished(status_a: dict | None, status_b: dict | None) -> bool:
    terminal = {"done", "error"}

    def done(s: dict | None) -> bool:
        return s is not None and s.get("state") in terminal

    return done(status_a) and done(status_b)


def run_dashboard(
    episodes: int,
    fps: float,
    max_steps: int,
    no_gui: bool,
) -> int:
    projects = _load_projects()
    gyn = _project_by_id(projects, "gynasium")
    two = _project_by_id(projects, "gymnasium_two")
    duel_gyn = _repo_root(gyn) / DUEL_SUBDIR
    duel_two = _repo_root(two) / DUEL_SUBDIR

    for py, proj in ((_python(gyn), gyn), (_python(two), two)):
        if not py.is_file():
            print(f"Missing venv python: {py} ({proj['id']})", file=sys.stderr)
            return 1

    procs: list[subprocess.Popen] = []
    shutdown = False

    def _stop_children(*_args):
        nonlocal shutdown
        shutdown = True
        for p in procs:
            if p.poll() is None:
                p.terminate()

    signal.signal(signal.SIGINT, _stop_children)
    signal.signal(signal.SIGTERM, _stop_children)

    try:
        procs.append(_spawn_demo(gyn, episodes=episodes, max_steps=max_steps, duel_dir=duel_gyn))
        procs.append(_spawn_demo(two, episodes=episodes, max_steps=max_steps, duel_dir=duel_two))
    except OSError as exc:
        print(f"Failed to spawn demo: {exc}", file=sys.stderr)
        _stop_children()
        return 1

    interval = 1.0 / max(fps, 1.0)
    use_gui = not no_gui

    if use_gui:
        import matplotlib.pyplot as plt

        plt.ion()
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        ax_gyn, ax_two = axes[0]
        ax_status = axes[1, 0]
        axes[1, 1].axis("off")
        ax_gyn.set_title("Gynasium")
        ax_two.set_title("GymnasiumTwo")
        ax_status.axis("off")
        status_text = ax_status.text(
            0.02,
            0.98,
            "",
            transform=ax_status.transAxes,
            va="top",
            ha="left",
            fontsize=9,
            family="monospace",
        )
        im_gyn = ax_gyn.imshow([[0]], aspect="auto")
        im_two = ax_two.imshow([[0]], aspect="auto")
        ax_gyn.axis("off")
        ax_two.axis("off")
        fig.tight_layout()
    else:
        fig = ax_gyn = ax_two = ax_status = status_text = im_gyn = im_two = None
        plt = None

    finished = False
    while not shutdown and not finished:
        status_gyn = _read_status(duel_gyn)
        status_two = _read_status(duel_two)
        frame_gyn = _read_frame(duel_gyn)
        frame_two = _read_frame(duel_two)

        if use_gui and plt is not None:
            if frame_gyn is not None:
                im_gyn.set_data(frame_gyn)
                ax_gyn.set_title(f"Gynasium — ep {status_gyn.get('episode', 0) if status_gyn else 0}")
            if frame_two is not None:
                im_two.set_data(frame_two)
                ax_two.set_title(
                    f"GymnasiumTwo — ep {status_two.get('episode', 0) if status_two else 0}"
                )
            panel = "\n\n".join(
                [
                    _format_status("Gynasium", status_gyn),
                    _format_status("GymnasiumTwo", status_two),
                ]
            )
            status_text.set_text(panel)
            fig.canvas.draw_idle()
            fig.canvas.flush_events()
            if not plt.fignum_exists(fig.number):
                shutdown = True
                break
            plt.pause(interval)
        else:
            time.sleep(interval)

        if _both_finished(status_gyn, status_two):
            finished = True
            break

        if all(p.poll() is not None for p in procs) and not finished:
            finished = True

    _stop_children()
    for p in procs:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()

    if use_gui and plt is not None and fig is not None and plt.fignum_exists(fig.number):
        status_gyn = _read_status(duel_gyn)
        status_two = _read_status(duel_two)
        frame_gyn = _read_frame(duel_gyn)
        frame_two = _read_frame(duel_two)
        if frame_gyn is not None:
            im_gyn.set_data(frame_gyn)
        if frame_two is not None:
            im_two.set_data(frame_two)
        status_text.set_text(
            "\n\n".join(
                [
                    _format_status("Gynasium (final)", status_gyn),
                    _format_status("GymnasiumTwo (final)", status_two),
                ]
            )
        )
        SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(SUMMARY_PATH, dpi=120, bbox_inches="tight")
        if not no_gui:
            plt.ioff()
            plt.show(block=False)
    elif no_gui:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        for ax, duel_dir, title in (
            (axes[0], duel_gyn, "Gynasium"),
            (axes[1], duel_two, "GymnasiumTwo"),
        ):
            frame = _read_frame(duel_dir)
            if frame is not None:
                ax.imshow(frame)
            ax.set_title(title)
            ax.axis("off")
        SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(SUMMARY_PATH, dpi=120, bbox_inches="tight")
        plt.close(fig)

    metrics_gyn = duel_gyn / "metrics.json"
    metrics_two = duel_two / "metrics.json"
    print(f"Summary image: {SUMMARY_PATH}")
    print(f"Gynasium metrics: {metrics_gyn}")
    print(f"GymnasiumTwo metrics: {metrics_two}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Freeway duel dashboard (hub)")
    parser.add_argument("--episodes", type=int, default=5, help="Episodes per repo (default: 5)")
    parser.add_argument("--fps", type=float, default=15.0, help="UI poll rate (default: 15)")
    parser.add_argument(
        "--max-steps-per-episode",
        type=int,
        default=500,
        help="Passed to demo-eval subprocesses (default: 500)",
    )
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Headless: poll until done, write summary.png",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return run_dashboard(
        episodes=args.episodes,
        fps=args.fps,
        max_steps=args.max_steps_per_episode,
        no_gui=args.no_gui,
    )


if __name__ == "__main__":
    raise SystemExit(main())
