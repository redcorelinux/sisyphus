#!/usr/bin/python3

import subprocess
import sisyphus.check
import sisyphus.database
import sys

def start(pkgname):
    if sisyphus.check.root():
        portageExec = subprocess.Popen(['emerge', '--quiet', '--unmerge', '--ask'] + list(pkgname))
        portageExec.wait()
        sisyphus.database.syncLocal()
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")
