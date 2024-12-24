#!/usr/bin/python3

import atexit
import fcntl
import io
import os
import pickle
import signal
import selectors
import subprocess
import sys
import sisyphus.checkenv
import sisyphus.getclr
import sisyphus.revdepsolve
import sisyphus.syncdb
import sisyphus.watchdog


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


def start(depclean=False, gfx_ui=False):
    args = ['--quiet', '--depclean']

    if not sisyphus.checkenv.root() and depclean:
        print(f"{sisyphus.getclr.bright_red}\nRoot permissions are required to perform this action.\n{sisyphus.getclr.reset}")
        sys.exit()
    else:
        if gfx_ui:
            sisyphus.revdepsolve.start.__wrapped__(depclean=True)
        else:
            sisyphus.revdepsolve.start(depclean=True)

        is_installed, is_needed, is_vague, rm_list = pickle.load(
            open(os.path.join(sisyphus.getfs.p_mtd_dir, "sisyphus_pkgrevdeps.pickle"), "rb"))

    if gfx_ui:
        p_exe = subprocess.Popen(
            ['emerge'] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # kill portage if the program dies or it's terminated by the user
        atexit.register(sisyphus.watchdog.start, p_exe)

        for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
            print(p_out.rstrip())

        p_exe.wait()
        sisyphus.syncdb.lcl_tbl()

    else:
        print(f"\n{sisyphus.getclr.green}These are the orphaned packages that would be{sisyphus.getclr.reset} 'safely' {sisyphus.getclr.green}unmerged, in order:{sisyphus.getclr.reset}\n")
        print(
            f"\n{sisyphus.getclr.magenta}{', '.join(rm_list)}{sisyphus.getclr.reset}\n")
        print(
            f"\n{sisyphus.getclr.bright_white}Total: {len(rm_list)} orphaned package(s){sisyphus.getclr.reset}\n")

        while True:
            user_input = input(
                f"{sisyphus.getclr.bright_white}Would you like to proceed?{sisyphus.getclr.reset} [{sisyphus.getclr.bright_green}Yes{sisyphus.getclr.reset}/{sisyphus.getclr.bright_red}No{sisyphus.getclr.reset}] ")
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
                sisyphus.syncdb.lcl_tbl()
                break
            elif user_input.lower() in ['no', 'n']:
                break
            else:
                print(
                    f"\nApologies, the response '{user_input}' was not recognized.\n")
