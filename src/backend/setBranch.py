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
    gentooRemote = []
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

    gentooRemote = [remote, sisyphus.getFilesystem.gentooRepo]
    redcoreRemote = [remote, sisyphus.getFilesystem.redcoreRepo]
    portageConfigRemote = [remote, sisyphus.getFilesystem.portageConfigRepo]

    return gentooRemote,redcoreRemote,portageConfigRemote

@animation.wait('injecting Gentoo Linux portage tree')
def injectGentooRepo(branch,remote):
    gentooRemote,redcoreRemote,portageConfigRemote = getBranchRemote(branch,remote)

    if not os.path.isdir(os.path.join(sisyphus.getFilesystem.gentooRepoDir, '.git')):
        git.Repo.clone_from("/".join(gentooRemote), sisyphus.getFilesystem.gentooRepoDir, depth=1, branch=branch)

@animation.wait('injecting Redcore Linux ebuild overlay')
def injectRedcoreRepo(branch,remote):
    gentooRemote,redcoreRemote,portageConfigRemote = getBranchRemote(branch,remote)

    if not os.path.isdir(os.path.join(sisyphus.getFilesystem.redcoreRepoDir, '.git')):
        git.Repo.clone_from("/".join(redcoreRemote), sisyphus.getFilesystem.redcoreRepoDir, depth=1, branch=branch)

@animation.wait('injecting Redcore Linux portage config')
def injectPortageConfigRepo(branch,remote):
    gentooRemote,redcoreRemote,portageConfigRemote = getBranchRemote(branch,remote)

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

def cliExec(branch,remote):
    if sisyphus.checkEnvironment.root():
        sisyphus.purgeEnvironment.branch()
        sisyphus.purgeEnvironment.metadata()
        injectGentooRepo(branch,remote)
        injectRedcoreRepo(branch,remote)
        injectPortageConfigRepo(branch,remote)
        sisyphus.setJobs.cliExec()
        sisyphus.setProfile.cliExec()
        giveWarning(branch,remote)
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")
