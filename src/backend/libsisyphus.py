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

gentooEbuildDir = '/usr/ports/gentoo'
redcoreEbuildDir = '/usr/ports/redcore'
portageConfigDir = '/opt/redcore-build'
portageCacheDir = '/var/cache/packages'
portageMetadataDir = '/var/cache/edb'
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

    portageExec.wait()
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

    portageExec.wait()
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
        if "[binary" in portageOutput.rstrip():
            isBinary = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            areBinaries.append(isBinary)

        if "[ebuild" in portageOutput.rstrip():
            isSource = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            areSources.append(isSource)

    portageExec.wait()
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
        if "[binary" in portageOutput.rstrip():
            isBinary = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            areBinaries.append(isBinary)

        if "[ebuild" in portageOutput.rstrip():
            isSource = str(portageOutput.rstrip().split("]")[1].split("[")[0].strip("\ "))
            areSources.append(isSource)

    portageExec.wait()
    return areBinaries,areSources,needsConfig

def fetchRemoteDatabase():
    remotePkgCsv,remoteDescCsv = getCsvUrl()
    http = urllib3.PoolManager()

    with http.request('GET', remotePkgCsv, preload_content=False) as tmp_buffer, open(remotePkgsDB, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)

    with http.request('GET', remoteDescCsv, preload_content=False) as tmp_buffer, open(remoteDscsDB, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)

def makeLocalDatabase():
    subprocess.call(['/usr/share/sisyphus/helpers/make_local_csv'])

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

def checkPortageTree():
    os.chdir(gentooEbuildDir)
    needsPortageTreeSync = int()

    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    localHash = subprocess.check_output(['git', 'rev-parse', '@'])
    remoteHash = subprocess.check_output(['git', 'rev-parse', '@{u}'])

    gitExec = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE)

    if not localHash.decode().strip() == remoteHash.decode().strip():
        needsPortageTreeSync = int(1)

    gitExec.wait()
    return needsPortageTreeSync

def checkOverlayTree():
    os.chdir(redcoreEbuildDir)
    needsOverlayTreeSync = int()

    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    localHash = subprocess.check_output(['git', 'rev-parse', '@'])
    remoteHash = subprocess.check_output(['git', 'rev-parse', '@{u}'])

    gitExec = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE)

    if not localHash.decode().strip() == remoteHash.decode().strip():
        needsOverlayTreeSync = int(1)

    gitExec.wait()
    return needsOverlayTreeSync

