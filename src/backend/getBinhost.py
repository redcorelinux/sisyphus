#!/usr/bin/python3

import subprocess

def start():
    isBinhost = []
    portageExec = subprocess.Popen(['emerge', '--info', '--verbose'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = portageExec.communicate()

    for portageOutput in stdout.decode('ascii').splitlines():
        if "PORTAGE_BINHOST" in portageOutput:
            isBinhost = portageOutput.rstrip().split("=")[1].strip('\"')

    return isBinhost
