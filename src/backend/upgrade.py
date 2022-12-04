#!/usr/bin/python3

import atexit
import io
import os
import pickle
import subprocess
import sys
import sisyphus.checkenv
import sisyphus.download
import sisyphus.getcolor
import sisyphus.getfs
import sisyphus.killemerge
import sisyphus.solvedeps
import sisyphus.syncdb
import sisyphus.update


def start():
    if sisyphus.checkenv.root():
        sisyphus.update.start()
        sisyphus.solvedeps.world()
        areBinaries, areSources, needsConfig = pickle.load(open(os.path.join(
            sisyphus.getfs.portageMetadataDir, "sisyphus_worlddeps.pickle"), "rb"))

        if needsConfig == 0:
            if len(areSources) == 0:
                if not len(areBinaries) == 0:
                    os.chdir(sisyphus.getfs.portageCacheDir)
                    print("\n" + sisyphus.getcolor.green + "These are the binary packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.magenta + ", ".join(
                        areBinaries) + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + sisyphus.getcolor.reset + "\n")
                    if input(sisyphus.getcolor.bright_white + "Would you like to proceed?" + sisyphus.getcolor.reset + " " + "[" + sisyphus.getcolor.bright_green + "y" + sisyphus.getcolor.reset + "/" + sisyphus.getcolor.bright_red + "N" + sisyphus.getcolor.reset + "]" + " ").lower().strip()[:1] == "y":
                        sisyphus.download.world()
                        portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly',
                                                       '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                        portageExec.wait()
                        sisyphus.syncdb.localTable()
                    else:
                        print(sisyphus.getcolor.bright_green +
                              "\nOk!\n" + sisyphus.getcolor.reset)
                        sys.exit()
                else:
                    print(sisyphus.getcolor.bright_red +
                          "\nNo package found!\n" + sisyphus.getcolor.reset)
                    sys.exit()
            else:
                print(sisyphus.getcolor.bright_red +
                      "\nSource package(s) found in the mix!\n" + sisyphus.getcolor.reset)
                print(sisyphus.getcolor.bright_yellow + "Use" + sisyphus.getcolor.reset + " " + "'" +
                      "sisyphus install" + " " + " ".join(pkgname) + " " + "--ebuild" + "'" + sisyphus.getcolor.reset)
                sys.exit()
        else:
            # don't silently fail if a source package requested without the --ebuild option needs a keyword, mask, REQUIRED_USE or USE change
            print(sisyphus.getcolor.bright_red +
                  "\nInvalid request!\n" + sisyphus.getcolor.reset)
            print(sisyphus.getcolor.bright_yellow + "Use" + sisyphus.getcolor.reset + " " + "'" +
                  "sisyphus install" + " " + " ".join(pkgname) + " " + "--ebuild" + "'" + sisyphus.getcolor.reset)
            sys.exit()
    else:
        print(sisyphus.getcolor.bright_red +
              "\nYou need root permissions to do this!\n" + sisyphus.getcolor.reset)
        sys.exit()


