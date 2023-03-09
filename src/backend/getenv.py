#!/usr/bin/python3

import io
import os
import subprocess
import sisyphus.getfs


def binhostURL():
    binhostURL = []
    p_exe = subprocess.Popen(
        ['emerge', '--info', '--verbose'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
        if "PORTAGE_BINHOST" in p_out:
            binhostURL = p_out.rstrip().split("=")[1].strip('\"')
    p_exe.wait()

    return binhostURL


def csvURL():
    csvURL = binhostURL()
    packagesCsvURL = []
    descriptionsCsvURL = []

    if "packages-next" in csvURL:
        packagesCsvURL = csvURL.replace(
            'packages-next', 'csv-next') + 'remotePackagesPre.csv'
        descriptionsCsvURL = csvURL.replace(
            'packages-next', 'csv-next') + 'remoteDescriptionsPre.csv'
    else:
        packagesCsvURL = csvURL.replace(
            'packages', 'csv') + 'remotePackagesPre.csv'
        descriptionsCsvURL = csvURL.replace(
            'packages', 'csv') + 'remoteDescriptionsPre.csv'

    return packagesCsvURL, descriptionsCsvURL


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
