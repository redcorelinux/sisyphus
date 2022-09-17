#!/usr/bin/python3

import atexit
import subprocess
import sys
import sisyphus.checkEnvironment
import sisyphus.killPortage
import sisyphus.syncDatabase

def start():
    if sisyphus.checkEnvironment.root():
        portageExec = subprocess.Popen(['emerge', '--quiet', '--depclean', '--ask'])
        portageExec.wait()
        sisyphus.syncDatabase.syncLocal()
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

def startqt():
    portageExec = subprocess.Popen(['emerge', '--depclean'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = portageExec.communicate()
    # kill portage if the program dies or it's terminated by the user
    atexit.register(sisyphus.killPortage.start, portageExec)

    for portageOutput in stdout.decode('ascii').splitlines():
        print(portageOutput)

    sisyphus.syncDatabase.syncLocal()
