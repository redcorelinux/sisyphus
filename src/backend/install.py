#!/usr/bin/python3

import atexit
import io
import os
import pickle
import signal
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


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def start(pkgname, ebuild=False, gfx_ui=False, oneshot=False):
    if not sisyphus.checkenv.root():
        print(sisyphus.getcolor.bright_red +
              "\nYou need root permissions to do this!\n" + sisyphus.getcolor.reset)
        sys.exit()
    else:
        if gfx_ui:
            sisyphus.solvedeps.start.__wrapped__(pkgname)  # undecorate
        else:
            sisyphus.update.start(gfx_ui=False)
            sisyphus.solvedeps.start(pkgname)

        bin_list, src_list, need_cfg = pickle.load(
            open(os.path.join(sisyphus.getfs.p_mtd_dir, "sisyphus_pkgdeps.pickle"), "rb"))

    if need_cfg != 0:  # catch aliens
        p_exe = subprocess.Popen(['emerge', '--quiet', '--pretend', '--getbinpkg', '--rebuilt-binaries',
                                 '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname))
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
            print(sisyphus.getcolor.bright_red +
                  "\nCannot proceed!\n" + sisyphus.getcolor.reset)
            print(sisyphus.getcolor.bright_yellow +
                  "Apply the above changes to your portage configuration files and try again" + sisyphus.getcolor.reset)
            sys.exit()
    else:
        if len(bin_list) == 0 and len(src_list) == 0:
            print(sisyphus.getcolor.bright_red +
                  "\nNo package found!\n" + sisyphus.getcolor.reset)
            sys.exit()

        if ebuild:  # ebuild mode
            if len(bin_list) == 0 and len(src_list) != 0:  # source mode, ignore aliens
                print("\n" + sisyphus.getcolor.green +
                      "These are the source packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n")
                print("\n" + sisyphus.getcolor.green +
                      ", ".join(src_list) + sisyphus.getcolor.reset + "\n")
                print("\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(
                    len(src_list)) + " " + "source package(s)" + sisyphus.getcolor.reset + "\n")
                while True:
                    user_input = input(sisyphus.getcolor.bright_white + "Would you like to proceed?" + sisyphus.getcolor.reset + " " +
                                       "[" + sisyphus.getcolor.bright_green + "Yes" + sisyphus.getcolor.reset + "/" + sisyphus.getcolor.bright_red + "No" + sisyphus.getcolor.reset + "]" + " ")
                    if user_input.lower() in ['yes', 'y', '']:
                        p_exe = subprocess.Popen(['emerge', '--quiet', '--verbose', '--with-bdeps=y', '--misspell-suggestion=n',
                                                 '--fuzzy-search=n'] + (['--oneshot'] if oneshot else []) + list(pkgname))
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
                print("\n" + sisyphus.getcolor.green +
                      "These are the binary packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n")
                print("\n" + sisyphus.getcolor.magenta +
                      ", ".join(bin_list) + sisyphus.getcolor.reset + "\n")
                print("\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(
                    len(bin_list)) + " " + "binary package(s)" + sisyphus.getcolor.reset + "\n")

                print("\n" + sisyphus.getcolor.green +
                      "These are the source packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n")
                print("\n" + sisyphus.getcolor.green +
                      ", ".join(src_list) + sisyphus.getcolor.reset + "\n")
                print("\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(
                    len(src_list)) + " " + "source package(s)" + sisyphus.getcolor.reset + "\n")
                while True:
                    user_input = input(sisyphus.getcolor.bright_white + "Would you like to proceed?" + sisyphus.getcolor.reset + " " +
                                       "[" + sisyphus.getcolor.bright_green + "Yes" + sisyphus.getcolor.reset + "/" + sisyphus.getcolor.bright_red + "No" + sisyphus.getcolor.reset + "]" + " ")
                    if user_input.lower() in ['yes', 'y', '']:
                        sisyphus.download.start(dl_world=False, gfx_ui=False)
                        os.chdir(sisyphus.getfs.p_cch_dir)
                        p_exe = subprocess.Popen(['emerge', '--quiet', '--verbose', '--usepkg', '--rebuilt-binaries', '--with-bdeps=y',
                                                 '--misspell-suggestion=n', '--fuzzy-search=n'] + (['--oneshot'] if oneshot else []) + list(pkgname))
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
                print("\n" + sisyphus.getcolor.green +
                      "These are the binary packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n")
                print("\n" + sisyphus.getcolor.magenta +
                      ", ".join(bin_list) + sisyphus.getcolor.reset + "\n")
                print("\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(
                    len(bin_list)) + " " + "binary package(s)" + sisyphus.getcolor.reset + "\n")
                while True:
                    user_input = input(sisyphus.getcolor.bright_white + "Would you like to proceed?" + sisyphus.getcolor.reset + " " +
                                       "[" + sisyphus.getcolor.bright_green + "Yes" + sisyphus.getcolor.reset + "/" + sisyphus.getcolor.bright_red + "No" + sisyphus.getcolor.reset + "]" + " ")
                    if user_input.lower() in ['yes', 'y', '']:
                        sisyphus.download.start(dl_world=False, gfx_ui=False)
                        os.chdir(sisyphus.getfs.p_cch_dir)
                        p_exe = subprocess.Popen(['emerge', '--quiet', '--verbose', '--usepkg', '--usepkgonly', '--rebuilt-binaries',
                                                 '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + (['--oneshot'] if oneshot else []) + list(pkgname))
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
                    print("Use sisyphus CLI:" + " " + "'" + "sisyphus install" +
                          " " + " ".join(pkgname) + "--ebuild" + "'")

                    for i in range(9, 0, -1):
                        print(f"Killing application in : {i} seconds!")
                        time.sleep(1)

                    sys.exit(app.exec_())  # kill GUI window
                else:
                    print(sisyphus.getcolor.bright_red +
                          "\nSource package(s) found in the mix!\n" + sisyphus.getcolor.reset)
                    print(sisyphus.getcolor.bright_yellow + "Use" + sisyphus.getcolor.reset + " " +
                          "'" + "sisyphus install" + " " + " ".join(pkgname) + " " + "--ebuild" + "'")
                    sys.exit()
            elif len(bin_list) != 0 and len(src_list) != 0:  # hybrid mode (noop), catch aliens
                if gfx_ui:
                    print("\nSource package(s) found in the mix!\n")
                    print("Use sisyphus CLI:" + " " + "'" + "sisyphus install" +
                          " " + " ".join(pkgname) + "--ebuild" + "'")

                    for i in range(9, 0, -1):
                        print(f"Killing application in : {i} seconds!")
                        time.sleep(1)

                    sys.exit(app.exec_())  # kill GUI window
                else:
                    print(sisyphus.getcolor.bright_red +
                          "\nSource package(s) found in the mix!\n" + sisyphus.getcolor.reset)
                    print(sisyphus.getcolor.bright_yellow + "Use" + sisyphus.getcolor.reset + " " +
                          "'" + "sisyphus install" + " " + " ".join(pkgname) + " " + "--ebuild" + "'")
                sys.exit()
            elif len(bin_list) != 0 and len(src_list) == 0:  # binary mode
                if gfx_ui:
                    print(
                        "\n" + "These are the binary packages that will be merged, in order:" + "\n")
                    print("\n" + ", ".join(bin_list) + "\n\n" + "Total:" + " " +
                          str(len(bin_list)) + " " + "binary package(s)" + "\n\n")
                    sisyphus.download.start(dl_world=False, gfx_ui=True)
                    os.chdir(sisyphus.getfs.p_cch_dir)
                    p_exe = subprocess.Popen(['emerge', '--quiet', '--verbose', '--usepkg', '--usepkgonly', '--rebuilt-binaries', '--with-bdeps=y',
                                             '--misspell-suggestion=n', '--fuzzy-search=n'] + pkgname, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    # kill portage if the program dies or it's terminated by the user
                    atexit.register(sisyphus.killemerge.start, p_exe)

                    for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
                        print(p_out.rstrip())

                    p_exe.wait()
                    sisyphus.syncdb.lcl_tbl()
                else:
                    print("\n" + sisyphus.getcolor.green +
                          "These are the binary packages that would be merged, in order:" + sisyphus.getcolor.reset + "\n")
                    print("\n" + sisyphus.getcolor.magenta +
                          ", ".join(bin_list) + sisyphus.getcolor.reset + "\n")
                    print("\n" + sisyphus.getcolor.bright_white + "Total:" + " " + str(
                        len(bin_list)) + " " + "binary package(s)" + sisyphus.getcolor.reset + "\n")
                    while True:
                        user_input = input(sisyphus.getcolor.bright_white + "Would you like to proceed?" + sisyphus.getcolor.reset + " " +
                                           "[" + sisyphus.getcolor.bright_green + "Yes" + sisyphus.getcolor.reset + "/" + sisyphus.getcolor.bright_red + "No" + sisyphus.getcolor.reset + "]" + " ")
                        if user_input.lower() in ['yes', 'y', '']:
                            sisyphus.download.start(
                                dl_world=False, gfx_ui=False)
                            os.chdir(sisyphus.getfs.p_cch_dir)
                            p_exe = subprocess.Popen(['emerge', '--quiet', '--verbose', '--usepkg', '--usepkgonly', '--rebuilt-binaries',
                                                     '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + (['--oneshot'] if oneshot else []) + list(pkgname))
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
