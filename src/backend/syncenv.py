#!/usr/bin/python3

import os
import subprocess
import sisyphus.getfs


def gentooRepo():
    os.chdir(sisyphus.getfs.gentooRepoDir)
    localBranch = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    remoteBranch = subprocess.check_output(
        ['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    gitExecStage1 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] +
                                     localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE)
    gitExecStage1.wait()

    gitExecStage2 = subprocess.Popen(['git', 'reset', '--hard'] + remoteBranch.decode(
    ).strip().replace('refs/remotes/', '').split() + ['--quiet'], stdout=subprocess.PIPE)
    gitExecStage2.wait()


def redcoreRepo():
    os.chdir(sisyphus.getfs.redcoreRepoDir)
    localBranch = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    remoteBranch = subprocess.check_output(
        ['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    gitExecStage1 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] +
                                     localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE)
    gitExecStage1.wait()

    gitExecStage2 = subprocess.Popen(['git', 'reset', '--hard'] + remoteBranch.decode(
    ).strip().replace('refs/remotes/', '').split() + ['--quiet'], stdout=subprocess.PIPE)
    gitExecStage2.wait()


def portageConfigRepo():
    os.chdir(sisyphus.getfs.portageConfigDir)
    localBranch = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    remoteBranch = subprocess.check_output(
        ['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    gitExecStage1 = subprocess.Popen(['git', 'stash'], stdout=subprocess.PIPE)
    gitExecStage1.wait()
    gitExecStage2 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] +
                                     localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE)
    gitExecStage2.wait()
    gitExecStage3 = subprocess.Popen(['git', 'reset', '--hard'] + remoteBranch.decode(
    ).strip().replace('refs/remotes/', '').split() + ['--quiet'], stdout=subprocess.PIPE)
    gitExecStage3.wait()
    gitExecStage4 = subprocess.Popen(
        ['git', 'stash', 'apply'], stdout=subprocess.PIPE)
    gitExecStage4.wait()
    gitExecStage5 = subprocess.Popen(
        ['git', 'stash', 'clear'], stdout=subprocess.PIPE)
    gitExecStage5.wait()
    gitExecStage6 = subprocess.Popen(
        ['git', 'gc', '--prune=now', '--quiet'], stdout=subprocess.PIPE)
    gitExecStage6.wait()
