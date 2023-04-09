#!/usr/bin/python3

import atexit
import io
import signal
import subprocess
import sys
import sisyphus.checkenv
import sisyphus.getcolor
import sisyphus.killemerge
import sisyphus.syncdb


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def start(pkgname, gfx_ui=False, unmerge=False):
    args = ['--quiet', '--depclean']

    if not sisyphus.checkenv.root() and (unmerge or depclean):
        print(sisyphus.getcolor.bright_red +
              "\nYou need root permissions to do this!\n" + sisyphus.getcolor.reset)
        sys.exit()

    if unmerge:
        p_exe = subprocess.Popen(
            ['emerge', '--quiet', '--unmerge', '--ask'] + list(pkgname))
        try:
            p_exe.wait()
            sisyphus.syncdb.lcl_tbl()
        except KeyboardInterrupt:
            p_exe.terminate()
            try:
                p_exe.wait(1)
            except subprocess.TimeoutExpired:
                p_exe.kill()
            sys.exit()
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
            p_exe = subprocess.Popen(
                ['emerge'] + args + ['--ask'] + list(pkgname))
            try:
                p_exe.wait()
                sisyphus.syncdb.lcl_tbl()
            except KeyboardInterrupt:
                p_exe.terminate()
                try:
                    p_exe.wait(1)
                except subprocess.TimeoutExpired:
                    p_exe.kill()
                sys.exit()