def syncPortageTree():
    os.chdir(gentooEbuildDir)
    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    remoteBranch = subprocess.check_output(['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    gitExecStage1 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE)
    gitExecStage1.wait()
    gitExecStage2 = subprocess.Popen(['git', 'reset', '--hard'] + remoteBranch.decode().strip().replace('refs/remotes/','').split() + ['--quiet'], stdout=subprocess.PIPE)
    gitExecStage2.wait()

def syncOverlayTree():
    os.chdir(redcoreEbuildDir)
    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    remoteBranch = subprocess.check_output(['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    gitExecStage1 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE)
    gitExecStage1.wait()
    gitExecStage2 = subprocess.Popen(['git', 'reset', '--hard'] + remoteBranch.decode().strip().replace('refs/remotes/','').split() + ['--quiet'], stdout=subprocess.PIPE)
    gitExecStage2.wait()

def syncPortageConfig():
    os.chdir(portageConfigDir)
    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    remoteBranch = subprocess.check_output(['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    gitExecStage1 = subprocess.Popen(['git', 'stash'], stdout=subprocess.PIPE)
    gitExecStage1.wait()
    gitExecStage2 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE)
    gitExecStage2.wait()
    gitExecStage3 = subprocess.Popen(['git', 'reset', '--hard'] + remoteBranch.decode().strip().replace('refs/remotes/','').split() + ['--quiet'], stdout=subprocess.PIPE)
    gitExecStage3.wait()
    gitExecStage4 = subprocess.Popen(['git', 'stash', 'apply'], stdout=subprocess.PIPE)
    gitExecStage4.wait()
    gitExecStage5 = subprocess.Popen(['git', 'stash', 'clear'], stdout=subprocess.PIPE)
    gitExecStage5.wait()
    gitExecStage6 = subprocess.Popen(['git', 'gc', '--prune=now', '--quiet'], stdout=subprocess.PIPE)
    gitExecStage6.wait()

@animation.wait('refreshing metadata')
def refreshPortageMetadata():
    if os.path.isdir(portageMetadataDir):
        for files in os.listdir(portageMetadataDir):
            if os.path.isfile(os.path.join(portageMetadataDir, files)):
                os.remove(os.path.join(portageMetadataDir, files))
            else:
                shutil.rmtree(os.path.join(portageMetadataDir, files))

    portageExecStage1 = subprocess.Popen(['emerge', '--quiet', '--regen'], stdout=subprocess.PIPE)
    portageExecStage1.wait()
    portageExecStage2 = subprocess.Popen(['emerge', '--quiet', '--metadata'], stdout=subprocess.PIPE)
    portageExecStage2.wait()

def cleanCacheDir():
    if os.path.isdir(portageCacheDir):
        for files in os.listdir(portageCacheDir):
            if os.path.isfile(os.path.join(portageCacheDir, files)):
                os.remove(os.path.join(portageCacheDir, files))
            else:
                shutil.rmtree(os.path.join(portageCacheDir, files))

def checkUpdate():
    checkPortageTree()
    checkOverlayTree()

@animation.wait('fetching updates')
def startUpdate():
    checkRoot()
    cleanCacheDir()

    needsPortageTreeSync = checkPortageTree()
    needsOverlayTreeSync = checkOverlayTree()

    if needsPortageTreeSync == 1:
        if needsOverlayTreeSync == 1:
            syncPortageTree()
            syncOverlayTree()
            syncPortageConfig()
            syncRemoteDatabase()
            refreshPortageMetadata()
        elif not needsOverlayTreeSync == 1:
            syncPortageTree()
            syncOverlayTree()
            syncPortageConfig()
            syncRemoteDatabase()
            refreshPortageMetadata()
    elif not needsPortageTreeSync == 1:
        if needsOverlayTreeSync == 1:
            syncPortageTree()
            syncOverlayTree()
            syncPortageConfig()
            syncRemoteDatabase()
            refreshPortageMetadata()
        elif not needsOverlayTreeSync == 1:
            syncPortageConfig()

@animation.wait('syncing spm changes')
def startSyncSPM():
    syncLocalDatabase()

@animation.wait('recovering databases')
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
    subprocess.call(['emerge', '--search', '--getbinpkg'] + pkgList)

def startInstall(pkgList):
    startUpdate()

    binhostURL = getBinhostURL()
    areBinaries,areSources,needsConfig = getPackageDeps(pkgList)

    if needsConfig == 0:
        if len(areSources) == 0:
            if not len(areBinaries) == 0:
                os.chdir(portageCacheDir)
                print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n"  + str(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
                if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                    for index, binary in enumerate([package + '.tbz2' for package in areBinaries]):
                        print(">>> Fetching" + " " + binhostURL + binary)
                        wget.download(binhostURL + binary)
                        print("\n")

                        subprocess.call(['qtbz2', '-x'] + binary.rstrip().split("/")[1].split())
                        CATEGORY = subprocess.check_output(['qxpak', '-x', '-O'] + binary.rstrip().split("/")[1].replace('tbz2', 'xpak').split() + ['CATEGORY'])

                        if os.path.exists(binary.rstrip().split("/")[1].replace('tbz2', 'xpak')):
                            os.remove(binary.rstrip().split("/")[1].replace('tbz2', 'xpak'))

                        if os.path.isdir(os.path.join(portageCacheDir, CATEGORY.decode().strip())):
                            shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(binary.rstrip().split("/")[1])))
                        else:
                            os.makedirs(os.path.join(portageCacheDir, CATEGORY.decode().strip()))
                            shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(binary.rstrip().split("/")[1])))

                        if os.path.exists(binary.rstrip().split("/")[1]):
                            os.remove(binary.rstrip().split("/")[1])

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
                    for index, binary in enumerate([package + '.tbz2' for package in areBinaries]):
                        print(">>> Fetching" + " " + binhostURL + binary)
                        wget.download(binhostURL + binary)
                        print("\n")

                        subprocess.call(['qtbz2', '-x'] + binary.rstrip().split("/")[1].split())
                        CATEGORY = subprocess.check_output(['qxpak', '-x', '-O'] + binary.rstrip().split("/")[1].replace('tbz2', 'xpak').split() + ['CATEGORY'])

                        if os.path.exists(binary.rstrip().split("/")[1].replace('tbz2', 'xpak')):
                            os.remove(binary.rstrip().split("/")[1].replace('tbz2', 'xpak'))

                        if os.path.isdir(os.path.join(portageCacheDir, CATEGORY.decode().strip())):
                            shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(binary.rstrip().split("/")[1])))
                        else:
                            os.makedirs(os.path.join(portageCacheDir, CATEGORY.decode().strip()))
                            shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(binary.rstrip().split("/")[1])))

                        if os.path.exists(binary.rstrip().split("/")[1]):
                            os.remove(binary.rstrip().split("/")[1])

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
    startUpdate()

    binhostURL = getBinhostURL()
    areBinaries,areSources,needsConfig = getWorldDeps()

    if needsConfig == 0:
        if len(areSources) == 0:
            if not len(areBinaries) == 0:
                os.chdir(portageCacheDir)
                print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n"  + str(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
                if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                    for index, binary in enumerate([package + '.tbz2' for package in areBinaries]):
                        print(">>> Fetching" + " " + binhostURL + binary)
                        wget.download(binhostURL + binary)
                        print("\n")

                        subprocess.call(['qtbz2', '-x'] + binary.rstrip().split("/")[1].split())
                        CATEGORY = subprocess.check_output(['qxpak', '-x', '-O'] + binary.rstrip().split("/")[1].replace('tbz2', 'xpak').split() + ['CATEGORY'])

                        if os.path.exists(binary.rstrip().split("/")[1].replace('tbz2', 'xpak')):
                            os.remove(binary.rstrip().split("/")[1].replace('tbz2', 'xpak'))

                        if os.path.isdir(os.path.join(portageCacheDir, CATEGORY.decode().strip())):
                            shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(binary.rstrip().split("/")[1])))
                        else:
                            os.makedirs(os.path.join(portageCacheDir, CATEGORY.decode().strip()))
                            shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(binary.rstrip().split("/")[1])))

                        if os.path.exists(binary.rstrip().split("/")[1]):
                            os.remove(binary.rstrip().split("/")[1])

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
                    for index, binary in enumerate([package + '.tbz2' for package in areBinaries]):
                        print(">>> Fetching" + " " + binhostURL + binary)
                        wget.download(binhostURL + binary)
                        print("\n")

                        subprocess.call(['qtbz2', '-x'] + binary.rstrip().split("/")[1].split())
                        CATEGORY = subprocess.check_output(['qxpak', '-x', '-O'] + binary.rstrip().split("/")[1].replace('tbz2', 'xpak').split() + ['CATEGORY'])

                        if os.path.exists(binary.rstrip().split("/")[1].replace('tbz2', 'xpak')):
                            os.remove(binary.rstrip().split("/")[1].replace('tbz2', 'xpak'))

                        if os.path.isdir(os.path.join(portageCacheDir, CATEGORY.decode().strip())):
                            shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(binary.rstrip().split("/")[1])))
                        else:
                            os.makedirs(os.path.join(portageCacheDir, CATEGORY.decode().strip()))
                            shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(portageCacheDir, CATEGORY.decode().strip()), os.path.basename(binary.rstrip().split("/")[1])))

                        if os.path.exists(binary.rstrip().split("/")[1]):
                            os.remove(binary.rstrip().split("/")[1])

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
    subprocess.call(['emerge', '--info'])

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

