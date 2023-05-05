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


@animation.wait('resolving dependencies')
def start(pkgname=None):
    bin_list = []
    src_list = []
    is_vague = int()
    need_cfg = int()

    if pkgname:
        args = ['--quiet', '--pretend', '--getbinpkg', '--rebuilt-binaries',
                '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname)
    else:
        args = ['--quiet', '--update', '--deep', '--newuse', '--pretend', '--getbinpkg', '--rebuilt-binaries',
                '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world']

    p_exe = subprocess.Popen(
        ['emerge'] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = p_exe.communicate()

        for p_out in stderr.decode('utf-8').splitlines():
            if pkgname:
                if any(key in p_out for key in ["short ebuild name",
                                                "is ambiguous",
                                                "there are no ebuilds to satisfy"]):  # likely very fragile
                    is_vague = int(1)

            if any(key in p_out for key in ["The following keyword changes are necessary to proceed:",
                                            "The following mask changes are necessary to proceed:",
                                            "The following USE changes are necessary to proceed:",
                                            "The following REQUIRED_USE flag constraints are unsatisfied:",
                                            "One of the following masked packages is required to complete your request:"]):  # likely very fragile
                need_cfg = int(1)

        for p_out in stdout.decode('utf-8').splitlines():
            if "[binary" in p_out:
                is_bin = p_out.split("]")[1].split("[")[0].strip(" ")
                bin_list.append(is_bin)

            if "[ebuild" in p_out:
                is_src = p_out.split("]")[1].split("[")[0].strip(" ")
                src_list.append(is_src)

        if pkgname:
            pickle.dump([bin_list, src_list, is_vague, need_cfg], open(
                os.path.join(sisyphus.getfs.p_mtd_dir, "sisyphus_pkgdeps.pickle"), "wb"))
        else:
            pickle.dump([bin_list, src_list, is_vague, need_cfg], open(
                os.path.join(sisyphus.getfs.p_mtd_dir, "sisyphus_worlddeps.pickle"), "wb"))
    except KeyboardInterrupt:
        p_exe.terminate()
        try:
            p_exe.wait(1)
        except subprocess.TimeoutExpired:
            p_exe.kill()
        sys.exit()
