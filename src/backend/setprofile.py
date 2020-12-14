#!/usr/bin/python3

import animation
import subprocess

@animation.wait('setting up hardened profile')
def start():
    eselectExec = subprocess.Popen(['eselect', 'profile', 'set', 'default/linux/amd64/17.1/hardened'])
    eselectExec.wait()
    envExec = subprocess.Popen(['env-update'], stdout=subprocess.DEVNULL)
    envExec.wait()
