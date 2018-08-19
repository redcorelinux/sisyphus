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

# only run as root (CLI + GUI frontend)

def checkRoot():
    if not os.getuid() == 0:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

# only run in binary mode (binmode) or hybrid mode (mixedmode) (CLI + GUI frontend)

def checkSystemMode():
    portageBinCfg = '/opt/redcore-build/conf/intel/portage/make.conf.amd64-binmode'
    portageCfgSym = '/etc/portage/make.conf'

    if not os.path.islink(portageCfgSym):
        print("\nmake.conf is not a symlink, refusing to run!\n")
        sys.exit(1)
    else:
        if os.path.realpath(portageCfgSym) == portageBinCfg:
            pass
        else:
            print("\nThe system is not set to binmode, refusing to run!\n")
            sys.exit(1)

# get current mirror information, so we know where we download from (CLI + GUI frontend)

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

# download remote CSV's to be imported into the database (CLI + GUI frontend)

def fetchRemoteDatabase():
    remotePkgsURL = getRemotePkgsURL()
    remoteDscsURL = getRemoteDscsURL()
    http = urllib3.PoolManager()

    with http.request('GET', remotePkgsURL, preload_content=False) as tmp_buffer, open(remotePkgsDB, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)

    with http.request('GET', remoteDscsURL, preload_content=False) as tmp_buffer, open(remoteDscsDB, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)

# generate local CSV's to be imported into the database (CLI + GUI frontend)

def makeLocalDatabase():
    subprocess.check_call(['/usr/share/sisyphus/helpers/make_local_csv']) # this is really hard to do in python, so we cheat with a bash helper script

# download and import remote CSV's into the database (CLI + GUI frontend)

def syncRemoteDatabase():
    fetchRemoteDatabase()

    sisyphusdb = sqlite3.connect(sisyphusDB)
    sisyphusdb.cursor().execute('''drop table if exists remote_packages''')
    sisyphusdb.cursor().execute('''create table remote_packages (category TEXT,name TEXT,version TEXT,slot TEXT)''')
    with open(remotePkgsDB) as rmtCsv:
        for row in csv.reader(rmtCsv):
            sisyphusdb.cursor().execute("insert into remote_packages (category, name, version, slot) values (?, ?, ?, ?);", row)
    sisyphusdb.commit()
    sisyphusdb.close()

    sisyphusdb = sqlite3.connect(sisyphusDB)
    sisyphusdb.cursor().execute('''drop table if exists remote_descriptions''')
    sisyphusdb.cursor().execute('''create table remote_descriptions (category TEXT,name TEXT,description TEXT)''')
    with open(remoteDscsDB) as rmtCsv:
        for row in csv.reader(rmtCsv):
            sisyphusdb.cursor().execute("insert into remote_descriptions (category, name, description) values (?, ?, ?);", row)
    sisyphusdb.commit()
    sisyphusdb.close()

# generate and import local CSV's into the database (CLI + GUI frontend)

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

# sync portage tree (CLI + GUI frontend)

def syncPortageTree():
    subprocess.call(['emerge', '--sync', '--quiet'])

# sync portage configuration files (CLI + GUI frontend)

def syncPortageCfg():
    os.chdir(portageCfg)
    subprocess.call(['git', 'pull', '--quiet'])

# check remote timestamps...if newer than local timestamps, sync everything (CLI + GUI frontend)

@animation.wait('syncing remote database')
def syncAll():
    checkRoot()

    remotePkgsURL = getRemotePkgsURL()
    remoteDscsURL = getRemoteDscsURL()
    http = urllib3.PoolManager()

    reqRemotePkgsTS = http.request('HEAD',remotePkgsURL)
    remotePkgsTS = int(parser.parse(reqRemotePkgsTS.headers['last-modified']).strftime("%s"))
    localPkgsTS = int(os.path.getctime(remotePkgsDB))

    reqRemoteDscsTS = http.request('HEAD',remoteDscsURL)
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

# regenerate local CSV's and import them into the database (CLI frontend)
# if something is installed with portage directly using emerge, sisyphus won't be aware of it
# this will parse local portage database and import the changes into sisyphus database

@animation.wait('syncing local database')
def startSyncSPM():
    syncLocalDatabase()

# sync portage tree and portage configuration files (CLI frontend)

@animation.wait('syncing portage')
def startSync():
    syncPortageTree()
    syncPortageCfg()

# regenerate sisyphus database (CLI frontend)
# if for some reason sisyphus database gets corrupted or deleted, we can still regenerate it from portage database
# this will fetch remote information from mirrors, parse local portage database and regenerate sisyphus database

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

# call portage to solve package(s) dependencies (CLI frontend)

@animation.wait('resolving dependencies')
def solvePkgDeps(pkgList):
    pkgDeps = []
    portageExec = subprocess.Popen(['emerge', '-qgp'] + pkgList, stdout=subprocess.PIPE)
    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "/" in portageOutput.rstrip():
            pkgDep = str(portageOutput.rstrip().split("]")[1].strip("\ "))
            pkgDeps.append(pkgDep)
    return pkgDeps

# call portage to solve world dependencies (CLI frontend)

@animation.wait('resolving dependencies')
def solveWorldDeps():
    worldDeps = []
    portageExec = subprocess.Popen(['emerge', '-uDNqgp', '--backtrack=100', '--with-bdeps=y', '@world'], stdout=subprocess.PIPE)
    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "/" in portageOutput.rstrip():
            worldDep = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            worldDeps.append(worldDep)
    return worldDeps

# fetch binaries and call portage to install the package(s) from local cache (CLI frontend)

