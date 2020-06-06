#!/usr/bin/python3

import subprocess
import sisyphus.check
import sisyphus.sync

def start(pkgList):
    sisyphus.check.root()
    portageExec = subprocess.Popen(['emerge', '--quiet', '--depclean', '--ask'] + pkgList)
    portageExec.wait()
    sisyphus.database.syncLocal()
