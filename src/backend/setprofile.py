#!/usr/bin/python3

import animation
import platform
import subprocess

@animation.wait('setting up profile')
def cliExec():
    if platform.uname()[4] == 'x86_64':
        eselectExec = subprocess.Popen(['eselect', 'profile', 'set', 'default/linux/amd64/17.1/hardened'])
        eselectExec.wait()

    if platform.uname()[4] == 'aarch64':
        eselectExec = subprocess.Popen(['eselect', 'profile', 'set', 'default/linux/arm64/17.0'])
        eselectExec.wait()

    envExec = subprocess.Popen(['env-update'], stdout=subprocess.DEVNULL)
    envExec.wait()
