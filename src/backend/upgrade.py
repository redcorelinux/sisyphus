#!/usr/bin/python3

import atexit
import io
import os
import pickle
import signal
import subprocess
import sys
import time
import sisyphus.checkenv
import sisyphus.dlpkg
import sisyphus.getclr
import sisyphus.getfs
import sisyphus.killemerge
import sisyphus.solvedeps
import sisyphus.syncdb
import sisyphus.update


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def start(ebuild=False, gfx_ui=False):
    if not sisyphus.checkenv.root():
        print(sisyphus.getclr.bright_red +
              "\nYou need root permissions to do this!\n" + sisyphus.getclr.reset)
        sys.exit()
    else:
        if gfx_ui:
            sisyphus.solvedeps.start.__wrapped__()  # undecorate
        else:
            sisyphus.update.start(gfx_ui=False)
            sisyphus.solvedeps.start()

        bin_list, src_list, is_vague, need_cfg = pickle.load(
            open(os.path.join(sisyphus.getfs.p_mtd_dir, "sisyphus_worlddeps.pickle"), "rb"))

    if need_cfg != 0:  # catch aliens
        p_exe = subprocess.Popen(['emerge', '--quiet', '--update', '--deep', '--newuse', '--pretend', '--getbinpkg',
                                 '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
        try:
            p_exe.wait()
        except KeyboardInterrupt:
            p_exe.terminate()
            try:
                p_exe.wait(1)
            except subprocess.TimeoutExpired:
                p_exe.kill()
            sys.exit()
        if gfx_ui:
            print("\nCannot proceed!\n")
            print(
                "Apply the above changes to your portage configuration files and try again")

            for i in range(9, 0, -1):
                print(f"Killing application in : {i} seconds!")
                time.sleep(1)

            sys.exit(app.exec_())  # kill GUI window
        else:
            print(sisyphus.getclr.bright_red +
                  "\nCannot proceed!\n" + sisyphus.getclr.reset)
            print(sisyphus.getclr.bright_yellow +
                  "Apply the above changes to your portage configuration files and try again" + sisyphus.getclr.reset)
            sys.exit()
    else:
        if len(bin_list) == 0 and len(src_list) == 0:
            if gfx_ui:
                print("\nNo package upgrades found!\n")
            else:
                print(sisyphus.getclr.bright_red +
                      "\nNo package upgrades found!\n" + sisyphus.getclr.reset)
                sys.exit()

        if ebuild:  # ebuild mode
            if len(bin_list) == 0 and len(src_list) != 0:  # source mode, ignore aliens
                print("\n" + sisyphus.getclr.green +
                      "These are the source packages that would be merged, in order:" + sisyphus.getclr.reset + "\n")
                print("\n" + sisyphus.getclr.green +
                      ", ".join(src_list) + sisyphus.getclr.reset + "\n")
                print("\n" + sisyphus.getclr.bright_white + "Total:" + " " + str(
                    len(src_list)) + " " + "source package(s)" + sisyphus.getclr.reset + "\n")
                while True:
                    user_input = input(sisyphus.getclr.bright_white + "Would you like to proceed?" + sisyphus.getclr.reset + " " +
                                       "[" + sisyphus.getclr.bright_green + "Yes" + sisyphus.getclr.reset + "/" + sisyphus.getclr.bright_red + "No" + sisyphus.getclr.reset + "]" + " ")
                    if user_input.lower() in ['yes', 'y', '']:
                        p_exe = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse',
                                                 '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                        try:
                            p_exe.wait()
                        except KeyboardInterrupt:
                            p_exe.terminate()
                            try:
                                p_exe.wait(1)
                            except subprocess.TimeoutExpired:
                                p_exe.kill()
                            sys.exit()
                        sisyphus.syncdb.lcl_tbl()
                        break
                    elif user_input.lower() in ['no', 'n']:
                        break
                    else:
                        print("\nSorry, response" + " " + "'" +
                              user_input + "'" + " " + "not understood.\n")
                        continue
            elif len(bin_list) != 0 and len(src_list) != 0:  # hybrid mode, ignore aliens
                print("\n" + sisyphus.getclr.green +
                      "These are the binary packages that would be merged, in order:" + sisyphus.getclr.reset + "\n")
                print("\n" + sisyphus.getclr.magenta +
                      ", ".join(bin_list) + sisyphus.getclr.reset + "\n")
                print("\n" + sisyphus.getclr.bright_white + "Total:" + " " + str(
                    len(bin_list)) + " " + "binary package(s)" + sisyphus.getclr.reset + "\n")

                print("\n" + sisyphus.getclr.green +
                      "These are the source packages that would be merged, in order:" + sisyphus.getclr.reset + "\n")
                print("\n" + sisyphus.getclr.green +
                      ", ".join(src_list) + sisyphus.getclr.reset + "\n")
                print("\n" + sisyphus.getclr.bright_white + "Total:" + " " + str(
                    len(src_list)) + " " + "source package(s)" + sisyphus.getclr.reset + "\n")
                while True:
                    user_input = input(sisyphus.getclr.bright_white + "Would you like to proceed?" + sisyphus.getclr.reset + " " +
                                       "[" + sisyphus.getclr.bright_green + "Yes" + sisyphus.getclr.reset + "/" + sisyphus.getclr.bright_red + "No" + sisyphus.getclr.reset + "]" + " ")
                    if user_input.lower() in ['yes', 'y', '']:
                        sisyphus.dlpkg.start(dl_world=True, gfx_ui=False)
                        os.chdir(sisyphus.getfs.p_cch_dir)
                        p_exe = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg',
                                                 '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                        try:
                            p_exe.wait()
                        except KeyboardInterrupt:
                            p_exe.terminate()
                            try:
                                p_exe.wait(1)
                            except subprocess.TimeoutExpired:
                                p_exe.kill()
                            sys.exit()
                        sisyphus.syncdb.lcl_tbl()
                        break
                    elif user_input.lower() in ['no', 'n']:
                        break
                    else:
                        print("\nSorry, response" + " " + "'" +
                              user_input + "'" + " " + "not understood.\n")
                        continue
            elif len(bin_list) != 0 and len(src_list) == 0:  # binary mode, fallback
                print("\n" + sisyphus.getclr.green +
                      "These are the binary packages that would be merged, in order:" + sisyphus.getclr.reset + "\n")
                print("\n" + sisyphus.getclr.magenta +
                      ", ".join(bin_list) + sisyphus.getclr.reset + "\n")
                print("\n" + sisyphus.getclr.bright_white + "Total:" + " " + str(
                    len(bin_list)) + " " + "binary package(s)" + sisyphus.getclr.reset + "\n")
                while True:
                    user_input = input(sisyphus.getclr.bright_white + "Would you like to proceed?" + sisyphus.getclr.reset + " " +
                                       "[" + sisyphus.getclr.bright_green + "Yes" + sisyphus.getclr.reset + "/" + sisyphus.getclr.bright_red + "No" + sisyphus.getclr.reset + "]" + " ")
                    if user_input.lower() in ['yes', 'y', '']:
                        sisyphus.dlpkg.start(dl_world=True, gfx_ui=False)
                        os.chdir(sisyphus.getfs.p_cch_dir)
                        p_exe = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly',
                                                 '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                        try:
                            p_exe.wait()
                        except KeyboardInterrupt:
                            p_exe.terminate()
                            try:
                                p_exe.wait(1)
                            except subprocess.TimeoutExpired:
                                p_exe.kill()
                            sys.exit()
                        sisyphus.syncdb.lcl_tbl()
                        break
                    elif user_input.lower() in ['no', 'n']:
                        break
                    else:
                        print("\nSorry, response" + " " + "'" +
                              user_input + "'" + " " + "not understood.\n")
                        continue
        else:  # non-ebuild mode
            if len(bin_list) == 0 and len(src_list) != 0:  # source mode (noop), catch aliens
                if gfx_ui:
                    print("\nSource package(s) found in the mix!\n")
                    print("Use sisyphus CLI:" + " " + "'" + "sisyphus upgrade --ebuild" +
                          "'" + " " + "to perform the upgrade;" + " " + "Aborting.")

                    for i in range(9, 0, -1):
                        print(f"Killing application in : {i} seconds!")
                        time.sleep(1)

                    sys.exit(app.exec_())  # kill GUI window
                else:
                    print(sisyphus.getclr.bright_red +
                          "\nSource package(s) found in the mix!\n" + sisyphus.getclr.reset)
                    print(sisyphus.getclr.bright_yellow + "Use" +
                          sisyphus.getclr.reset + " " + "'" + "sisyphus upgrade --ebuild" + "'")
                    sys.exit()
            elif len(bin_list) != 0 and len(src_list) != 0:  # hybrid mode (noop), catch aliens
                if gfx_ui:
                    print("\nSource package(s) found in the mix!\n")
                    print("Use sisyphus CLI:" + " " + "'" + "sisyphus upgrade --ebuild" +
                          "'" + " " + "to perform the upgrade;" + " " + "Aborting.")

                    for i in range(9, 0, -1):
                        print(f"Killing application in : {i} seconds!")
                        time.sleep(1)

                    sys.exit(app.exec_())  # kill GUI window
                else:
                    print(sisyphus.getclr.bright_red +
                          "\nSource package(s) found in the mix!\n" + sisyphus.getclr.reset)
                    print(sisyphus.getclr.bright_yellow + "Use" +
                          sisyphus.getclr.reset + " " + "'" + "sisyphus upgrade --ebuild" + "'")
                    sys.exit()
            elif len(bin_list) != 0 and len(src_list) == 0:  # binary mode
                if gfx_ui:
                    print(
                        "\n" + "These are the binary packages that will be merged, in order:" + "\n")
                    print("\n" + ", ".join(bin_list) + "\n\n" + "Total:" + " " +
                          str(len(bin_list)) + " " + "binary package(s)" + "\n\n")
                    sisyphus.dlpkg.start(dl_world=True, gfx_ui=True)
                    os.chdir(sisyphus.getfs.p_cch_dir)
                    p_exe = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly', '--rebuilt-binaries',
                                             '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    # kill portage if the program dies or it's terminated by the user
                    atexit.register(sisyphus.killemerge.start, p_exe)

                    for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
                        print(p_out.rstrip())

                    p_exe.wait()
                    sisyphus.syncdb.lcl_tbl()
                else:
                    print("\n" + sisyphus.getclr.green +
                          "These are the binary packages that would be merged, in order:" + sisyphus.getclr.reset + "\n")
                    print("\n" + sisyphus.getclr.magenta +
                          ", ".join(bin_list) + sisyphus.getclr.reset + "\n")
                    print("\n" + sisyphus.getclr.bright_white + "Total:" + " " + str(
                        len(bin_list)) + " " + "binary package(s)" + sisyphus.getclr.reset + "\n")
                    while True:
                        user_input = input(sisyphus.getclr.bright_white + "Would you like to proceed?" + sisyphus.getclr.reset + " " +
                                           "[" + sisyphus.getclr.bright_green + "Yes" + sisyphus.getclr.reset + "/" + sisyphus.getclr.bright_red + "No" + sisyphus.getclr.reset + "]" + " ")
                        if user_input.lower() in ['yes', 'y', '']:
                            sisyphus.dlpkg.start(
                                dl_world=True, gfx_ui=False)
                            os.chdir(sisyphus.getfs.p_cch_dir)
                            p_exe = subprocess.Popen(['emerge', '--quiet', '--verbose', '--update', '--deep', '--newuse', '--usepkg', '--usepkgonly',
                                                     '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'])
                            try:
                                p_exe.wait()
                            except KeyboardInterrupt:
                                p_exe.terminate()
                                try:
                                    p_exe.wait(1)
                                except subprocess.TimeoutExpired:
                                    p_exe.kill()
                                sys.exit()
                            sisyphus.syncdb.lcl_tbl()
                            break
                        elif user_input.lower() in ['no', 'n']:
                            break
                        else:
                            print("\nSorry, response" + " " + "'" +
                                  user_input + "'" + " " + "not understood.\n")
                            continue
