#!/usr/bin/python3

import atexit
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
import sisyphus.depsolve
import sisyphus.dlbinpkg
import sisyphus.getclr
import sisyphus.getfs
import sisyphus.syncdb
import sisyphus.syncall
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


def start(ebuild=False, gfx_ui=False):
    go_args = ['--quiet', '--verbose', '--update', '--deep', '--newuse',
               '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n']
    nogo_args = ['--quiet', '--update', '--deep', '--newuse', '--pretend', '--getbinpkg',
                  '--rebuilt-binaries', '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n',]
    if not sisyphus.checkenv.root():
        print(f"{sisyphus.getclr.bright_red}\nRoot permissions are required for this operation.\n{sisyphus.getclr.reset}")
        sys.exit()
    else:
        if gfx_ui:
            sisyphus.depsolve.start.__wrapped__()  # undecorate
        else:
            sisyphus.syncall.start(gfx_ui=False)
            sisyphus.depsolve.start()

        bin_list, src_list, is_vague, need_cfg = pickle.load(
            open(os.path.join(sisyphus.getfs.p_mtd_dir, "sisyphus_worlddeps.pickle"), "rb"))

    if need_cfg != 0:  # catch aliens
        p_exe = subprocess.Popen(['emerge'] + nogo_args + ['@world'])
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
            print(f"{sisyphus.getclr.bright_red}\nCannot proceed!\n{sisyphus.getclr.reset}{sisyphus.getclr.bright_yellow}Please apply the above changes to your portage configuration files and try again!{sisyphus.getclr.reset}")
            sys.exit()
    else:
        if len(bin_list) == 0 and len(src_list) == 0:
            if gfx_ui:
                print("\nThe system is up to date; no package upgrades are required.\n")
            else:
                print(
                    f"{sisyphus.getclr.bright_red}\nThe system is up to date; no package upgrades are required.\n{sisyphus.getclr.reset}")
                sys.exit()

        if ebuild:  # ebuild mode
            if len(bin_list) == 0 and len(src_list) != 0:  # source mode, ignore aliens
                print(
                    f"\n{sisyphus.getclr.green}These are the source packages that would be merged, in order:{sisyphus.getclr.reset}\n")
                print(
                    f"\n{sisyphus.getclr.green}{', '.join(src_list)}{sisyphus.getclr.reset}\n")
                print(
                    f"\n{sisyphus.getclr.bright_white}Total: {len(src_list)} source package(s){sisyphus.getclr.reset}\n")
                while True:
                    user_input = input(
                        f"{sisyphus.getclr.bright_white}Would you like to proceed?{sisyphus.getclr.reset} [{sisyphus.getclr.bright_green}Yes{sisyphus.getclr.reset}/{sisyphus.getclr.bright_red}No{sisyphus.getclr.reset}] ")
                    if user_input.lower() in ['yes', 'y', '']:
                        p_exe = subprocess.Popen(
                            ['emerge'] + go_args + ['@world'])
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
                print(
                    f"\n{sisyphus.getclr.green}These are the binary packages that would be merged, in order:{sisyphus.getclr.reset}\n")
                print(
                    f"\n{sisyphus.getclr.magenta}{', '.join(bin_list)}{sisyphus.getclr.reset}\n")
                print(
                    f"\n{sisyphus.getclr.bright_white}Total: {len(bin_list)} binary package(s){sisyphus.getclr.reset}\n")

                print(
                    f"\n{sisyphus.getclr.green}These are the source packages that would be merged, in order:{sisyphus.getclr.reset}\n")
                print(
                    f"\n{sisyphus.getclr.green}{', '.join(src_list)}{sisyphus.getclr.reset}\n")
                print(
                    f"\n{sisyphus.getclr.bright_white}Total: {len(src_list)} source package(s){sisyphus.getclr.reset}\n")
                while True:
                    user_input = input(
                        f"{sisyphus.getclr.bright_white}Would you like to proceed?{sisyphus.getclr.reset} [{sisyphus.getclr.bright_green}Yes{sisyphus.getclr.reset}/{sisyphus.getclr.bright_red}No{sisyphus.getclr.reset}] ")
                    if user_input.lower() in ['yes', 'y', '']:
                        sisyphus.dlbinpkg.start(dl_world=True, gfx_ui=False)
                        os.chdir(sisyphus.getfs.p_cch_dir)
                        p_exe = subprocess.Popen(
                            ['emerge'] + go_args + ['--usepkg', '--rebuilt-binaries', '@world'])
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
                print(
                    f"\n{sisyphus.getclr.green}These are the binary packages that would be merged, in order:{sisyphus.getclr.reset}\n")
                print(
                    f"\n{sisyphus.getclr.magenta}{', '.join(bin_list)}{sisyphus.getclr.reset}\n")
                print(
                    f"\n{sisyphus.getclr.bright_white}Total: {len(bin_list)} binary package(s){sisyphus.getclr.reset}\n")
                while True:
                    user_input = input(
                        f"{sisyphus.getclr.bright_white}Would you like to proceed?{sisyphus.getclr.reset} [{sisyphus.getclr.bright_green}Yes{sisyphus.getclr.reset}/{sisyphus.getclr.bright_red}No{sisyphus.getclr.reset}] ")
                    if user_input.lower() in ['yes', 'y', '']:
                        sisyphus.dlbinpkg.start(dl_world=True, gfx_ui=False)
                        os.chdir(sisyphus.getfs.p_cch_dir)
                        p_exe = subprocess.Popen(
                            ['emerge'] + go_args + ['--usepkg', '--usepkgonly', '--rebuilt-binaries', '@world'])
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
                        f"Use the Sisyphus CLI command: 'sisyphus upgrade --ebuild' to perform the upgrade; Aborting.")

                    for i in range(9, 0, -1):
                        print(f"Killing application in : {i} seconds!")
                        time.sleep(1)

                    os.kill(os.getpid(), signal.SIGTERM)  # kill GUI window
                else:
                    print(
                        f"{sisyphus.getclr.bright_red}\nSource package(s) found in the mix!{sisyphus.getclr.reset}")
                    print(
                        f"{sisyphus.getclr.bright_yellow}Use{sisyphus.getclr.reset} 'sisyphus upgrade --ebuild' to perform the upgrade; Aborting.")
                    sys.exit()
            elif len(bin_list) != 0 and len(src_list) != 0:  # hybrid mode (noop), catch aliens
                if gfx_ui:
                    print("\nSource package(s) found in the mix!\n")
                    print(
                        f"Use the Sisyphus CLI command: 'sisyphus upgrade --ebuild' to perform the upgrade; Aborting.")

                    for i in range(9, 0, -1):
                        print(f"Killing application in : {i} seconds!")
                        time.sleep(1)

                    os.kill(os.getpid(), signal.SIGTERM)  # kill GUI window
                else:
                    print(
                        f"{sisyphus.getclr.bright_red}\nSource package(s) found in the mix!{sisyphus.getclr.reset}")
                    print(
                        f"{sisyphus.getclr.bright_yellow}Use{sisyphus.getclr.reset} 'sisyphus upgrade --ebuild' to perform the upgrade; Aborting.")
                    sys.exit()
            elif len(bin_list) != 0 and len(src_list) == 0:  # binary mode
                if gfx_ui:
                    print(
                        f"\nThese are the binary packages that will be merged, in order:\n")
                    print(", ".join(bin_list) +
                          f"\n\nTotal: {len(bin_list)} binary package(s)\n")
                    sisyphus.dlbinpkg.start(dl_world=True, gfx_ui=True)
                    os.chdir(sisyphus.getfs.p_cch_dir)
                    p_exe = subprocess.Popen(['emerge'] + go_args + ['--usepkg', '--usepkgonly',
                                             '--rebuilt-binaries', '@world'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    # kill portage if the program dies or it's terminated by the user
                    atexit.register(sisyphus.watchdog.start, p_exe)

                    for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
                        print(p_out.rstrip())

                    p_exe.wait()
                    sisyphus.syncdb.lcl_tbl()
                else:
                    print(
                        f"\n{sisyphus.getclr.green}These are the binary packages that would be merged, in order:{sisyphus.getclr.reset}\n")
                    print(
                        f"\n{sisyphus.getclr.magenta}{', '.join(bin_list)}{sisyphus.getclr.reset}\n")
                    print(
                        f"\n{sisyphus.getclr.bright_white}Total: {len(bin_list)} binary package(s){sisyphus.getclr.reset}\n")
                    while True:
                        user_input = input(
                            f"{sisyphus.getclr.bright_white}Would you like to proceed?{sisyphus.getclr.reset} [{sisyphus.getclr.bright_green}Yes{sisyphus.getclr.reset}/{sisyphus.getclr.bright_red}No{sisyphus.getclr.reset}] ")
                        if user_input.lower() in ['yes', 'y', '']:
                            sisyphus.dlbinpkg.start(
                                dl_world=True, gfx_ui=False)
                            os.chdir(sisyphus.getfs.p_cch_dir)
                            p_exe = subprocess.Popen(
                                ['emerge'] + go_args + ['--usepkg', '--usepkgonly', '--rebuilt-binaries', '@world'])
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
