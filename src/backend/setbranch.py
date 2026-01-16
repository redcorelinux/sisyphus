#!/usr/bin/python3

import animation
import colorama
import git
import os
import random
import signal
import sys
import time
import sisyphus.checkenv
import sisyphus.getfs
import sisyphus.purgeenv
import sisyphus.setjobs
import sisyphus.setmirror
import sisyphus.setprofile
import sisyphus.warnbranch
from colorama import Fore, Back, Style

colorama.init()


branch_remote_map = {
    "master": {
        "github": sisyphus.getfs.rmt_gh_addr,
        "gitlab": sisyphus.getfs.rmt_gl_addr,
        "pagure": sisyphus.getfs.rmt_pg_addr,
        "codeberg": sisyphus.getfs.rmt_cb_addr
    },
    "next": {
        "github": sisyphus.getfs.rmt_gh_addr,
        "gitlab": sisyphus.getfs.rmt_gl_addr,
        "pagure": sisyphus.getfs.rmt_pg_addr,
        "codeberg": sisyphus.getfs.rmt_cb_addr
    }
}


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def get_branch_remote(branch, remote):
    gentoo_remote = []
    redcore_remote = []
    portage_cfg_remote = []

    if branch in branch_remote_map and remote in branch_remote_map[branch]:
        remote = branch_remote_map[branch][remote]
    else:
        # set a default remote here if needed
        pass

    gentoo_remote = [remote, sisyphus.getfs.g_repo]
    redcore_remote = [remote, sisyphus.getfs.r_repo]
    portage_cfg_remote = [remote, sisyphus.getfs.p_cfg_repo]

    return gentoo_remote, redcore_remote, portage_cfg_remote


@animation.wait('injecting Gentoo Linux portage tree')
def insert_gentoo_repo(branch, remote, gfx_ui=False):
    gentoo_remote, redcore_remote, portage_cfg_remote = get_branch_remote(
        branch, remote)

    if gfx_ui:
        print("\ninjecting Gentoo Linux portage tree", flush=True)
    else:
        pass

    if not os.path.isdir(os.path.join(sisyphus.getfs.gentoo_ebuild_dir, '.git')):
        git.Repo.clone_from(
            "/".join(gentoo_remote), sisyphus.getfs.gentoo_ebuild_dir, depth=1, branch=branch)

    if gfx_ui:
        print("\r" + " " * len("injecting Gentoo Linux portage tree") +
              "\r", end='', flush=True)
    else:
        pass


@animation.wait('injecting Redcore Linux ebuild overlay')
def insert_redcore_repo(branch, remote, gfx_ui=False):
    gentoo_remote, redcore_remote, portage_cfg_remote = get_branch_remote(
        branch, remote)

    if gfx_ui:
        print("\ninjecting Redcore Linux ebuild overlay", flush=True)
    else:
        pass

    if not os.path.isdir(os.path.join(sisyphus.getfs.redcore_ebuild_dir, '.git')):
        git.Repo.clone_from(
            "/".join(redcore_remote), sisyphus.getfs.redcore_ebuild_dir, depth=1, branch=branch)

    if gfx_ui:
        print("\r" + " " * len("injecting Redcore Linux ebuild overlay") +
              "\r", end='', flush=True)
    else:
        pass


@animation.wait('injecting Redcore Linux portage config')
def insert_portage_cfg_repo(branch, remote, gfx_ui=False):
    gentoo_remote, redcore_remote, portage_cfg_remote = get_branch_remote(
        branch, remote)

    if gfx_ui:
        print("\ninjecting Redcore Linux portage config", flush=True)
    else:
        pass

    if not os.path.isdir(os.path.join(sisyphus.getfs.portage_cfg_dir, '.git')):
        git.Repo.clone_from("/".join(portage_cfg_remote),
                            sisyphus.getfs.portage_cfg_dir, depth=1, branch=branch)

    if gfx_ui:
        print("\r" + " " * len("injecting Redcore Linux portage config") +
              "\r", end='', flush=True)
    else:
        pass


def set_branch_master_index():
    mirrorList = sisyphus.setmirror.getList()
    odd_indices = [i + 1 for i in range(len(mirrorList)) if (i + 1) % 2 == 1]
    chosen_index = random.choice(odd_indices)
    sisyphus.setmirror.setActive(chosen_index)


def set_branch_next_index():
    mirrorList = sisyphus.setmirror.getList()
    even_indices = [i + 1 for i in range(len(mirrorList)) if (i + 1) % 2 == 0]
    chosen_index = random.choice(even_indices)
    sisyphus.setmirror.setActive(chosen_index)


def set_binhost_index(branch, remote, gfx_ui=False):
    if gfx_ui:
        print(f"\nThe active branch has been switched to '{branch}'")
        print(f"\nThe active remote has been switched to '{remote}'")
    else:
        print(
            f"{Fore.GREEN}\nThe active branch has been switched to '{branch}'{Style.RESET_ALL}")
        print(
            f"{Fore.GREEN}\nThe active remote has been switched to '{remote}'{Style.RESET_ALL}")

    if "master" in branch:
        set_branch_master_index()
    elif "next" in branch:
        set_branch_next_index()
        if gfx_ui:
            # GUI client shows own warning
            pass
        else:
            sisyphus.warnbranch.start(branch, quiet=False)


def start(branch, remote, gfx_ui=False):
    is_online = sisyphus.checkenv.connectivity()

    if is_online != 1:
        if gfx_ui:
            print("\nNo internet connection detected. Aborting!\n")
            for i in range(9, 0, -1):
                print(f"Killing application in : {i} seconds!")
                time.sleep(1)

            os.kill(os.getpid(), signal.SIGTERM)  # kill GUI window
        else:
            print(
                f"{Fore.RED}{Style.BRIGHT}\nNo internet connection detected; Aborting!\n{Style.RESET_ALL}")
            sys.exit()
    else:
        if gfx_ui:
            sisyphus.purgeenv.branch.__wrapped__()
            sisyphus.purgeenv.metadata.__wrapped__()
            insert_gentoo_repo.__wrapped__(branch, remote, gfx_ui=True)
            insert_redcore_repo.__wrapped__(branch, remote, gfx_ui=True)
            insert_portage_cfg_repo.__wrapped__(branch, remote, gfx_ui=True)
            set_binhost_index(branch, remote, gfx_ui=True)
            sisyphus.setprofile.start.__wrapped__()
            sisyphus.setjobs.start()
        else:
            sisyphus.purgeenv.branch()
            sisyphus.purgeenv.metadata()
            insert_gentoo_repo(branch, remote, gfx_ui=False)
            insert_redcore_repo(branch, remote, gfx_ui=False)
            insert_portage_cfg_repo(branch, remote, gfx_ui=False)
            set_binhost_index(branch, remote, gfx_ui=False)
            sisyphus.setprofile.start()
            sisyphus.setjobs.start()
