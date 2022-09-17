#!/usr/bin/python3

import subprocess
import sys
import sisyphus.checkEnvironment
import sisyphus.syncDatabase

def start(pkgname):
    if sisyphus.checkEnvironment.root():
        portageExec = subprocess.Popen(['emerge', '--quiet', '--unmerge', '--ask'] + list(pkgname), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = portageExec.communicate()
        sisyphus.syncDatabase.syncLocal()
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")
