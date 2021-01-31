#!/usr/bin/python3

import subprocess
import io

def getURL():
    remotePackagesCsvURL = []
    remoteDescriptionsCsvURL = []
    portageExec = subprocess.Popen(['emerge', '--info', '--verbose'], stdout=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "PORTAGE_BINHOST" in portageOutput.rstrip():
            if "packages-next" in portageOutput.rstrip():
                remotePackagesCsvURL = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages-next', 'csv-next') + 'remotePackagesPre.csv')
                remoteDescriptionsCsvURL = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages-next', 'csv-next') + 'remoteDescriptionsPre.csv')
            else:
                remotePackagesCsvURL = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages', 'csv') + 'remotePackagesPre.csv')
                remoteDescriptionsCsvURL = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages', 'csv') + 'remoteDescriptionsPre.csv')

    portageExec.wait()
    return remotePackagesCsvURL,remoteDescriptionsCsvURL
