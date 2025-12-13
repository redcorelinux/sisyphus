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


@animation.wait('resolving reverse dependencies')
def start(pkgname=None, depclean=False, unmerge=False):
    pattern = r'(\b[a-zA-Z0-9-_]+/[a-zA-Z0-9-_]+):\s+([0-9]+(?:\.[0-9]+){0,4})(_[a-zA-Z0-9]+)?(-r[1-9][0-9]*)?'
    rm_list = []

    args = ['--quiet', '--pretend', '--verbose']
    if unmerge:
        args.append('--unmerge')
    else:
        args.append('--depclean')

    if pkgname:
        args.extend(pkgname)

    is_installed = int(1)
    is_needed = int(0)
    is_vague = int(0)

    try:
        p_exe = subprocess.Popen(
            ['emerge'] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        stdout, stderr = p_exe.communicate()

        stdout_lines = stdout.decode('utf-8').splitlines()
        stderr_lines = stderr.decode('utf-8').splitlines()
        combined_output = stdout_lines + stderr_lines

        ambiguous_patterns = [
            r"short ebuild name",
            r"is ambiguous"
        ]

        pkg_missing_patterns = [
            r"Couldn't find",
            r"to depclean\."
        ]

        required_patterns = [
            r"pulled in by:",
            r"required"
        ]

        for p_out in stdout_lines:
            match = re.search(pattern, p_out)
            if match:
                to_remove = f"{match.group(1)}-{match.group(2)}"
                if match.group(3):
                    to_remove += match.group(3)
                if match.group(4):
                    to_remove += match.group(4)
                rm_list.append(to_remove)

        is_installed = int(not any(re.search(p, line)
                                   for line in combined_output for p in pkg_missing_patterns))
        is_needed = int(any(re.search(p, line)
                            for line in combined_output for p in required_patterns))
        is_vague = int(any(re.search(p, line)
                       for line in combined_output for p in ambiguous_patterns))

    except KeyboardInterrupt:
        p_exe.terminate()
        try:
            p_exe.wait(1)
        except subprocess.TimeoutExpired:
            p_exe.kill()
        sys.exit()

    pickle.dump([is_installed, is_needed, is_vague, rm_list], open(
        os.path.join(sisyphus.getfs.pkg_metadata_dir, "sisyphus_pkgrevdeps.pickle"), "wb"))
