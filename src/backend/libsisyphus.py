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

from dateutil import parser

redcore_portage_config_path = '/opt/redcore-build'

rmtPkgCsv = '/var/lib/sisyphus/csv/remotePackagesPre.csv'
rmtDscCsv = '/var/lib/sisyphus/csv/remoteDescriptionsPre.csv'
lclPkgCsv = '/var/lib/sisyphus/csv/localPackagesPre.csv'
sisyphusDB = '/var/lib/sisyphus/db/sisyphus.db'
mirrorCfg = '/etc/sisyphus/mirrors.conf'

def checkRoot():
    if not os.getuid() == 0:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

def checkSystemMode():
    portage_binmode_make_conf = '/opt/redcore-build/conf/intel/portage/make.conf.amd64-binmode'
    portage_mixedmode_make_conf = '/opt/redcore-build/conf/intel/portage/make.conf.amd64-mixedmode'
    portage_make_conf_symlink = '/etc/portage/make.conf'

    if not os.path.islink(portage_make_conf_symlink):
        print("\nmake.conf is not a symlink, refusing to run!\n")
        sys.exit(1)
    else:
        if os.path.realpath(portage_make_conf_symlink) == portage_binmode_make_conf:
            pass
        elif os.path.realpath(portage_make_conf_symlink) == portage_mixedmode_make_conf:
            pass
        else:
            print("\nThe system is not set to binmode or mixedmode, refusing to run!\n")
            sys.exit(1)

def fetchRemoteDatabaseCSV():
    portageExec = subprocess.Popen(['emerge', '--info', '--verbose'], stdout=subprocess.PIPE)
    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "PORTAGE_BINHOST" in portageOutput.rstrip():
            rmtCsvUrl = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages', 'csv') + 'remotePackagesPre.csv')
            rmtDscUrl = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages', 'csv') + 'remoteDescriptionsPre.csv')

    http = urllib3.PoolManager()

    with http.request('GET', rmtCsvUrl, preload_content=False) as tmp_buffer, open(rmtPkgCsv, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)

    with http.request('GET', rmtDscUrl, preload_content=False) as tmp_buffer, open(rmtDscCsv, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)

def syncGitRepos():
    subprocess.check_call(['emerge', '--sync', '--quiet'])

def syncPortageCfg():
    os.chdir(redcore_portage_config_path)
    subprocess.call(['git', 'pull', '--quiet'])

def syncRemoteDatabaseCSV():
    sisyphusdb = sqlite3.connect(sisyphusDB)
    sisyphusdb.cursor().execute('''drop table if exists remote_packages''')
    sisyphusdb.cursor().execute('''create table remote_packages (category TEXT,name TEXT,version TEXT,slot TEXT)''')
    with open(rmtPkgCsv) as rmtCsv:
        for row in csv.reader(rmtCsv):
            sisyphusdb.cursor().execute("insert into remote_packages (category, name, version, slot) values (?, ?, ?, ?);", row)
    sisyphusdb.commit()
    sisyphusdb.close()

    sisyphusdb = sqlite3.connect(sisyphusDB)
    sisyphusdb.cursor().execute('''drop table if exists remote_descriptions''')
    sisyphusdb.cursor().execute('''create table remote_descriptions (category TEXT,name TEXT,description TEXT)''')
    with open(rmtDscCsv) as rmtCsv:
        for row in csv.reader(rmtCsv):
            sisyphusdb.cursor().execute("insert into remote_descriptions (category, name, description) values (?, ?, ?);", row)
    sisyphusdb.commit()
    sisyphusdb.close()
        
def syncRemoteDatabaseTable():
    fetchRemoteDatabaseCSV()
    syncRemoteDatabaseCSV()

