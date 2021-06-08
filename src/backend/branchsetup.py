#!/usr/bin/python3

import animation
import git
import os
import sys
import sisyphus.check
import sisyphus.filesystem
import sisyphus.purge
import sisyphus.setjobs
import sisyphus.setprofile

def getBranchRemote(branch,remote):
    portageRemote = []
    redcoreRemote = []
    portageConfigRemote = []
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

    return portageRemote,redcoreRemote,portageConfigRemote

@animation.wait('injecting Gentoo Linux portage tree')
def injectGentooPortageTree(branch,remote):
    portageRemote,redcoreRemote,portageConfigRemote = getBranchRemote(branch,remote)

    if not os.path.isdir(os.path.join(sisyphus.filesystem.portageRepoDir, '.git')):
        git.Repo.clone_from("/".join(portageRemote), sisyphus.filesystem.portageRepoDir, depth=1, branch=branch)

@animation.wait('injecting Redcore Linux ebuild overlay')
def injectRedcoreEbuildOverlay(branch,remote):
    portageRemote,redcoreRemote,portageConfigRemote = getBranchRemote(branch,remote)

    if not os.path.isdir(os.path.join(sisyphus.filesystem.redcoreRepoDir, '.git')):
        git.Repo.clone_from("/".join(redcoreRemote), sisyphus.filesystem.redcoreRepoDir, depth=1, branch=branch)

@animation.wait('injecting Redcore Linux portage config')
def injectRedcorePortageConfig(branch,remote):
    portageRemote,redcoreRemote,portageConfigRemote = getBranchRemote(branch,remote)

    if not os.path.isdir(os.path.join(sisyphus.filesystem.portageConfigDir, '.git')):
        git.Repo.clone_from("/".join(portageConfigRemote), sisyphus.filesystem.portageConfigDir, depth=1, branch=branch)

def warnAboutBinaryRepository(branch,remote):
    if "master" in branch:
        print("\nThe switch to branch" + " " + "'" + branch + "'" +  " " + "from remote" + " " + "'" + remote + "'" + " " + "is now complete")
        print("You must pair this branch with the stable binhost (binary repository)")
        print("Hint : Use the odd numbers (1,3,5,7) from 'sisyphus mirror list'")
        print("Examples : 'sisyphus mirror set 1' or 'sisyphus mirror set 5'\n")
    elif "next" in branch:
        print("\nThe switch to branch" + " " + "'" + branch + "'" +  " " + "from remote" + " " + "'" + remote + "'" + " " + "is now complete")
        print("You must pair this branch with the testing binhost (binary repository)")
        print("Hint : Use the even numbers (2,4,6,8) from 'sisyphus mirror list'")
        print("Examples : 'sisyphus mirror set 4' or 'sisyphus mirror set 8'\n")


def start(branch,remote):
    if sisyphus.check.root():
        sisyphus.purge.branch()
        sisyphus.purge.metadata()
        injectGentooPortageTree(branch,remote)
        injectRedcoreEbuildOverlay(branch,remote)
        injectRedcorePortageConfig(branch,remote)
        sisyphus.setjobs.start()
        sisyphus.setprofile.start()
        warnAboutBinaryRepository(branch,remote)
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")
