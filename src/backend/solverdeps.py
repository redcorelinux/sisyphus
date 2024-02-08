#!/usr/bin/python3

import animation
import os
import pickle
import signal
import subprocess
import sys
import sisyphus.getfs


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


@animation.wait('resolving reverse dependencies')
def start(pkgname=None):
    is_needed = int(0)

    p_exe = subprocess.Popen(
        ['emerge', '--depclean', '--quiet', '--pretend', '--verbose'] + list(pkgname), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        stdout, stderr = p_exe.communicate()

        for p_out in stdout.decode('utf-8').splitlines():
            if any(key in p_out for key in ["pulled in by:", "required"]):
                is_needed = int(1)

        pickle.dump(is_needed, open(os.path.join(
            sisyphus.getfs.p_mtd_dir, "sisyphus_pkgrdeps.pickle"), "wb"))
    except KeyboardInterrupt:
        p_exe.terminate()
        try:
            p_exe.wait(1)
        except subprocess.TimeoutExpired:
            p_exe.kill()
        sys.exit()
