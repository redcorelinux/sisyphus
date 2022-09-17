#!/usr/bin/python3

import os
import subprocess
import sisyphus.getFilesystem

def syncStage1():
    os.chdir(sisyphus.getFilesystem.portageRepoDir)
    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    remoteBranch = subprocess.check_output(['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    gitExecStage1 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'])
    gitExecStage1.wait()

    gitExecStage2 = subprocess.Popen(['git', 'reset', '--hard'] + remoteBranch.decode().strip().replace('refs/remotes/','').split() + ['--quiet'])
    gitExecStage2.wait()

def syncStage2():
    os.chdir(sisyphus.getFilesystem.redcoreRepoDir)
    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    remoteBranch = subprocess.check_output(['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    gitExecStage1 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'])
    gitExecStage1.wait()

    gitExecStage2 = subprocess.Popen(['git', 'reset', '--hard'] + remoteBranch.decode().strip().replace('refs/remotes/','').split() + ['--quiet'])
    gitExecStage2.wait()

def syncStage3():
    os.chdir(sisyphus.getFilesystem.portageConfigDir)
    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    remoteBranch = subprocess.check_output(['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    gitExecStage1 = subprocess.Popen(['git', 'stash'])
    gitExecStage1.wait()
    gitExecStage2 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'])
    gitExecStage2.wait()
    gitExecStage3 = subprocess.Popen(['git', 'reset', '--hard'] + remoteBranch.decode().strip().replace('refs/remotes/','').split() + ['--quiet'])
    gitExecStage3.wait()
    gitExecStage4 = subprocess.Popen(['git', 'stash', 'apply'])
    gitExecStage4.wait()
    gitExecStage5 = subprocess.Popen(['git', 'stash', 'clear'])
    gitExecStage5.wait()
    gitExecStage6 = subprocess.Popen(['git', 'gc', '--prune=now', '--quiet'])
    gitExecStage6.wait()
