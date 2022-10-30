#!/usr/bin/python3

import atexit
import io
import os
import shutil
import subprocess
import sys
import wget
import sisyphus.checkenv
import sisyphus.getenv
import sisyphus.getfs
import sisyphus.killemerge
import sisyphus.solvedeps
import sisyphus.syncdb
import sisyphus.update

def start(pkgname):
    if sisyphus.checkenv.root():
        sisyphus.update.start()

        binhostURL = sisyphus.getenv.binhostURL()
        areBinaries,areSources,needsConfig = sisyphus.solvedeps.package(pkgname)

        if needsConfig == 0:
            if len(areSources) == 0:
                if not len(areBinaries) == 0:
                    os.chdir(sisyphus.getfs.portageCacheDir)
                    print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n"  + "  ".join(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
                    if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                        for index, binary in enumerate([package + '.tbz2' for package in areBinaries], start=1):
                            print(">>> Downloading binary ({}".format(index) + " " + "of" + " " + str(len(areBinaries)) + ")" + " " + binary)
                            wget.download(binhostURL + binary)
                            print("\n")

                            if os.path.isdir(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0])):
                                shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0]), os.path.basename(binary.rstrip().split("/")[1])))
                            else:
                                os.makedirs(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0]))
                                shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0]), os.path.basename(binary.rstrip().split("/")[1])))

                            if os.path.exists(binary.rstrip().split("/")[1]):
                                os.remove(binary.rstrip().split("/")[1])

                        portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname))
                        portageExec.wait()
                        sisyphus.syncdb.localTable()
                    else:
                        sys.exit("\n" + "Ok; Quitting." + "\n")
                else:
                    sys.exit("\n" + "No package found; Quitting." + "\n")
            else:
                sys.exit("\n" + "Source package(s) found in the mix;" + " " + "Use" + " " + "'" + "sisyphus install" + " " + " ".join(pkgname) + " " + "--ebuild" + "'" + ";" + " " + "Quitting." + "\n")
        else:
            # don't silently fail if a source package requested without the --ebuild option needs a keyword, mask, REQUIRED_USE or USE change
            sys.exit("\n" + "Invalid request;" " " + "Use" + " " + "'" + "sisyphus install" + " " + " ".join(pkgname) + " " + "--ebuild" + "'" + ";" + " " + "Quitting." + "\n")
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

def estart(pkgname):
    if sisyphus.checkenv.root():
        sisyphus.update.start()

        binhostURL = sisyphus.getenv.binhostURL()
        areBinaries,areSources,needsConfig = sisyphus.solvedeps.package(pkgname)

        if needsConfig == 0:
            if len(areSources) == 0:
                if not len(areBinaries) == 0:
                    os.chdir(sisyphus.getfs.portageCacheDir)
                    print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n"  + "  ".join(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
                    if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                        for index, binary in enumerate([package + '.tbz2' for package in areBinaries], start=1):
                            print(">>> Downloading binary ({}".format(index) + " " + "of" + " " + str(len(areBinaries)) + ")" + " " + binary)
                            wget.download(binhostURL + binary)
                            print("\n")

                            if os.path.isdir(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0])):
                                shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0]), os.path.basename(binary.rstrip().split("/")[1])))
                            else:
                                os.makedirs(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0]))
                                shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0]), os.path.basename(binary.rstrip().split("/")[1])))

                            if os.path.exists(binary.rstrip().split("/")[1]):
                                os.remove(binary.rstrip().split("/")[1])

                        portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname))
                        portageExec.wait()
                        sisyphus.syncdb.localTable()
                    else:
                        sys.exit("\n" + "Ok; Quitting." + "\n")
                else:
                    sys.exit("\n" + "No package found; Quitting." + "\n")
            else:
                if not len(areBinaries) == 0:
                    os.chdir(sisyphus.getfs.portageCacheDir)
                    print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n" + "  ".join(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
                    print("\n" + "These are the source packages that would be merged, in order:" + "\n\n"  + "  ".join(areSources) + "\n\n" + "Total:" + " " + str(len(areSources)) + " " + "source package(s)" + "\n")
                    if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                        for index, binary in enumerate([package + '.tbz2' for package in areBinaries], start=1):
                            print(">>> Downloading binary ({}".format(index) + " " + "of" + " " + str(len(areBinaries)) + ")" + " " + binary)
                            wget.download(binhostURL + binary)
                            print("\n")

                            if os.path.isdir(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0])):
                                shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0]), os.path.basename(binary.rstrip().split("/")[1])))
                            else:
                                os.makedirs(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0]))
                                shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0]), os.path.basename(binary.rstrip().split("/")[1])))

                            if os.path.exists(binary.rstrip().split("/")[1]):
                                os.remove(binary.rstrip().split("/")[1])

                        portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--usepkg', '--rebuilt-binaries', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname))
                        portageExec.wait()
                        sisyphus.syncdb.localTable()
                    else:
                        sys.exit("\n" + "Ok; Quitting." + "\n")
                else:
                    print("\n" + "These are the source packages that would be merged, in order:" + "\n\n"  + "  ".join(areSources) + "\n\n" + "Total:" + " " + str(len(areSources)) + " " + "source package(s)" + "\n")
                    if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                        portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname))
                        portageExec.wait()
                        sisyphus.syncdb.localTable()
                    else:
                        sys.exit("\n" + "Ok; Quitting." + "\n")
        else:
            portageExec = subprocess.Popen(['emerge', '--quiet', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname))
            portageExec.wait()
            sys.exit("\n" + "Cannot proceed; Apply the above changes to your portage configuration files and try again; Quitting." + "\n")
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

def startx(pkgname):
    binhostURL = sisyphus.getenv.binhostURL()
    areBinaries,areSources,needsConfig = sisyphus.solvedeps.package.__wrapped__(pkgname) #undecorate

    os.chdir(sisyphus.getfs.portageCacheDir)
    print("\n" + "These are the binary packages that will be merged, in order:" + "\n\n" + "  ".join(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n\n")
    for index, binary in enumerate([package + '.tbz2' for package in areBinaries], start=1):
        print(">>> Downloading binary ({}".format(index) + " " + "of" + " " + str(len(areBinaries)) + ")" + " " + binary)
        wget.download(binhostURL + binary)
        print("\n")

        if os.path.isdir(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0])):
            shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0]), os.path.basename(binary.rstrip().split("/")[1])))
        else:
            os.makedirs(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0]))
            shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(sisyphus.getfs.portageCacheDir, binary.rstrip().split("/")[0]), os.path.basename(binary.rstrip().split("/")[1])))

        if os.path.exists(binary.rstrip().split("/")[1]):
            os.remove(binary.rstrip().split("/")[1])

    portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgname, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # kill portage if the program dies or it's terminated by the user
    atexit.register(sisyphus.killemerge.start, portageExec)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        print(portageOutput.rstrip())

    portageExec.wait()
    sisyphus.syncdb.localTable()
