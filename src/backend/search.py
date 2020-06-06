#!/usr/bin/python3

import subprocess

def start(pkgList):
    subprocess.call(['emerge', '--search', '--getbinpkg'] + pkgList)
