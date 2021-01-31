#!/usr/bin/python3

import sisyphus.binhost

def getURL():
    remotePackagesCsvURL = []
    remoteDescriptionsCsvURL = []
    binhostURL = sisyphus.binhost.getURL()

    if "packages-next" in binhostURL:
        remotePackagesCsvURL = binhostURL.replace('packages-next', 'csv-next') + 'remotePackagesPre.csv'
        remoteDescriptionsCsvURL = binhostURL.replace('packages-next', 'csv-next') + 'remoteDescriptionsPre.csv'
    else:
        remotePackagesCsvURL = binhostURL.replace('packages', 'csv') + 'remotePackagesPre.csv'
        remoteDescriptionsCsvURL = binhostURL.replace('packages', 'csv') + 'remoteDescriptionsPre.csv'

    return remotePackagesCsvURL,remoteDescriptionsCsvURL
