#!/usr/bin/python3

import subprocess
import sisyphus.check
import sisyphus.database

def start(pkgname):
    sisyphus.check.root()
    portageExec = subprocess.Popen(['emerge', '--quiet', '--unmerge', '--ask'] + list(pkgname))
    portageExec.wait()
    sisyphus.database.syncLocal()
