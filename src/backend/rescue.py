#!/usr/bin/python3

import animation
import os
import sisyphus.database
import sisyphus.filesystem

@animation.wait('recovering databases')
def start():
    if os.path.exists(sisyphus.filesystem.remotePkgsDB):
        os.remove(sisyphus.filesystem.remotePkgsDB)
    if os.path.exists(sisyphus.filesystem.remoteDscsDB):
        os.remove(sisyphus.filesystem.remoteDscsDB)
    if os.path.exists(sisyphus.filesystem.localPkgsDB):
        os.remove(sisyphus.filesystem.localPkgsDB)
    if os.path.exists(sisyphus.filesystem.sisyphusDB):
        os.remove(sisyphus.filesystem.sisyphusDB)

    sisyphus.database.syncRemote()
    sisyphus.database.syncLocal()
