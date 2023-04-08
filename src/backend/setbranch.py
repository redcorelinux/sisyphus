#!/usr/bin/python3

import animation
import git
import os
import signal
import sys
import sisyphus.checkenv
import sisyphus.getcolor
import sisyphus.getfs
import sisyphus.purgeenv
import sisyphus.setjobs
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


def brch_s_warn(branch, remote):
    if "master" in branch:
        print(sisyphus.getcolor.green + "\nActive branch switched:" +
              " " + sisyphus.getcolor.reset + "'" + branch + "'")
        print(sisyphus.getcolor.green + "Active remote switched:" +
              " " + sisyphus.getcolor.reset + "'" + remote + "'")
        print(sisyphus.getcolor.bright_yellow + "\nUse" + sisyphus.getcolor.reset + " " + "'" + "sisyphus mirror set 3" + "'" + " " + sisyphus.getcolor.bright_yellow +
              "or" + sisyphus.getcolor.reset + " " + "'" + "sisyphus mirror set 7" + "'" + " " + sisyphus.getcolor.bright_yellow + "to pair the binhost" + sisyphus.getcolor.reset)
        print(sisyphus.getcolor.bright_yellow + "Use" + sisyphus.getcolor.reset + " " + "'" +
              "sisyphus branch --help" + "'" + " " + sisyphus.getcolor.bright_yellow + "for help" + sisyphus.getcolor.reset)
    elif "next" in branch:
        print(sisyphus.getcolor.green + "\nActive branch switched:" +
              " " + sisyphus.getcolor.reset + "'" + branch + "'")
        print(sisyphus.getcolor.green + "Active remote switched:" +
              " " + sisyphus.getcolor.reset + "'" + remote + "'")
        print(sisyphus.getcolor.bright_yellow + "\nUse" + sisyphus.getcolor.reset + " " + "'" + "sisyphus mirror set 4" + "'" + " " + sisyphus.getcolor.bright_yellow +
              "or" + sisyphus.getcolor.reset + " " + "'" + "sisyphus mirror set 8" + "'" + " " + sisyphus.getcolor.bright_yellow + "to pair the binhost" + sisyphus.getcolor.reset)
        print(sisyphus.getcolor.bright_yellow + "Use" + sisyphus.getcolor.reset + " " + "'" +
              "sisyphus branch --help" + "'" + " " + sisyphus.getcolor.bright_yellow + "for help" + sisyphus.getcolor.reset)


def start(branch, remote):
    if sisyphus.checkenv.root():
        sisyphus.purgeenv.branch()
        sisyphus.purgeenv.metadata()
        ins_g_repo(branch, remote)
        ins_r_repo(branch, remote)
        ins_p_cfg_repo(branch, remote)
        sisyphus.setjobs.start()
        sisyphus.setprofile.start()
        brch_s_warn(branch, remote)
    else:
        print(sisyphus.getcolor.bright_red +
              "\nYou need root permissions to do this!\n" + sisyphus.getcolor.reset)
        sys.exit()
