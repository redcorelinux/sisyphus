#!/usr/bin/python3

import animation
import os
import sisyphus.database
import sisyphus.filesystem

@animation.wait('recovering databases')
def start():
    if os.path.exists(sisyphus.filesystem.remotePackagesCsv):
        os.remove(sisyphus.filesystem.remotePackagesCsv)
    if os.path.exists(sisyphus.filesystem.remoteDescriptionsCsv):
        os.remove(sisyphus.filesystem.remoteDescriptionsCsv)
    if os.path.exists(sisyphus.filesystem.localPackagesCsv):
        os.remove(sisyphus.filesystem.localPackagesCsv)
    if os.path.exists(sisyphus.filesystem.localDatabase):
        os.remove(sisyphus.filesystem.localDatabase)

    sisyphus.database.syncRemote()
    sisyphus.database.syncLocal()
