#!/usr/bin/python3

import animation
import git
import os
import random
import signal
import sys
import time
import sisyphus.checkenv
import sisyphus.getclr
import sisyphus.getfs
import sisyphus.purgeenv
import sisyphus.setjobs
import sisyphus.setmirror
import sisyphus.setprofile


brch_rmt_map = {
    "master": {
        "github": sisyphus.getfs.rmt_gh_addr,
        "gitlab": sisyphus.getfs.rmt_gl_addr,
        "pagure": sisyphus.getfs.rmt_pg_addr
    },
    "next": {
        "github": sisyphus.getfs.rmt_gh_addr,
        "gitlab": sisyphus.getfs.rmt_gl_addr,
        "pagure": sisyphus.getfs.rmt_pg_addr
    }
}


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def get_brch_rmt(branch, remote):
    g_rmt = []
    r_rmt = []
    p_cfg_rmt = []

    if branch in brch_rmt_map and remote in brch_rmt_map[branch]:
        remote = brch_rmt_map[branch][remote]
    else:
        # set a default remote here if needed
        pass

    g_rmt = [remote, sisyphus.getfs.g_repo]
    r_rmt = [remote, sisyphus.getfs.r_repo]
    p_cfg_rmt = [remote, sisyphus.getfs.p_cfg_repo]

    return g_rmt, r_rmt, p_cfg_rmt


@animation.wait('injecting Gentoo Linux portage tree')
def ins_g_repo(branch, remote, gfx_ui=False):
    g_rmt, r_rmt, p_cfg_rmt = get_brch_rmt(branch, remote)

    if gfx_ui:
        print("\ninjecting Gentoo Linux portage tree", flush=True)
    else:
        pass

    if not os.path.isdir(os.path.join(sisyphus.getfs.g_src_dir, '.git')):
        git.Repo.clone_from(
            "/".join(g_rmt), sisyphus.getfs.g_src_dir, depth=1, branch=branch)

    if gfx_ui:
        print("\r" + " " * len("injecting Gentoo Linux portage tree") +
              "\r", end='', flush=True)
    else:
        pass


@animation.wait('injecting Redcore Linux ebuild overlay')
def ins_r_repo(branch, remote, gfx_ui=False):
    g_rmt, r_rmt, p_cfg_rmt = get_brch_rmt(branch, remote)

    if gfx_ui:
        print("\ninjecting Rentoo Linux ebuild overlay", flush=True)
    else:
        pass

    if not os.path.isdir(os.path.join(sisyphus.getfs.r_src_dir, '.git')):
        git.Repo.clone_from(
            "/".join(r_rmt), sisyphus.getfs.r_src_dir, depth=1, branch=branch)

    if gfx_ui:
        print("\r" + " " * len("injecting Redcore Linux ebuild overlay") +
              "\r", end='', flush=True)
    else:
        pass


@animation.wait('injecting Redcore Linux portage config')
def ins_p_cfg_repo(branch, remote, gfx_ui=False):
    g_rmt, r_rmt, p_cfg_rmt = get_brch_rmt(branch, remote)

    if gfx_ui:
        print("\ninjecting Redcore Linux portage config", flush=True)
    else:
        pass

    if not os.path.isdir(os.path.join(sisyphus.getfs.p_cfg_dir, '.git')):
        git.Repo.clone_from("/".join(p_cfg_rmt),
                            sisyphus.getfs.p_cfg_dir, depth=1, branch=branch)

    if gfx_ui:
        print("\r" + " " * len("injecting Redcore Linux portage config") +
              "\r", end='', flush=True)
    else:
        pass


def set_brch_master_index():
    mirrorList = sisyphus.setmirror.getList()
    odd_indices = [i + 1 for i in range(len(mirrorList)) if (i + 1) % 2 == 1]
    chosen_index = random.choice(odd_indices)
    sisyphus.setmirror.setActive(chosen_index)


def set_brch_next_index():
    mirrorList = sisyphus.setmirror.getList()
    even_indices = [i + 1 for i in range(len(mirrorList)) if (i + 1) % 2 == 0]
    chosen_index = random.choice(even_indices)
    sisyphus.setmirror.setActive(chosen_index)


def set_bhst_index(branch, remote, gfx_ui=False):
    if gfx_ui:
        print(f"\nThe active branch has been switched to '{branch}'")
        print(f"\nThe active remote has been switched to '{remote}'")
    else:
        print(f"{sisyphus.getclr.green}\nThe active branch has been switched to '{branch}'{sisyphus.getclr.reset}")
        print(f"{sisyphus.getclr.green}\nThe active remote has been switched to '{remote}'{sisyphus.getclr.reset}")

    if "master" in branch:
        set_brch_master_index()
    elif "next" in branch:
        set_brch_next_index()


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
                f"{sisyphus.getclr.bright_red}\nNo internet connection detected; Aborting!\n{sisyphus.getclr.reset}")
            sys.exit()
    else:
        if gfx_ui:
            sisyphus.purgeenv.branch.__wrapped__()
            sisyphus.purgeenv.metadata.__wrapped__()
            ins_g_repo.__wrapped__(branch, remote, gfx_ui=True)
            ins_r_repo.__wrapped__(branch, remote, gfx_ui=True)
            ins_p_cfg_repo.__wrapped__(branch, remote, gfx_ui=True)
            set_bhst_index(branch, remote, gfx_ui=True)
            sisyphus.setprofile.start.__wrapped__()
            sisyphus.setjobs.start()
        else:
            sisyphus.purgeenv.branch()
            sisyphus.purgeenv.metadata()
            ins_g_repo(branch, remote, gfx_ui=False)
            ins_r_repo(branch, remote, gfx_ui=False)
            ins_p_cfg_repo(branch, remote, gfx_ui=False)
            set_bhst_index(branch, remote, gfx_ui=False)
            sisyphus.setprofile.start()
            sisyphus.setjobs.start()
