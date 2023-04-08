#!/usr/bin/python3

import os
import signal
import subprocess
import sisyphus.getfs


def sigint_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def g_repo():
    os.chdir(sisyphus.getfs.g_src_dir)
    lcl_brch = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    rmt_brch = subprocess.check_output(
        ['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    g_exe1 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] +
                              lcl_brch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE)
    try:
        g_exe1.wait()
    except KeyboardInterrupt:
        g_exe1.terminate()
        try:
            g_exe1.wait(1)
        except subprocess.TimeoutExpired:
            g_exe1.kill()
        sys.exit()

    g_exe2 = subprocess.Popen(['git', 'reset', '--hard'] + rmt_brch.decode().strip(
    ).replace('refs/remotes/', '').split() + ['--quiet'], stdout=subprocess.PIPE)
    try:
        g_exe2.wait()
    except KeyboardInterrupt:
        g_exe2.terminate()
        try:
            g_exe2.wait()
        except subprocess.TimeoutExpired:
            g_exe2.kill()
        sys.exit()


def r_repo():
    os.chdir(sisyphus.getfs.r_src_dir)
    lcl_brch = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    rmt_brch = subprocess.check_output(
        ['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    g_exe1 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] +
                              lcl_brch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE)
    try:
        g_exe1.wait()
    except KeyboardInterrupt:
        g_exe1.terminate()
        try:
            g_exe1.wait(1)
        except subprocess.TimeoutExpired:
            g_exe1.kill()
        sys.exit()

    g_exe2 = subprocess.Popen(['git', 'reset', '--hard'] + rmt_brch.decode().strip(
    ).replace('refs/remotes/', '').split() + ['--quiet'], stdout=subprocess.PIPE)
    try:
        g_exe2.wait()
    except KeyboardInterrupt:
        g_exe2.terminate()
        try:
            g_exe2.wait(1)
        except subprocess.TimeoutExpired:
            g_exe2.kill()
        sys.exit()


def p_cfg_repo():
    os.chdir(sisyphus.getfs.p_cfg_dir)
    lcl_brch = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    rmt_brch = subprocess.check_output(
        ['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    g_exe1 = subprocess.Popen(['git', 'stash'], stdout=subprocess.PIPE)
    try:
        g_exe1.wait()
    except KeyboardInterrupt:
        g_exe1.terminate()
        try:
            g_exe1.wait(1)
        except subprocess.TimeoutExpired:
            g_exe1.kill()
        sys.exit()
    g_exe2 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] +
                              lcl_brch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE)
    try:
        g_exe2.wait()
    except KeyboardInterrupt:
        g_exe2.terminate()
        try:
            g_exe2.wait(1)
        except subprocess.TimeoutExpired:
            g_exe2.kill()
        sys.exit()
    g_exe3 = subprocess.Popen(['git', 'reset', '--hard'] + rmt_brch.decode().strip(
    ).replace('refs/remotes/', '').split() + ['--quiet'], stdout=subprocess.PIPE)
    try:
        g_exe3.wait()
    except KeyboardInterrupt:
        g_exe3.terminate()
        try:
            g_exe3.wait(1)
        except subprocess.TimeoutExpired:
            g_exe3.kill()
        sys.exit()
    g_exe4 = subprocess.Popen(
        ['git', 'stash', 'apply'], stdout=subprocess.PIPE)
    try:
        g_exe4.wait()
    except KeyboardInterrupt:
        g_exe4.terminate()
        try:
            g_exe4.wait(1)
        except subprocess.TimeoutExpired:
            g_exe4.kill()
        sys.exit()
    g_exe5 = subprocess.Popen(
        ['git', 'stash', 'clear'], stdout=subprocess.PIPE)
    try:
        g_exe5.wait()
    except KeyboardInterrupt:
        g_exe5.terminate()
        try:
            g_exe5.wait(1)
        except subprocess.TimeoutExpired:
            g_exe5.kill()
        sys.exit()
    g_exe6 = subprocess.Popen(
        ['git', 'gc', '--prune=now', '--quiet'], stdout=subprocess.PIPE)
    try:
        g_exe6.wait()
    except KeyboardInterrupt:
        g_exe6.terminate()
        try:
            g_exe6.wait(1)
        except subprocess.TimeoutExpired:
            g_exe6.kill()
        sys.exit()