def startInstall(pkgList):
    syncAll()

    binhostURL = getBinhostURL()
    pkgDeps = solvePkgDeps(pkgList)
    pkgBins = []

    if input("Would you like to merge these packages?" + " " + str(pkgDeps) + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
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
        os.remove(str(binpkg + '.xpak')) # we extracted the categories, safe to delete

        if os.path.isdir(portageCache + CATEGORY.decode().strip()):
            shutil.move(str(binpkg + '.tbz2'), os.path.join(portageCache + CATEGORY.decode().strip(), os.path.basename(str(binpkg + '.tbz2'))))
        else:
            os.makedirs(portageCache + CATEGORY.decode().strip())
            shutil.move(str(binpkg + '.tbz2'), os.path.join(portageCache + CATEGORY.decode().strip(), os.path.basename(str(binpkg + '.tbz2'))))

        if os.path.exists(str(binpkg + '.tbz2')):
            os.remove(str(binpkg + '.tbz2')) # we moved the binaries in cache, safe to delete

    portageExec = subprocess.Popen(['emerge', '-q'] + pkgList)
    portageExec.wait()
    syncLocalDatabase()

# call portage to uninstall the package(s) (CLI frontend)

def startUninstall(pkgList):
    portageExec = subprocess.Popen(['emerge', '-cqa'] + pkgList)
    portageExec.wait()
    syncLocalDatabase()

# call portage to force-uninstall the package(s) (CLI frontend)

def startUninstallForce(pkgList):
    portageExec = subprocess.Popen(['emerge', '-Cqa'] + pkgList)
    portageExec.wait()
    syncLocalDatabase()

# call portage to remove orphan package(s) (CLI frontend)

def removeOrphans():
    portageExec = subprocess.Popen(['emerge', '-cqa'])
    portageExec.wait()
    syncLocalDatabase()

# call portage to perform a system upgrade (CLI frontend)

def startUpgrade():
    syncAll()

    binhostURL = getBinhostURL()
    worldDeps = solveWorldDeps()
    worldBins = []

    if input("Would you like to merge these packages?" + " " + str(worldDeps) + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
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
        os.remove(str(worldpkg + '.xpak')) # we extracted the categories, safe to delete

        if os.path.isdir(portageCache + CATEGORY.decode().strip()):
            shutil.move(str(worldpkg + '.tbz2'), os.path.join(portageCache + CATEGORY.decode().strip(), os.path.basename(str(worldpkg + '.tbz2'))))
        else:
            os.makedirs(portageCache + CATEGORY.decode().strip())
            shutil.move(str(worldpkg + '.tbz2'), os.path.join(portageCache + CATEGORY.decode().strip(), os.path.basename(str(worldpkg + '.tbz2'))))

        if os.path.exists(str(worldpkg + '.tbz2')):
            os.remove(str(worldpkg + '.tbz2')) # we moved the binaries in cache, safe to delete

    portageExec = subprocess.Popen(['emerge', '-uDNq', '--backtrack=100', '--with-bdeps=y', '@world'])
    portageExec.wait()
    syncLocalDatabase()

# call portage to search for package(s) (CLI frontend)

def startSearch(pkgList):
    subprocess.check_call(['emerge', '-sg'] + pkgList) # FIXME : query sisyphus.db instead of searching through portage

# check remote timestamps...if newer than local timestamps, sync everything (CLI + GUI frontend)

def startUpdate():
    syncAll()

# display information about installed core packages and portage configuration (CLI frontend)

def sysInfo():
    subprocess.check_call(['emerge', '--info'])

# kill background portage process if sisyphus dies (CLI + GUI frontend)

def portageKill(portageCmd):
        portageCmd.terminate()

# get a list of mirrors (GUI frontend)

def getMirrors():
    mirrorList = []
    with open(mirrorCfg) as mirrorFile:
        for line in mirrorFile.readlines():
            if 'PORTAGE_BINHOST=' in line:
                url = line.split("=")[1].replace('"', '').rstrip()
                mirror = {'isActive':True,'Url':url}
                if line.startswith('#'):
                    mirror['isActive'] = False
                mirrorList.append(mirror)
    mirrorFile.close()
    return mirrorList

# set the active mirror (GUI frontend)

def setActiveMirror(mirrorList):
    with open(mirrorCfg, 'w+') as mirrorFile:
        mirrorFile.write("#######################################################\n")
        mirrorFile.write("# Support for multiple mirrors is somewhat incomplete #\n")
        mirrorFile.write("#    Uncomment only one mirror from the list bellow   #\n")
        mirrorFile.write("#######################################################\n")
        mirrorFile.write("\n")
        for line in mirrorList :
            mirror = 'PORTAGE_BINHOST=' + '"' + line['Url'] + '"'
            if not line['isActive']:
                mirror = '# ' + mirror
            mirrorFile.write(mirror + "\n")
            mirrorFile.write("\n")

# get a list of mirrors (CLI frontend)

def listRepo():
    mirrorList = getMirrors()
    for i, line in enumerate(mirrorList):
        if line['isActive']:
            print(i+1,'*',line['Url'])
        else:
            print(i+1,' ',line['Url'])

# set the active mirror (CLI frontend)

def setRepo(mirror):
    mirror = int(mirror[0])
    mirrorList = getMirrors()
    if mirror not in range(1,len(mirrorList)+1):
        print('mirror index is wrong, please check with "sisyphus mirror list"')
    else:
        for i in range(0,len(mirrorList)):
            indx = i+1
            if indx == mirror :
                mirrorList[i]['isActive'] = True
            else:
                mirrorList[i]['isActive'] = False
        setActiveMirror(mirrorList)

# display help menu (CLI frontend)

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
