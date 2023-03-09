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
        bin_list, src_list, need_cfg = pickle.load(open(os.path.join(
            sisyphus.getfs.portageMetadataDir, "sisyphus_worlddeps.pickle"), "rb"))

        if need_cfg == 0:
            if len(src_list) == 0:
                if not len(bin_list) == 0:
                    os.chdir(sisyphus.getfs.portageCacheDir)
                    print("\n" + sisyphus.getcolor.green + "These are the binary packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.magenta + ", ".join(
                        bin_list) + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(len(bin_list)) + " " + "binary package(s)" + sisyphus.getcolor.reset + "\n")
                    while True:
                        user_input = input(sisyphus.getcolor.bright_white + "Would you like to proceed?" + sisyphus.getcolor.reset + " " +
                                           "[" + sisyphus.getcolor.bright_green + "Yes" + sisyphus.getcolor.reset + "/" + sisyphus.getcolor.bright_red + "No " + sisyphus.getcolor.reset + "]" + " ")
                        if user_input.lower() in ['yes', 'y', '']:
                            sisyphus.download.worldbinpkgonly()
                            p_exe = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly',
                                                      '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                            p_exe.wait()
                            sisyphus.syncdb.lcl_tbl()
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
                          "\nNo package upgrades found!\n" + sisyphus.getcolor.reset)
                    sys.exit()
            else:
                print(sisyphus.getcolor.bright_red +
                      "\nSource package(s) found in the mix!\n" + sisyphus.getcolor.reset)
                print(sisyphus.getcolor.bright_yellow + "Use" +
                      sisyphus.getcolor.reset + " " + "'" + "sisyphus upgrade --ebuild" + "'")
                sys.exit()
        else:
            # don't silently fail if a source package requested without the --ebuild option needs a keyword, mask, REQUIRED_USE or USE change
            print(sisyphus.getcolor.bright_red +
                  "\nInvalid request!\n" + sisyphus.getcolor.reset)
            print(sisyphus.getcolor.bright_yellow + "Use" +
                  sisyphus.getcolor.reset + " " + "'" + "sisyphus upgrade --ebuild" + "'")
            sys.exit()
    else:
        print(sisyphus.getcolor.bright_red +
              "\nYou need root permissions to do this!\n" + sisyphus.getcolor.reset)
        sys.exit()


def estart():
    if sisyphus.checkenv.root():
        sisyphus.update.start()
        sisyphus.solvedeps.world()
        bin_list, src_list, need_cfg = pickle.load(open(os.path.join(
            sisyphus.getfs.portageMetadataDir, "sisyphus_worlddeps.pickle"), "rb"))

        if need_cfg == 0:
            if len(src_list) == 0:
                if not len(bin_list) == 0:
                    os.chdir(sisyphus.getfs.portageCacheDir)
                    print("\n" + sisyphus.getcolor.green + "These are the binary packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.magenta + ", ".join(
                        bin_list) + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(len(bin_list)) + " " + "binary package(s)" + sisyphus.getcolor.reset + "\n")
                    while True:
                        user_input = input(sisyphus.getcolor.bright_white + "Would you like to proceed?" + sisyphus.getcolor.reset + " " +
                                           "[" + sisyphus.getcolor.bright_green + "Yes" + sisyphus.getcolor.reset + "/" + sisyphus.getcolor.bright_red + "No" + sisyphus.getcolor.reset + "]" + " ")
                        if user_input.lower() in ['yes', 'y', '']:
                            sisyphus.download.worldbinpkgonly()
                            p_exe = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly',
                                                      '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                            p_exe.wait()
                            sisyphus.syncdb.lcl_tbl()
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
                          "\nNo package upgrades found!\n" + sisyphus.getcolor.reset)
                    sys.exit()
            else:
                if not len(bin_list) == 0:
                    os.chdir(sisyphus.getfs.portageCacheDir)
                    print("\n" + sisyphus.getcolor.green + "These are the binary packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.magenta + ", ".join(
                        bin_list) + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(len(bin_list)) + " " + "binary package(s)" + sisyphus.getcolor.reset + "\n")
                    print("\n" + sisyphus.getcolor.green + "These are the source packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.green + ", ".join(
                        src_list) + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(len(src_list)) + " " + "source package(s)" + sisyphus.getcolor.reset + "\n")
                    while True:
                        user_input = input(sisyphus.getcolor.bright_white + "Would you like to proceed?" + sisyphus.getcolor.reset + " " +
                                           "[" + sisyphus.getcolor.bright_green + "Yes" + sisyphus.getcolor.reset + "/" + sisyphus.getcolor.bright_red + "No" + sisyphus.getcolor.reset + "]" + " ")
                        if user_input.lower() in ['yes', 'y', '']:
                            sisyphus.download.worldbinpkg()
                            p_exe = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg',
                                                      '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                            p_exe.wait()
                            sisyphus.syncdb.lcl_tbl()
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
                    print("\n" + sisyphus.getcolor.green + "These are the source packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.green + ", ".join(
                        src_list) + sisyphus.getcolor.reset + "\n\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(len(src_list)) + " " + "source package(s)" + sisyphus.getcolor.reset + "\n")
                    while True:
                        user_input = input(sisyphus.getcolor.bright_white + "Would you like to proceed?" + sisyphus.getcolor.reset + " " +
                                           "[" + sisyphus.getcolor.bright_green + "Yes" + sisyphus.getcolor.reset + "/" + sisyphus.getcolor.bright_red + "No" + sisyphus.getcolor.reset + "]" + " ")
                        if user_input.lower() in ['yes', 'y', '']:
                            p_exe = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--backtrack=100',
                                                      '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            p_exe.wait()
                            sisyphus.syncdb.lcl_tbl()
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
            p_exe = subprocess.Popen(['emerge', '--quiet', '--update', '--deep', '--newuse', '--pretend', '--getbinpkg',
                                      '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
            p_exe.wait()
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
    bin_list, src_list, need_cfg = pickle.load(open(os.path.join(
        sisyphus.getfs.portageMetadataDir, "sisyphus_worlddeps.pickle"), "rb"))

    if not len(src_list) == 0:
        print("\n" + "Source package(s) found in the mix;" + " " + "Use sisyphus CLI:" + " " + "'" +
              "sisyphus upgrade --ebuild" + "'" + " " + "to perform the upgrade;" + " " + "Aborting." + "\n")
    else:
        if not len(bin_list) == 0:
            os.chdir(sisyphus.getfs.portageCacheDir)
            print("\n" + "These are the binary packages that will be merged, in order:" + "\n\n" + ", ".join(
                bin_list) + "\n\n" + "Total:" + " " + str(len(bin_list)) + " " + "binary package(s)" + "\n\n")
            sisyphus.download.xworldbinpkgonly()
            p_exe = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly', '--rebuilt-binaries',
                                      '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # kill portage if the program dies or it's terminated by the user
            atexit.register(sisyphus.killemerge.start, p_exe)

            for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
                print(p_out.rstrip())

            p_exe.wait()
            sisyphus.syncdb.lcl_tbl()
        else:
            print("\nNo package upgrades found!\n")
