#!/usr/bin/python3

import animation
import os
import sisyphus.getfs
import sisyphus.syncDatabase

@animation.wait('recovering databases')
def cliExec():
    if os.path.exists(sisyphus.getfs.remotePackagesCsv):
        os.remove(sisyphus.getfs.remotePackagesCsv)
    if os.path.exists(sisyphus.getfs.remoteDescriptionsCsv):
        os.remove(sisyphus.getfs.remoteDescriptionsCsv)
    if os.path.exists(sisyphus.getfs.localPackagesCsv):
        os.remove(sisyphus.getfs.localPackagesCsv)
    if os.path.exists(sisyphus.getfs.localDatabase):
        os.remove(sisyphus.getfs.localDatabase)

    sisyphus.syncDatabase.remoteTable()
    sisyphus.syncDatabase.localTable()
