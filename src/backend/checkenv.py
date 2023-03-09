#!/usr/bin/python3

import os
import subprocess
import sisyphus.getenv


def root():
    return True if os.getuid() == 0 else False


def sanity():
    activeBranch = sisyphus.getenv.systemBranch()
    bh_addr = sisyphus.getenv.bh_addr()
    isSane = int()

    if "packages-next" in bh_addr:
        if activeBranch == "next":
            isSane = int(1)
        else:
            isSane = int(0)
    else:
        if activeBranch == "master":
            isSane = int(1)
        else:
            isSane = int(0)

    return isSane
