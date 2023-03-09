#!/usr/bin/python3

import os
import subprocess
import sisyphus.getenv


def root():
    return True if os.getuid() == 0 else False


def sanity():
    act_brch = sisyphus.getenv.sys_brch()
    bh_addr = sisyphus.getenv.bh_addr()
    isSane = int()

    if "packages-next" in bh_addr:
        if act_brch == "next":
            isSane = int(1)
        else:
            isSane = int(0)
    else:
        if act_brch == "master":
            isSane = int(1)
        else:
            isSane = int(0)

    return isSane
