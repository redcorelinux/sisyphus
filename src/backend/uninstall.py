#!/usr/bin/python3

import atexit
import io
import subprocess
import sys
import sisyphus.checkenv
import sisyphus.getcolor
import sisyphus.killemerge
import sisyphus.syncdb


def start(pkgname):
    if sisyphus.checkenv.root():
        p_exe = subprocess.Popen(
            ['emerge', '--quiet', '--depclean', '--ask'] + list(pkgname))
        p_exe.wait()
        sisyphus.syncdb.localTable()
    else:
        print(sisyphus.getcolor.bright_red +
              "\nYou need root permissions to do this!\n" + sisyphus.getcolor.reset)
        sys.exit()


def fstart(pkgname):
    if sisyphus.checkenv.root():
        p_exe = subprocess.Popen(
            ['emerge', '--quiet', '--unmerge', '--ask'] + list(pkgname))
        p_exe.wait()
        sisyphus.syncdb.localTable()
    else:
        print(sisyphus.getcolor.bright_red +
              "\nYou need root permissions to do this!\n" + sisyphus.getcolor.reset)
        sys.exit()


def xstart(pkgname):
    p_exe = subprocess.Popen(
        ['emerge', '--depclean'] + pkgname, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # kill portage if the program dies or it's terminated by the user
    atexit.register(sisyphus.killemerge.start, p_exe)

    for portageOutput in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
        print(portageOutput.rstrip())

    p_exe.wait()
    sisyphus.syncdb.localTable()
