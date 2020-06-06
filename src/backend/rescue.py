#!/usr/bin/python3

import animation
import os
import sisyphus.database

remotePkgsDB = '/var/lib/sisyphus/csv/remotePackagesPre.csv'
remoteDscsDB = '/var/lib/sisyphus/csv/remoteDescriptionsPre.csv'
localPkgsDB = '/var/lib/sisyphus/csv/localPackagesPre.csv'
sisyphusDB = '/var/lib/sisyphus/db/sisyphus.db'

@animation.wait('recovering databases')
def start():
    if os.path.exists(remotePkgsDB):
        os.remove(remotePkgsDB)
    if os.path.exists(remoteDscsDB):
        os.remove(remoteDscsDB)
    if os.path.exists(localPkgsDB):
        os.remove(localPkgsDB)
    if os.path.exists(sisyphusDB):
        os.remove(sisyphusDB)

    sisyphus.database.syncRemote()
    sisyphus.database.syncLocal()
