#!/usr/bin/python3

import os
import sisyphus.getfs

marker_dirs = [
    sisyphus.getfs.gentoo_ebuild_dir,
    sisyphus.getfs.redcore_ebuild_dir,
    sisyphus.getfs.portage_cfg_dir,
]


def markers_exist():
    for d in marker_dirs:
        if not os.path.isdir(d):
            return False

        git_path = os.path.join(d, ".git")
        if not os.path.exists(git_path):
            return False

        entries = [f for f in os.listdir(d) if f != ".git"]

        if os.path.isdir(git_path):
            if not entries:
                return False
        elif os.path.isfile(git_path):
            if entries:
                return False
            # else pass to bypass firstRun during ISO spin
        else:
            return False

    return True
