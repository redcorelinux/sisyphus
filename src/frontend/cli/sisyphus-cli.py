#!/usr/bin/python3

import sys
from libsisyphus import *

#checkSystemMode()

pkgList = sys.argv[2:]

if "__main__" == __name__:
    if sys.argv[1:]:
        if "install" in sys.argv[1:]:
            startInstall(pkgList)
        elif "uninstall" in sys.argv[1:]:
            startUninstall(pkgList)
        elif "force-uninstall" in sys.argv[1:]:
            startUninstallForce(pkgList)
        elif "remove-orphans" in sys.argv[1:]:
            removeOrphans()
        elif "update" in sys.argv[1:]:
            startUpdate()
        elif "upgrade" in sys.argv[1:]:
            startUpgrade()
        elif "search" in sys.argv[1:]:
            startSearch(pkgList)
        elif "spmsync" in sys.argv[1:]:
            startSyncSPM()
        elif "rescue" in sys.argv[1:]:
            rescueDB()
        elif "sysinfo" in sys.argv[1:]:
            sysInfo()
        elif "mirror" in sys.argv[1:]:
            if "list" in sys.argv[2:]:
                listRepo()
            elif "set" in sys.argv[2:]:
                if sys.argv[3:]:
                    setRepo(sys.argv[3:])
                else:
                    showHelp()
            else:
                showHelp()
        elif "help" in sys.argv[1:]:
            showHelp()
    else:
        showHelp()
