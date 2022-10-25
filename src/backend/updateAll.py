#!/usr/bin/python3

import animation
import sys
import time
import sisyphus.checkEnvironment
import sisyphus.getEnvironment
import sisyphus.purgeEnvironment
import sisyphus.syncDatabase
import sisyphus.syncEnvironment

def syncAll():
    sisyphus.purgeEnvironment.cache()
    sisyphus.syncEnvironment.gentooRepo()
    sisyphus.syncEnvironment.redcoreRepo()
    sisyphus.syncEnvironment.portageConfigRepo()
    sisyphus.syncDatabase.remoteTable()

@animation.wait('fetching updates')
def start():
    activeBranch = sisyphus.checkEnvironment.branch()
    binhostURL = sisyphus.getEnvironment.binhostURL()
    isSane = sisyphus.checkEnvironment.sanity()

    if isSane == 1:
        syncAll()
    else:
        if "packages-next" in binhostURL:
            print("\nCurrent branch: '" + activeBranch + "' (stable)" + "\nCurrent binhost: '" + binhostURL + "' (testing)")
        else:
            print("\nCurrent branch: '" + activeBranch + "' (testing)" + "\nCurrent binhost: '" + binhostURL + "' (stable)")
        sys.exit("\nInvalid branch - binhost pairing; Use 'sisyphus branch --help' for help; Quitting.")

def startqt():
    activeBranch = sisyphus.checkEnvironment.branch()
    binhostURL = sisyphus.getEnvironment.binhostURL()
    isSane = sisyphus.checkEnvironment.sanity()

    if isSane == 1:
        syncAll()
    else:
        if "packages-next" in binhostURL:
            print("\nCurrent branch: '" + activeBranch + "' (stable)" + "\nCurrent binhost: '" + binhostURL + "' (testing)")
        else:
            print("\nCurrent branch: '" + activeBranch + "' (testing)" + "\nCurrent binhost: '" + binhostURL + "' (stable)")
        print("\nInvalid branch - binhost pairing; Use 'sisyphus branch --help' for help; Quitting in 10 seconds.\n")
        t = int(10)
        while t:
            mins, secs = divmod(t, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)
            print(timer, end="\r")
            time.sleep(1)
            t -= 1

        sys.exit()
