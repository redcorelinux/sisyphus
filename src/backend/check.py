#!/usr/bin/python3

import os
import subprocess
import sisyphus.binhost
import sisyphus.filesystem

def root():
    return True if os.getuid() == 0 else False

def branch():
    if os.path.isdir(os.path.join(sisyphus.filesystem.portageRepoDir, '.git')):
        os.chdir(sisyphus.filesystem.portageRepoDir)
        needsMatch = int()

        isBinhost = sisyphus.binhost.start()
        localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])

        if "packages-next" in isBinhost:
            if localBranch.decode().strip() == "next":
                needsMatch = int(0)
            else:
                needsMatch = int(1)
        else:
            if localBranch.decode().strip() == "master":
                needsMatch = int(0)
            else:
                needsMatch = int(1)

        return needsMatch,localBranch
