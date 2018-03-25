#!/usr/bin/python3

import sys
from libsisyphus import *

check_system_mode()

def listRepo():
    mirrorList = getMirrors()
    for i, line in enumerate(mirrorList):
        if line['isActive']:
            print(i+1,'*',line['Url'])
        else:
            print(i+1,' ',line['Url'])

def setRepo(mirror):
    mirror = int(mirror[0])
    mirrorList = getMirrors()
    newMirrorList = []
    if mirror not in range(1,len(mirrorList)+1):
        print('mirror index is wrong, please check with "sisyphus mirror list"')
    else:
        for i, line in enumerate(mirrorList):
            indx = i+1
            if indx == mirror :
                line['isActive'] = True
            else:
                line['isActive'] = False
            newMirrorList.append(line)
        setActiveMirror(newMirrorList)

PKGLIST = sys.argv[2:]

if "__main__" == __name__:
    if "install" in sys.argv[1:]:
        sisyphus_pkg_install(PKGLIST)
    elif "uninstall" in sys.argv[1:]:
        sisyphus_pkg_uninstall(PKGLIST)
    elif "force-uninstall" in sys.argv[1:]:
        sisyphus_pkg_force_uninstall(PKGLIST)
    elif "remove-orphans" in sys.argv[1:]:
        sisyphus_pkg_remove_orphans()
    elif "update" in sys.argv[1:]:
        sisyphus_pkg_system_update()
    elif "upgrade" in sys.argv[1:]:
        sisyphus_pkg_system_upgrade()
    elif "search" in sys.argv[1:]:
        sisyphus_pkg_search(PKGLIST)
    elif "spmsync" in sys.argv[1:]:
        sisyphus_pkg_spmsync()
    elif "rescue" in sys.argv[1:]:
        sisyphus_db_rescue()
    elif "sysinfo" in sys.argv[1:]:
        sisyphus_pkg_sysinfo()
    elif "mirror" in sys.argv[1:]:
        if not sys.argv[2:]:
            sisyphus_pkg_help()
        elif "list" in sys.argv[2]:
            listRepo()
        elif "set" in sys.argv[2:]:
            if not sys.argv[3:]:
                sisyphus_pkg_help()
            else:
                setRepo(sys.argv[3:])
    elif "help" in sys.argv[1:]:
        sisyphus_pkg_help()
    elif not sys.argv[1:]:
        sisyphus_pkg_help()
