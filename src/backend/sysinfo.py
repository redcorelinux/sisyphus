#!/usr/bin/python3

import subprocess


def show():
    subprocess.call(['emerge', '--info'])

