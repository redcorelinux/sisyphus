#!/usr/bin/python3

import os
import subprocess
import sisyphus.getenv


def root():
    return True if os.getuid() == 0 else False


def sanity():
    act_brch = sisyphus.getenv.sys_brch()
    bh_addr = sisyphus.getenv.bh_addr()
    is_sane = int()

    if "packages-next" in bh_addr:
        if act_brch == "next":
            is_sane = int(1)
        else:
            is_sane = int(0)
    else:
        if act_brch == "master":
            is_sane = int(1)
        else:
            is_sane = int(0)

    return is_sane
