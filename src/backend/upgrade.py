#!/usr/bin/python3

import atexit
import io
import os
import pickle
import subprocess
import sys
import sisyphus.checkenv
import sisyphus.download
import sisyphus.getfs
import sisyphus.killemerge
import sisyphus.solvedeps
import sisyphus.syncdb
import sisyphus.update


def start():
    if sisyphus.checkenv.root():
        sisyphus.update.start()
        sisyphus.solvedeps.world()
        areBinaries,areSources,needsConfig = pickle.load(open(os.path.join(sisyphus.getfs.portageMetadataDir, "sisyphus_solvedeps_world.pickle"), "rb"))

        if needsConfig == 0:
            if len(areSources) == 0:
                if not len(areBinaries) == 0:
                    os.chdir(sisyphus.getfs.portageCacheDir)
                    print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n"  + "  ".join(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
                    if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                        sisyphus.download.world()
                        portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                        portageExec.wait()
                        sisyphus.syncdb.localTable()
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


def estart():
    if sisyphus.checkenv.root():
        sisyphus.update.start()
        sisyphus.solvedeps.world()
        areBinaries,areSources,needsConfig = pickle.load(open(os.path.join(sisyphus.getfs.portageMetadataDir, "sisyphus_solvedeps_world.pickle"), "rb"))

        if needsConfig == 0:
            if len(areSources) == 0:
                if not len(areBinaries) == 0:
                    os.chdir(sisyphus.getfs.portageCacheDir)
                    print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n"  + "  ".join(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
                    if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                        sisyphus.download.world()
                        portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                        portageExec.wait()
                        sisyphus.syncdb.localTable()
                    else:
                        sys.exit("\n" + "Ok; Quitting." + "\n")
                else:
                    sys.exit("\n" + "No package upgrades found; Quitting." + "\n")
            else:
                if not len(areBinaries) == 0:
                    os.chdir(sisyphus.getfs.portageCacheDir)
                    print("\n" + "These are the binary packages that would be merged, in order:" + "\n\n" + "  ".join(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n")
                    print("\n" + "These are the source packages that would be merged, in order:" + "\n\n"  + "  ".join(areSources) + "\n\n" + "Total:" + " " + str(len(areSources)) + " " + "source package(s)" + "\n")
                    if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                        sisyphus.download.world()
                        portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                        portageExec.wait()
                        sisyphus.syncdb.localTable()
                    else:
                        sys.exit("\n" + "Ok; Quitting." + "\n")
                else:
                    print("\n" + "These are the source packages that would be merged, in order:" + "\n\n"  + "  ".join(areSources) + "\n\n" + "Total:" + " " + str(len(areSources)) + " " + "source package(s)" + "\n")
                    if input("Would you like to proceed?" + " " + "[y/N]" + " ").lower().strip()[:1] == "y":
                        portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        portageExec.wait()
                        sisyphus.syncdb.localTable()
                    else:
                        sys.exit("\n" + "Ok; Quitting." + "\n")
        else:
            portageExec = subprocess.Popen(['emerge', '--quiet', '--update', '--deep', '--newuse', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
            portageExec.wait()
            sys.exit("\n" + "Cannot proceed; Apply the above changes to your portage configuration files and try again; Quitting." + "\n")
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")


def xstart():
    sisyphus.solvedeps.world.__wrapped__() #undecorate
    areBinaries,areSources,needsConfig = pickle.load(open(os.path.join(sisyphus.getfs.portageMetadataDir, "sisyphus_solvedeps_world.pickle"), "rb"))

    if not len(areSources) == 0:
        print("\n" + "Source package(s) found in the mix;" + " " + "Use sisyphus CLI:" +  " " + "'" + "sisyphus upgrade --ebuild" + "'" + " " + "to perform the upgrade;" + " " + "Aborting." + "\n")
    else:
        if not len(areBinaries) == 0:
            os.chdir(sisyphus.getfs.portageCacheDir)
            print("\n" + "These are the binary packages that will be merged, in order:" + "\n\n" + "  ".join(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n\n")
            sisyphus.download.world()
            portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # kill portage if the program dies or it's terminated by the user
            atexit.register(sisyphus.killemerge.start, portageExec)

            for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
                print(portageOutput.rstrip())

            portageExec.wait()
            sisyphus.syncdb.localTable()
        else:
            print("\n" + "No package upgrades found; Quitting." + "\n")
