#!/usr/bin/python3

import atexit
import io
import subprocess
import sys
import sisyphus.check
import sisyphus.database
import sisyphus.killportage

def start():
    if sisyphus.check.root():
        portageExec = subprocess.Popen(['emerge', '--quiet', '--depclean', '--ask'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = portageExec.communicate()
        sisyphus.database.syncLocal()
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

def startqt():
    portageExec = subprocess.Popen(['emerge', '--depclean'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = portageExec.communicate()
    # kill portage if the program dies or it's terminated by the user
    atexit.register(sisyphus.killportage.start, portageExec)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        print(portageOutput.rstrip())

    sisyphus.database.syncLocal()
