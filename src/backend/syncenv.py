#!/usr/bin/python3

import os
import sys
import signal
import subprocess
import sisyphus.getfs
from pathlib import Path


def sigint_handler(signum, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def run_git(cmd, cwd=None):
    proc = subprocess.Popen(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)
    try:
        return proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        try:
            proc.wait(1)
        except subprocess.TimeoutExpired:
            proc.kill()
        sys.exit()


def get_branch(repo_dir):
    lcl_brch = subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir, stderr=subprocess.DEVNULL,).decode().strip()

    rmt_brch = subprocess.check_output(
        ["git", "rev-parse", "--symbolic-full-name", "@{u}"], cwd=repo_dir, stderr=subprocess.DEVNULL,).decode().strip()

    return lcl_brch, rmt_brch


def repo_sync(repo_dir, mode="hard"):
    repo_dir = Path(repo_dir)

    if not (repo_dir / ".git").exists():
        return

    try:
        lcl_brch, rmt_brch = get_branch(repo_dir)
    except subprocess.CalledProcessError:
        print(
            f"[WARN] Skipping {repo_dir}: no upstream or bad HEAD", file=sys.stderr)
        return

    upstream = rmt_brch.replace("refs/remotes/", "")

    if mode == "stash":
        run_git(["git", "stash"], cwd=repo_dir)

    run_git(["git", "fetch", "--depth=1", "origin",
            lcl_brch, "--quiet"], cwd=repo_dir)

    run_git(["git", "reset", "--hard", upstream, "--quiet"], cwd=repo_dir)

    if mode == "stash":
        run_git(["git", "stash", "apply"], cwd=repo_dir)
        run_git(["git", "stash", "clear"], cwd=repo_dir)
        run_git(["git", "gc", "--prune=now", "--quiet"], cwd=repo_dir)


def overlay_sync(base_dir, mode="hard"):
    base = Path(base_dir)
    for entry in base.iterdir():
        if not entry.is_dir():
            continue
        if not (entry / ".git").is_dir():
            continue

        repo_sync(entry, mode=mode)
