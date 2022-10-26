#!/usr/bin/python3

import subprocess

def cliExec(pkgname):
    subprocess.call(['emerge', '--search', '--getbinpkg'] + list(pkgname))
