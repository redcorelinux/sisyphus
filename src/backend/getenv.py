#!/usr/bin/python3

import io
import os
import signal
import subprocess
import sisyphus.getfs


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def bhst_addr():
    bhst_addr = []
    p_exe = subprocess.Popen(
        ['emerge', '--info', '--verbose'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for p_out in io.TextIOWrapper(p_exe.stdout, encoding="utf-8"):
        if "PORTAGE_BINHOST" in p_out:
            bhst_addr = p_out.rstrip().split("=")[1].strip('\"')
    try:
        p_exe.wait()
    except KeyboardInterrupt:
        p_exe.terminate()
        try:
            p_exe.wait(1)
        except subprocess.TimeoutExpired:
            p_exe.kill()
        sys.exit()

    return bhst_addr


def csv_addr():
    csv_addr = bhst_addr()
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


def sys_brch():
    actv_brch = None

    if os.path.isdir(os.path.join(sisyphus.getfs.g_src_dir, '.git')):
        os.chdir(sisyphus.getfs.g_src_dir)
        lcl_brch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])

        if lcl_brch.decode().strip() == 'master':
            actv_brch = str('master')

        if lcl_brch.decode().strip() == 'next':
            actv_brch = str('next')

    return actv_brch
