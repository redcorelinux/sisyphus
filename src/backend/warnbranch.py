#!/usr/bin/python3

import typer
import sisyphus.getenv

def start(branch=None, quiet=False):
    if quiet:
        return
    branch = branch or sisyphus.getenv.system_branch()
    if branch != "next":
        return
    
    typer.secho(
        f"\nWARNING: Branch '{branch}' detected (testing/development)."
        f"\n• Sisyphus GUI disabled — use Sisyphus CLI instead."
        f"\n• sisyphus install: --ebuild option enabled by default."
        f"\n• sisyphus upgrade: --ebuild option enabled by default."
        f"\n• sisyphus search: binary search inaccurate — use --ebuild option."
        f"\n• 'emerge --sync' BROKEN — use 'sisyphus update' to sync the trees."
        f"\n• 'emaint sync -a' BROKEN — use 'sisyphus update' to sync the trees."
        f"\n• Binary package availability lags behind the git (source) state.",
        fg=typer.colors.YELLOW
    )
