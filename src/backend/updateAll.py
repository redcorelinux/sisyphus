#!/usr/bin/python3

import animation
import sys
import time
import sisyphus.checkEnvironment
import sisyphus.getBinhost
import sisyphus.purgeEnvironment
import sisyphus.syncDatabase
import sisyphus.syncEnvironment

def syncAll():
    sisyphus.purgeEnvironment.cache()
    sisyphus.syncEnvironment.syncStage1()
    sisyphus.syncEnvironment.syncStage2()
    sisyphus.syncEnvironment.syncStage3()
    sisyphus.syncDatabase.syncRemote()

@animation.wait('fetching updates')
def start():
    activeBranch = sisyphus.checkEnvironment.branch()
    isBinhost = sisyphus.getBinhost.start()
    isSane = sisyphus.checkEnvironment.sanity()

    if isSane == 1:
        syncAll()
    else:
        if "packages-next" in isBinhost:
            print("\nCurrent branch: '" + activeBranch + "' (stable)" + "\nCurrent binhost: '" + isBinhost + "' (testing)")
        else:
            print("\nCurrent branch: '" + activeBranch + "' (testing)" + "\nCurrent binhost: '" + isBinhost + "' (stable)")
        sys.exit("\nInvalid branch - binhost pairing; Use 'sisyphus branch --help' for help; Quitting.")

def startqt():
    activeBranch = sisyphus.checkEnvironment.branch()
    isBinhost = sisyphus.getBinhost.start()
    isSane = sisyphus.checkEnvironment.sanity()

    if isSane == 1:
        syncAll()
    else:
        if "packages-next" in isBinhost:
            print("\nCurrent branch: '" + activeBranch + "' (stable)" + "\nCurrent binhost: '" + isBinhost + "' (testing)")
        else:
            print("\nCurrent branch: '" + activeBranch + "' (testing)" + "\nCurrent binhost: '" + isBinhost + "' (stable)")
        print("\nInvalid branch - binhost pairing; Use 'sisyphus branch --help' for help; Quitting in 10 seconds.\n")
        t = int(10)
        while t:
            mins, secs = divmod(t, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)
            print(timer, end="\r")
            time.sleep(1)
            t -= 1

        sys.exit()