def estart():
    if sisyphus.checkenv.root():
        sisyphus.update.start()
        sisyphus.solvedeps.world()
        areBinaries, areSources, needsConfig = pickle.load(open(os.path.join(
            sisyphus.getfs.portageMetadataDir, "sisyphus_worlddeps.pickle"), "rb"))

        if needsConfig == 0:
            if len(areSources) == 0:
                if not len(areBinaries) == 0:
                    os.chdir(sisyphus.getfs.portageCacheDir)
                    print("\n" + sisyphus.getcolor.green + "These are the binary packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.magenta + ", ".join(
                        areBinaries) + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + sisyphus.getcolor.reset + "\n")
                    if input(sisyphus.getcolor.bright_white + "Would you like to proceed?" + sisyphus.getcolor.reset + " " + "[" + sisyphus.getcolor.bright_green + "y" + sisyphus.getcolor.reset + "/" + sisyphus.getcolor.bright_red + "N" + sisyphus.getcolor.reset + "]" + " ").lower().strip()[:1] == "y":
                        sisyphus.download.world()
                        portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly',
                                                       '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                        portageExec.wait()
                        sisyphus.syncdb.localTable()
                    else:
                        print(sisyphus.getcolor.bright_green +
                              "\nOk!\n" + sisyphus.getcolor.reset)
                        sys.exit()
                else:
                    print(sisyphus.getcolor.bright_red +
                          "\nNo package found!\n" + sisyphus.getcolor.reset)
                    sys.exit()
            else:
                if not len(areBinaries) == 0:
                    os.chdir(sisyphus.getfs.portageCacheDir)
                    print("\n" + sisyphus.getcolor.green + "These are the binary packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.magenta + ", ".join(
                        areBinaries) + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + sisyphus.getcolor.reset + "\n")
                    print("\n" + sisyphus.getcolor.green + "These are the source packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.magenta + ", ".join(
                        areSources) + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(len(areSources)) + " " + "source package(s)" + sisyphus.getcolor.reset + "\n")
                    if input(sisyphus.getcolor.bright_white + "Would you like to proceed?" + sisyphus.getcolor.reset + " " + "[" + sisyphus.getcolor.bright_green + "y" + sisyphus.getcolor.reset + "/" + sisyphus.getcolor.bright_red + "N" + sisyphus.getcolor.reset + "]" + " ").lower().strip()[:1] == "y":
                        sisyphus.download.world()
                        portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg',
                                                       '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                        portageExec.wait()
                        sisyphus.syncdb.localTable()
                    else:
                        print(sisyphus.getcolor.bright_green +
                              "\nOk!\n" + sisyphus.getcolor.reset)
                        sys.exit()
                else:
                    print("\n" + sisyphus.getcolor.green + "These are the source packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.magenta + ", ".join(
                        areSources) + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(len(areSources)) + " " + "source package(s)" + sisyphus.getcolor.reset + "\n")
                    if input(sisyphus.getcolor.bright_white + "Would you like to proceed?" + sisyphus.getcolor.reset + " " + "[" + sisyphus.getcolor.bright_green + "y" + sisyphus.getcolor.reset + "/" + sisyphus.getcolor.bright_red + "N" + sisyphus.getcolor.reset + "]" + " ").lower().strip()[:1] == "y":
                        portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--backtrack=100',
                                                       '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        portageExec.wait()
                        sisyphus.syncdb.localTable()
                    else:
                        print(sisyphus.getcolor.bright_green +
                              "\nOk!\n" + sisyphus.getcolor.reset)
                        sys.exit()
        else:
            portageExec = subprocess.Popen(['emerge', '--quiet', '--update', '--deep', '--newuse', '--pretend', '--getbinpkg',
                                           '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
            portageExec.wait()
            print(sisyphus.getcolor.bright_red +
                  "\nCannot proceed!\n" + sisyphus.getcolor.reset)
            print(sisyphus.getcolor.bright_yellow +
                  "Apply the above changes to your portage configuration files and try again" + sisyphus.getcolor.reset)
            sys.exit()
    else:
        print(sisyphus.getcolor.bright_red +
              "\nYou need root permissions to do this!\n" + sisyphus.getcolor.reset)
        sys.exit()


def xstart():
    sisyphus.solvedeps.world.__wrapped__()  # undecorate
    areBinaries, areSources, needsConfig = pickle.load(open(os.path.join(
        sisyphus.getfs.portageMetadataDir, "sisyphus_worlddeps.pickle"), "rb"))

    if not len(areSources) == 0:
        print("\n" + "Source package(s) found in the mix;" + " " + "Use sisyphus CLI:" +  " " + "'" + "sisyphus upgrade --ebuild" + "'" + " " + "to perform the upgrade;" + " " + "Aborting." + "\n")
    else:
        if not len(areBinaries) == 0:
            os.chdir(sisyphus.getfs.portageCacheDir)
            print("\n" + "These are the binary packages that will be merged, in order:" + "\n\n" + ", ".join(areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n\n")
            sisyphus.download.world()
            portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly', '--rebuilt-binaries',
                                           '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # kill portage if the program dies or it's terminated by the user
            atexit.register(sisyphus.killemerge.start, portageExec)

            for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
                print(portageOutput.rstrip())

            portageExec.wait()
            sisyphus.syncdb.localTable()
        else:
            print("\nNo package upgrades found!\n")
