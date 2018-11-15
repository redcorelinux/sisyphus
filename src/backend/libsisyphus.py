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

@animation.wait('resolving binary dependencies')
def getPkgBinaryDeps(pkgList):
    binaryDeps = []
    portageExec = subprocess.Popen(['emerge', '--quiet', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgList, stdout=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "binary" in portageOutput.rstrip():
            binaryDep = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            binaryDeps.append(binaryDep)
    return binaryDeps

@animation.wait('resolving source dependencies')
def getPkgSourceDeps(pkgList):
    sourceDeps = []
    portageExec = subprocess.Popen(['emerge', '--quiet', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgList, stdout=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "ebuild" in portageOutput.rstrip():
            sourceDep = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            sourceDeps.append(sourceDep)
    return sourceDeps

@animation.wait('resolving binary dependencies')
def getWorldBinaryDeps():
    binaryDeps = []
    portageExec = subprocess.Popen(['emerge', '--quiet', '--update', '--deep', '--newuse', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "binary" in portageOutput.rstrip():
            binaryDep = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            binaryDeps.append(binaryDep)
    return binaryDeps

@animation.wait('resolving source dependencies')
def getWorldSourceDeps():
    sourceDeps = []
    portageExec = subprocess.Popen(['emerge', '--quiet', '--update', '--deep', '--newuse', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "ebuild" in portageOutput.rstrip():
            sourceDep = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            sourceDeps.append(sourceDep)
    return sourceDeps

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
    binaryDeps = getPkgBinaryDeps(pkgList)
    sourceDeps = getPkgSourceDeps(pkgList)
    binaryPkgs = []

    if len(sourceDeps) == 0:
        if not len(binaryDeps) == 0:
            os.chdir(portageCache)
            print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n"  + str(binaryDeps) + "\n\n" + "Total:" + " " + str(len(binaryDeps)) + " " + "binary package(s)" + "\n")
            if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                for index, url in enumerate([binhostURL + package + '.tbz2' for package in binaryDeps]):
                    print(">>> Fetching" + " " + url)
                    wget.download(url)
                    print("\n")

                for index, binpkg in enumerate(binaryDeps):
                    binaryPkg = str(binpkg.rstrip().split("/")[1])
                    binaryPkgs.append(binaryPkg)

                for index, binpkg in enumerate(binaryPkgs):
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

                portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgList)
                portageExec.wait()
                syncLocalDatabase()
            else:
                sys.exit("\n" + "Ok; Quitting." + "\n")
        else:
            sys.exit("\n" + "No package found; Quitting." + "\n")
    else:
        sys.exit("\n" + "No binary package found; Source package found; Use sisyphus --hybrid-install; Quitting." + "\n")

def startHybridInstall(pkgList):
    syncAll()

    binhostURL = getBinhostURL()
    binaryDeps = getPkgBinaryDeps(pkgList)
    sourceDeps = getPkgSourceDeps(pkgList)
    binaryPkgs = []

    if len(sourceDeps) == 0:
        if not len(binaryDeps) == 0:
            os.chdir(portageCache)
            print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n"  + str(binaryDeps) + "\n\n" + "Total:" + " " + str(len(binaryDeps)) + " " + "binary package(s)" + "\n")
            if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                for index, url in enumerate([binhostURL + package + '.tbz2' for package in binaryDeps]):
                    print(">>> Fetching" + " " + url)
                    wget.download(url)
                    print("\n")

                for index, binpkg in enumerate(binaryDeps):
                    binaryPkg = str(binpkg.rstrip().split("/")[1])
                    binaryPkgs.append(binaryPkg)

                for index, binpkg in enumerate(binaryPkgs):
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

                portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgList)
                portageExec.wait()
                syncLocalDatabase()
            else:
                sys.exit("\n" + "Ok; Quitting." + "\n")
        else:
            sys.exit("\n" + "No package found; Quitting." + "\n")
    else:
        if not len(binaryDeps) == 0:
            os.chdir(portageCache)
            print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n" + str(binaryDeps) + "\n\n" + "Total:" + " " + str(len(binaryDeps)) + " " + "binary package(s)" + "\n")
            print("\n" + "These are the source packages that would be merged, in order:" + "\n\n"  + str(sourceDeps) + "\n\n" + "Total:" + " " + str(len(sourceDeps)) + " " + "source package(s)" + "\n")
            if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                for index, url in enumerate([binhostURL + package + '.tbz2' for package in binaryDeps]):
                    print(">>> Fetching" + " " + url)
                    wget.download(url)
                    print("\n")

                for index, binpkg in enumerate(binaryDeps):
                    binaryPkg = str(binpkg.rstrip().split("/")[1])
                    binaryPkgs.append(binaryPkg)

                for index, binpkg in enumerate(binaryPkgs):
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

                portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--usepkg', '--rebuilt-binaries', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgList)
                portageExec.wait()
                syncLocalDatabase()
            else:
                sys.exit("\n" + "Ok; Quitting." + "\n")
        else:
            print("\n" + "These are the source packages that would be merged, in order:" + "\n\n"  + str(sourceDeps) + "\n\n" + "Total:" + " " + str(len(sourceDeps)) + " " + "source package(s)" + "\n")
            if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgList)
                portageExec.wait()
                syncLocalDatabase()
            else:
                sys.exit("\n" + "Ok; Quitting." + "\n")

def startUpgrade():
    syncAll()

    binhostURL = getBinhostURL()
    binaryDeps = getWorldBinaryDeps()
    sourceDeps = getWorldSourceDeps()
    binaryPkgs = []

    if len(sourceDeps) == 0:
        if not len(binaryDeps) == 0:
            os.chdir(portageCache)
            print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n"  + str(binaryDeps) + "\n\n" + "Total:" + " " + str(len(binaryDeps)) + " " + "binary package(s)" + "\n")
            if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                for index, url in enumerate([binhostURL + package + '.tbz2' for package in binaryDeps]):
                    print(">>> Fetching" + " " + url)
                    wget.download(url)
                    print("\n")

                for index, worldpkg in enumerate(binaryDeps):
                    binaryPkg = str(worldpkg.rstrip().split("/")[1])
                    binaryPkgs.append(binaryPkg)

                for index, worldpkg in enumerate(binaryPkgs):
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

                portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                portageExec.wait()
                syncLocalDatabase()
            else:
                sys.exit("\n" + "Ok; Quitting." + "\n")
        else:
            sys.exit("\n" + "No package upgrades found; Quitting." + "\n")
    else:
        sys.exit("\n" + "No binary package upgrades found; Source package upgrades found; Use sisyphus --hybrid-upgrade; Quitting." + "\n")

def startHybridUpgrade():
    syncAll()

    binhostURL = getBinhostURL()
    binaryDeps = getWorldBinaryDeps()
    sourceDeps = getWorldSourceDeps()
    binaryPkgs = []

    if len(sourceDeps) == 0:
        if not len(binaryDeps) == 0:
            os.chdir(portageCache)
            print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n"  + str(binaryDeps) + "\n\n" + "Total:" + " " + str(len(binaryDeps)) + " " + "binary package(s)" + "\n")
            if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                for index, url in enumerate([binhostURL + package + '.tbz2' for package in binaryDeps]):
                    print(">>> Fetching" + " " + url)
                    wget.download(url)
                    print("\n")

                for index, worldpkg in enumerate(binaryDeps):
                    binaryPkg = str(worldpkg.rstrip().split("/")[1])
                    binaryPkgs.append(binaryPkg)

                for index, worldpkg in enumerate(binaryPkgs):
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

                portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                portageExec.wait()
                syncLocalDatabase()
            else:
                sys.exit("\n" + "Ok; Quitting." + "\n")
        else:
            sys.exit("\n" + "No package upgrades found; Quitting." + "\n")
    else:
        if not len(binaryDeps) == 0:
            os.chdir(portageCache)
            print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n" + str(binaryDeps) + "\n\n" + "Total:" + " " + str(len(binaryDeps)) + " " + "binary package(s)" + "\n")
            print("\n" + "These are the source packages that would be merged, in order:" + "\n\n"  + str(sourceDeps) + "\n\n" + "Total:" + " " + str(len(sourceDeps)) + " " + "source package(s)" + "\n")
            if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                for index, url in enumerate([binhostURL + package + '.tbz2' for package in binaryDeps]):
                    print(">>> Fetching" + " " + url)
                    wget.download(url)
                    print("\n")

                for index, worldpkg in enumerate(binaryDeps):
                    binaryPkg = str(worldpkg.rstrip().split("/")[1])
                    binaryPkgs.append(binaryPkg)

                for index, worldpkg in enumerate(binaryPkgs):
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

                portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                portageExec.wait()
                syncLocalDatabase()
            else:
                sys.exit("\n" + "Ok; Quitting." + "\n")
        else:
            print("\n" + "These are the source packages that would be merged, in order:" + "\n\n"  + str(sourceDeps) + "\n\n" + "Total:" + " " + str(len(sourceDeps)) + " " + "source package(s)" + "\n")
            if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                portageExec.wait()
                syncLocalDatabase()
            else:
                sys.exit("\n" + "Ok; Quitting." + "\n")

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
        print('mirror index is wrong, please check with "sisyphus --mirror --list"')
    else:
        for i in range(0, len(mirrorList)):
            indx = i + 1
            if indx == mirror:
                mirrorList[i]['isActive'] = True
            else:
                mirrorList[i]['isActive'] = False
        writeMirrorCfg(mirrorList)

def showHelp():
    print("\n" + "Usage : sisyphus command [package(s)] || [file(s)]" + "\n")
    print("Sisyphus is a simple python wrapper around portage, gentoolkit, and portage-utils which provides")
    print("an apt-get/yum-alike interface to these commands, to assist newcomer people transitioning from")
    print("Debian/RedHat-based systems to Gentoo." + "\n")
    print("Commands :" + "\n")
    print("--install")
    print("* Install binary packages" + "\n")
    print("--hybrid-install")
    print("* Install binary and/or ebuild (source) packages" + "\n")
    print("--uninstall")
    print("* Uninstall packages *SAFELY* by checking for reverse dependencies")
    print("* If reverse dependencies exist, the package(s) will NOT be uninstalled to prevent the possible breakage of the system")
    print("* If you really want to uninstall the package, make sure you uninstall all reverse dependencies as well")
    print("* This will not allways be possible, as the reverse dependency chain may be way to long and require you to uninstall critical system packages" + "\n")
    print("--force-uninstall")
    print("* Uninstall packages *UNSAFELY* by ignoring reverse dependencies")
    print("* This may break your system if you uninstall critical system packages")
    print("* It will try the best it can to preserve the libraries required by other packages to prevent such a breakage")
    print("* Upgrading the system may pull the packages back in, to fix the reverse dependency chain" + "\n")
    print("--remove-orphans")
    print("* Uninstall packages that are no longer needed")
    print("* When you uninstall a package without it's reverse dependencies, those dependencies will become orphans if nothing else requires them")
    print("* In addition, a package may no longer depend on another one, so that other package becomes orphan as well if nothing else requires it")
    print("* Use this option to check the whole dependency chain for such packages, and uninstall them" + "\n")
    print("--update")
    print("* Update the Portage tree, Overlay(s), Portage config files && Sisyphus's package database" + "\n")
    print("--upgrade")
    print("* Upgrade the system using binary packages" + "\n")
    print("--hybrid-upgrade")
    print("* Upgrade the system using binary and/or ebuild (source) packages" + "\n")
    print("--search")
    print("* Search for packages")
    print("* In binary mode this will return available binary packages")
    print("* In source mode this will return binary and ebuild (source) packages" + "\n")
    print("--spmsync")
    print("* Sync Sisyphus's package database with Portage's package database")
    print("* When you install something with Portage directly (emerge), Sisyphus is not aware of that package, and it doesn't track it in it's database")
    print("* Use this option to synchronize Sisyphus's package database with Portage's package database" + "\n")
    print("--rescue")
    print("* Resurrect Sisyphus's package database if lost or corrupted")
    print("* If for some reason Sisyphus's package database is lost or corrupted, it can be resurrected using Portage's package database")
    print("* If Portage's package database is corrupted (in this case you're screwed anyway :D), only a partial resurrection will be possible")
    print("* If Portage's package database is intact, full resurrection will be possible" + "\n")
    print("--mirror --list")
    print("* List available binary package repository mirrors (the active one is marked with *)" + "\n")
    print("--mirror --set INDEX")
    print("* Switch the binary package repository to the selected mirror" + "\n")
    print("--sysinfo")
    print("* Display information about installed core packages and portage configuration" + "\n")
    print("--help")
    print("* Display this help information" + "\n")
