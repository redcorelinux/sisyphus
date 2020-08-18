#!/usr/bin/python3

import subprocess
import sisyphus.check
import sisyphus.database
import sys

def start():
    if sisyphus.check.root() == 0:
        portageExec = subprocess.Popen(['emerge', '--quiet', '--depclean', '--ask'])
        portageExec.wait()
        sisyphus.database.syncLocal()
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")
