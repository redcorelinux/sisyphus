#!/usr/bin/python3

import atexit
import io
import os
import signal
import subprocess
import sys
import pickle
import sisyphus.getfs
import sisyphus.killemerge


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def start(dl_world=False, gfx_ui=False):
    dl_list = []

    if dl_world:
        file_path = os.path.join(
            sisyphus.getfs.p_mtd_dir, "sisyphus_worlddeps.pickle")
    else:
        file_path = os.path.join(
            sisyphus.getfs.p_mtd_dir, "sisyphus_pkgdeps.pickle")

    with open(file_path, "rb") as f:
        bin_list, src_list, need_cfg = pickle.load(f)

    dl_list = [f'={package}' for package in bin_list]

    args = ['--nodeps', '--quiet', '--verbose', '--getbinpkg', '--fetchonly', '--rebuilt-binaries',
            '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n'] + list(dl_list)

    if gfx_ui:
        p_exe = subprocess.Popen(
            ['emerge'] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # kill portage if the program dies or it's terminated by the user
        atexit.register(sisyphus.killemerge.start, p_exe)

        for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
            print(p_out.rstrip())

        p_exe.wait()
    else:
        p_exe = subprocess.Popen(['emerge'] + args)
        try:
            p_exe.wait()
        except KeyboardInterrupt:
            p_exe.terminate()
            try:
                p_exe.wait(1)
            except subprocess.TimeoutExpired:
                p_exe.kill()
            sys.exit()
