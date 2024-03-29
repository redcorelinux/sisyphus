#!/usr/bin/python3

import animation
import git
import os
import random
import signal
import sys
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
def ins_g_repo(branch, remote):
    g_rmt, r_rmt, p_cfg_rmt = get_brch_rmt(branch, remote)

    if not os.path.isdir(os.path.join(sisyphus.getfs.g_src_dir, '.git')):
        git.Repo.clone_from(
            "/".join(g_rmt), sisyphus.getfs.g_src_dir, depth=1, branch=branch)


@animation.wait('injecting Redcore Linux ebuild overlay')
def ins_r_repo(branch, remote):
    g_rmt, r_rmt, p_cfg_rmt = get_brch_rmt(branch, remote)

    if not os.path.isdir(os.path.join(sisyphus.getfs.r_src_dir, '.git')):
        git.Repo.clone_from(
            "/".join(r_rmt), sisyphus.getfs.r_src_dir, depth=1, branch=branch)


@animation.wait('injecting Redcore Linux portage config')
def ins_p_cfg_repo(branch, remote):
    g_rmt, r_rmt, p_cfg_rmt = get_brch_rmt(branch, remote)

    if not os.path.isdir(os.path.join(sisyphus.getfs.p_cfg_dir, '.git')):
        git.Repo.clone_from("/".join(p_cfg_rmt),
                            sisyphus.getfs.p_cfg_dir, depth=1, branch=branch)


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


def set_bhst_index(branch, remote):
    if "master" in branch:
        print(f"{sisyphus.getclr.green}\nThe active branch has been switched to '{branch}'{sisyphus.getclr.reset}")
        print(f"{sisyphus.getclr.green}The active remote has been switched to '{remote}'{sisyphus.getclr.reset}")
        set_brch_master_index()  # Set binhost index for branch 'master' (random odd index)
    elif "next" in branch:
        print(f"{sisyphus.getclr.green}\nThe active branch has been switched to '{branch}'{sisyphus.getclr.reset}")
        print(f"{sisyphus.getclr.green}The active remote has been switched to '{remote}'{sisyphus.getclr.reset}")
        set_brch_next_index()  # Set binhost index for branch 'next' (random even index)


def start(branch, remote):
    is_online = sisyphus.checkenv.connectivity()

    if sisyphus.checkenv.root():
        if is_online == 1:
            sisyphus.purgeenv.branch()
            sisyphus.purgeenv.metadata()
            ins_g_repo(branch, remote)
            ins_r_repo(branch, remote)
            ins_p_cfg_repo(branch, remote)
            sisyphus.setjobs.start()
            sisyphus.setprofile.start()
            set_bhst_index(branch, remote)
        else:
            print(
                f"{sisyphus.getclr.bright_red}\nNo internet connection detected; Aborting!\n{sisyphus.getclr.reset}")
            sys.exit()
    else:
        print(f"{sisyphus.getclr.bright_red}\nRoot permissions are required to perform this action.\n{sisyphus.getclr.reset}")
        sys.exit()
