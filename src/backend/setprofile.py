#!/usr/bin/python3

import animation
import subprocess

@animation.wait('setting up hardened profile')
def start():
    subprocess.call(['eselect', 'profile', 'set', 'default/linux/amd64/17.0/hardened'])
    subprocess.call(['env-update'])
