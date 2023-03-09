#!/usr/bin/python3

import os
import subprocess
import sisyphus.getenv


def root():
    return True if os.getuid() == 0 else False


def sanity():
    activeBranch = sisyphus.getenv.systemBranch()
    bhaddr = sisyphus.getenv.bhaddr()
    isSane = int()

    if "packages-next" in bhaddr:
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
