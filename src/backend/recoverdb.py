#!/usr/bin/python3

import animation
import os
import sisyphus.getfs
import sisyphus.syncdb


@animation.wait('recovering databases')
def start():
    if os.path.exists(sisyphus.getfs.remotePackagesCsv):
        os.remove(sisyphus.getfs.remotePackagesCsv)
    if os.path.exists(sisyphus.getfs.remoteDescriptionsCsv):
        os.remove(sisyphus.getfs.remoteDescriptionsCsv)
    if os.path.exists(sisyphus.getfs.localPackagesCsv):
        os.remove(sisyphus.getfs.localPackagesCsv)
    if os.path.exists(sisyphus.getfs.localDatabase):
        os.remove(sisyphus.getfs.localDatabase)

    sisyphus.syncdb.remoteTable()
    sisyphus.syncdb.localTable()
