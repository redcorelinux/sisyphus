#!/usr/bin/python3

import animation
import os
import subprocess
import sisyphus.filesystem

@animation.wait('injecting gentoo linux portage tree - branch master')
def setGitlabMasterStage1():
    if not os.path.isdir(os.path.join(sisyphus.filesystem.portageRepoDir, '.git')):
        os.chdir(sisyphus.filesystem.portageRepoDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://gitlab.com/redcore/portage.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'master', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'master', 'origin/master', '--quiet'])

@animation.wait('injecting redcore linux ebuild tree - branch master')
def setGitlabMasterStage2():
    if not os.path.isdir(os.path.join(sisyphus.filesystem.redcoreRepoDir, '.git')):
        os.chdir(sisyphus.filesystem.redcoreRepoDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://gitlab.com/redcore/redcore-desktop.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'master', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'master', 'origin/master', '--quiet'])

@animation.wait('injecting redcore linux portage configuration - branch master')
def setGitlabMasterStage3():
    if not os.path.isdir(os.path.join(sisyphus.filesystem.portageConfigDir, '.git')):
        os.chdir(sisyphus.filesystem.portageConfigDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://gitlab.com/redcore/redcore-build.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'master', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'master', 'origin/master', '--quiet'])

def gitlabStart():
    setGitlabMasterStage1()
    setGitlabMasterStage2()
    setGitlabMasterStage3()

@animation.wait('injecting gentoo linux portage tree - branch master')
def setPagureMasterStage1():
    if not os.path.isdir(os.path.join(sisyphus.filesystem.portageRepoDir, '.git')):
        os.chdir(sisyphus.filesystem.portageRepoDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://pagure.io/redcore/portage.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'master', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'master', 'origin/master', '--quiet'])

@animation.wait('injecting redcore linux ebuild tree - branch master')
def setPagureMasterStage2():
    if not os.path.isdir(os.path.join(sisyphus.filesystem.redcoreRepoDir, '.git')):
        os.chdir(sisyphus.filesystem.redcoreRepoDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://pagure.io/redcore/redcore-desktop.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'master', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'master', 'origin/master', '--quiet'])

@animation.wait('injecting redcore linux portage configuration - branch master')
def setPagureMasterStage3():
    if not os.path.isdir(os.path.join(sisyphus.filesystem.portageConfigDir, '.git')):
        os.chdir(sisyphus.filesystem.portageConfigDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://pagure.io/redcore/redcore-build.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'master', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'master', 'origin/master', '--quiet'])

def pagureStart():
    setPagureMasterStage1()
    setPagureMasterStage2()
    setPagureMasterStage3()
