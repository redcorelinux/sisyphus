#!/usr/bin/python3

import animation
import colorama
import os
import signal
import sys
import time
import sisyphus.checkenv
import sisyphus.getenv
import sisyphus.syncdb
import sisyphus.syncenv
import sisyphus.verifysig
from colorama import Fore, Back, Style

colorama.init()


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def gfx_sync():
    sisyphus.syncenv.repo_sync(sisyphus.getfs.gentoo_ebuild_dir, mode="hard")
    sisyphus.syncenv.repo_sync(sisyphus.getfs.redcore_ebuild_dir, mode="hard")
    sisyphus.syncenv.repo_sync(sisyphus.getfs.portage_cfg_dir, mode="stash")
    sisyphus.syncenv.overlay_sync("/var/db/repos", mode="hard")
    sisyphus.syncdb.remote_table()


@animation.wait('fetching updates')
def cli_sync():
    gfx_sync()


def start(verifysig=False, gfx_ui=False):
    active_branch = sisyphus.getenv.system_branch()
    binpkg_addr = sisyphus.getenv.binpkg_addr()
    is_online = sisyphus.checkenv.connectivity()
    unread_count = sisyphus.checkenv.news()

    if is_online != 1:
        if gfx_ui:
            print("\nNo internet connection detected. Aborting!\n")
            for i in range(15, 0, -1):
                print(f"Killing application in : {i} seconds!")
                time.sleep(1)

            os.kill(os.getpid(), signal.SIGTERM)  # kill GUI window
        else:
            print(
                f"{Fore.RED}{Style.BRIGHT}\nNo internet connection detected; Aborting!\n{Style.RESET_ALL}")
            sys.exit()
    else:
        git_head_before = sisyphus.checkenv.git_head()

        if gfx_ui:
            gfx_sync()
        else:
            cli_sync()

        git_head_after = sisyphus.checkenv.git_head()

        git_synced = git_head_before != git_head_after and git_head_before is not None

        if verifysig and git_synced:
            sisyphus.verifysig.portage_tree(gfx_ui=gfx_ui)

        if gfx_ui:
            print(
                f"\n\nThere are {unread_count} unread Redcore Linux Project news article(s).")
        else:
            if unread_count > 0:
                print(
                    f"\n\nThere are {Fore.RED}{Style.BRIGHT}{unread_count}{Style.RESET_ALL} unread {Fore.WHITE}{Style.BRIGHT}Redcore Linux Project{Style.RESET_ALL} news article(s).")
            else:
                print(
                    f"\n\nThere are {Fore.GREEN}{unread_count}{Style.RESET_ALL} unread {Fore.WHITE}{Style.BRIGHT}Redcore Linux Project{Style.RESET_ALL} news article(s).")
