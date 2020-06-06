#!/usr/bin/python3

import animation
import os
import subprocess

gentooEbuildDir = '/usr/ports/gentoo'
redcoreEbuildDir = '/usr/ports/redcore'
portageConfigDir = '/opt/redcore-build'

@animation.wait('injecting gentoo linux portage tree - branch next')
def setGitlabNextStage1():
    if not os.path.isdir(os.path.join(gentooEbuildDir, '.git')):
        os.chdir(gentooEbuildDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://gitlab.com/redcore/portage.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'next', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'next', 'origin/next', '--quiet'])

@animation.wait('injecting redcore linux ebuild tree - branch next')
def setGitlabNextStage2():
    if not os.path.isdir(os.path.join(redcoreEbuildDir, '.git')):
        os.chdir(redcoreEbuildDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://gitlab.com/redcore/redcore-desktop.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'next', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'next', 'origin/next', '--quiet'])

@animation.wait('injecting redcore linux portage configuration - branch next')
def setGitlabNextStage3():
    if not os.path.isdir(os.path.join(portageConfigDir, '.git')):
        os.chdir(portageConfigDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://gitlab.com/redcore/redcore-build.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'next', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'next', 'origin/next', '--quiet'])

def startGitlab():
    setGitlabNextStage1()
    setGitlabNextStage2()
    setGitlabNextStage3()

@animation.wait('injecting gentoo linux portage tree - branch next')
def setPagureNextStage1():
    if not os.path.isdir(os.path.join(gentooEbuildDir, '.git')):
        os.chdir(gentooEbuildDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://pagure.io/redcore/portage.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'next', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'next', 'origin/next', '--quiet'])

@animation.wait('injecting redcore linux ebuild tree - branch next')
def setPagureNextStage2():
    if not os.path.isdir(os.path.join(redcoreEbuildDir, '.git')):
        os.chdir(redcoreEbuildDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://pagure.io/redcore/redcore-desktop.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'next', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'next', 'origin/next', '--quiet'])

@animation.wait('injecting redcore linux portage configuration - branch next')
def setPagureNextStage3():
    if not os.path.isdir(os.path.join(portageConfigDir, '.git')):
        os.chdir(portageConfigDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin', 'https://pagure.io/redcore/redcore-build.git'])
        subprocess.call(['git', 'fetch', '--depth=1', 'origin', 'next', '--quiet'])
        subprocess.call(['git', 'checkout', '-b', 'next', 'origin/next', '--quiet'])

def startPagure():
    setPagureNextStage1()
    setPagureNextStage2()
    setPagureNextStage3()
