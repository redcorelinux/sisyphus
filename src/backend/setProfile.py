#!/usr/bin/python3

import animation
import platform
import subprocess

@animation.wait('setting up profile')
def start():
    if platform.uname()[4] == 'x86_64':
        eselectExec = subprocess.Popen(['eselect', 'profile', 'set', 'default/linux/amd64/17.1/hardened'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        eselectExec.communicate()

    if platform.uname()[4] == 'aarch64':
        eselectExec = subprocess.Popen(['eselect', 'profile', 'set', 'default/linux/arm64/17.0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        eselectExec.communicate()

    envExec = subprocess.Popen(['env-update'], stdout=subprocess.DEVNULL)
    envExec.wait()
