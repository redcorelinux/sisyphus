#!/usr/bin/python3

import subprocess
import io

def getURL():
    remotePkgCsv = []
    remoteDescCsv = []
    portageExec = subprocess.Popen(['emerge', '--info', '--verbose'], stdout=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "PORTAGE_BINHOST" in portageOutput.rstrip():
            if "packages-next" in portageOutput.rstrip():
                remotePkgCsv = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages-next', 'csv-next') + 'remotePackagesPre.csv')
                remoteDescCsv = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages-next', 'csv-next') + 'remoteDescriptionsPre.csv')
            else:
                remotePkgCsv = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages', 'csv') + 'remotePackagesPre.csv')
                remoteDescCsv = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages', 'csv') + 'remoteDescriptionsPre.csv')

    portageExec.wait()
    return remotePkgCsv,remoteDescCsv
