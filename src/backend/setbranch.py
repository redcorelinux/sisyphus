#!/usr/bin/python3

import animation
import git
import os
import sys
import sisyphus.checkenv
import sisyphus.getcolor
import sisyphus.getfs
import sisyphus.purgeenv
import sisyphus.setjobs
import sisyphus.setprofile


def getBranchRemote(branch, remote):
    gentooRemote = []
    redcoreRemote = []
    portageConfigRemote = []
    if "master" in branch:
        if "gitlab" in remote:
            remote = sisyphus.getfs.remoteGitlab
        elif "pagure" in remote:
            remote = sisyphus.getfs.remotePagure
    elif "next" in branch:
        if "gitlab" in remote:
            remote = sisyphus.getfs.remoteGitlab
        elif "pagure" in remote:
            remote = sisyphus.getfs.remotePagure

    gentooRemote = [remote, sisyphus.getfs.gentooRepo]
    redcoreRemote = [remote, sisyphus.getfs.redcoreRepo]
    portageConfigRemote = [remote, sisyphus.getfs.portageConfigRepo]

    return gentooRemote, redcoreRemote, portageConfigRemote


@animation.wait('injecting Gentoo Linux portage tree')
def injectGentooRepo(branch, remote):
    gentooRemote, redcoreRemote, portageConfigRemote = getBranchRemote(
        branch, remote)

    if not os.path.isdir(os.path.join(sisyphus.getfs.gentooRepoDir, '.git')):
        git.Repo.clone_from("/".join(gentooRemote),
                            sisyphus.getfs.gentooRepoDir, depth=1, branch=branch)


@animation.wait('injecting Redcore Linux ebuild overlay')
def injectRedcoreRepo(branch, remote):
    gentooRemote, redcoreRemote, portageConfigRemote = getBranchRemote(
        branch, remote)

    if not os.path.isdir(os.path.join(sisyphus.getfs.redcoreRepoDir, '.git')):
        git.Repo.clone_from("/".join(redcoreRemote),
                            sisyphus.getfs.redcoreRepoDir, depth=1, branch=branch)


@animation.wait('injecting Redcore Linux portage config')
def injectPortageConfigRepo(branch, remote):
    gentooRemote, redcoreRemote, portageConfigRemote = getBranchRemote(
        branch, remote)

    if not os.path.isdir(os.path.join(sisyphus.getfs.portageConfigDir, '.git')):
        git.Repo.clone_from("/".join(portageConfigRemote),
                            sisyphus.getfs.portageConfigDir, depth=1, branch=branch)


def giveWarning(branch, remote):
    if "master" in branch:
        print(sisyphus.getcolor.green + "\nActive branch switched:" +
              " " + sisyphus.getcolor.reset + "'" + branch + "'")
        print(sisyphus.getcolor.green + "Active remote switched:" +
              " " + sisyphus.getcolor.reset + "'" + remote + "'")
        print(sisyphus.getcolor.bright_yellow + "\nUse" + sisyphus.getcolor.reset + " " + "'" + "sisyphus mirror set 3" + "'" + " " + sisyphus.getcolor.bright_yellow + "or" +
              sisyphus.getcolor.reset + " " + "'" + "sisyphus mirror set 7" + "'" + " " + sisyphus.getcolor.bright_yellow + "to pair the binhost" + sisyphus.getcolor.reset)
        print(sisyphus.getcolor.bright_yellow +
              "Use" + sisyphus.getcolor.reset + " " + "'" + "sisyphus branch --help" + "'" + " " + sisyphus.getcolor.bright_yellow + "for help" + sisyphus.getcolor.reset)
    elif "next" in branch:
        print(sisyphus.getcolor.green + "\nActive branch switched:" +
              " " + sisyphus.getcolor.reset + "'" + branch + "'")
        print(sisyphus.getcolor.green + "Active remote switched:" +
              " " + sisyphus.getcolor.reset + "'" + remote + "'")
        print(sisyphus.getcolor.bright_yellow + "\nUse" + sisyphus.getcolor.reset + " " + "'" + "sisyphus mirror set 4" + "'" + " " + sisyphus.getcolor.bright_yellow + "or" +
              sisyphus.getcolor.reset + " " + "'" + "sisyphus mirror set 8" + "'" + " " + sisyphus.getcolor.bright_yellow + "to pair the binhost" + sisyphus.getcolor.reset)
        print(sisyphus.getcolor.bright_yellow +
              "Use" + sisyphus.getcolor.reset + " " + "'" + "sisyphus branch --help" + "'" + " " + sisyphus.getcolor.bright_yellow + "for help" + sisyphus.getcolor.reset)


def start(branch, remote):
    if sisyphus.checkenv.root():
        sisyphus.purgeenv.branch()
        sisyphus.purgeenv.metadata()
        injectGentooRepo(branch, remote)
        injectRedcoreRepo(branch, remote)
        injectPortageConfigRepo(branch, remote)
        sisyphus.setjobs.start()
        sisyphus.setprofile.start()
        giveWarning(branch, remote)
    else:
        print(sisyphus.getcolor.bright_red +
              "\nYou need root permissions to do this!\n" + sisyphus.getcolor.reset)
        sys.exit()
