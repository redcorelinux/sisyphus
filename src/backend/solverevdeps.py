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
def start(pkgname=None, depclean=False, unmerge=False):
    is_installed = int(1)
    is_needed = int(0)
    is_vague = int(0)

    if unmerge:
        is_needed = int(0)
        try:
            p_exe = subprocess.Popen(['emerge', '--unmerge', '--quiet', '--pretend', '--verbose'] + list(
                pkgname), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            stdout, stderr = p_exe.communicate()

            for p_out in stderr.decode('utf-8').splitlines():
                if any(key in p_out for key in ["Couldn't find",
                                                "to depclean."]):
                    is_installed = int(0)

                if any(key in p_out for key in ["short ebuild name",
                                                "is ambiguous"]):
                    is_vague = int(1)
        except KeyboardInterrupt:
            p_exe.terminate()
            try:
                p_exe.wait(1)
            except subprocess.TimeoutExpired:
                p_exe.kill()
            sys.exit()
    else:
        try:
            p_exe = subprocess.Popen(['emerge', '--depclean', '--quiet', '--pretend',
                                     '--verbose'] + list(pkgname), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            stdout, stderr = p_exe.communicate()

            for p_out in stdout.decode('utf-8').splitlines():
                if any(key in p_out for key in ["pulled in by:",
                                                "required"]):
                    is_needed = int(1)

            for p_out in stderr.decode('utf-8').splitlines():
                if any(key in p_out for key in ["Couldn't find",
                                                "to depclean."]):
                    is_installed = int(0)

                if any(key in p_out for key in ["short ebuild name",
                                                "is ambiguous"]):
                    is_vague = int(1)

        except KeyboardInterrupt:
            p_exe.terminate()
            try:
                p_exe.wait(1)
            except subprocess.TimeoutExpired:
                p_exe.kill()
            sys.exit()

    pickle.dump([is_installed, is_needed, is_vague], open(os.path.join(
        sisyphus.getfs.p_mtd_dir, "sisyphus_pkgrevdeps.pickle"), "wb"))
