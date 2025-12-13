#!/usr/bin/python3

import io
import os
import signal
import subprocess
import sisyphus.getfs


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def binhost_addr():
    binhost_addr = []
    p_exe = subprocess.Popen(
        ['emerge', '--info', '--verbose'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
        if "PORTAGE_BINHOST" in p_out:
            binhost_addr = p_out.rstrip().split("=")[1].strip('\"')
    try:
        p_exe.wait()
    except KeyboardInterrupt:
        p_exe.terminate()
        try:
            p_exe.wait(1)
        except subprocess.TimeoutExpired:
            p_exe.kill()
        sys.exit()

    return binhost_addr


def csv_addr():
    csv_addr = binhost_addr()
    pkg_csv_addr = []
    desc_csv_addr = []

    if "packages-next" in csv_addr:
        pkg_csv_addr = csv_addr.replace(
            'packages-next', 'csv-next') + 'remotePackagesPre.csv'
        desc_csv_addr = csv_addr.replace(
            'packages-next', 'csv-next') + 'remoteDescriptionsPre.csv'
    else:
        pkg_csv_addr = csv_addr.replace(
            'packages', 'csv') + 'remotePackagesPre.csv'
        desc_csv_addr = csv_addr.replace(
            'packages', 'csv') + 'remoteDescriptionsPre.csv'

    return pkg_csv_addr, desc_csv_addr


def system_branch():
    active_branch = None

    if os.path.isdir(os.path.join(sisyphus.getfs.gentoo_ebuild_dir, '.git')):
        os.chdir(sisyphus.getfs.gentoo_ebuild_dir)
        local_branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])

        if local_branch.decode().strip() == 'master':
            active_branch = str('master')

        if local_branch.decode().strip() == 'next':
            active_branch = str('next')

    return active_branch
