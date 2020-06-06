#!/usr/bin/python3

import subprocess
import io

def getURL():
    binhostURL = []
    portageExec = subprocess.Popen(['emerge', '--info', '--verbose'], stdout=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "PORTAGE_BINHOST" in portageOutput.rstrip():
            binhostURL = str(portageOutput.rstrip().split("=")[1].strip('\"'))

    portageExec.wait()
    return binhostURL
