#!/usr/bin/python3

import animation
import sys
import time
import sisyphus.checkenv
import sisyphus.getcolor
import sisyphus.getenv
import sisyphus.purgeenv
import sisyphus.syncdb
import sisyphus.syncenv


def syncAll():
    sisyphus.purgeenv.cache()
    sisyphus.syncenv.gentooRepo()
    sisyphus.syncenv.redcoreRepo()
    sisyphus.syncenv.portageConfigRepo()
    sisyphus.syncdb.remoteTable()


@animation.wait('fetching updates')
def start():
    activeBranch = sisyphus.getenv.systemBranch()
    binhostURL = sisyphus.getenv.binhostURL()
    isSane = sisyphus.checkenv.sanity()

    if isSane == 1:
        syncAll()
    else:
        if "packages-next" in binhostURL:
            print(sisyphus.getcolor.green + "\n\nActive branch:" + " " + sisyphus.getcolor.reset + "'" + activeBranch + "'" + " " + "(stable)" +
                  " " + sisyphus.getcolor.green + "\nActive binhost:" + " " + sisyphus.getcolor.reset + "'" + binhostURL + "'" + " " + "(testing)")
        else:
            print(sisyphus.getcolor.green + "\n\nActive branch:" + " " + sisyphus.getcolor.reset + "'" + activeBranch + "'" + " " + "(testing)" +
                  " " + sisyphus.getcolor.green + "\nActive binhost:" + " " + sisyphus.getcolor.reset + "'" + binhostURL + "'" + " " + "(stable)")
        sys.exit(sisyphus.getcolor.bright_red + "\n\nInvalid configuration!" + sisyphus.getcolor.reset + sisyphus.getcolor.bright_yellow +
                 "\nUse" + sisyphus.getcolor.reset + " " + "'" + "sisyphus branch --help" + "'" + " " + sisyphus.getcolor.bright_yellow + "for help" + sisyphus.getcolor.reset)


def xstart():
    activeBranch = sisyphus.getenv.systemBranch()
    binhostURL = sisyphus.getenv.binhostURL()
    isSane = sisyphus.checkenv.sanity()

    if isSane == 1:
        syncAll()
    else:
        if "packages-next" in binhostURL:
            print("\n\nActive branch:" + " " + "'" + activeBranch + "'" + " " + "(stable)" +
                  "\nActive binhost:" + " " + "'" + binhostURL + "'" + " " + "(testing)")
        else:
            print("\n\nActive branch:" + " " + "'" + activeBranch + "'" + " " + "(testing)" +
                  "\nActive binhost:" + " " + "'" + binhostURL + "'" + " " + "(stable)")
        print("\n\nInvalid configuration!" +
              "\nUse 'sisyphus branch --help' for help\n")
        t = int(10)
        while t:
            mins, secs = divmod(t, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)
            print(timer, end="\r")
            time.sleep(1)
            t -= 1
        sys.exit()
