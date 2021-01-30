#!/usr/bin/python3

import atexit
import io
import subprocess
import sys
import sisyphus.check
import sisyphus.database
import sisyphus.killportage

def start(pkgname):
    if sisyphus.check.root():
        portageExec = subprocess.Popen(['emerge', '--quiet', '--depclean', '--ask'] + list(pkgname))
        portageExec.wait()
        sisyphus.database.syncLocal()
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

def startqt(pkgname):
    portageExec = subprocess.Popen(['emerge', '--depclean'] + pkgname, stdout=subprocess.PIPE)
    # kill portage if the program dies or it's terminated by the user
    atexit.register(sisyphus.killportage.start, portageExec)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        print(portageOutput.rstrip())

    portageExec.wait()
    sisyphus.database.syncLocal()
