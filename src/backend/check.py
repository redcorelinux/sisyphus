#!/usr/bin/python3

import os
import sys
import subprocess

gentooEbuildDir = '/usr/ports/gentoo'
redcoreEbuildDir = '/usr/ports/redcore'

def root():
    if not os.getuid() == 0:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

def portage():
    os.chdir(gentooEbuildDir)
    needsPortageSync = int()

    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    localHash = subprocess.check_output(['git', 'rev-parse', '@'])
    remoteHash = subprocess.check_output(['git', 'rev-parse', '@{u}'])

    gitExec = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE)

    if not localHash.decode().strip() == remoteHash.decode().strip():
        needsPortageSync = int(1)

    gitExec.wait()
    return needsPortageSync

def overlay():
    os.chdir(redcoreEbuildDir)
    needsOverlaySync = int()

    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    localHash = subprocess.check_output(['git', 'rev-parse', '@'])
    remoteHash = subprocess.check_output(['git', 'rev-parse', '@{u}'])

    gitExec = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE)

    if not localHash.decode().strip() == remoteHash.decode().strip():
        needsOverlaySync = int(1)

    gitExec.wait()
    return needsOverlaySync

def update():
    portage()
    overlay()
    
