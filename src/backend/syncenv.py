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
    local_branch = subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir, stderr=subprocess.DEVNULL,).decode().strip()

    remote_branch = subprocess.check_output(
        ["git", "rev-parse", "--symbolic-full-name", "@{u}"], cwd=repo_dir, stderr=subprocess.DEVNULL,).decode().strip()

    return local_branch, remote_branch


def repo_sync(repo_dir, mode="hard"):
    repo_dir = Path(repo_dir)

    if not (repo_dir / ".git").exists():
        return

    try:
        local_branch, remote_branch = get_branch(repo_dir)
    except subprocess.CalledProcessError:
        print(
            f"[WARN] Skipping {repo_dir}: no upstream or bad HEAD", file=sys.stderr)
        return

    upstream = remote_branch.replace("refs/remotes/", "")

    if mode == "stash":
        run_git(["git", "stash"], cwd=repo_dir)

    run_git(["git", "fetch", "--depth=1", "origin",
            local_branch, "--quiet"], cwd=repo_dir)

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
