#!/usr/bin/python3

import sys
from libsisyphus import *

pkgList = sys.argv[2:]

if "__main__" == __name__:
    if sys.argv[1:]:
        if "--install" in sys.argv[1:]:
            if not pkgList:
                sys.exit("\n" + "Nothing to install, please provide at least one package name; quitting" + "\n")
            else:
                startInstall(pkgList)
        elif "--hybrid-install" in sys.argv[1:]:
            if not pkgList:
                sys.exit("\n" + "Nothing to install, please provide at least one package name; quitting" + "\n")
            else:
                startHybridInstall(pkgList)
        elif "--uninstall" in sys.argv[1:]:
            if not pkgList:
                sys.exit("\n" + "Nothing to uninstall, please provide at least one package name; quitting" + "\n")
            else:
                startUninstall(pkgList)
        elif "--force-uninstall" in sys.argv[1:]:
            if not pkgList:
                sys.exit("\n" + "Nothing to force uninstall, please provide at least one package name; quitting" + "\n")
            else:
                startUninstallForce(pkgList)
        elif "--remove-orphans" in sys.argv[1:]:
            removeOrphans()
        elif "--update" in sys.argv[1:]:
            startUpdate()
        elif "--upgrade" in sys.argv[1:]:
            startUpgrade()
        elif "--hybrid-upgrade" in sys.argv[1:]:
            startHybridUpgrade()
        elif "--search" in sys.argv[1:]:
            if not pkgList:
                sys.exit("\n" + "Nothing to search, please provide at least one package name; quitting" + "\n")
            else:
                startSearch(pkgList)
        elif "--hybrid-search" in sys.argv[1:]:
            if not pkgList:
                sys.exit("\n" + "Nothing to search, please provide at least one package name; quitting" + "\n")
            else:
                startHybridSearch(pkgList)
        elif "--spmsync" in sys.argv[1:]:
            startSyncSPM()
        elif "--rescue" in sys.argv[1:]:
            rescueDB()
        elif "--sysinfo" in sys.argv[1:]:
            sysInfo()
        elif "--mirror" in sys.argv[1:]:
            if "--list" in sys.argv[2:]:
                printMirrorList()
            elif "--set" in sys.argv[2:]:
                if sys.argv[3:]:
                    setActiveMirror(sys.argv[3:])
                else:
                    showHelp()
            else:
                showHelp()
        elif "--help" in sys.argv[1:]:
            showHelp()
    else:
        showHelp()
