#!/usr/bin/python3

import io
import os
import subprocess
import sisyphus.getfs


def bh_addr():
    bh_addr = []
    p_exe = subprocess.Popen(
        ['emerge', '--info', '--verbose'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
        if "PORTAGE_BINHOST" in p_out:
            bh_addr = p_out.rstrip().split("=")[1].strip('\"')
    p_exe.wait()

    return bh_addr


def csv_addr():
    csv_addr = bh_addr()
    pcsv_addr = []
    dcsv_addr = []

    if "packages-next" in csv_addr:
        pcsv_addr = csv_addr.replace(
            'packages-next', 'csv-next') + 'remotePackagesPre.csv'
        dcsv_addr = csv_addr.replace(
            'packages-next', 'csv-next') + 'remoteDescriptionsPre.csv'
    else:
        pcsv_addr = csv_addr.replace(
            'packages', 'csv') + 'remotePackagesPre.csv'
        dcsv_addr = csv_addr.replace(
            'packages', 'csv') + 'remoteDescriptionsPre.csv'

    return pcsv_addr, dcsv_addr


def systemBranch():
    activeBranch = None

    if os.path.isdir(os.path.join(sisyphus.getfs.gentooRepoDir, '.git')):
        os.chdir(sisyphus.getfs.gentooRepoDir)
        localBranch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])

        if localBranch.decode().strip() == 'master':
            activeBranch = str('master')

        if localBranch.decode().strip() == 'next':
            activeBranch = str('next')

    return activeBranch
