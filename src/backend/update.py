#!/usr/bin/python3

import animation
import sys
import time
import sisyphus.binhost
import sisyphus.check
import sisyphus.database
import sisyphus.purge
import sisyphus.sync

def syncAll():
    sisyphus.purge.cache()
    sisyphus.sync.portage()
    sisyphus.sync.overlay()
    sisyphus.sync.portageCfg()
    sisyphus.database.syncRemote()

@animation.wait('fetching updates')
def start():
    isBinhost = sisyphus.binhost.start()
    needsMatch,localBranch = sisyphus.check.branch()

    if needsMatch == 0:
        syncAll()
    else:
        if "packages-next" in isBinhost:
            print("\nCurrent branch: '" + localBranch.decode().strip()  + "' (stable)" + "\nCurrent binhost: '" + isBinhost + "' (testing)")
        else:
            print("\nCurrent branch: '" + localBranch.decode().strip()  + "' (testing)" + "\nCurrent binhost: '" + isBinhost + "' (stable)")
        sys.exit("\nInvalid branch - binhost pairing; Use 'sisyphus branch --help' for help; Quitting.")

def startqt():
    isBinhost = sisyphus.binhost.start()
    needsMatch,localBranch = sisyphus.check.branch()

    if needsMatch == 0:
        syncAll()
    else:
        if "packages-next" in isBinhost:
            print("\nCurrent branch: '" + localBranch.decode().strip()  + "' (stable)" + "\nCurrent binhost: '" + isBinhost + "' (testing)")
        else:
            print("\nCurrent branch: '" + localBranch.decode().strip()  + "' (testing)" + "\nCurrent binhost: '" + isBinhost + "' (stable)")
        print("\nInvalid branch - binhost pairing; Use 'sisyphus branch --help' for help; Quitting in 10 seconds.\n")
        t = int(10)
        while t:
            mins, secs = divmod(t, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)
            print(timer, end="\r")
            time.sleep(1)
            t -= 1

        sys.exit()
