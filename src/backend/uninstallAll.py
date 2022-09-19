#!/usr/bin/python3

import atexit
import io
import subprocess
import sys
import sisyphus.checkEnvironment
import sisyphus.killPortage
import sisyphus.syncDatabase

def start(pkgname):
    if sisyphus.checkEnvironment.root():
        portageExec = subprocess.Popen(['emerge', '--quiet', '--depclean', '--ask'] + list(pkgname))
        portageExec.wait()
        sisyphus.syncDatabase.syncLocal()
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

def startqt(pkgname):
    portageExec = subprocess.Popen(['emerge', '--depclean'] + pkgname, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # kill portage if the program dies or it's terminated by the user
    atexit.register(sisyphus.killPortage.start, portageExec)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        print(portageOutput.rstrip())

    portageExec.wait()
    sisyphus.syncDatabase.syncLocal()
