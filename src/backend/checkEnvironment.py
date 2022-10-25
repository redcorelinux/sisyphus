#!/usr/bin/python3

import os
import subprocess
import sisyphus.getEnvironment
import sisyphus.getFilesystem

def root():
    return True if os.getuid() == 0 else False

def branch():
    activeBranch = None

    if os.path.isdir(os.path.join(sisyphus.getFilesystem.gentooRepoDir, '.git')):
        os.chdir(sisyphus.getFilesystem.gentooRepoDir)
        localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])

        if localBranch.decode().strip() == 'master':
            activeBranch = str('master')

        if localBranch.decode().strip() == 'next':
           activeBranch = str('next')

        return activeBranch

def sanity():
    activeBranch = branch()
    binhostURL = sisyphus.getEnvironment.binhostURL()
    isSane = int()

    if "packages-next" in binhostURL:
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
