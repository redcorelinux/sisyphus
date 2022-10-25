#!/usr/bin/python3

import animation
import git
import os
import sys
import sisyphus.checkEnvironment
import sisyphus.getFilesystem
import sisyphus.purgeEnvironment
import sisyphus.setJobs
import sisyphus.setProfile

def getBranchRemote(branch,remote):
    portageRemote = []
    redcoreRemote = []
    portageConfigRemote = []
    if "master" in branch:
        if "gitlab" in remote:
            remote = sisyphus.getFilesystem.remoteGitlab
        elif "pagure" in remote:
            remote = sisyphus.getFilesystem.remotePagure
        else:
            sys.exit("Usage: sisyphus-cli.py branch [OPTIONS] BRANCH" + "\n" +
                    "Try 'sisyphus-cli.py branch --help' for help." + "\n\n" +
                    "Error: Invalid remote" + " " + "'" + str(remote) + "'" + " " +  "(options : gitlab, pagure)"
                    )
    elif "next" in branch:
        if "gitlab" in remote:
            remote = sisyphus.getFilesystem.remoteGitlab
        elif "pagure" in remote:
            remote = sisyphus.getFilesystem.remotePagure
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

    portageRemote = [remote, sisyphus.getFilesystem.gentooRepo]
    redcoreRemote = [remote, sisyphus.getFilesystem.redcoreRepo]
    portageConfigRemote = [remote, sisyphus.getFilesystem.portageConfigRepo]

    return portageRemote,redcoreRemote,portageConfigRemote

@animation.wait('injecting Gentoo Linux portage tree')
def injectStage1(branch,remote):
    portageRemote,redcoreRemote,portageConfigRemote = getBranchRemote(branch,remote)

    if not os.path.isdir(os.path.join(sisyphus.getFilesystem.gentooRepoDir, '.git')):
        git.Repo.clone_from("/".join(portageRemote), sisyphus.getFilesystem.gentooRepoDir, depth=1, branch=branch)

@animation.wait('injecting Redcore Linux ebuild overlay')
def injectStage2(branch,remote):
    portageRemote,redcoreRemote,portageConfigRemote = getBranchRemote(branch,remote)

    if not os.path.isdir(os.path.join(sisyphus.getFilesystem.redcoreRepoDir, '.git')):
        git.Repo.clone_from("/".join(redcoreRemote), sisyphus.getFilesystem.redcoreRepoDir, depth=1, branch=branch)

@animation.wait('injecting Redcore Linux portage config')
def injectStage3(branch,remote):
    portageRemote,redcoreRemote,portageConfigRemote = getBranchRemote(branch,remote)

    if not os.path.isdir(os.path.join(sisyphus.getFilesystem.portageConfigDir, '.git')):
        git.Repo.clone_from("/".join(portageConfigRemote), sisyphus.getFilesystem.portageConfigDir, depth=1, branch=branch)

def giveWarning(branch,remote):
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
    if sisyphus.checkEnvironment.root():
        sisyphus.purgeEnvironment.branch()
        sisyphus.purgeEnvironment.metadata()
        injectStage1(branch,remote)
        injectStage2(branch,remote)
        injectStage3(branch,remote)
        sisyphus.setJobs.start()
        sisyphus.setProfile.start()
        giveWarning(branch,remote)
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")
