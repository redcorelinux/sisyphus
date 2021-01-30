#!/usr/bin/python3

import subprocess

def start(pkgname):
    subprocess.call(['emerge', '--search', '--getbinpkg'] + list(pkgname))
