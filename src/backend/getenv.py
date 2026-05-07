#!/usr/bin/python3

import os
import subprocess
import sisyphus.getfs


def binpkg_addr():
    files = [
        (sisyphus.getfs.binhostcfg, 'BINHOST (DEPRECATED)'),
        (sisyphus.getfs.binreposcfg, 'BINREPOS (CURRENT)')
    ]

    for path, ftype in files:
        if not os.path.exists(path):
            continue

        with open(path, 'r') as f:
            for line in f:
                clean = line.strip()
                if clean.startswith('#') or not clean:
                    continue

                if ftype == 'BINHOST (DEPRECATED)' and 'PORTAGE_BINHOST=' in clean:
                    return clean.split("=", 1)[1].replace('"', '').replace("'", "").strip()

                if ftype == 'BINREPOS (CURRENT)' and 'sync-uri =' in clean:
                    return clean.split("=", 1)[1].strip()
    return ""


def csv_addr():
    active_url = binpkg_addr()
    if not active_url:
        return None, None

    if "packages-next" in active_url:
        pkg_csv = active_url.replace(
            'packages-next', 'csv-next') + 'remotePackagesPre.csv'
        desc_csv = active_url.replace(
            'packages-next', 'csv-next') + 'remoteDescriptionsPre.csv'
    else:
        pkg_csv = active_url.replace(
            'packages', 'csv') + 'remotePackagesPre.csv'
        desc_csv = active_url.replace(
            'packages', 'csv') + 'remoteDescriptionsPre.csv'

    return pkg_csv, desc_csv


def system_branch():
    active_branch = None
    ebuild_dir = sisyphus.getfs.gentoo_ebuild_dir

    if os.path.isdir(os.path.join(ebuild_dir, '.git')):
        try:
            local_branch = subprocess.check_output(
                ['git', '-C', ebuild_dir, 'rev-parse', '--abbrev-ref', 'HEAD'],
                stderr=subprocess.DEVNULL
            ).decode().strip()

            if local_branch in ['master', 'next']:
                active_branch = local_branch
        except subprocess.CalledProcessError:
            pass

    return active_branch
