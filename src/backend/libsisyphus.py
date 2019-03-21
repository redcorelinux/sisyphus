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

gentooEbuildDir = '/usr/ports/gentoo'
redcoreEbuildDir = '/usr/ports/redcore'
portageConfigDir = '/opt/redcore-build'
portageCacheDir = '/var/cache/packages'
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

def getCsvUrl():
    remotePkgCsv = []
    remoteDescCsv = []
    portageExec = subprocess.Popen(['emerge', '--info', '--verbose'], stdout=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "PORTAGE_BINHOST" in portageOutput.rstrip():
            if "packages-next" in portageOutput.rstrip():
                remotePkgCsv = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages-next', 'csv-next') + 'remotePackagesPre.csv')
                remoteDescCsv = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages-next', 'csv-next') + 'remoteDescriptionsPre.csv')
            else:
                remotePkgCsv = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages', 'csv') + 'remotePackagesPre.csv')
                remoteDescCsv = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages', 'csv') + 'remoteDescriptionsPre.csv')
    return remotePkgCsv,remoteDescCsv

@animation.wait('resolving dependencies')
def getPackageDeps(pkgList):
    areBinaries = []
    areSources = []
    needsConfig = int()
    portageExec = subprocess.Popen(['emerge', '--quiet', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgList, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stderr, encoding="utf-8"):
        if "The following keyword changes are necessary to proceed:" in portageOutput.rstrip():
            needsConfig = int(1)

        if "The following mask changes are necessary to proceed:" in portageOutput.rstrip():
            needsConfig = int(1)

        if "The following USE changes are necessary to proceed:" in portageOutput.rstrip():
            needsConfig = int(1)

        if "The following REQUIRED_USE flag constraints are unsatisfied:" in portageOutput.rstrip():
            needsConfig = int(1)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "binary" in portageOutput.rstrip():
            isBinary = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            areBinaries.append(isBinary)

        if "ebuild" in portageOutput.rstrip():
            isSource = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            areSources.append(isSource)
    return areBinaries,areSources,needsConfig

@animation.wait('resolving dependencies')
def getWorldDeps():
    areBinaries = []
    areSources = []
    needsConfig = int()
    portageExec = subprocess.Popen(['emerge', '--quiet', '--update', '--deep', '--newuse', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for portageOutput in io.TextIOWrapper(portageExec.stderr, encoding="utf-8"):
        if "The following keyword changes are necessary to proceed:" in portageOutput.rstrip():
            needsConfig = int(1)

        if "The following mask changes are necessary to proceed:" in portageOutput.rstrip():
            needsConfig = int(1)

        if "The following USE changes are necessary to proceed:" in portageOutput.rstrip():
            needsConfig = int(1)

        if "The following REQUIRED_USE flag constraints are unsatisfied:" in portageOutput.rstrip():
            needsConfig = int(1)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "binary" in portageOutput.rstrip():
            isBinary = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            areBinaries.append(isBinary)

        if "ebuild" in portageOutput.rstrip():
            isSource = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            areSources.append(isSource)
    return areBinaries,areSources,needsConfig

def fetchRemoteDatabase():
    remotePkgCsv,remoteDescCsv = getCsvUrl()
    http = urllib3.PoolManager()

    with http.request('GET', remotePkgCsv, preload_content=False) as tmp_buffer, open(remotePkgsDB, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)

    with http.request('GET', remoteDescCsv, preload_content=False) as tmp_buffer, open(remoteDscsDB, 'wb') as output_file:
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
    os.chdir(gentooEbuildDir)
    subprocess.call(['git', 'pull', '--quiet'])

    os.chdir(redcoreEbuildDir)
    subprocess.call(['git', 'pull', '--quiet'])

def syncPortageCfg():
    os.chdir(portageConfigDir)
    subprocess.call(['git', 'pull', '--quiet'])

@animation.wait('syncing remote database')
def syncAll():
    checkRoot()

    remotePkgCsv,remoteDescCsv = getCsvUrl()
    http = urllib3.PoolManager()

    reqRemotePkgsTS = http.request('HEAD', remotePkgCsv)
    remotePkgsTS = int(parser.parse(reqRemotePkgsTS.headers['last-modified']).strftime("%s"))
    localPkgsTS = int(os.path.getctime(remotePkgsDB))

    reqRemoteDscsTS = http.request('HEAD', remoteDescCsv)
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
    subprocess.check_call(['emerge', '--search', '--getbinpkgonly'] + pkgList)

def startHybridSearch(pkgList):
    subprocess.check_call(['emerge', '--search', '--getbinpkg'] + pkgList)

def startUpdate():
    syncAll()

def startInstall(pkgList):
    syncAll()

    binhostURL = getBinhostURL()
    areBinaries,areSources,needsConfig = getPackageDeps(pkgList)
    binaryPkgs = []

    if len(areSources) == 0:
        if not len(areBinaries) == 0:
            os.chdir(portageCacheDir)
            print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n"  + str(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
            if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                for index, url in enumerate([binhostURL + package + '.tbz2' for package in areBinaries]):
                    print(">>> Fetching" + " " + url)
                    wget.download(url)
                    print("\n")

                for index, binpkg in enumerate(areBinaries):
                    binaryPkg = str(binpkg.rstrip().split("/")[1])
                    binaryPkgs.append(binaryPkg)

                for index, binpkg in enumerate(binaryPkgs):
                    subprocess.call(['qtbz2', '-x'] + str(binpkg + '.tbz2').split())
                    CATEGORY = subprocess.check_output(['qxpak', '-x', '-O'] + str(binpkg + '.xpak').split() + ['CATEGORY'])
                    os.remove(str(binpkg + '.xpak'))

                    if os.path.isdir(os.path.join(portageCacheDir, CATEGORY.decode().strip())):
                        shutil.move(str(binpkg + '.tbz2'), os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(str(binpkg + '.tbz2'))))
                    else:
                        os.makedirs(os.path.join(portageCacheDir, CATEGORY.decode().strip()))
                        shutil.move(str(binpkg + '.tbz2'), os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(str(binpkg + '.tbz2'))))

                    if os.path.exists(str(binpkg + '.tbz2')):
                        os.remove(str(binpkg + '.tbz2'))

                portageExec = subprocess.Popen(['emerge', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgList, stdout=subprocess.PIPE)

                for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
                    if not "These are the packages that would be merged, in order:" in portageOutput.rstrip():
                        if not "Calculating dependencies" in portageOutput.rstrip():
                            print(portageOutput.rstrip())

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
    areBinaries,areSources,needsConfig = getPackageDeps(pkgList)
    binaryPkgs = []

    if needsConfig == 0:
        if len(areSources) == 0:
            if not len(areBinaries) == 0:
                os.chdir(portageCacheDir)
                print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n"  + str(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
                if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                    for index, url in enumerate([binhostURL + package + '.tbz2' for package in areBinaries]):
                        print(">>> Fetching" + " " + url)
                        wget.download(url)
                        print("\n")

                    for index, binpkg in enumerate(areBinaries):
                        binaryPkg = str(binpkg.rstrip().split("/")[1])
                        binaryPkgs.append(binaryPkg)

                    for index, binpkg in enumerate(binaryPkgs):
                        subprocess.call(['qtbz2', '-x'] + str(binpkg + '.tbz2').split())
                        CATEGORY = subprocess.check_output(['qxpak', '-x', '-O'] + str(binpkg + '.xpak').split() + ['CATEGORY'])
                        os.remove(str(binpkg + '.xpak'))

                        if os.path.isdir(os.path.join(portageCacheDir, CATEGORY.decode().strip())):
                            shutil.move(str(binpkg + '.tbz2'), os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(str(binpkg + '.tbz2'))))
                        else:
                            os.makedirs(os.path.join(portageCacheDir, CATEGORY.decode().strip()))
                            shutil.move(str(binpkg + '.tbz2'), os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(str(binpkg + '.tbz2'))))

                        if os.path.exists(str(binpkg + '.tbz2')):
                            os.remove(str(binpkg + '.tbz2'))

                    portageExec = subprocess.Popen(['emerge', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgList, stdout=subprocess.PIPE)

                    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
                        if not "These are the packages that would be merged, in order:" in portageOutput.rstrip():
                            if not "Calculating dependencies" in portageOutput.rstrip():
                                print(portageOutput.rstrip())

                    portageExec.wait()
                    syncLocalDatabase()
                else:
                    sys.exit("\n" + "Ok; Quitting." + "\n")
            else:
                sys.exit("\n" + "No package found; Quitting." + "\n")
        else:
            if not len(areBinaries) == 0:
                os.chdir(portageCacheDir)
                print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n" + str(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
                print("\n" + "These are the source packages that would be merged, in order:" + "\n\n"  + str(areSources) + "\n\n" + "Total:" + " " + str(len(areSources)) + " " + "source package(s)" + "\n")
                if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                    for index, url in enumerate([binhostURL + package + '.tbz2' for package in areBinaries]):
                        print(">>> Fetching" + " " + url)
                        wget.download(url)
                        print("\n")

                    for index, binpkg in enumerate(areBinaries):
                        binaryPkg = str(binpkg.rstrip().split("/")[1])
                        binaryPkgs.append(binaryPkg)

                    for index, binpkg in enumerate(binaryPkgs):
                        subprocess.call(['qtbz2', '-x'] + str(binpkg + '.tbz2').split())
                        CATEGORY = subprocess.check_output(['qxpak', '-x', '-O'] + str(binpkg + '.xpak').split() + ['CATEGORY'])
                        os.remove(str(binpkg + '.xpak'))

                        if os.path.isdir(os.path.join(portageCacheDir, CATEGORY.decode().strip())):
                            shutil.move(str(binpkg + '.tbz2'), os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(str(binpkg + '.tbz2'))))
                        else:
                            os.makedirs(os.path.join(portageCacheDir, CATEGORY.decode().strip()))
                            shutil.move(str(binpkg + '.tbz2'), os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(str(binpkg + '.tbz2'))))

                        if os.path.exists(str(binpkg + '.tbz2')):
                            os.remove(str(binpkg + '.tbz2'))

                    portageExec = subprocess.Popen(['emerge', '--usepkg', '--rebuilt-binaries', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgList, stdout=subprocess.PIPE)

                    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
                        if not "These are the packages that would be merged, in order:" in portageOutput.rstrip():
                            if not "Calculating dependencies" in portageOutput.rstrip():
                                print(portageOutput.rstrip())

                    portageExec.wait()
                    syncLocalDatabase()
                else:
                    sys.exit("\n" + "Ok; Quitting." + "\n")
            else:
                print("\n" + "These are the source packages that would be merged, in order:" + "\n\n"  + str(areSources) + "\n\n" + "Total:" + " " + str(len(areSources)) + " " + "source package(s)" + "\n")
                if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                    portageExec = subprocess.Popen(['emerge', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgList, stdout=subprocess.PIPE)

                    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
                        if not "These are the packages that would be merged, in order:" in portageOutput.rstrip():
                            if not "Calculating dependencies" in portageOutput.rstrip():
                                print(portageOutput.rstrip())

                    portageExec.wait()
                    syncLocalDatabase()
                else:
                    sys.exit("\n" + "Ok; Quitting." + "\n")
    else:
        portageExec = subprocess.Popen(['emerge', '--quiet', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgList, stdout=subprocess.PIPE)

        for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
            if not "Local copy of remote index is up-to-date and will be used." in portageOutput.rstrip():
                if not "ebuild" in portageOutput.rstrip():
                    if not "binary" in portageOutput.rstrip():
                        print(portageOutput.rstrip())

        portageExec.wait()
        sys.exit("\n" + "Cannot proceed; Apply the above changes to your portage configuration files and try again; Quitting." + "\n")

def startUpgrade():
    syncAll()

    binhostURL = getBinhostURL()
    areBinaries,areSources,needsConfig = getWorldDeps()
    binaryPkgs = []

    if len(areSources) == 0:
        if not len(areBinaries) == 0:
            os.chdir(portageCacheDir)
            print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n"  + str(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
            if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                for index, url in enumerate([binhostURL + package + '.tbz2' for package in areBinaries]):
                    print(">>> Fetching" + " " + url)
                    wget.download(url)
                    print("\n")

                for index, binpkg in enumerate(areBinaries):
                    binaryPkg = str(binpkg.rstrip().split("/")[1])
                    binaryPkgs.append(binaryPkg)

                for index, binpkg in enumerate(binaryPkgs):
                    subprocess.call(['qtbz2', '-x'] + str(binpkg + '.tbz2').split())
                    CATEGORY = subprocess.check_output(['qxpak', '-x', '-O'] + str(binpkg + '.xpak').split() + ['CATEGORY'])
                    os.remove(str(binpkg + '.xpak'))

                    if os.path.isdir(os.path.join(portageCacheDir, CATEGORY.decode().strip())):
                        shutil.move(str(binpkg + '.tbz2'), os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(str(binpkg + '.tbz2'))))
                    else:
                        os.makedirs(os.path.join(portageCacheDir, CATEGORY.decode().strip()))
                        shutil.move(str(binpkg + '.tbz2'), os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(str(binpkg + '.tbz2'))))

                    if os.path.exists(str(binpkg + '.tbz2')):
                        os.remove(str(binpkg + '.tbz2'))

                portageExec = subprocess.Popen(['emerge', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE)

                for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
                    if not "These are the packages that would be merged, in order:" in portageOutput.rstrip():
                        if not "Calculating dependencies" in portageOutput.rstrip():
                            print(portageOutput.rstrip())

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
    areBinaries,areSources,needsConfig = getWorldDeps()
    binaryPkgs = []

    if needsConfig == 0:
        if len(areSources) == 0:
            if not len(areBinaries) == 0:
                os.chdir(portageCacheDir)
                print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n"  + str(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
                if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                    for index, url in enumerate([binhostURL + package + '.tbz2' for package in areBinaries]):
                        print(">>> Fetching" + " " + url)
                        wget.download(url)
                        print("\n")

                    for index, binpkg in enumerate(areBinaries):
                        binaryPkg = str(binpkg.rstrip().split("/")[1])
                        binaryPkgs.append(binaryPkg)

                    for index, binpkg in enumerate(binaryPkgs):
                        subprocess.call(['qtbz2', '-x'] + str(binpkg + '.tbz2').split())
                        CATEGORY = subprocess.check_output(['qxpak', '-x', '-O'] + str(binpkg + '.xpak').split() + ['CATEGORY'])
                        os.remove(str(binpkg + '.xpak'))

                        if os.path.isdir(os.path.join(portageCacheDir, CATEGORY.decode().strip())):
                            shutil.move(str(binpkg + '.tbz2'), os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(str(binpkg + '.tbz2'))))
                        else:
                            os.makedirs(os.path.join(portageCacheDir, CATEGORY.decode().strip()))
                            shutil.move(str(binpkg + '.tbz2'), os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(str(binpkg + '.tbz2'))))

                        if os.path.exists(str(binpkg + '.tbz2')):
                            os.remove(str(binpkg + '.tbz2'))

                    portageExec = subprocess.Popen(['emerge', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE)

                    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
                        if not "These are the packages that would be merged, in order:" in portageOutput.rstrip():
                            if not "Calculating dependencies" in portageOutput.rstrip():
                                print(portageOutput.rstrip())

                    portageExec.wait()
                    syncLocalDatabase()
                else:
                    sys.exit("\n" + "Ok; Quitting." + "\n")
            else:
                sys.exit("\n" + "No package upgrades found; Quitting." + "\n")
        else:
            if not len(areBinaries) == 0:
                os.chdir(portageCacheDir)
                print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n" + str(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
                print("\n" + "These are the source packages that would be merged, in order:" + "\n\n"  + str(areSources) + "\n\n" + "Total:" + " " + str(len(areSources)) + " " + "source package(s)" + "\n")
                if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                    for index, url in enumerate([binhostURL + package + '.tbz2' for package in areBinaries]):
                        print(">>> Fetching" + " " + url)
                        wget.download(url)
                        print("\n")

                    for index, binpkg in enumerate(areBinaries):
                        binaryPkg = str(binpkg.rstrip().split("/")[1])
                        binaryPkgs.append(binaryPkg)

                    for index, binpkg in enumerate(binaryPkgs):
                        subprocess.call(['qtbz2', '-x'] + str(binpkg + '.tbz2').split())
                        CATEGORY = subprocess.check_output(['qxpak', '-x', '-O'] + str(binpkg + '.xpak').split() + ['CATEGORY'])
                        os.remove(str(binpkg + '.xpak'))

                        if os.path.isdir(os.path.join(portageCacheDir, CATEGORY.decode().strip())):
                            shutil.move(str(binpkg + '.tbz2'), os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(str(binpkg + '.tbz2'))))
                        else:
                            os.makedirs(os.path.join(portageCacheDir, CATEGORY.decode().strip()))
                            shutil.move(str(binpkg + '.tbz2'), os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(str(binpkg + '.tbz2'))))

                        if os.path.exists(str(binpkg + '.tbz2')):
                            os.remove(str(binpkg + '.tbz2'))

                    portageExec = subprocess.Popen(['emerge', '--update', '--deep', '--newuse', '--usepkg', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE)

                    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
                        if not "These are the packages that would be merged, in order:" in portageOutput.rstrip():
                            if not "Calculating dependencies" in portageOutput.rstrip():
                                print(portageOutput.rstrip())

                    portageExec.wait()
                    syncLocalDatabase()
                else:
                    sys.exit("\n" + "Ok; Quitting." + "\n")
            else:
                print("\n" + "These are the source packages that would be merged, in order:" + "\n\n"  + str(areSources) + "\n\n" + "Total:" + " " + str(len(areSources)) + " " + "source package(s)" + "\n")
                if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                    portageExec = subprocess.Popen(['emerge', '--update', '--deep', '--newuse', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE)

                    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
                        if not "These are the packages that would be merged, in order:" in portageOutput.rstrip():
                            if not "Calculating dependencies" in portageOutput.rstrip():
                                print(portageOutput.rstrip())

                    portageExec.wait()
                    syncLocalDatabase()
                else:
                    sys.exit("\n" + "Ok; Quitting." + "\n")
    else:
        portageExec = subprocess.Popen(['emerge', '--quiet', '--update', '--deep', '--newuse', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE)

        for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
            if not "Local copy of remote index is up-to-date and will be used." in portageOutput.rstrip():
                if not "ebuild" in portageOutput.rstrip():
                    if not "binary" in portageOutput.rstrip():
                        print(portageOutput.rstrip())

        portageExec.wait()
        sys.exit("\n" + "Cannot proceed; Apply the above changes to your portage configuration files and try again; Quitting." + "\n")

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
        mirrorFile.write("#######################################################\n")
        mirrorFile.write("#       Please avoid using the Main Repository        #\n")
        mirrorFile.write("#    http://mirrors.redcorelinux.org/redcorelinux     #\n")
        mirrorFile.write("#  as the bandwidth is limited, use mirrors instead   #\n")
        mirrorFile.write("#######################################################\n")
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
        print("\n" + "Mirror index is wrong, please check with sisyphus --mirror --list" + "\n")
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
    print("* Search for binary packages" + "\n")
    print("--hybrid-search")
    print("* Search for binary and/or ebuild (source) packages" + "\n")
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
