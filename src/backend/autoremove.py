#!/usr/bin/python3

import atexit
import io
import subprocess
import sys
import sisyphus.checkenv
import sisyphus.getcolor
import sisyphus.killemerge
import sisyphus.syncdb


def start():
    if sisyphus.checkenv.root():
        portageExec = subprocess.Popen(
            ['emerge', '--quiet', '--depclean', '--ask'])
        portageExec.wait()
        sisyphus.syncdb.localTable()
    else:
        print(sisyphus.getcolor.bright_red +
              "\nYou need root permissions to do this!\n" + sisyphus.getcolor.reset)
        sys.exit()


def xstart():
    portageExec = subprocess.Popen(
        ['emerge', '--depclean'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # kill portage if the program dies or it's terminated by the user
    atexit.register(sisyphus.killemerge.start, portageExec)

    for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
        print(portageOutput.rstrip())

    portageExec.wait()
    sisyphus.syncdb.localTable()
