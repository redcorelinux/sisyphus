#!/usr/bin/python3

import subprocess
import sisyphus.check
import sisyphus.sync

def start():
    sisyphus.check.root()
    portageExec = subprocess.Popen(['emerge', '--quiet', '--depclean', '--ask'])
    portageExec.wait()
    sisyphus.database.syncLocal()