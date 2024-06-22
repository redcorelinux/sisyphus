#!/usr/bin/python3

import animation
import platform
import signal
import subprocess


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


@animation.wait('setting up profile')
def start():
    if platform.uname()[4] == 'x86_64':
        e_exe = subprocess.Popen(
            ['eselect', 'profile', 'set', 'default/linux/amd64/23.0/split-usr/hardened'])
        try:
            e_exe.wait()
        except KeyboardInterrupt:
            e_exe.terminate()
            try:
                e_exe.wait(1)
            except subprocess.TimeoutExpired:
                e_exe.kill()
            sys.exit()

    if platform.uname()[4] == 'aarch64':
        e_exe = subprocess.Popen(
            ['eselect', 'profile', 'set', 'default/linux/arm64/23.0/split-usr'])
        try:
            e_exe.wait()
        except KeyboardInterrupt:
            e_exe.terminate()
            try:
                e_exe.wait(1)
            except subprocess.TimeoutExpired:
                e_exe.kill()
            sys.exit()

    env_exe = subprocess.Popen(['env-update'], stdout=subprocess.DEVNULL)
    try:
        env_exe.wait()
    except KeyboardInterrupt:
        env_exe.terminate()
        try:
            env_exe.wait(1)
        except subprocess.TimeoutExpired:
            env_exe.kill()
        sys.exit()
