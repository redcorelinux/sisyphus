#!/usr/bin/python3

import atexit
import io
import subprocess
import sys
import sisyphus.checkEnvironment
import sisyphus.syncDatabase
import sisyphus.killPortage

def start(pkgname):
    if sisyphus.checkEnvironment.root():
        portageExec = subprocess.Popen(['emerge', '--quiet', '--depclean', '--ask'] + list(pkgname), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = portageExec.communicate()
        sisyphus.syncDatabase.syncLocal()
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

def startqt(pkgname):
    portageExec = subprocess.Popen(['emerge', '--depclean'] + pkgname, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = portageExec.communicate()
    # kill portage if the program dies or it's terminated by the user
    atexit.register(sisyphus.killPortage.start, portageExec)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        print(portageOutput.rstrip())

    sisyphus.syncDatabase.syncLocal()
