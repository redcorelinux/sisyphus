#!/usr/bin/python3

import os
import subprocess
import sisyphus.binhost
import sisyphus.filesystem

def root():
    return True if os.getuid() == 0 else False


def branch():
    binhostURL = sisyphus.binhost.getURL()
    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    mismatch = int()

    if "packages-next" in binhostURL:
        os.chdir(sisyphus.filesystem.portageRepoDir)
        if localBranch.decode().strip() == "next":
            print(binhostURL.replace('packages-next', 'csv-next') + 'remotePackagesPre.csv')
            mismatch = int(0)
        else:
            mismatch = int(1)
    else:
        if localBranch.decode().strip() == "master":
            mismatch = int(0)
        else:
            mismatch = int(1)

    return localBranch,mismatch
branch()

def portage():
    if os.path.isdir(os.path.join(sisyphus.filesystem.portageRepoDir, '.git')):
        os.chdir(sisyphus.filesystem.portageRepoDir)
        needsPortageSync = int()

        localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        localHash = subprocess.check_output(['git', 'rev-parse', '@'])
        remoteHash = subprocess.check_output(['git', 'rev-parse', '@{u}'])

        gitExec = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        if not localHash.decode().strip() == remoteHash.decode().strip():
            needsPortageSync = int(1)

        gitExec.wait()
        return needsPortageSync

def overlay():
    if os.path.isdir(os.path.join(sisyphus.filesystem.redcoreRepoDir, '.git')):
        os.chdir(sisyphus.filesystem.redcoreRepoDir)
        needsOverlaySync = int()

        localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        localHash = subprocess.check_output(['git', 'rev-parse', '@'])
        remoteHash = subprocess.check_output(['git', 'rev-parse', '@{u}'])

        gitExec = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        if not localHash.decode().strip() == remoteHash.decode().strip():
            needsOverlaySync = int(1)

        gitExec.wait()
        return needsOverlaySync

def update():
    portage()
    overlay()
    
