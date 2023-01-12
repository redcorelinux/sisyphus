#!/usr/bin/python3

import atexit
import io
import os
import pickle
import subprocess
import sys
import sisyphus.checkenv
import sisyphus.getcolor
import sisyphus.getfs
import sisyphus.killemerge
import sisyphus.solvedeps
import sisyphus.syncdb
import sisyphus.update


def start(pkgname):
    if sisyphus.checkenv.root():
        sisyphus.update.start()
        sisyphus.solvedeps.pkg(pkgname)
        areBinaries, areSources, needsConfig = pickle.load(open(os.path.join(
            sisyphus.getfs.portageMetadataDir, "sisyphus_pkgdeps.pickle"), "rb"))

        if needsConfig == 0:
            if len(areSources) == 0:
                if not len(areBinaries) == 0:
                    os.chdir(sisyphus.getfs.portageCacheDir)
                    print("\n" + sisyphus.getcolor.green + "These are the binary packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.magenta + ", ".join(
                        areBinaries) + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + sisyphus.getcolor.reset + "\n")
                    while True:
                        user_input = input(sisyphus.getcolor.bright_white + "Would you like to proceed?" + sisyphus.getcolor.reset + " " +
                                           "[" + sisyphus.getcolor.bright_green + "Yes" + sisyphus.getcolor.reset + "/" + sisyphus.getcolor.bright_red + "No" + sisyphus.getcolor.reset + "]" + " ")
                        if user_input.lower() in ['yes', 'y', '']:
                            portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--getbinpkg', '--getbinpkgonly', '--fetchonly',
                                                           '--rebuilt-binaries', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname))
                            portageExec.wait()
                            portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--usepkg', '--usepkgonly',
                                                           '--rebuilt-binaries', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname))
                            portageExec.wait()
                            sisyphus.syncdb.localTable()
                            break
                        elif user_input.lower() in ['no', 'n']:
                            print(sisyphus.getcolor.bright_green +
                                  "\nOk!\n" + sisyphus.getcolor.reset)
                            break
                            sys.exit()
                        else:
                            print("\nSorry, response" + " " + "'" +
                                  user_input + "'" + " " + "not understood.\n")
                            continue
                else:
                    print(sisyphus.getcolor.bright_red +
                          "\nNo package found!\n" + sisyphus.getcolor.reset)
                    sys.exit()
            else:
                print(sisyphus.getcolor.bright_red +
                      "\nSource package(s) found in the mix!\n" + sisyphus.getcolor.reset)
                print(sisyphus.getcolor.bright_yellow + "Use" + sisyphus.getcolor.reset + " " +
                      "'" + "sisyphus install" + " " + " ".join(pkgname) + " " + "--ebuild" + "'")
                sys.exit()
        else:
            # don't silently fail if a source package requested without the --ebuild option needs a keyword, mask, REQUIRED_USE or USE change
            print(sisyphus.getcolor.bright_red +
                  "\nInvalid request!\n" + sisyphus.getcolor.reset)
            print(sisyphus.getcolor.bright_yellow + "Use" + sisyphus.getcolor.reset + " " +
                  "'" + "sisyphus install" + " " + " ".join(pkgname) + " " + "--ebuild" + "'")
            sys.exit()
    else:
        print(sisyphus.getcolor.bright_red +
              "\nYou need root permissions to do this!\n" + sisyphus.getcolor.reset)
        sys.exit()


