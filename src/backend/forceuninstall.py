#!/usr/bin/python3

import subprocess
import sys
import sisyphus.check
import sisyphus.database

def start(pkgname):
    if sisyphus.check.root():
        portageExec = subprocess.Popen(['emerge', '--quiet', '--unmerge', '--ask'] + list(pkgname), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = portageExec.communicate()
        sisyphus.database.syncLocal()
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")
