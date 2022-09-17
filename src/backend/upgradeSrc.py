#!/usr/bin/python3

import os
import shutil
import subprocess
import sys
import wget
import sisyphus.checkEnvironment
import sisyphus.getBinhost
import sisyphus.getFilesystem
import sisyphus.resolveDeps
import sisyphus.syncDatabase
import sisyphus.updateAll

def start():
    if sisyphus.checkEnvironment.root():
        sisyphus.updateAll.start()

        binhostURL = sisyphus.getBinhost.start()
        areBinaries,areSources,needsConfig = sisyphus.resolveDeps.world()

        if needsConfig == 0:
            if len(areSources) == 0:
                if not len(areBinaries) == 0:
                    os.chdir(sisyphus.getFilesystem.portageCacheDir)
                    print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n"  + "  ".join(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
                    if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                        for index, binary in enumerate([package + '.tbz2' for package in areBinaries], start=1):
                            print(">>> Downloading binary ({}".format(index) + " " + "of" + " " + str(len(areBinaries)) + ")" + " " + binary)
                            wget.download(binhostURL + binary)
                            print("\n")

                            if os.path.isdir(os.path.join(sisyphus.getFilesystem.portageCacheDir, binary.rstrip().split("/")[0])):
                                shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(sisyphus.getFilesystem.portageCacheDir, binary.rstrip().split("/")[0]), os.path.basename(binary.rstrip().split("/")[1])))
                            else:
                                os.makedirs(os.path.join(sisyphus.getFilesystem.portageCacheDir, binary.rstrip().split("/")[0]))
                                shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(sisyphus.getFilesystem.portageCacheDir, binary.rstrip().split("/")[0]), os.path.basename(binary.rstrip().split("/")[1])))

                            if os.path.exists(binary.rstrip().split("/")[1]):
                                os.remove(binary.rstrip().split("/")[1])

                        portageExec = subprocess.Popen(['emerge', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = portageExec.communicate()

                        for portageOutput in stdout.decode('ascii').splitlines():
                            if not "These are the packages that would be merged, in order:" in portageOutput:
                                if not "Calculating dependencies" in portageOutput:
                                    print(portageOutput)

                        sisyphus.syncDatabase.syncLocal()
                    else:
                        sys.exit("\n" + "Ok; Quitting." + "\n")
                else:
                    sys.exit("\n" + "No package upgrades found; Quitting." + "\n")
            else:
                if not len(areBinaries) == 0:
                    os.chdir(sisyphus.getFilesystem.portageCacheDir)
                    print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n" + "  ".join(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
                    print("\n" + "These are the source packages that would be merged, in order:" + "\n\n"  + "  ".join(areSources) + "\n\n" + "Total:" + " " + str(len(areSources)) + " " + "source package(s)" + "\n")
                    if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                        for index, binary in enumerate([package + '.tbz2' for package in areBinaries], start=1):
                            print(">>> Downloading binary ({}".format(index) + " " + "of" + " " + str(len(areBinaries)) + ")" + " " + binary)
                            wget.download(binhostURL + binary)
                            print("\n")

                            if os.path.isdir(os.path.join(sisyphus.getFilesystem.portageCacheDir, binary.rstrip().split("/")[0])):
                                shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(sisyphus.getFilesystem.portageCacheDir, binary.rstrip().split("/")[0]), os.path.basename(binary.rstrip().split("/")[1])))
                            else:
                                os.makedirs(os.path.join(sisyphus.getFilesystem.portageCacheDir, binary.rstrip().split("/")[0]))
                                shutil.move(binary.rstrip().split("/")[1], os.path.join(os.path.join(sisyphus.getFilesystem.portageCacheDir, binary.rstrip().split("/")[0]), os.path.basename(binary.rstrip().split("/")[1])))

                            if os.path.exists(binary.rstrip().split("/")[1]):
                                os.remove(binary.rstrip().split("/")[1])

                        portageExec = subprocess.Popen(['emerge', '--update', '--deep', '--newuse', '--usepkg', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = portageExec.communicate()

                        for portageOutput in stdout.decode('ascii').splitlines():
                            if not "These are the packages that would be merged, in order:" in portageOutput:
                                if not "Calculating dependencies" in portageOutput:
                                    print(portageOutput)

                        sisyphus.syncDatabase.syncLocal()
                    else:
                        sys.exit("\n" + "Ok; Quitting." + "\n")
                else:
                    print("\n" + "These are the source packages that would be merged, in order:" + "\n\n"  + "  ".join(areSources) + "\n\n" + "Total:" + " " + str(len(areSources)) + " " + "source package(s)" + "\n")
                    if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                        portageExec = subprocess.Popen(['emerge', '--update', '--deep', '--newuse', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = portageExec.communicate()

                        for portageOutput in stdout.decode('ascii').splitlines():
                            if not "These are the packages that would be merged, in order:" in portageOutput:
                                if not "Calculating dependencies" in portageOutput:
                                    print(portageOutput)

                        sisyphus.syncDatabase.syncLocal()
                    else:
                        sys.exit("\n" + "Ok; Quitting." + "\n")
        else:
            portageExec = subprocess.Popen(['emerge', '--quiet', '--update', '--deep', '--newuse', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = portageExec.communicate()

            for portageOutput in stdout.decode('ascii').splitlines():
                if not "Local copy of remote index is up-to-date and will be used." in portageOutput:
                    if not "ebuild" in portageOutput:
                        if not "binary" in portageOutput:
                            print(portageOutput)

            sys.exit("\n" + "Cannot proceed; Apply the above changes to your portage configuration files and try again; Quitting." + "\n")
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")
