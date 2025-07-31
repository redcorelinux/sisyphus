#!/usr/bin/python3

import animation
import os
import pickle
import re
import signal
import subprocess
import sys
import sisyphus.getfs


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


@animation.wait('resolving dependencies')
def start(pkgname=None, nodeps=False, onlydeps=False):
    bin_list = []
    src_list = []
    is_missing = []
    is_vague = int()
    need_cfg = int()

    if pkgname:
        args = ['--quiet', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--misspell-suggestion=n', '--fuzzy-search=n'] + \
            (['--nodeps'] if nodeps else ['--with-bdeps=y']) + \
            (['--onlydeps'] if onlydeps else []) + list(pkgname)
    else:
        args = ['--quiet', '--update', '--deep', '--newuse', '--pretend', '--getbinpkg', '--rebuilt-binaries',
                '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world']

    p_exe = subprocess.Popen(
        ['emerge'] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        stdout, stderr = p_exe.communicate()

        stdout_lines = stdout.decode('utf-8').splitlines()
        stderr_lines = stderr.decode('utf-8').splitlines()
        combined_output = stdout_lines + stderr_lines

        ambiguous_patterns = [
            r"short ebuild name",
            r"is ambiguous",
        ]

        config_patterns = [
            r"The following .* changes are necessary to proceed",
            r"REQUIRED_USE flag constraints are unsatisfied",
            r"masked packages.*required to complete your request"
        ]

        pkg_missing_patterns = [
            r"no ebuilds.*satisfy"
        ]

        if pkgname:
            is_missing = int(any(
                any(re.search(p, line) for p in pkg_missing_patterns)
                for line in combined_output
            ))
        else:
            is_missing = 0

        if pkgname:
            is_vague = int(any(
                any(re.search(p, line) for p in ambiguous_patterns)
                for line in combined_output
            ))
        else:
            is_vague = 0

        need_cfg = int(any(
            any(re.search(p, line) for p in config_patterns)
            for line in combined_output
        ))

        for p_out in stdout_lines:
            if "[binary" in p_out:
                is_bin = p_out.split("]")[1].split("[")[0].strip()
                bin_list.append(is_bin)

            if "[ebuild" in p_out:
                is_src = p_out.split("]")[1].split("[")[0].strip()
                src_list.append(is_src)

        if pkgname:
            pickle.dump([bin_list, src_list, is_missing, is_vague, need_cfg], open(
                os.path.join(sisyphus.getfs.p_mtd_dir, "sisyphus_pkgdeps.pickle"), "wb"))
        else:
            pickle.dump([bin_list, src_list, is_missing, is_vague, need_cfg], open(
                os.path.join(sisyphus.getfs.p_mtd_dir, "sisyphus_worlddeps.pickle"), "wb"))
    except KeyboardInterrupt:
        p_exe.terminate()
        try:
            p_exe.wait(1)
        except subprocess.TimeoutExpired:
            p_exe.kill()
        sys.exit()