@animation.wait('syncing remote database tables')
def syncAll():
    checkRoot()

    portageExec = subprocess.Popen(['emerge', '--info', '--verbose'], stdout=subprocess.PIPE)
    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        if "PORTAGE_BINHOST" in portageOutput.rstrip():
            rmtCsvUrl = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages', 'csv') + 'remotePackagesPre.csv')
            rmtDscUrl = str(portageOutput.rstrip().split("=")[1].strip('\"').replace('packages', 'csv') + 'remoteDescriptionsPre.csv')

    http = urllib3.PoolManager()

    reqRmtPkgTs = http.request('HEAD',rmtCsvUrl)
    rmtPkgTs = int(parser.parse(reqRmtPkgTs.headers['last-modified']).strftime("%s"))
    lclPkgTs = int(os.path.getctime(rmtPkgCsv))

    reqRmtDscTs = http.request('HEAD',rmtDscUrl)
    rmtDscTs = int(parser.parse(reqRmtDscTs.headers['last-modified']).strftime("%s"))
    lclDscTs = int(os.path.getctime(rmtDscCsv))

    if rmtPkgTs > lclPkgTs or rmtDscTs > lclDscTs:
        fetchRemoteDatabaseCSV()
        syncGitRepos()
        syncPortageCfg()
        syncRemoteDatabaseTable()

def makeLocalDatabaseCSV():
    subprocess.check_call(['/usr/share/sisyphus/helpers/make_local_csv']) # this is really hard to do in python, so we cheat with a bash helper script

def syncLocalDatabaseTable():
    sisyphusdb = sqlite3.connect(sisyphusDB)
    sisyphusdb.cursor().execute('''drop table if exists local_packages''')
    sisyphusdb.cursor().execute('''create table local_packages (category TEXT,name TEXT,version TEXT,slot TEXT)''')
    with open(lclPkgCsv) as lclCsv:
        for row in csv.reader(lclCsv):
            sisyphusdb.cursor().execute("insert into local_packages (category, name, version, slot) values (?, ?, ?, ?);", row)
    sisyphusdb.commit()
    sisyphusdb.close()

@animation.wait('syncing local database tables')
def startSyncSPM():
    makeLocalDatabaseCSV()
    syncLocalDatabaseTable()

def startInstall(pkgList):
    syncAll()
    portageExec = subprocess.Popen(['emerge', '-aq'] + pkgList)
    portageExec.communicate()
    makeLocalDatabaseCSV()
    syncLocalDatabaseTable()

def startUninstall(pkgList):
    portageExec = subprocess.Popen(['emerge', '--depclean', '-aq'] + pkgList)
    portageExec.communicate()
    makeLocalDatabaseCSV()
    syncLocalDatabaseTable()

def startUninstallForce(pkgList):
    portageExec = subprocess.Popen(['emerge', '--unmerge', '-aq'] + pkgList)
    portageExec.communicate()
    makeLocalDatabaseCSV()
    syncLocalDatabaseTable()

def removeOrphans():
    portageExec = subprocess.Popen(['emerge', '--depclean', '-aq'])
    portageExec.communicate()
    makeLocalDatabaseCSV()
    syncLocalDatabaseTable()

def startUpgrade():
    syncAll()
    portageExec = subprocess.Popen(['emerge', '-uDaNq', '--backtrack=100', '--with-bdeps=y', '@world'])
    portageExec.communicate()
    makeLocalDatabaseCSV()
    syncLocalDatabaseTable()

def startSearch(pkgList):
    subprocess.check_call(['emerge', '--search'] + pkgList)

def startUpdate():
    syncAll()

@animation.wait('syncing portage tree && portage config files')
def startSync():
    syncGitRepos()
    syncPortageCfg()

def sysInfo():
    subprocess.check_call(['emerge', '--info'])

@animation.wait('resurrecting database tables')
def rescueDB():
    if os.path.exists(rmtPkgCsv):
        os.remove(rmtPkgCsv)
    if os.path.exists(rmtDscCsv):
        os.remove(rmtDscCsv)
    if os.path.exists(lclPkgCsv):
        os.remove(lclPkgCsv)
    if os.path.exists(sisyphusDB):
        os.remove(sisyphusDB)

    fetchRemoteDatabaseCSV()
    syncRemoteDatabaseCSV()

    makeLocalDatabaseCSV()
    syncLocalDatabaseTable()

def portageKill(portageCmd):
        portageCmd.terminate()

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
