#!/usr/bin/python3

import sisyphus.check
import sisyphus.branchreset
import sisyphus.branchmaster
import sisyphus.branchnext
import sisyphus.metadata
import sisyphus.setjobs
import sisyphus.setprofile

def gitlabMaster():
    sisyphus.check.root()
    sisyphus.branchreset.start()
    sisyphus.branchmaster.startGitlab()
    sisyphus.setjobs.start()
    sisyphus.setprofile.start()
    sisyphus.metadata.regenAnimated()

def PagureMaster():
    sisyphus.check.root()
    sisyphus.branchreset.start()
    sisyphus.branchmaster.startPagure()
    sisyphus.setjobs.start()
    sisyphus.setprofile.start()
    sisyphus.metadata.regenAnimated()

def GitlabNext():
    sisyphus.check.root()
    sisyphus.branchreset.start()
    sisyphus.branchnext.startGitlab()
    sisyphus.setjobs.start()
    sisyphus.setprofile.start()
    sisyphus.metadata.regenAnimated()

def PagureNext():
    sisyphus.check.root()
    sisyphus.branchreset.start()
    sisyphus.branchnext.startPagure()
    sisyphus.setjobs.start()
    sisyphus.setprofile.start()
    sisyphus.metadata.regenAnimated()
