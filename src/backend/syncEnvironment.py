#!/usr/bin/python3

import os
import subprocess
import sisyphus.getFilesystem

def syncStage1():
    os.chdir(sisyphus.getFilesystem.portageRepoDir)
    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    remoteBranch = subprocess.check_output(['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    gitExecStage1 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    gitExecStage1.communicate()

    gitExecStage2 = subprocess.Popen(['git', 'reset', '--hard'] + remoteBranch.decode().strip().replace('refs/remotes/','').split() + ['--quiet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    gitExecStage2.communicate()

def syncStage2():
    os.chdir(sisyphus.getFilesystem.redcoreRepoDir)
    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    remoteBranch = subprocess.check_output(['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    gitExecStage1 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    gitExecStage1.communicate()

    gitExecStage2 = subprocess.Popen(['git', 'reset', '--hard'] + remoteBranch.decode().strip().replace('refs/remotes/','').split() + ['--quiet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    gitExecStage2.communicate()

def syncStage3():
    os.chdir(sisyphus.getFilesystem.portageConfigDir)
    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    remoteBranch = subprocess.check_output(['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    gitExecStage1 = subprocess.Popen(['git', 'stash'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    gitExecStage1.communicate()
    gitExecStage2 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    gitExecStage2.communicate()
    gitExecStage3 = subprocess.Popen(['git', 'reset', '--hard'] + remoteBranch.decode().strip().replace('refs/remotes/','').split() + ['--quiet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    gitExecStage3.communicate()
    gitExecStage4 = subprocess.Popen(['git', 'stash', 'apply'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    gitExecStage4.communicate()
    gitExecStage5 = subprocess.Popen(['git', 'stash', 'clear'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    gitExecStage5.communicate()
    gitExecStage6 = subprocess.Popen(['git', 'gc', '--prune=now', '--quiet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    gitExecStage6.communicate()
