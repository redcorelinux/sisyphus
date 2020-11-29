#!/usr/bin/python3

import os
import shutil
import subprocess
import sys
import io
import wget
import sisyphus.binhost
import sisyphus.check
import sisyphus.database
import sisyphus.filesystem
import sisyphus.solvedeps
import sisyphus.update

def start(pkgname):
    if sisyphus.check.root():
        sisyphus.update.start()

        binhostURL = sisyphus.binhost.getURL()
        areBinaries,areSources,needsConfig = sisyphus.solvedeps.package(pkgname)

        if needsConfig == 0:
            if len(areSources) == 0:
                if not len(areBinaries) == 0:
                    os.chdir(sisyphus.filesystem.portageCacheDir)
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

                            if os.path.isdir(os.path.join(sisyphus.filesystem.portageCacheDir, CATEGORY.decode().strip())):
                                shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(sisyphus.filesystem.portageCacheDir, CATEGORY.decode().strip()), os.path.basename(binary.rstrip().split("/")[1])))
                            else:
                                os.makedirs(os.path.join(sisyphus.filesystem.portageCacheDir, CATEGORY.decode().strip()))
                                shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(sisyphus.filesystem.portageCacheDir, CATEGORY.decode().strip()), os.path.basename(binary.rstrip().split("/")[1])))

                            if os.path.exists(binary.rstrip().split("/")[1]):
                                os.remove(binary.rstrip().split("/")[1])

                        portageExec = subprocess.Popen(['emerge', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname), stdout=subprocess.PIPE)

                        for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
                            if not "These are the packages that would be merged, in order:" in portageOutput.rstrip():
                                if not "Calculating dependencies" in portageOutput.rstrip():
                                    print(portageOutput.rstrip())

                        portageExec.wait()
                        sisyphus.database.syncLocal()
                    else:
                        sys.exit("\n" + "Ok; Quitting." + "\n")
                else:
                    sys.exit("\n" + "No package found; Quitting." + "\n")
            else:
                sys.exit("\n" + "Source package(s) found in the mix;" + " " + "Use" + " " + "'" + "sisyphus install" + " " + ''.join(pkgname) + " " + "--ebuild" + "'" + ";" + " " + "Quitting." + "\n")
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")