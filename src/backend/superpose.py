#!/usr/bin/python3

import configparser
import git
import pathlib
from colorama import Fore, Back, Style

CFG_FILE = '/etc/portage/repos.conf/eselect-repo.conf'


def is_cfg_useful(path):
    with path.open() as f:
        useful_lines = [
            line.strip()
            for line in f
            if line.strip() and not line.lstrip().startswith("#")
        ]
    return bool(useful_lines)


def is_cfg_valid():
    cfg_path = pathlib.Path(CFG_FILE)
    if not cfg_path.is_file():
        print(f"\n{Fore.RED}Config file {Style.RESET_ALL}{CFG_FILE}{Fore.RED} not found, nothing to do!{Style.RESET_ALL}\n")
        return False

    if not is_cfg_useful(cfg_path):
        print(f"\n{Fore.RED}Config file {Style.RESET_ALL}{CFG_FILE}{Fore.RED} has no repositories configured, nothing to do!{Style.RESET_ALL}\n")
        return False

    return True


def clone_overlays():
    config = configparser.ConfigParser()
    config.read(CFG_FILE)

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
            print(
                f"\n{Fore.GREEN}Cloning {Style.RESET_ALL}{repo_name}{Fore.GREEN} from {Style.RESET_ALL}{sync_uri}{Fore.GREEN} to {Style.RESET_ALL}{location}{Fore.GREEN} (depth=1) {Style.RESET_ALL}...")
            try:
                git.Repo.clone_from(sync_uri, location, depth=1)
                print(
                    f"{Fore.GREEN}Successfully cloned {Style.RESET_ALL}{repo_name}")
            except Exception as e:
                print(
                    f"{Fore.RED}Error cloning {Style.RESET_ALL}{repo_name} : {Fore.RED}{e}{Style.RESET_ALL}")
        else:
            print(
                f"\n{Fore.RED}Sync type {Style.RESET_ALL}{sync_type}{Fore.RED} not supported for {Style.RESET_ALL}{repo_name}\n")


def start():
    if is_cfg_valid():
        clone_overlays()
