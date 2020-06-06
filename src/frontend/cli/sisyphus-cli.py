#!/usr/bin/python3

import sisyphus.branchinject
import sisyphus.check
import sisyphus.help
import sisyphus.install
import sisyphus.mirror
import sisyphus.removeorphans
import sisyphus.rescue
import sisyphus.search
import sisyphus.setjobs
import sisyphus.sysinfo
import sisyphus.uninstall
import sisyphus.uninstallforce
import sisyphus.update
import sisyphus.upgrade
import sys

sisyphus.check.update()
sisyphus.setjobs.start.__wrapped__() # undecorate
pkgList = sys.argv[2:]

if "__main__" == __name__:
    if sys.argv[1:]:
        if "--install" in sys.argv[1:]:
            if not pkgList:
                sys.exit("\n" + "Nothing to install, please provide at least one package name; quitting" + "\n")
            else:
                sisyphus.install.start(pkgList)
        elif "--uninstall" in sys.argv[1:]:
            if not pkgList:
                sys.exit("\n" + "Nothing to uninstall, please provide at least one package name; quitting" + "\n")
            else:
                sisyphus.uninstall.start(pkgList)
        elif "--force-uninstall" in sys.argv[1:]:
            if not pkgList:
                sys.exit("\n" + "Nothing to force uninstall, please provide at least one package name; quitting" + "\n")
            else:
                sisyphus.uninstallforce.start(pkgList)
        elif "--remove-orphans" in sys.argv[1:]:
            sisyphus.removeorphans.start()
        elif "--search" in sys.argv[1:]:
            if not pkgList:
                sys.exit("\n" + "Nothing to search, please provide at least one package name; quitting" + "\n")
            else:
                sisyphus.search.start(pkgList)
        elif "--update" in sys.argv[1:]:
            sisyphus.update.start()
        elif "--upgrade" in sys.argv[1:]:
            sisyphus.upgrade.start()
        elif "--rescue" in sys.argv[1:]:
            sisyphus.rescue.start()
        elif "--sysinfo" in sys.argv[1:]:
            sisyphus.sysinfo.show()
        elif "--mirror" in sys.argv[1:]:
            if "--list" in sys.argv[2:]:
                sisyphus.mirror.printList()
            elif "--set" in sys.argv[2:]:
                if sys.argv[3:]:
                    sisyphus.mirror.setActive(sys.argv[3:])
                else:
                    sisyphus.help.show()
            else:
                sisyphus.help.show()
        elif "--branch=master" in sys.argv[1:]:
            if "--remote=gitlab" in sys.argv[2:]:
                sisyphus.branchinject.gitlabMaster()
            elif "--remote=pagure" in sys.argv[2:]:
                sisyphus.branchinject.pagureMaster()
            else:
                sisyphus.help.show()
        elif "--branch=next" in sys.argv[1:]:
            if "--remote=gitlab" in sys.argv[2:]:
                sisyphus.branchinject.gitlabNext()
            elif "--remote=pagure" in sys.argv[2:]:
                sisyphus.branchinject.pagureNext()
            else:
                sisyphus.help.show()
        elif "--help" in sys.argv[1:]:
            sisyphus.help.show()
    else:
        sisyphus.help.show()
