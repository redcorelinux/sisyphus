#!/usr/bin/python3

import animation
import platform
import subprocess


@animation.wait('setting up profile')
def start():
    if platform.uname()[4] == 'x86_64':
        e_exe = subprocess.Popen(
            ['eselect', 'profile', 'set', 'default/linux/amd64/17.1/hardened'])
        e_exe.wait()

    if platform.uname()[4] == 'aarch64':
        e_exe = subprocess.Popen(
            ['eselect', 'profile', 'set', 'default/linux/arm64/17.0'])
        e_exe.wait()

    env_exe = subprocess.Popen(['env-update'], stdout=subprocess.DEVNULL)
    env_exe.wait()
