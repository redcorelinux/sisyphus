#!/usr/bin/python3

import os
import subprocess
import sisyphus.getfs


def gentooRepo():
    os.chdir(sisyphus.getfs.gentooRepoDir)
    lcl_brch = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    rmt_brch = subprocess.check_output(
        ['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    g_exe1 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] +
                              lcl_brch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE)
    g_exe1.wait()

    g_exe2 = subprocess.Popen(['git', 'reset', '--hard'] + rmt_brch.decode(
    ).strip().replace('refs/remotes/', '').split() + ['--quiet'], stdout=subprocess.PIPE)
    g_exe2.wait()


def redcoreRepo():
    os.chdir(sisyphus.getfs.redcoreRepoDir)
    lcl_brch = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    rmt_brch = subprocess.check_output(
        ['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    g_exe1 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] +
                              lcl_brch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE)
    g_exe1.wait()

    g_exe2 = subprocess.Popen(['git', 'reset', '--hard'] + rmt_brch.decode(
    ).strip().replace('refs/remotes/', '').split() + ['--quiet'], stdout=subprocess.PIPE)
    g_exe2.wait()


def portageConfigRepo():
    os.chdir(sisyphus.getfs.portageConfigDir)
    lcl_brch = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    rmt_brch = subprocess.check_output(
        ['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    g_exe1 = subprocess.Popen(['git', 'stash'], stdout=subprocess.PIPE)
    g_exe1.wait()
    g_exe2 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] +
                              lcl_brch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE)
    g_exe2.wait()
    g_exe3 = subprocess.Popen(['git', 'reset', '--hard'] + rmt_brch.decode(
    ).strip().replace('refs/remotes/', '').split() + ['--quiet'], stdout=subprocess.PIPE)
    g_exe3.wait()
    g_exe4 = subprocess.Popen(
        ['git', 'stash', 'apply'], stdout=subprocess.PIPE)
    g_exe4.wait()
    g_exe5 = subprocess.Popen(
        ['git', 'stash', 'clear'], stdout=subprocess.PIPE)
    g_exe5.wait()
    g_exe6 = subprocess.Popen(
        ['git', 'gc', '--prune=now', '--quiet'], stdout=subprocess.PIPE)
    g_exe6.wait()
