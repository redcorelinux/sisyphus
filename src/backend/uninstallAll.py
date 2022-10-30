#!/usr/bin/python3

import atexit
import io
import subprocess
import sys
import sisyphus.checkenv
import sisyphus.killemerge
import sisyphus.syncDatabase

def cliExec(pkgname):
    if sisyphus.checkenv.root():
        portageExec = subprocess.Popen(['emerge', '--quiet', '--depclean', '--ask'] + list(pkgname))
        portageExec.wait()
        sisyphus.syncDatabase.localTable()
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

def cliExecForce(pkgname):
    if sisyphus.checkenv.root():
        portageExec = subprocess.Popen(['emerge', '--quiet', '--unmerge', '--ask'] + list(pkgname))
        portageExec.wait()
        sisyphus.syncDatabase.localTable()
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

def guiExec(pkgname):
    portageExec = subprocess.Popen(['emerge', '--depclean'] + pkgname, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # kill portage if the program dies or it's terminated by the user
    atexit.register(sisyphus.killemerge.cliExec, portageExec)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        print(portageOutput.rstrip())

    portageExec.wait()
    sisyphus.syncDatabase.localTable()
