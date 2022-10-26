#!/usr/bin/python3

import atexit
import io
import subprocess
import sys
import sisyphus.checkEnvironment
import sisyphus.killPortage
import sisyphus.syncDatabase

def cliExec():
    if sisyphus.checkEnvironment.root():
        portageExec = subprocess.Popen(['emerge', '--quiet', '--depclean', '--ask'])
        portageExec.wait()
        sisyphus.syncDatabase.localTable()
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

def guiExec():
    portageExec = subprocess.Popen(['emerge', '--depclean'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # kill portage if the program dies or it's terminated by the user
    atexit.register(sisyphus.killPortage.cliExec, portageExec)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        print(portageOutput.rstrip())

    portageExec.wait()
    sisyphus.syncDatabase.localTable()
