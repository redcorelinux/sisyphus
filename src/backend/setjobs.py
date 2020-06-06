#!/usr/bin/python3

import animation
import subprocess

@animation.wait('adjusting MAKEOPTS')
def start():
    subprocess.call(['/usr/share/sisyphus/helpers/set_jobs'])