@animation.wait('resetting branch configuration')
def resetBranch():
    if os.path.isdir(gentooEbuildDir):
        for files in os.listdir(gentooEbuildDir):
            if os.path.isfile(os.path.join(gentooEbuildDir, files)):
                os.remove(os.path.join(gentooEbuildDir, files))
            else:
                shutil.rmtree(os.path.join(gentooEbuildDir, files))
    else:
        os.makedirs(gentooEbuildDir)

    if os.path.isdir(redcoreEbuildDir):
        for files in os.listdir(redcoreEbuildDir):
            if os.path.isfile(os.path.join(redcoreEbuildDir, files)):
                os.remove(os.path.join(redcoreEbuildDir, files))
            else:
                shutil.rmtree(os.path.join(redcoreEbuildDir, files))
    else:
        os.makedirs(redcoreEbuildDir)

    if os.path.isdir(portageConfigDir):
        for files in os.listdir(portageConfigDir):
            if os.path.isfile(os.path.join(portageConfigDir, files)):
                os.remove(os.path.join(portageConfigDir, files))
            else:
                shutil.rmtree(os.path.join(portageConfigDir, files))
    else:
        os.makedirs(portageConfigDir)

@animation.wait('injecting gentoo linux portage tree - branch master')
def setGitlabMasterStage1():
    if not os.path.isdir(os.path.join(gentooEbuildDir, '.git')):
        os.chdir(gentooEbuildDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://gitlab.com/redcore/portage.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'master', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'master', 'origin/master', '--quiet'])

@animation.wait('injecting redcore linux ebuild tree - branch master')
def setGitlabMasterStage2():
    if not os.path.isdir(os.path.join(redcoreEbuildDir, '.git')):
        os.chdir(redcoreEbuildDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://gitlab.com/redcore/redcore-desktop.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'master', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'master', 'origin/master', '--quiet'])

@animation.wait('injecting redcore linux portage configuration - branch master')
def setGitlabMasterStage3():
    if not os.path.isdir(os.path.join(portageConfigDir, '.git')):
        os.chdir(portageConfigDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://gitlab.com/redcore/redcore-build.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'master', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'master', 'origin/master', '--quiet'])

def setGitlabMaster():
    setGitlabMasterStage1()
    setGitlabMasterStage2()
    setGitlabMasterStage3()

@animation.wait('injecting gentoo linux portage tree - branch master')
def setPagureMasterStage1():
    if not os.path.isdir(os.path.join(gentooEbuildDir, '.git')):
        os.chdir(gentooEbuildDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://pagure.io/redcore/portage.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'master', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'master', 'origin/master', '--quiet'])

@animation.wait('injecting redcore linux ebuild tree - branch master')
def setPagureMasterStage2():
    if not os.path.isdir(os.path.join(redcoreEbuildDir, '.git')):
        os.chdir(redcoreEbuildDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://pagure.io/redcore/redcore-desktop.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'master', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'master', 'origin/master', '--quiet'])

@animation.wait('injecting redcore linux portage configuration - branch master')
def setPagureMasterStage3():
    if not os.path.isdir(os.path.join(portageConfigDir, '.git')):
        os.chdir(portageConfigDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://pagure.io/redcore/redcore-build.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'master', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'master', 'origin/master', '--quiet'])

def setPagureMaster():
    setPagureMasterStage1()
    setPagureMasterStage2()
    setPagureMasterStage3()

@animation.wait('injecting gentoo linux portage tree - branch next')
def setGitlabNextStage1():
    if not os.path.isdir(os.path.join(gentooEbuildDir, '.git')):
        os.chdir(gentooEbuildDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://gitlab.com/redcore/portage.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'next', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'next', 'origin/next', '--quiet'])

@animation.wait('injecting redcore linux ebuild tree - branch next')
def setGitlabNextStage2():
    if not os.path.isdir(os.path.join(redcoreEbuildDir, '.git')):
        os.chdir(redcoreEbuildDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://gitlab.com/redcore/redcore-desktop.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'next', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'next', 'origin/next', '--quiet'])

@animation.wait('injecting redcore linux portage configuration - branch next')
def setGitlabNextStage3():
    if not os.path.isdir(os.path.join(portageConfigDir, '.git')):
        os.chdir(portageConfigDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://gitlab.com/redcore/redcore-build.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'next', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'next', 'origin/next', '--quiet'])

def setGitlabNext():
    setGitlabNextStage1()
    setGitlabNextStage2()
    setGitlabNextStage3()

@animation.wait('injecting gentoo linux portage tree - branch next')
def setPagureNextStage1():
    if not os.path.isdir(os.path.join(gentooEbuildDir, '.git')):
        os.chdir(gentooEbuildDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://pagure.io/redcore/portage.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'next', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'next', 'origin/next', '--quiet'])

@animation.wait('injecting redcore linux ebuild tree - branch next')
def setPagureNextStage2():
    if not os.path.isdir(os.path.join(redcoreEbuildDir, '.git')):
        os.chdir(redcoreEbuildDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://pagure.io/redcore/redcore-desktop.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'next', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'next', 'origin/next', '--quiet'])

@animation.wait('injecting redcore linux portage configuration - branch next')
def setPagureNextStage3():
    if not os.path.isdir(os.path.join(portageConfigDir, '.git')):
        os.chdir(portageConfigDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://pagure.io/redcore/redcore-build.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'next', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'next', 'origin/next', '--quiet'])

def setPagureNext():
    setPagureNextStage1()
    setPagureNextStage2()
    setPagureNextStage3()

@animation.wait('setting up hardened profile')
def setHardenedProfile():
    subprocess.call(['eselect', 'profile', 'set', 'default/linux/amd64/17.0/hardened'])
    subprocess.call(['env-update'])

@animation.wait('adjusting MAKEOPTS')
def setJobs():
    subprocess.call(['/usr/share/sisyphus/helpers/set_jobs'])

def injectGitlabMaster():
    checkRoot()
    resetBranch()
    setGitlabMaster()
    setHardenedProfile()
    setJobs()
    refreshPortageMetadata()

def injectPagureMaster():
    checkRoot()
    resetBranch()
    setPagureMaster()
    setHardenedProfile()
    setJobs()
    refreshPortageMetadata()

def injectGitlabNext():
    checkRoot()
    resetBranch()
    setGitlabNext()
    setHardenedProfile()
    setJobs()
    refreshPortageMetadata()

def injectPagureNext():
    checkRoot()
    resetBranch()
    setPagureNext()
    setHardenedProfile()
    setJobs()
    refreshPortageMetadata()

def showHelp():
    print("\n" + "Usage : sisyphus command [package(s)] || [file(s)]" + "\n")
    print("Sisyphus is a simple python wrapper around portage, gentoolkit, and portage-utils which provides")
    print("an apt-get/yum-alike interface to these commands, to assist newcomer people transitioning from")
    print("Debian/RedHat-based systems to Gentoo." + "\n")
    print("Commands :" + "\n")
    print("--install")
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
    print("* Update the Portage tree, the Redcore Overlay(s), Portage configs && Sisyphus's package database" + "\n")
    print("--upgrade")
    print("* Upgrade the system using binary and/or ebuild (source) packages" + "\n")
    print("--search")
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
    print("--mirror --set 'INDEX'")
    print("* Change the binary package repository to the selected mirror" + "\n")
    print("--branch='BRANCH' --remote='REMOTE'")
    print("* Pull the branch 'BRANCH' of the Portage tree, Redcore overlay && Portage configs. Use 'REMOTE' git repositories.")
    print("* 'BRANCH' can be one of the following : master, next")
    print("* 'REMOTE' can be one of the following : gitlab, pagure")
    print("*")
    print("* Examples: ")
    print("* '--branch=master --remote=gitlab' will pull the branch 'master' from gitlab.com")
    print("* '--branch=next --remote=pagure' will pull the branch 'next' from pagure.io")
    print("*")
    print("* !!! WARNING !!!")
    print("* Once you changed the branch, you must pair the branch 'BRANCH' with the correct binary repository")
    print("* Branch 'master' must be paired with the stable binary repository (odd numbers in 'sisyphus --mirror --list'). Examples : 'sisyphus --mirror --set 1' or 'sisyphus --mirror --set 5' ")
    print("* Branch 'next' must be paired with the testing binary repository (even numbers in 'sisyphus --mirror --list'). Examples : 'sisyphus --mirror --set 2' or 'sisyphus --mirror --set 8'" + "\n")
    print("--sysinfo")
    print("* Display information about installed core packages and portage configuration" + "\n")
    print("--help")
    print("* Display this help information" + "\n")
