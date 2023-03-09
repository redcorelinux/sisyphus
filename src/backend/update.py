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
    sisyphus.syncenv.gentooRepo()
    sisyphus.syncenv.redcoreRepo()
    sisyphus.syncenv.portageConfigRepo()
    sisyphus.syncdb.remoteTable()


@animation.wait('fetching updates')
def start():
    act_brch = sisyphus.getenv.sys_brch()
    bh_addr = sisyphus.getenv.bh_addr()
    isSane = sisyphus.checkenv.sanity()

    if isSane == 1:
        syncAll()
    else:
        if "packages-next" in bh_addr:
            print(sisyphus.getcolor.green + "\n\nActive branch:" + " " + sisyphus.getcolor.reset + "'" + act_brch + "'" + " " + "(stable)" +
                  " " + sisyphus.getcolor.green + "\nActive binhost:" + " " + sisyphus.getcolor.reset + "'" + bh_addr + "'" + " " + "(testing)")
        else:
            print(sisyphus.getcolor.green + "\n\nActive branch:" + " " + sisyphus.getcolor.reset + "'" + act_brch + "'" + " " + "(testing)" +
                  " " + sisyphus.getcolor.green + "\nActive binhost:" + " " + sisyphus.getcolor.reset + "'" + bh_addr + "'" + " " + "(stable)")
        sys.exit(sisyphus.getcolor.bright_red + "\n\nInvalid configuration!" + sisyphus.getcolor.reset + sisyphus.getcolor.bright_yellow +
                 "\nUse" + sisyphus.getcolor.reset + " " + "'" + "sisyphus branch --help" + "'" + " " + sisyphus.getcolor.bright_yellow + "for help" + sisyphus.getcolor.reset)


def xstart():
    act_brch = sisyphus.getenv.sys_brch()
    bh_addr = sisyphus.getenv.bh_addr()
    isSane = sisyphus.checkenv.sanity()

    if isSane == 1:
        syncAll()
    else:
        if "packages-next" in bh_addr:
            print("\n\nActive branch:" + " " + "'" + act_brch + "'" + " " + "(stable)" +
                  "\nActive binhost:" + " " + "'" + bh_addr + "'" + " " + "(testing)")
        else:
            print("\n\nActive branch:" + " " + "'" + act_brch + "'" + " " + "(testing)" +
                  "\nActive binhost:" + " " + "'" + bh_addr + "'" + " " + "(stable)")
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
