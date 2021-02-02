#!/usr/bin/python3

import animation
import sys
import time
import sisyphus.cache
import sisyphus.binhost
import sisyphus.check
import sisyphus.database
import sisyphus.metadata
import sisyphus.sync

def dosync():
    sisyphus.sync.portage()
    sisyphus.sync.overlay()
    sisyphus.sync.portageCfg()
    sisyphus.database.syncRemote()
    sisyphus.metadata.regenSilent()

def checksync():
    sisyphus.cache.clean()

    needsPortage = sisyphus.check.portage()
    needsOverlay = sisyphus.check.overlay()

    if needsPortage == 1:
        if needsOverlay == 1:
            dosync()
        elif not needsOverlay == 1:
            dosync()
    elif not needsPortage == 1:
        if needsOverlay == 1:
            dosync()
        elif not needsOverlay == 1:
            sisyphus.sync.portageCfg()

@animation.wait('fetching updates')
def start():
    binhostURL = sisyphus.binhost.getURL()
    needsMatch,localBranch = sisyphus.check.match()

    if needsMatch == 0:
        checksync()
    else:
        if "packages-next" in binhostURL:
            print("\nCurrent branch: '" + localBranch.decode().strip()  + "' (stable)" + "\nCurrent binhost: '" + binhostURL + "' (testing)")
        else:
            print("\nCurrent branch: '" + localBranch.decode().strip()  + "' (testing)" + "\nCurrent binhost: '" + binhostURL + "' (stable)")
        sys.exit("\nInvalid branch - binhost pairing; Use 'sisyphus branch --help' for help; Quitting.")

def startqt():
    binhostURL = sisyphus.binhost.getURL()
    needsMatch,localBranch = sisyphus.check.match()

    if needsMatch == 0:
        checksync()
    else:
        if "packages-next" in binhostURL:
            print("\nCurrent branch: '" + localBranch.decode().strip()  + "' (stable)" + "\nCurrent binhost: '" + binhostURL + "' (testing)")
        else:
            print("\nCurrent branch: '" + localBranch.decode().strip()  + "' (testing)" + "\nCurrent binhost: '" + binhostURL + "' (stable)")
        print("\nInvalid branch - binhost pairing; Use 'sisyphus branch --help' for help; Quitting in 10 seconds.\n")
        t = int(10)
        while t:
            mins, secs = divmod(t, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)
            print(timer, end="\r")
            time.sleep(1)
            t -= 1

        sys.exit()
