#!/usr/bin/python3

import os
import subprocess
import sisyphus.filesystem

def portage():
    os.chdir(sisyphus.filesystem.portageRepoDir)
    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    remoteBranch = subprocess.check_output(['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    gitExecStage1 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = gitExecStage1.communicate()

    gitExecStage2 = subprocess.Popen(['git', 'reset', '--hard'] + remoteBranch.decode().strip().replace('refs/remotes/','').split() + ['--quiet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = gitExecStage2.communicate()

def overlay():
    os.chdir(sisyphus.filesystem.redcoreRepoDir)
    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    remoteBranch = subprocess.check_output(['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    gitExecStage1 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = gitExecStage1.communicate()

    gitExecStage2 = subprocess.Popen(['git', 'reset', '--hard'] + remoteBranch.decode().strip().replace('refs/remotes/','').split() + ['--quiet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = gitExecStage2.communicate()

def portageCfg():
    os.chdir(sisyphus.filesystem.portageConfigDir)
    localBranch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    remoteBranch = subprocess.check_output(['git', 'rev-parse', '--symbolic-full-name', '@{u}'])

    gitExecStage1 = subprocess.Popen(['git', 'stash'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = gitExecStage1.communicate()
    gitExecStage2 = subprocess.Popen(['git', 'fetch', '--depth=1', 'origin'] + localBranch.decode().strip().split() + ['--quiet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = gitExecStage2.communicate()
    gitExecStage3 = subprocess.Popen(['git', 'reset', '--hard'] + remoteBranch.decode().strip().replace('refs/remotes/','').split() + ['--quiet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = gitExecStage3.communicate()
    gitExecStage4 = subprocess.Popen(['git', 'stash', 'apply'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = gitExecStage4.communicate()
    gitExecStage5 = subprocess.Popen(['git', 'stash', 'clear'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = gitExecStage5.communicate()
    gitExecStage6 = subprocess.Popen(['git', 'gc', '--prune=now', '--quiet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = gitExecStage6.communicate()
