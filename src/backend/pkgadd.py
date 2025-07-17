#!/usr/bin/python3

import atexit
import colorama
import fcntl
import io
import os
import pickle
import selectors
import signal
import subprocess
import sys
import time
import sisyphus.checkenv
import sisyphus.colsview
import sisyphus.depsolve
import sisyphus.dlbinpkg
import sisyphus.getfs
import sisyphus.syncdb
import sisyphus.syncall
import sisyphus.watchdog
from colorama import Fore, Back, Style

colorama.init()


def set_nonblocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)


def spinner_animation():
    spinner = ['-', '\\', '|', '/']
    sel = selectors.DefaultSelector()
    sel.register(sys.stdin, selectors.EVENT_READ)

    for _ in range(10):
        for char in spinner:
            sys.stdout.write('\b' + char)
            sys.stdout.flush()
            events = sel.select(timeout=0.1)
            if events:
                return
    sys.stdout.write('\b')


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def start(pkgname, ebuild=False, gfx_ui=False, oneshot=False, nodeps=False):
    go_args = ['--quiet', '--verbose',
               '--misspell-suggestion=n', '--fuzzy-search=n']
    nogo_args = ['--quiet', '--pretend', '--getbinpkg',
                 '--rebuilt-binaries', '--misspell-suggestion=n', '--fuzzy-search=n']
    if not sisyphus.checkenv.root():
        print(f"{Fore.RED}{Style.BRIGHT}\nRoot permissions are required for this operation.\n{Style.RESET_ALL}")
        sys.exit()
    else:
        if gfx_ui:
            sisyphus.depsolve.start.__wrapped__(
                pkgname, nodeps=False)  # undecorate
        else:
            sisyphus.syncall.start(gfx_ui=False)
            if nodeps:
                sisyphus.depsolve.start(pkgname, nodeps=True)
            else:
                sisyphus.depsolve.start(pkgname, nodeps=False)

        bin_list, src_list, is_vague, need_cfg = pickle.load(
            open(os.path.join(sisyphus.getfs.p_mtd_dir, "sisyphus_pkgdeps.pickle"), "rb"))

    if is_vague != 0:  # catch ambiguous packages
        p_exe = subprocess.Popen(
            ['emerge'] + nogo_args + (['--nodeps'] if nodeps else ['--with-bdeps=y']) + list(pkgname))
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
            pass  # GUI always calls <category>/<pkgname>, no ambiguity
        else:
            sys.exit()

    elif need_cfg != 0:  # catch aliens
        p_exe = subprocess.Popen(
            ['emerge'] + nogo_args + (['--nodeps'] if nodeps else ['--with-bdeps=y']) + list(pkgname))
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
            print("\nCannot proceed!\nPlease apply the above changes to your portage configuration files and try again.")
            for i in range(9, 0, -1):
                print(f"Killing application in : {i} seconds!")
                time.sleep(1)

            os.kill(os.getpid(), signal.SIGTERM)  # kill GUI window
        else:
            print(f"{Fore.RED}{Style.BRIGHT}\nCannot proceed!\n{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}Please apply the above changes to your portage configuration files and try again!{Style.RESET_ALL}")
            sys.exit()
    else:
        if len(bin_list) == 0 and len(src_list) == 0:
            print(f"{Fore.RED}{Style.BRIGHT}\nOne or more of the selected packages cannot be located for installation.\n{Style.RESET_ALL}")
        if ebuild:  # ebuild mode
            if len(bin_list) == 0 and len(src_list) != 0:  # source mode, ignore aliens
                sisyphus.colsview.print_packages(src_list=src_list)
                while True:
                    user_input = input(
                        f"{Fore.WHITE}{Style.BRIGHT}Would you like to proceed?{Style.RESET_ALL} [{Fore.GREEN}{Style.BRIGHT}Yes{Style.RESET_ALL}/{Fore.RED}{Style.BRIGHT}No{Style.RESET_ALL}] ")
                    if user_input.lower() in ['yes', 'y', '']:
                        p_exe = subprocess.Popen(['emerge'] + go_args + (['--nodeps'] if nodeps else [
                                                 '--with-bdeps=y']) + (['--oneshot'] if oneshot else []) + list(pkgname))
                        try:
                            set_nonblocking(sys.stdout.fileno())
                            spinner_animation()

                            sel = selectors.DefaultSelector()
                            sel.register(sys.stdin, selectors.EVENT_READ)

                            while True:
                                events = sel.select(timeout=0.1)
                                for key, mask in events:
                                    if key.fileobj == sys.stdin:
                                        line = sys.stdin.readline().strip()
                                        if line.lower() == 'q':
                                            sys.exit()
                                if p_exe.poll() is not None:
                                    break
                        except KeyboardInterrupt:
                            p_exe.terminate()
                            try:
                                p_exe.wait(1)
                            except subprocess.TimeoutExpired:
                                p_exe.kill()
                            sys.exit()
                        finally:
                            p_exe.wait()
                        sisyphus.syncdb.lcl_tbl()
                        break
                    elif user_input.lower() in ['no', 'n']:
                        break
                    else:
                        print(
                            f"\nApologies, the response '{user_input}' was not recognized.\n")
                        continue
            elif len(bin_list) != 0 and len(src_list) != 0:  # hybrid mode, ignore aliens
                sisyphus.colsview.print_packages(
                    bin_list=bin_list, src_list=src_list)
                while True:
                    user_input = input(
                        f"{Fore.WHITE}{Style.BRIGHT}Would you like to proceed?{Style.RESET_ALL} [{Fore.GREEN}{Style.BRIGHT}Yes{Style.RESET_ALL}/{Fore.RED}{Style.BRIGHT}No{Style.RESET_ALL}] ")
                    if user_input.lower() in ['yes', 'y', '']:
                        sisyphus.dlbinpkg.start(dl_world=False, gfx_ui=False)
                        os.chdir(sisyphus.getfs.p_cch_dir)
                        p_exe = subprocess.Popen(['emerge'] + go_args + ['--usepkg', '--rebuilt-binaries'] + (
                            ['--nodeps'] if nodeps else ['--with-bdeps=y']) + (['--oneshot'] if oneshot else []) + list(pkgname))
                        try:
                            set_nonblocking(sys.stdout.fileno())
                            spinner_animation()

                            sel = selectors.DefaultSelector()
                            sel.register(sys.stdin, selectors.EVENT_READ)

                            while True:
                                events = sel.select(timeout=0.1)
                                for key, mask in events:
                                    if key.fileobj == sys.stdin:
                                        line = sys.stdin.readline().strip()
                                        if line.lower() == 'q':
                                            sys.exit()
                                if p_exe.poll() is not None:
                                    break
                        except KeyboardInterrupt:
                            p_exe.terminate()
                            try:
                                p_exe.wait(1)
                            except subprocess.TimeoutExpired:
                                p_exe.kill()
                            sys.exit()
                        finally:
                            p_exe.wait()
                        sisyphus.syncdb.lcl_tbl()
                        break
                    elif user_input.lower() in ['no', 'n']:
                        break
                    else:
                        print(
                            f"\nApologies, the response '{user_input}' was not recognized.\n")
                        continue
            elif len(bin_list) != 0 and len(src_list) == 0:  # binary mode, fallback
                sisyphus.colsview.print_packages(bin_list=bin_list)
                while True:
                    user_input = input(
                        f"{Fore.WHITE}{Style.BRIGHT}Would you like to proceed?{Style.RESET_ALL} [{Fore.GREEN}{Style.BRIGHT}Yes{Style.RESET_ALL}/{Fore.RED}{Style.BRIGHT}No{Style.RESET_ALL}] ")
                    if user_input.lower() in ['yes', 'y', '']:
                        sisyphus.dlbinpkg.start(dl_world=False, gfx_ui=False)
                        os.chdir(sisyphus.getfs.p_cch_dir)
                        p_exe = subprocess.Popen(['emerge'] + go_args + ['--usepkg', '--usepkgonly', '--rebuilt-binaries'] + (
                            ['--nodeps'] if nodeps else ['--with-bdeps=y']) + (['--oneshot'] if oneshot else []) + list(pkgname))
                        try:
                            set_nonblocking(sys.stdout.fileno())
                            spinner_animation()

                            sel = selectors.DefaultSelector()
                            sel.register(sys.stdin, selectors.EVENT_READ)

                            while True:
                                events = sel.select(timeout=0.1)
                                for key, mask in events:
                                    if key.fileobj == sys.stdin:
                                        line = sys.stdin.readline().strip()
                                        if line.lower() == 'q':
                                            sys.exit()
                                if p_exe.poll() is not None:
                                    break
                        except KeyboardInterrupt:
                            p_exe.terminate()
                            try:
                                p_exe.wait(1)
                            except subprocess.TimeoutExpired:
                                p_exe.kill()
                            sys.exit()
                        finally:
                            p_exe.wait()
                        sisyphus.syncdb.lcl_tbl()
                        break
                    elif user_input.lower() in ['no', 'n']:
                        break
                    else:
                        print(
                            f"\nApologies, the response '{user_input}' was not recognized.\n")
                        continue
        else:  # non-ebuild mode
            if len(bin_list) == 0 and len(src_list) != 0:  # source mode (noop), catch aliens
                if gfx_ui:
                    print("\nSource package(s) found in the mix!\n")
                    print(
                        f"Use the Sisyphus CLI command: 'sisyphus install {' '.join(pkgname)} --ebuild' to perform the install; Aborting.")

                    for i in range(9, 0, -1):
                        print(f"Killing application in : {i} seconds!")
                        time.sleep(1)

                    os.kill(os.getpid(), signal.SIGTERM)  # kill GUI window
                else:
                    print(
                        f"{Fore.RED}{Style.BRIGHT}\nSource package(s) found in the mix!\n{Style.RESET_ALL}")
                    print(
                        f"{Fore.WHITE}{Style.BRIGHT}Use 'sisyphus install {' '.join(pkgname)} --ebuild' to perform the install; Aborting.{Style.RESET_ALL}")
                    sys.exit()
            elif len(bin_list) != 0 and len(src_list) != 0:  # hybrid mode (noop), catch aliens
                if gfx_ui:
                    print("\nSource package(s) found in the mix!\n")
                    print(
                        f"Use the Sisyphus CLI command:: 'sisyphus install {' '.join(pkgname)} --ebuild' to perform the install; Aborting.")

                    for i in range(9, 0, -1):
                        print(f"Killing application in : {i} seconds!")
                        time.sleep(1)

                    os.kill(os.getpid(), signal.SIGTERM)  # kill GUI window
                else:
                    print(
                        f"{Fore.RED}{Style.BRIGHT}\nSource package(s) found in the mix!\n{Style.RESET_ALL}")
                    print(
                        f"{Fore.WHITE}{Style.BRIGHT}Use 'sisyphus install {' '.join(pkgname)} --ebuild' to perform the install; Aborting.{Style.RESET_ALL}")
                    sys.exit()
            elif len(bin_list) != 0 and len(src_list) == 0:  # binary mode
                if gfx_ui:
                    sisyphus.dlbinpkg.start(dl_world=False, gfx_ui=True)
                    os.chdir(sisyphus.getfs.p_cch_dir)
                    p_exe = subprocess.Popen(['emerge'] + go_args + ['--usepkg', '--usepkgonly', '--rebuilt-binaries'] + (
                        # --nodeps && --oneshot are set to False in the graphical client
                        ['--nodeps'] if nodeps else ['--with-bdeps=y']) + (['--oneshot'] if oneshot else []) + pkgname, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    # kill portage if the program dies or it's terminated by the user
                    atexit.register(sisyphus.watchdog.start, p_exe)

                    for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
                        print(p_out.rstrip())

                    p_exe.wait()
                    sisyphus.syncdb.lcl_tbl()
                else:
                    sisyphus.colsview.print_packages(bin_list=bin_list)
                    while True:
                        user_input = input(
                            f"{Fore.WHITE}{Style.BRIGHT}Would you like to proceed?{Style.RESET_ALL} [{Fore.GREEN}{Style.BRIGHT}Yes{Style.RESET_ALL}/{Fore.RED}{Style.BRIGHT}No{Style.RESET_ALL}] ")
                        if user_input.lower() in ['yes', 'y', '']:
                            sisyphus.dlbinpkg.start(
                                dl_world=False, gfx_ui=False)
                            os.chdir(sisyphus.getfs.p_cch_dir)
                            p_exe = subprocess.Popen(['emerge'] + go_args + ['--usepkg', '--usepkgonly', '--rebuilt-binaries'] + (
                                ['--nodeps'] if nodeps else ['--with-bdeps=y']) + (['--oneshot'] if oneshot else []) + list(pkgname))
                            try:
                                set_nonblocking(sys.stdout.fileno())
                                spinner_animation()

                                sel = selectors.DefaultSelector()
                                sel.register(sys.stdin, selectors.EVENT_READ)

                                while True:
                                    events = sel.select(timeout=0.1)
                                    for key, mask in events:
                                        if key.fileobj == sys.stdin:
                                            line = sys.stdin.readline().strip()
                                            if line.lower() == 'q':
                                                sys.exit()
                                    if p_exe.poll() is not None:
                                        break
                            except KeyboardInterrupt:
                                p_exe.terminate()
                                try:
                                    p_exe.wait(1)
                                except subprocess.TimeoutExpired:
                                    p_exe.kill()
                                sys.exit()
                            finally:
                                p_exe.wait()
                            sisyphus.syncdb.lcl_tbl()
                            break
                        elif user_input.lower() in ['no', 'n']:
                            break
                        else:
                            print(
                                f"\nApologies, the response '{user_input}' was not recognized.\n")
                            continue
