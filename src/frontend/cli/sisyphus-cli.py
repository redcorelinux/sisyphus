#!/usr/bin/python3

import sys
from libsisyphus import *

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
            startSync()
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
                printMirrorList()
            elif "set" in sys.argv[2:]:
                if sys.argv[3:]:
                    setActiveMirror(sys.argv[3:])
                else:
                    showHelp()
            else:
                showHelp()
        elif "help" in sys.argv[1:]:
            showHelp()
    else:
        showHelp()
