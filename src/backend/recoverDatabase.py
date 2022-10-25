#!/usr/bin/python3

import animation
import os
import sisyphus.getFilesystem
import sisyphus.syncDatabase

@animation.wait('recovering databases')
def start():
    if os.path.exists(sisyphus.getFilesystem.remotePackagesCsv):
        os.remove(sisyphus.getFilesystem.remotePackagesCsv)
    if os.path.exists(sisyphus.getFilesystem.remoteDescriptionsCsv):
        os.remove(sisyphus.getFilesystem.remoteDescriptionsCsv)
    if os.path.exists(sisyphus.getFilesystem.localPackagesCsv):
        os.remove(sisyphus.getFilesystem.localPackagesCsv)
    if os.path.exists(sisyphus.getFilesystem.localDatabase):
        os.remove(sisyphus.getFilesystem.localDatabase)

    sisyphus.syncDatabase.remoteTable()
    sisyphus.syncDatabase.localTable()
