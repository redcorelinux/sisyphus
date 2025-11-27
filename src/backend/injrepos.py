#!/usr/bin/python3

import animation
import configparser
import git
import pathlib

HEADER_MARKER = "# created by eselect-repo"


def cfg_check(path: pathlib.Path) -> bool:
    with path.open() as f:
        useful_lines = [
            line.strip()
            for line in f
            if line.strip() and not line.lstrip().startswith("#")
        ]
    return not useful_lines


@animation.wait('injecting eselect-repository ebuild overlays')
def inject_repos(cfg_file='/etc/portage/repos.conf/eselect-repo.conf'):
    cfg_path = pathlib.Path(cfg_file)
    if not cfg_path.is_file():
        print(f"Config file {cfg_file} not found, nothing to do.")
        return

    with cfg_path.open() as f:
        lines = [line.rstrip("\n") for line in f]

    non_empty = [l for l in lines if l.strip()]
    if non_empty and all(l.strip().startswith(HEADER_MARKER) for l in non_empty):
        print(
            f"Config file {cfg_file} only has eselect-repo header, nothing to do.")
        return

    if cfg_check(cfg_path):
        print(
            f"Config file {cfg_file} has no repositories configured, nothing to do.")
        return

    config = configparser.ConfigParser()
    config.read(cfg_file)

    for repo_name in config.sections():
        location = config[repo_name].get('location')
        sync_uri = config[repo_name].get('sync-uri')
        sync_type = config[repo_name].get('sync-type')

        if not location or not sync_uri:
            continue

        repo_path = pathlib.Path(location)
        if repo_path.exists():
            continue

        repo_path.parent.mkdir(parents=True, exist_ok=True)

        if sync_type == 'git':
            try:
                git.Repo.clone_from(sync_uri, location, depth=1)
            except Exception as e:
                print(f"Error cloning {repo_name}: {e}")
        else:
            print(f"Sync type '{sync_type}' not supported for {repo_name}")


def start():
    inject_repos()
