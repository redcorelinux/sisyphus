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
import sisyphus.getfs
import sisyphus.killemerge
import sisyphus.solverevdeps
import sisyphus.syncdb


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


def start(pkgname, depclean=False, gfx_ui=False, unmerge=False):
    args = ['--quiet', '--depclean']

    if not sisyphus.checkenv.root() and (unmerge or depclean):
        print(f"{sisyphus.getclr.bright_red}\nRoot permissions are required to perform this action.\n{sisyphus.getclr.reset}")
        sys.exit()
    else:
        if gfx_ui:
            sisyphus.solverevdeps.start.__wrapped__(
                pkgname, depclean=True, unmerge=False)
        else:
            if unmerge:
                sisyphus.solverevdeps.start.__wrapped__(
                    pkgname, depclean=False, unmerge=True)
            else:
                sisyphus.solverevdeps.start(
                    pkgname, depclean=True, unmerge=False)

        is_installed, is_needed, is_vague = pickle.load(open(os.path.join(
            sisyphus.getfs.p_mtd_dir, "sisyphus_pkgrevdeps.pickle"), "rb"))

    if is_vague != 0:  # catch ambiguous packages
        if unmerge:
            p_exe = subprocess.Popen(
                ['emerge', '--unmerge', '--quiet', '--pretend', '--verbose'] + list(pkgname))
            try:
                p_exe.wait()
            except KeyboardInterrupt:
                p_exe.terminate()
                try:
                    p_exe.wait(1)
                except subprocess.TimeoutExpired:
                    p_exe.kill()
                sys.exit()
        else:
            if gfx_ui:
                pass  # GUI always calls <category>/<pkgname>, no ambiguity
            else:
                p_exe = subprocess.Popen(
                    ['emerge', '--depclean', '--quiet', '--pretend', '--verbose'] + list(pkgname))
                try:
                    p_exe.wait()
                except KeyboardInterrupt:
                    p_exe.terminate()
                    try:
                        p_exe.wait(1)
                    except subprocess.TimeoutExpired:
                        p_exe.kill()
                    sys.exit()

    elif is_needed != 0:
        if unmerge:
            pass
        else:
            if gfx_ui:
                p_exe = subprocess.Popen(['emerge'] + args + ['--pretend', '--verbose'] + list(
                    pkgname), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # kill portage if the program dies or it's terminated by the user
                atexit.register(sisyphus.killemerge.start, p_exe)

                for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
                    print(p_out.rstrip())

                p_exe.wait()
                print(
                    "\nUnable to proceed! There are other packages with dependencies that prevent removal.")
            else:
                p_exe = subprocess.Popen(
                    ['emerge'] + args + ['--pretend', '--verbose'] + list(pkgname))
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
                print(f"{sisyphus.getclr.bright_red}\nUnable to proceed! Other packages have dependencies preventing removal.{sisyphus.getclr.reset}")
                print(f"{sisyphus.getclr.bright_white}Use the {sisyphus.getclr.reset}{sisyphus.getclr.green}'--force'{sisyphus.getclr.reset}{sisyphus.getclr.bright_white} option to override at your own risk!{sisyphus.getclr.reset}\n")
    else:
        if is_installed == 0:
            print(f"{sisyphus.getclr.bright_red}\nUnable to proceed! One or more selected packages could not be located for removal.\n{sisyphus.getclr.reset}")
            sys.exit()
        else:
            if unmerge:
                print(f"\n{sisyphus.getclr.bright_white}Selected packages are slated for{sisyphus.getclr.reset} {sisyphus.getclr.green}'forced'{sisyphus.getclr.reset} {sisyphus.getclr.bright_white}removal.{sisyphus.getclr.reset}\n")
                while True:
                    user_input = input(
                        f"{sisyphus.getclr.bright_white}Would you like to proceed?{sisyphus.getclr.reset} [{sisyphus.getclr.bright_green}Yes{sisyphus.getclr.reset}/{sisyphus.getclr.bright_red}No{sisyphus.getclr.reset}] ")
                    if user_input.lower() in ['yes', 'y', '']:
                        while True:
                            confirmation_input = input(
                                f"{sisyphus.getclr.bright_white}Are you sure you would like to proceed?{sisyphus.getclr.reset} [{sisyphus.getclr.bright_green}Yes{sisyphus.getclr.reset}/{sisyphus.getclr.bright_red}No{sisyphus.getclr.reset}] ")
                            if confirmation_input.lower() in ['yes', 'y', '']:
                                p_exe = subprocess.Popen(
                                    ['emerge', '--quiet', '--unmerge'] + list(pkgname))
                                try:
                                    set_nonblocking(sys.stdout.fileno())
                                    spinner_animation()

                                    sel = selectors.DefaultSelector()
                                    sel.register(
                                        sys.stdin, selectors.EVENT_READ)

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
                            elif confirmation_input.lower() in ['no', 'n']:
                                break
                            else:
                                print(
                                    f"\nApologies, the response '{confirmation_input}' was not recognized.\n")
                                continue
                        break
                    elif user_input.lower() in ['no', 'n']:
                        break
                    else:
                        print(
                            f"\nApologies, the response '{user_input}' was not recognized.\n")
                        continue
            else:
                if gfx_ui:
                    p_exe = subprocess.Popen(
                        ['emerge'] + args + pkgname, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    # kill portage if the program dies or it's terminated by the user
                    atexit.register(sisyphus.killemerge.start, p_exe)

                    for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
                        print(p_out.rstrip())

                    p_exe.wait()
                    sisyphus.syncdb.lcl_tbl()
                else:
                    print(f"\n{sisyphus.getclr.bright_white}Selected packages are slated for{sisyphus.getclr.reset} {sisyphus.getclr.green}'safe'{sisyphus.getclr.reset} {sisyphus.getclr.bright_white}removal.{sisyphus.getclr.reset}\n")
                    while True:
                        user_input = input(
                            f"{sisyphus.getclr.bright_white}Would you like to proceed?{sisyphus.getclr.reset} [{sisyphus.getclr.bright_green}Yes{sisyphus.getclr.reset}/{sisyphus.getclr.bright_red}No{sisyphus.getclr.reset}] ")
                        if user_input.lower() in ['yes', 'y', '']:
                            p_exe = subprocess.Popen(
                                ['emerge'] + args + list(pkgname))
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
