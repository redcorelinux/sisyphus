#!/usr/bin/python3

import os
import sys
import subprocess
import sisyphus.getfs


KEY_PATH = os.path.join(
    '/usr',
    'share',
    'openpgp-keys',
    'gentoo-release.asc',
)


def start():
    tree = sisyphus.getfs.g_src_dir
    g_exec = subprocess.Popen(['gemato', 'verify', tree, '-s', '-K', KEY_PATH],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

    for line in g_exec.stdout:
        print(line, end='')

    g_exec.wait()

    err = g_exec.stderr.read()
    if err:
        print(err, file=sys.stderr)

    if g_exec.returncode != 0:
        print(
            f"\nPortage tree signature verification failed for '{tree}'\n", file=sys.stderr,)
        sys.exit(g_exec.returncode)
