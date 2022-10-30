#!/usr/bin/python3

import io
import subprocess


def binhostURL():
    binhostURL = []
    portageExec = subprocess.Popen(['emerge', '--info', '--verbose'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "PORTAGE_BINHOST" in portageOutput:
            binhostURL = portageOutput.rstrip().split("=")[1].strip('\"')

    portageExec.wait()
    return binhostURL


def csvURL():
    csvURL = binhostURL()
    packagesCsvURL = []
    descriptionsCsvURL = []

    if "packages-next" in csvURL:
        packagesCsvURL = csvURL.replace('packages-next', 'csv-next') + 'remotePackagesPre.csv'
        descriptionsCsvURL = csvURL.replace('packages-next', 'csv-next') + 'remoteDescriptionsPre.csv'
    else:
        packagesCsvURL = csvURL.replace('packages', 'csv') + 'remotePackagesPre.csv'
        descriptionsCsvURL = csvURL.replace('packages', 'csv') + 'remoteDescriptionsPre.csv'

    return packagesCsvURL,descriptionsCsvURL