def estart(pkgname):
    if sisyphus.checkenv.root():
        sisyphus.update.start()
        sisyphus.solvedeps.pkg(pkgname)
        areBinaries, areSources, needsConfig = pickle.load(open(os.path.join(
            sisyphus.getfs.portageMetadataDir, "sisyphus_pkgdeps.pickle"), "rb"))

        if needsConfig == 0:
            if len(areSources) == 0:
                if not len(areBinaries) == 0:
                    os.chdir(sisyphus.getfs.portageCacheDir)
                    print("\n" + sisyphus.getcolor.green + "These are the binary packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.magenta + ", ".join(
                        areBinaries) + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + sisyphus.getcolor.reset + "\n")
                    while True:
                        user_input = input(sisyphus.getcolor.bright_white + "Would you like to proceed?" + sisyphus.getcolor.reset + " " +
                                           "[" + sisyphus.getcolor.bright_green + "Yes" + sisyphus.getcolor.reset + "/" + sisyphus.getcolor.bright_red + "No" + sisyphus.getcolor.reset + "]" + " ")
                        if user_input.lower() in ['yes', 'y', '']:
                            portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--getbinpkg', '--getbinpkgonly', '--fetchonly',
                                                           '--rebuilt-binaries', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname))
                            portageExec.wait()
                            portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--usepkg', '--usepkgonly',
                                                            '--rebuilt-binaries', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname))
                            portageExec.wait()
                            sisyphus.syncdb.localTable()
                            break
                        elif user_input.lower() in ['no', 'n']:
                            print(sisyphus.getcolor.bright_green +
                                  "\nOk!\n" + sisyphus.getcolor.reset)
                            break
                            sys.exit()
                        else:
                            print("\nSorry, response" + " " + "'" +
                                  user_input + "'" + " " + "not understood.\n")
                            continue
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
                    while True:
                        user_input = input(sisyphus.getcolor.bright_white + "Would you like to proceed?" + sisyphus.getcolor.reset + " " +
                                           "[" + sisyphus.getcolor.bright_green + "Yes" + sisyphus.getcolor.reset + "/" + sisyphus.getcolor.bright_red + "No" + sisyphus.getcolor.reset + "]" + " ")
                        if user_input.lower() in ['yes', 'y', '']:
                            portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--getbinpkg', '--fetchonly',
                                                           '--rebuilt-binaries', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname))
                            portageExec.wait()
                            portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--usepkg', '--rebuilt-binaries',
                                                           '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname))
                            portageExec.wait()
                            sisyphus.syncdb.localTable()
                            break
                        elif user_input.lower() in ['no', 'n']:
                            print(sisyphus.getcolor.bright_green +
                                  "\nOk!\n" + sisyphus.getcolor.reset)
                            break
                            sys.exit()
                        else:
                            print("\nSorry, response" + " " + "'" +
                                  user_input + "'" + " " + "not understood.\n")
                            continue
                else:
                    print("\n" + sisyphus.getcolor.green + "These are the source packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.magenta + ", ".join(
                        areSources) + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(len(areSources)) + " " + "source package(s)" + sisyphus.getcolor.reset + "\n")
                    while True:
                        user_input = input(sisyphus.getcolor.bright_white + "Would you like to proceed?" + sisyphus.getcolor.reset + " " +
                                           "[" + sisyphus.getcolor.bright_green + "Yes" + sisyphus.getcolor.reset + "/" + sisyphus.getcolor.bright_red + "No" + sisyphus.getcolor.reset + "]" + " ")
                        if user_input.lower() in ['yes', 'y', '']:
                            portageExec = subprocess.Popen(
                                ['emerge', '--quiet', '--verbose', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname))
                            portageExec.wait()
                            sisyphus.syncdb.localTable()
                            break
                        elif user_input.lower() in ['no', 'n']:
                            print(sisyphus.getcolor.bright_green +
                                  "\nOk!\n" + sisyphus.getcolor.reset)
                            break
                            sys.exit()
                        else:
                            print("\nSorry, response" + " " + "'" +
                                  user_input + "'" + " " + "not understood!\n")
                            continue
        else:
            portageExec = subprocess.Popen(['emerge', '--quiet', '--pretend', '--getbinpkg', '--rebuilt-binaries',
                                           '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname))
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


def xstart(pkgname):
    sisyphus.solvedeps.pkg.__wrapped__(pkgname)  # undecorate
    areBinaries, areSources, needsConfig = pickle.load(open(os.path.join(
        sisyphus.getfs.portageMetadataDir, "sisyphus_pkgdeps.pickle"), "rb"))

    os.chdir(sisyphus.getfs.portageCacheDir)
    print("\n" + "These are the binary packages that will be merged, in order:" + "\n\n" + ", ".join(
        areBinaries) + "\n\n" + "Total:" + " " + str(len(areBinaries)) + " " + "binary package(s)" + "\n\n")
    portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--getbinpkg', '--getbinpkgonly', '--fetchonly',
                                   '--rebuilt-binaries', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgname, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # kill portage if the program dies or it's terminated by the user
    atexit.register(sisyphus.killemerge.start, portageExec)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        print(portageOutput.rstrip())

    portageExec.wait()
    portageExec = subprocess.Popen(['emerge', '--quiet', '--verbose', '--usepkg', '--usepkgonly', '--rebuilt-binaries',
                                   '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgname, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # kill portage if the program dies or it's terminated by the user
    atexit.register(sisyphus.killemerge.start, portageExec)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        print(portageOutput.rstrip())

    portageExec.wait()
    sisyphus.syncdb.localTable()
