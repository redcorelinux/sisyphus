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
        p_exe = subprocess.Popen(['emerge', '--quiet', '--depclean', '--ask'])
        p_exe.wait()
        sisyphus.syncdb.lcl_tbl()
    else:
        print(sisyphus.getcolor.bright_red +
              "\nYou need root permissions to do this!\n" + sisyphus.getcolor.reset)
        sys.exit()


def xstart():
    p_exe = subprocess.Popen(['emerge', '--depclean'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # kill portage if the program dies or it's terminated by the user
    atexit.register(sisyphus.killemerge.start, p_exe)

    for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
        print(p_out.rstrip())

    p_exe.wait()
    sisyphus.syncdb.lcl_tbl()
