#!/usr/bin/python3

import animation
import os
import subprocess
import sisyphus.check
import sisyphus.branchreset
import sisyphus.filesystem
import sisyphus.metadata
import sisyphus.setjobs
import sisyphus.setprofile
import sys

def getBranchRemote(branch,remote):
    portageRemote = []
    redcoreRemote = []
    portageConfigRemote = []
    remoteBranch = []
    if "master" in branch:
        if "gitlab" in remote:
            remote = sisyphus.filesystem.remoteGitlab
        elif "pagure" in remote:
            remote = sisyphus.filesystem.remotePagure
        else:
            sys.exit("Usage: sisyphus-cli.py branch [OPTIONS] BRANCH" + "\n" +
                    "Try 'sisyphus-cli.py branch --help' for help." + "\n\n" +
                    "Error: Invalid remote" + " " + "'" + str(remote) + "'" + " " +  "(options : gitlab, pagure)"
                    )
    elif "next" in branch:
        if "gitlab" in remote:
            remote = sisyphus.filesystem.remoteGitlab
        elif "pagure" in remote:
            remote = sisyphus.filesystem.remotePagure
        else:
            sys.exit("Usage: sisyphus-cli.py branch [OPTIONS] BRANCH" + "\n" +
                    "Try 'sisyphus-cli.py branch --help' for help." + "\n\n" +
                    "Error: Invalid remote" + " " + "'" + str(remote) + "'" + " " +  "(options : gitlab, pagure)"
                    )
    else:
        sys.exit("Usage: sisyphus-cli.py branch [OPTIONS] BRANCH" + "\n" +
                "Try 'sisyphus-cli.py branch --help' for help." + "\n\n" +
                "Error: Invalid branch" + " " + "'" + str(branch) + "'" +" " +  "(options : master, next)"
                )

    portageRemote = [remote, sisyphus.filesystem.portageRepo]
    redcoreRemote = [remote, sisyphus.filesystem.redcoreRepo]
    portageConfigRemote = [remote, sisyphus.filesystem.portageConfigRepo]
    remoteBranch = ['origin', branch]

    return portageRemote,redcoreRemote,portageConfigRemote,remoteBranch

@animation.wait('injecting Gentoo Linux portage tree')
def injectGentooPortageTree(branch,remote):
    portageRemote,redcoreRemote,portageConfigRemote,remoteBranch = getBranchRemote(branch,remote)

    if not os.path.isdir(os.path.join(sisyphus.filesystem.portageRepoDir, '.git')):
        os.chdir(sisyphus.filesystem.portageRepoDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin'] + "/".join(portageRemote).split())
        subprocess.call(['git', 'fetch', '--depth=1', 'origin'] + branch.split() +  ['--quiet'])
        subprocess.call(['git', 'checkout', '-b'] + branch.split() + "/".join(remoteBranch).split() + ['--quiet'])

@animation.wait('injecting Redcore Linux ebuild overlay')
def injectRedcoreEbuildOverlay(branch,remote):
    portageRemote,redcoreRemote,portageConfigRemote,remoteBranch = getBranchRemote(branch,remote)

    if not os.path.isdir(os.path.join(sisyphus.filesystem.redcoreRepoDir, '.git')):
        os.chdir(sisyphus.filesystem.redcoreRepoDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin'] + "/".join(redcoreRemote).split())
        subprocess.call(['git', 'fetch', '--depth=1', 'origin'] + branch.split() +  ['--quiet'])
        subprocess.call(['git', 'checkout', '-b'] + branch.split() + "/".join(remoteBranch).split() + ['--quiet'])

@animation.wait('injecting Redcore Linux portage config')
def injectRedcorePortageConfig(branch,remote):
    portageRemote,redcoreRemote,portageConfigRemote,remoteBranch = getBranchRemote(branch,remote)

    if not os.path.isdir(os.path.join(sisyphus.filesystem.portageConfigDir, '.git')):
        os.chdir(sisyphus.filesystem.portageConfigDir)
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin'] + "/".join(portageConfigRemote).split())
        subprocess.call(['git', 'fetch', '--depth=1', 'origin'] + branch.split() +  ['--quiet'])
        subprocess.call(['git', 'checkout', '-b'] + branch.split() + "/".join(remoteBranch).split() + ['--quiet'])

def warnAboutBinaryRepository(branch,remote):
    if "master" in branch:
        print("\nThe switch to branch" + " " + "'" + branch + "'" +  " " + "from remote" + " " + "'" + remote + "'" + " " + "is now complete")
        print("You must pair this branch with the stable binary package repository")
        print("Hint : Use the odd numbers (1,3,5,7) from 'sisyphus mirror list'")
        print("Examples : 'sisyphus mirror set 1' or 'sisyphus mirror set 5'\n")
    elif "next" in branch:
        print("\nThe switch to branch" + " " + "'" + branch + "'" +  " " + "from remote" + " " + "'" + remote + "'" + " " + "is now complete")
        print("You must pair this branch with the testing binary package repository")
        print("Hint : Use the even numbers (2,4,6,8) from 'sisyphus mirror list'")
        print("Examples : 'sisyphus mirror set 4' or 'sisyphus mirror set 8'\n")


def start(branch,remote):
    sisyphus.check.root()
    sisyphus.branchreset.start()
    injectGentooPortageTree(branch,remote)
    injectRedcoreEbuildOverlay(branch,remote)
    injectRedcorePortageConfig(branch,remote)
    sisyphus.setjobs.start()
    sisyphus.setprofile.start()
    sisyphus.metadata.regenAnimated()
    warnAboutBinaryRepository(branch,remote)
