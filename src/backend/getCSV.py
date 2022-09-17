#!/usr/bin/python3

import sisyphus.getBinhost

def start():
    isPackageCsv = []
    isDescriptionCsv = []
    isBinhost = sisyphus.getBinhost.start()

    if "packages-next" in isBinhost:
        isPackageCsv = isBinhost.replace('packages-next', 'csv-next') + 'remotePackagesPre.csv'
        isDescriptionCsv = isBinhost.replace('packages-next', 'csv-next') + 'remoteDescriptionsPre.csv'
    else:
        isPackageCsv = isBinhost.replace('packages', 'csv') + 'remotePackagesPre.csv'
        isDescriptionCsv = isBinhost.replace('packages', 'csv') + 'remoteDescriptionsPre.csv'

    return isPackageCsv,isDescriptionCsv
