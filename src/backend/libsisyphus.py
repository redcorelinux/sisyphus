#!/usr/bin/python3

import animation
import csv
import os
import shutil
import sqlite3
import subprocess
import sys
import urllib3
import io
import wget
from dateutil import parser

portageCfg = '/opt/redcore-build/'
portageCache = '/var/cache/packages/'
remotePkgsDB = '/var/lib/sisyphus/csv/remotePackagesPre.csv'
remoteDscsDB = '/var/lib/sisyphus/csv/remoteDescriptionsPre.csv'
localPkgsDB = '/var/lib/sisyphus/csv/localPackagesPre.csv'
sisyphusDB = '/var/lib/sisyphus/db/sisyphus.db'
mirrorCfg = '/etc/sisyphus/mirrors.conf'

def checkRoot():
    if not os.getuid() == 0:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

def getMirrorList():
    mirrorList = []

    with open(mirrorCfg) as mirrorFile:
        for line in mirrorFile.readlines():
            if 'PORTAGE_BINHOST=' in line:
                url = line.split("=")[1].replace('"', '').rstrip()
                mirror = {'isActive': True, 'Url': url}
                if line.startswith('#'):
                    mirror['isActive'] = False
                mirrorList.append(mirror)
            mirrorFile.close()
        return mirrorList

