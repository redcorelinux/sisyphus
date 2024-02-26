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
        print(sisyphus.getclr.bright_red +
              "\nYou need root permissions to do this!\n" + sisyphus.getclr.reset)
        sys.exit()
    else:
        if gfx_ui:
            sisyphus.solverevdeps.start.__wrapped__(pkgname)
        else:
            sisyphus.solverevdeps.start(pkgname)

        is_needed = pickle.load(
            open(os.path.join(sisyphus.getfs.p_mtd_dir, "sisyphus_pkgrevdeps.pickle"), "rb"))

    if is_needed != 0:
        if gfx_ui:
            p_exe = subprocess.Popen(['emerge'] + args + ['--pretend', '--verbose'] + list(
                pkgname), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # kill portage if the program dies or it's terminated by the user
            atexit.register(sisyphus.killemerge.start, p_exe)

            for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
                print(p_out.rstrip())

            p_exe.wait()
            print("\nWon't uninstall! Other packages depend on " + str(pkgname))
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
            print(sisyphus.getclr.bright_red +
                  "\nWon't uninstall! Other packages depend on " + sisyphus.getclr.reset + str(pkgname))
            print(sisyphus.getclr.bright_white + "Use the " + sisyphus.getclr.reset + sisyphus.getclr.green + "'--force'" +
                  sisyphus.getclr.reset + sisyphus.getclr.bright_white + " option to override at your own risk!\n" + sisyphus.getclr.reset)
    else:
        if unmerge:
            print("\n" + sisyphus.getclr.bright_white + "Selected packages are slated for" + sisyphus.getclr.reset + " " + sisyphus.getclr.green +
                  "'forced'" + sisyphus.getclr.reset + " " + sisyphus.getclr.bright_white + "removal." + sisyphus.getclr.reset + "\n")
            while True:
                user_input = input(sisyphus.getclr.bright_white + "Would you like to proceed?" + sisyphus.getclr.reset + " " +
                                   "[" + sisyphus.getclr.bright_green + "Yes" + sisyphus.getclr.reset + "/" + sisyphus.getclr.bright_red + "No" + sisyphus.getclr.reset + "]" + " ")
                if user_input.lower() in ['yes', 'y', '']:
                    while True:
                        confirmation_input = input(sisyphus.getclr.bright_white + "Are you sure you would like to proceed?" + sisyphus.getclr.reset + " " +
                                                   "[" + sisyphus.getclr.bright_green + "Yes" + sisyphus.getclr.reset + "/" + sisyphus.getclr.bright_red + "No" + sisyphus.getclr.reset + "]" + " ")
                        if confirmation_input.lower() in ['yes', 'y', '']:
                            p_exe = subprocess.Popen(
                                ['emerge', '--quiet', '--unmerge'] + list(pkgname))
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
                        elif confirmation_input.lower() in ['no', 'n']:
                            break
                        else:
                            print("\nSorry, response" + " " + "'" +
                                  confirmation_input + "'" + " " + "not understood.\n")
                            continue
                    break
                elif user_input.lower() in ['no', 'n']:
                    break
                else:
                    print("\nSorry, response" + " " + "'" +
                          user_input + "'" + " " + "not understood.\n")
                    continue
        elif depclean:
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
                print("\n" + sisyphus.getclr.bright_white + "Selected packages are slated for" + sisyphus.getclr.reset + " " + sisyphus.getclr.green +
                      "'safe'" + sisyphus.getclr.reset + " " + sisyphus.getclr.bright_white + "removal." + sisyphus.getclr.reset + "\n")
                while True:
                    user_input = input(sisyphus.getclr.bright_white + "Would you like to proceed?" + sisyphus.getclr.reset + " " +
                                       "[" + sisyphus.getclr.bright_green + "Yes" + sisyphus.getclr.reset + "/" + sisyphus.getclr.bright_red + "No" + sisyphus.getclr.reset + "]" + " ")
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
                        print("\nSorry, response" + " " + "'" +
                              user_input + "'" + " " + "not understood.\n")
                        continue
