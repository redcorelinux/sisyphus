#!/usr/bin/python3

import atexit
import colorama
import fcntl
import io
import os
import pickle
import signal
import selectors
import subprocess
import sys
import sisyphus.checkenv
import sisyphus.colsview
import sisyphus.revdepsolve
import sisyphus.syncdb
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


def start(ask=False, depclean=False, gfx_ui=False):
    args = ['--quiet', '--depclean']

    if not sisyphus.checkenv.root() and depclean:
        print(
            f"{Fore.WHITE}\nYou need root permissions to do this, exiting!\n{Style.RESET_ALL}")
        sys.exit()
    else:
        if gfx_ui:
            sisyphus.revdepsolve.start.__wrapped__(depclean=True)
        else:
            sisyphus.revdepsolve.start(depclean=True)

        is_installed, is_needed, is_vague, rm_list = pickle.load(
            open(os.path.join(sisyphus.getfs.p_mtd_dir, "sisyphus_pkgrevdeps.pickle"), "rb"))

    if len(rm_list) == 0:
        if gfx_ui:
            print("\nThe system is clean; no orphaned packages found.\n")
        else:
            print(
                f"{Fore.GREEN}{Style.BRIGHT}\nThe system is clean; no orphaned packages found.\n{Style.RESET_ALL}")
            sys.exit()

    else:
        if gfx_ui:
            p_exe = subprocess.Popen(
                ['emerge'] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # kill portage if the program dies or it's terminated by the user
            atexit.register(sisyphus.watchdog.start, p_exe)

            for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
                print(p_out.rstrip())

            p_exe.wait()
            sisyphus.syncdb.local_table()

        else:
            sisyphus.colsview.print_packages(rm_list=rm_list)
            while True:
                if ask:
                    user_input = input(
                        f"{Fore.WHITE}{Style.BRIGHT}Would you like to proceed?{Style.RESET_ALL} [{Fore.GREEN}{Style.BRIGHT}Yes{Style.RESET_ALL}/{Fore.RED}{Style.BRIGHT}No{Style.RESET_ALL}] ")
                else:
                    user_input = 'yes'

                if user_input.lower() in ['yes', 'y', '']:
                    p_exe = subprocess.Popen(['emerge'] + args)
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
                    sisyphus.syncdb.local_table()
                    break
                elif user_input.lower() in ['no', 'n']:
                    break
                else:
                    print(
                        f"\nApologies, the response '{user_input}' was not recognized.\n")