def getBinhostURL():
    binhostURL = []
    portageExec = subprocess.Popen(['emerge', '--info', '--verbose'], stdout=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "PORTAGE_BINHOST" in portageOutput.rstrip():
            binhostURL = str(portageOutput.rstrip().split("=")[1].strip('\"'))
    return binhostURL

def getRemotePkgsURL():
    remotePkgsURL = []
    portageExec = subprocess.Popen(['emerge', '--info', '--verbose'], stdout=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "PORTAGE_BINHOST" in portageOutput.rstrip():
            remotePkgsURL = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages', 'csv') + 'remotePackagesPre.csv')
    return remotePkgsURL

def getRemoteDscsURL():
    remoteDscsURL = []
    portageExec = subprocess.Popen(['emerge', '--info', '--verbose'], stdout=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "PORTAGE_BINHOST" in portageOutput.rstrip():
            remoteDscsURL = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages', 'csv') + 'remoteDescriptionsPre.csv')
    return remoteDscsURL

@animation.wait('resolving dependencies')
def getPkgDeps(pkgList):
    pkgDeps = []
    portageExec = subprocess.Popen(['emerge', '--quiet', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgList, stdout=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "binary" in portageOutput.rstrip():
            pkgDep = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            pkgDeps.append(pkgDep)
    return pkgDeps

@animation.wait('resolving dependencies')
def getWorldDeps():
    worldDeps = []
    portageExec = subprocess.Popen(['emerge', '--quiet', '--update', '--deep', '--newuse', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "binary" in portageOutput.rstrip():
            worldDep = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            worldDeps.append(worldDep)
    return worldDeps

def fetchRemoteDatabase():
    remotePkgsURL = getRemotePkgsURL()
    remoteDscsURL = getRemoteDscsURL()
    http = urllib3.PoolManager()

    with http.request('GET', remotePkgsURL, preload_content=False) as tmp_buffer, open(remotePkgsDB, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)

    with http.request('GET', remoteDscsURL, preload_content=False) as tmp_buffer, open(remoteDscsDB, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)

def makeLocalDatabase():
    subprocess.check_call(['/usr/share/sisyphus/helpers/make_local_csv'])

def syncRemoteDatabase():
    fetchRemoteDatabase()

    sisyphusdb = sqlite3.connect(sisyphusDB)
    sisyphusdb.cursor().execute('''drop table if exists remote_packages''')
    sisyphusdb.cursor().execute('''drop table if exists remote_descriptions''')
    sisyphusdb.cursor().execute('''create table remote_packages (category TEXT,name TEXT,version TEXT,slot TEXT)''')
    sisyphusdb.cursor().execute('''create table remote_descriptions (category TEXT,name TEXT,description TEXT)''')

    with open(remotePkgsDB) as rmtCsv:
        for row in csv.reader(rmtCsv):
            sisyphusdb.cursor().execute("insert into remote_packages (category, name, version, slot) values (?, ?, ?, ?);", row)

    with open(remoteDscsDB) as rmtCsv:
        for row in csv.reader(rmtCsv):
            sisyphusdb.cursor().execute("insert into remote_descriptions (category, name, description) values (?, ?, ?);", row)

    sisyphusdb.commit()
    sisyphusdb.close()

def syncLocalDatabase():
    makeLocalDatabase()

    sisyphusdb = sqlite3.connect(sisyphusDB)
    sisyphusdb.cursor().execute('''drop table if exists local_packages''')
    sisyphusdb.cursor().execute('''create table local_packages (category TEXT,name TEXT,version TEXT,slot TEXT)''')

    with open(localPkgsDB) as lclCsv:
        for row in csv.reader(lclCsv):
            sisyphusdb.cursor().execute("insert into local_packages (category, name, version, slot) values (?, ?, ?, ?);", row)

    sisyphusdb.commit()
    sisyphusdb.close()

def syncPortageTree():
    subprocess.call(['emerge', '--sync', '--quiet'])

def syncPortageCfg():
    os.chdir(portageCfg)
    subprocess.call(['git', 'pull', '--quiet'])

@animation.wait('syncing remote database')
def syncAll():
    checkRoot()

    remotePkgsURL = getRemotePkgsURL()
    remoteDscsURL = getRemoteDscsURL()
    http = urllib3.PoolManager()

    reqRemotePkgsTS = http.request('HEAD', remotePkgsURL)
    remotePkgsTS = int(parser.parse(reqRemotePkgsTS.headers['last-modified']).strftime("%s"))
    localPkgsTS = int(os.path.getctime(remotePkgsDB))

    reqRemoteDscsTS = http.request('HEAD', remoteDscsURL)
    remoteDscsTS = int(parser.parse(reqRemoteDscsTS.headers['last-modified']).strftime("%s"))
    localDscsTS = int(os.path.getctime(remoteDscsDB))

    if remotePkgsTS < localPkgsTS:
        pass
    elif remoteDscsTS < localDscsTS:
        pass
    else:
        syncPortageTree()
        syncPortageCfg()
        syncRemoteDatabase()

@animation.wait('syncing local database')
def startSyncSPM():
    syncLocalDatabase()

@animation.wait('syncing portage')
def startSync():
    syncPortageTree()
    syncPortageCfg()

@animation.wait('resurrecting database')
def rescueDB():
    if os.path.exists(remotePkgsDB):
        os.remove(remotePkgsDB)
    if os.path.exists(remoteDscsDB):
        os.remove(remoteDscsDB)
    if os.path.exists(localPkgsDB):
        os.remove(localPkgsDB)
    if os.path.exists(sisyphusDB):
        os.remove(sisyphusDB)

    syncRemoteDatabase()
    syncLocalDatabase()

def startSearch(pkgList):
    subprocess.check_call(['emerge', '--search', '--getbinpkg'] + pkgList)

def startUpdate():
    syncAll()

def startInstall(pkgList):
    syncAll()

    binhostURL = getBinhostURL()
    pkgDeps = getPkgDeps(pkgList)
    pkgBins = []

    if not len(pkgDeps) == 0:
        os.chdir(portageCache)
        if input("\n" + "These are the packages that would be merged, in order:" + "\n\n"  + str(pkgDeps) + "\n\n" + "Total:" + " " + str(len(pkgDeps)) + " " + "package(s)" + "\n\n" "Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
            for index, url in enumerate([binhostURL + package + '.tbz2' for package in pkgDeps]):
                print(">>> Fetching" + " " + url)
                wget.download(url)
                print("\n")
        else:
            sys.exit("\n" + "Quitting!")

        for index, binpkg in enumerate(pkgDeps):
            pkgBin = str(binpkg.rstrip().split("/")[1])
            pkgBins.append(pkgBin)

        for index, binpkg in enumerate(pkgBins):
            subprocess.call(['qtbz2', '-x'] + str(binpkg + '.tbz2').split())
            CATEGORY = subprocess.check_output(['qxpak', '-x', '-O'] + str(binpkg + '.xpak').split() + ['CATEGORY'])
            os.remove(str(binpkg + '.xpak'))

            if os.path.isdir(portageCache + CATEGORY.decode().strip()):
                shutil.move(str(binpkg + '.tbz2'), os.path.join(portageCache + CATEGORY.decode().strip(), os.path.basename(str(binpkg + '.tbz2'))))
            else:
                os.makedirs(portageCache + CATEGORY.decode().strip())
                shutil.move(str(binpkg + '.tbz2'), os.path.join(portageCache + CATEGORY.decode().strip(), os.path.basename(str(binpkg + '.tbz2'))))

            if os.path.exists(str(binpkg + '.tbz2')):
                os.remove(str(binpkg + '.tbz2'))

        portageExec = subprocess.Popen(['emerge', '--quiet', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgList)
        portageExec.wait()
        syncLocalDatabase()
    else:
        sys.exit("\n" + "No such package; quitting." + "\n")

def startUpgrade():
    syncAll()

    binhostURL = getBinhostURL()
    worldDeps = getWorldDeps()
    worldBins = []

    if not len(worldDeps) == 0:
        os.chdir(portageCache)
        if input("\n" + "These are the packages that would be merged, in order:" + "\n\n"  + str(worldDeps) + "\n\n" + "Total:" + " " + str(len(worldDeps)) + " " + "package(s)" + "\n\n" "Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
            for index, url in enumerate([binhostURL + package + '.tbz2' for package in worldDeps]):
                print(">>> Fetching" + " " + url)
                wget.download(url)
                print("\n")
        else:
            sys.exit("\n" + "Quitting!")

        for index, worldpkg in enumerate(worldDeps):
            worldBin = str(worldpkg.rstrip().split("/")[1])
            worldBins.append(worldBin)

        for index, worldpkg in enumerate(worldBins):
            subprocess.call(['qtbz2', '-x'] + str(worldpkg + '.tbz2').split())
            CATEGORY = subprocess.check_output(['qxpak', '-x', '-O'] + str(worldpkg + '.xpak').split() + ['CATEGORY'])
            os.remove(str(worldpkg + '.xpak'))

            if os.path.isdir(portageCache + CATEGORY.decode().strip()):
                shutil.move(str(worldpkg + '.tbz2'), os.path.join(portageCache + CATEGORY.decode().strip(), os.path.basename(str(worldpkg + '.tbz2'))))
            else:
                os.makedirs(portageCache + CATEGORY.decode().strip())
                shutil.move(str(worldpkg + '.tbz2'), os.path.join(portageCache + CATEGORY.decode().strip(), os.path.basename(str(worldpkg + '.tbz2'))))

            if os.path.exists(str(worldpkg + '.tbz2')):
                os.remove(str(worldpkg + '.tbz2'))

        portageExec = subprocess.Popen(['emerge', '--quiet', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
        portageExec.wait()
        syncLocalDatabase()
    else:
        sys.exit("\n" + "Nothing to upgrade; quitting." + "\n")

def startUninstall(pkgList):
    portageExec = subprocess.Popen(['emerge', '--quiet', '--depclean', '--ask'] + pkgList)
    portageExec.wait()
    syncLocalDatabase()

def startUninstallForce(pkgList):
    portageExec = subprocess.Popen(['emerge', '--quiet', '--unmerge', '--ask'] + pkgList)
    portageExec.wait()
    syncLocalDatabase()

def removeOrphans():
    portageExec = subprocess.Popen(['emerge', '--quiet', '--depclean', '--ask'])
    portageExec.wait()
    syncLocalDatabase()

def sysInfo():
    subprocess.check_call(['emerge', '--info'])

def portageKill(portageCmd):
    portageCmd.terminate()


def printMirrorList():
    mirrorList = getMirrorList()

    for i, line in enumerate(mirrorList):
        if line['isActive']:
            print(i + 1, '*', line['Url'])
        else:
            print(i + 1, ' ', line['Url'])

def writeMirrorCfg(mirrorList):
    with open(mirrorCfg, 'w+') as mirrorFile:
        mirrorFile.write("#######################################################\n")
        mirrorFile.write("# Support for multiple mirrors is somewhat incomplete #\n")
        mirrorFile.write("#    Uncomment only one mirror from the list bellow   #\n")
        mirrorFile.write("#######################################################\n")
        mirrorFile.write("\n")
        for line in mirrorList:
            mirror = 'PORTAGE_BINHOST=' + '"' + line['Url'] + '"'
            if not line['isActive']:
                mirror = '# ' + mirror
            mirrorFile.write(mirror + "\n")
            mirrorFile.write("\n")

def setActiveMirror(mirror):
    mirror = int(mirror[0])
    mirrorList = getMirrorList()
    if mirror not in range(1, len(mirrorList) + 1):
        print('mirror index is wrong, please check with "sisyphus mirror list"')
    else:
        for i in range(0, len(mirrorList)):
            indx = i + 1
            if indx == mirror:
                mirrorList[i]['isActive'] = True
            else:
                mirrorList[i]['isActive'] = False
        writeMirrorCfg(mirrorList)

def showHelp():
    print("\nUsage : sisyphus command [package(s)] || [file(s)]\n")
    print("Sisyphus is a simple python wrapper around portage, gentoolkit, and portage-utils that provides")
    print("an apt-get/yum-alike interface to these commands, to assist newcomer people transitioning from")
    print("Debian/RedHat-based systems to Gentoo.\n")
    print("Commands :\n")
    print("install - Install new packages")
    print("uninstall - Uninstall packages *safely* (INFO : If reverse deps are found, package(s) will NOT be uninstalled)")
    print("force-uninstall - Uninstall packages *unsafely* (WARNING : This option will ignore reverse deps, which may break your system)")
    print("remove-orphans - Uninstall packages that are no longer needed")
    print("update - Update the Portage tree, Overlay(s), Portage config files && Sisyphus database remote_packages table")
    print("upgrade -  Upgrade the system")
    print("search - Search for packages")
    print("spmsync - Sync Sisyphus database with Portage database (if you install something with Portage, not Sisyphus)")
    print("rescue - Rescue Sisyphus database if lost or corrupted")
    print("mirror list - List available mirrors (the active one is marked with *)")
    print("mirror set INDEX - Switch the repository to the selected mirror")
    print("sysinfo - Display information about installed core packages and portage configuration")
