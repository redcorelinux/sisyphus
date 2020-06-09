#!/usr/bin/python3

import os
import subprocess
import sisyphus.check
import sisyphus.branchreset
import sisyphus.filesystem
import sys

def start(branch,remote):
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
   
    sisyphus.check.root()
    sisyphus.branchreset.start()

    if not os.path.isdir(os.path.join(sisyphus.filesystem.portageRepoDir, '.git')):
        os.chdir(sisyphus.filesystem.portageRepoDir)
        print("\nInjecting branch" + " " + "'" + branch + "'" +  " " + "from" + " " + "/".join(portageRemote))
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin'] + "/".join(portageRemote).split())
        subprocess.call(['git', 'fetch', '--depth=1', 'origin'] + branch.split() +  ['--quiet'])
        subprocess.call(['git', 'checkout', '-b'] + branch.split() + "/".join(remoteBranch).split() + ['--quiet'])

    if not os.path.isdir(os.path.join(sisyphus.filesystem.redcoreRepoDir, '.git')):
        os.chdir(sisyphus.filesystem.redcoreRepoDir)
        print("\nInjecting branch" + " " + "'" + branch + "'" +  " " + "from" + " " + "/".join(redcoreRemote) + "\n")
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin'] + "/".join(redcoreRemote).split())
        subprocess.call(['git', 'fetch', '--depth=1', 'origin'] + branch.split() +  ['--quiet'])
        subprocess.call(['git', 'checkout', '-b'] + branch.split() + "/".join(remoteBranch).split() + ['--quiet'])

    if not os.path.isdir(os.path.join(sisyphus.filesystem.portageConfigDir, '.git')):
        os.chdir(sisyphus.filesystem.portageConfigDir)
        print("Injecting branch" + " " + "'" + branch + "'" +  " " + "from" + " " + "/".join(portageConfigRemote) + "\n")
        subprocess.call(['git', 'init', '-q'])
        subprocess.call(['git', 'remote', 'add', 'origin'] + "/".join(portageConfigRemote).split())
        subprocess.call(['git', 'fetch', '--depth=1', 'origin'] + branch.split() +  ['--quiet'])
        subprocess.call(['git', 'checkout', '-b'] + branch.split() + "/".join(remoteBranch).split() + ['--quiet'])

    sisyphus.setjobs.start()
    sisyphus.setprofile.start()
    sisyphus.metadata.regenAnimated()
