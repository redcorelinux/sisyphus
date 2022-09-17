#!/usr/bin/python3

import atexit
import os
import shutil
import subprocess
import sys
import wget
import sisyphus.checkEnvironment
import sisyphus.getBinhost
import sisyphus.getFilesystem
import sisyphus.killPortage
import sisyphus.resolveDeps
import sisyphus.syncDatabase
import sisyphus.updateAll

def start():
    if sisyphus.checkEnvironment.root():
        sisyphus.updateAll.start()

        isBinhost = sisyphus.getBinhost.start()
        areBinaries,areSources,needsConfig = sisyphus.resolveDeps.world()

        if needsConfig == 0:
            if len(areSources) == 0:
                if not len(areBinaries) == 0:
                    os.chdir(sisyphus.getFilesystem.portageCacheDir)
                    print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n"  + "  ".join(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
                    if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                        for index, binary in enumerate([package + '.tbz2' for package in areBinaries], start=1):
                            print(">>> Downloading binary ({}".format(index) + " " + "of" + " " + str(len(areBinaries)) + ")" + " " + binary)
                            wget.download(isBinhost + binary)
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
                sys.exit("\n" + "Source package(s) found in the mix;" + " " + "Use" + " " + "'" + "sisyphus upgrade --ebuild" + "'" + ";" + " " + "Quitting." + "\n")
        else:
            # don't silently fail if a source package requested without the --ebuild option needs a keyword, mask, REQUIRED_USE or USE change
            sys.exit("\n" + "Invalid request;" " " + "Use" + " " + "'" + "sisyphus upgrade --ebuild" + "'" + ";" + " " + "Quitting." + "\n")
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

def startqt():
    isBinhost = sisyphus.getBinhost.start()
    areBinaries,areSources,needsConfig = sisyphus.resolveDeps.world.__wrapped__() #undecorate

    if not len(areSources) == 0:
        print("\n" + "Source package(s) found in the mix;" + " " + "Use sisyphus CLI:" +  " " + "'" + "sisyphus upgrade --ebuild" + "'" + " " + "to perform the upgrade;" + " " + "Aborting." + "\n")
    else:
        if not len(areBinaries) == 0:
            os.chdir(sisyphus.getFilesystem.portageCacheDir)
            print("\n" + "These are the binary packages that will be merged, in order:" + "\n\n" + "  ".join(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n\n")
            for index, binary in enumerate([package + '.tbz2' for package in areBinaries], start=1):
                print(">>> Downloading binary ({}".format(index) + " " + "of" + " " + str(len(areBinaries)) + ")" + " " + binary)
                wget.download(isBinhost + binary)
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
            # kill portage if the program dies or it's terminated by the user
            atexit.register(sisyphus.killPortage.start, portageExec)

            for portageOutput in stdout.decode('ascii').splitlines():
                if not "These are the packages that would be merged, in order:" in portageOutput:
                    if not "Calculating dependencies" in portageOutput:
                        print(portageOutput)

            sisyphus.syncDatabase.syncLocal()
        else:
            print("\n" + "No package upgrades found; Quitting." + "\n")
