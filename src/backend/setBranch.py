#!/usr/bin/python3

import animation
import git
import os
import sys
import sisyphus.checkenv
import sisyphus.getfs
import sisyphus.purgeenv
import sisyphus.setJobs
import sisyphus.setProfile

def getBranchRemote(branch,remote):
    gentooRemote = []
    redcoreRemote = []
    portageConfigRemote = []
    if "master" in branch:
        if "gitlab" in remote:
            remote = sisyphus.getfs.remoteGitlab
        elif "pagure" in remote:
            remote = sisyphus.getfs.remotePagure
        else:
            sys.exit("Usage: sisyphus-cli.py branch [OPTIONS] BRANCH" + "\n" +
                    "Try 'sisyphus-cli.py branch --help' for help." + "\n\n" +
                    "Error: Invalid remote" + " " + "'" + str(remote) + "'" + " " +  "(options : gitlab, pagure)"
                    )
    elif "next" in branch:
        if "gitlab" in remote:
            remote = sisyphus.getfs.remoteGitlab
        elif "pagure" in remote:
            remote = sisyphus.getfs.remotePagure
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

    gentooRemote = [remote, sisyphus.getfs.gentooRepo]
    redcoreRemote = [remote, sisyphus.getfs.redcoreRepo]
    portageConfigRemote = [remote, sisyphus.getfs.portageConfigRepo]

    return gentooRemote,redcoreRemote,portageConfigRemote

@animation.wait('injecting Gentoo Linux portage tree')
def injectGentooRepo(branch,remote):
    gentooRemote,redcoreRemote,portageConfigRemote = getBranchRemote(branch,remote)

    if not os.path.isdir(os.path.join(sisyphus.getfs.gentooRepoDir, '.git')):
        git.Repo.clone_from("/".join(gentooRemote), sisyphus.getfs.gentooRepoDir, depth=1, branch=branch)

@animation.wait('injecting Redcore Linux ebuild overlay')
def injectRedcoreRepo(branch,remote):
    gentooRemote,redcoreRemote,portageConfigRemote = getBranchRemote(branch,remote)

    if not os.path.isdir(os.path.join(sisyphus.getfs.redcoreRepoDir, '.git')):
        git.Repo.clone_from("/".join(redcoreRemote), sisyphus.getfs.redcoreRepoDir, depth=1, branch=branch)

@animation.wait('injecting Redcore Linux portage config')
def injectPortageConfigRepo(branch,remote):
    gentooRemote,redcoreRemote,portageConfigRemote = getBranchRemote(branch,remote)

    if not os.path.isdir(os.path.join(sisyphus.getfs.portageConfigDir, '.git')):
        git.Repo.clone_from("/".join(portageConfigRemote), sisyphus.getfs.portageConfigDir, depth=1, branch=branch)

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
    if sisyphus.checkenv.root():
        sisyphus.purgeenv.branch()
        sisyphus.purgeenv.metadata()
        injectGentooRepo(branch,remote)
        injectRedcoreRepo(branch,remote)
        injectPortageConfigRepo(branch,remote)
        sisyphus.setJobs.cliExec()
        sisyphus.setProfile.cliExec()
        giveWarning(branch,remote)
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")
