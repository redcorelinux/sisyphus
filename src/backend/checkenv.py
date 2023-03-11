#!/usr/bin/python3

import os
import subprocess
import sisyphus.getenv


def root():
    return True if os.getuid() == 0 else False


def sanity():
    actv_brch = sisyphus.getenv.sys_brch()
    bhst_addr = sisyphus.getenv.bhst_addr()
    is_sane = int()

    if "packages-next" in bhst_addr:
        if actv_brch == "next":
            is_sane = int(1)
        else:
            is_sane = int(0)
    else:
        if actv_brch == "master":
            is_sane = int(1)
        else:
            is_sane = int(0)

    return is_sane
