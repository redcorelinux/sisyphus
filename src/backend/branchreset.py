#!/usr/bin/python3

import animation
import os
import shutil
import sisyphus.filesystem

@animation.wait('resetting branch configuration')
def start():
    if os.path.isdir(sisyphus.filesystem.portageRepoDir):
        for files in os.listdir(sisyphus.filesystem.portageRepoDir):
            if os.path.isfile(os.path.join(sisyphus.filesystem.portageRepoDir, files)):
                os.remove(os.path.join(sisyphus.filesystem.portageRepoDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.filesystem.portageRepoDir, files))
    else:
        os.makedirs(sisyphus.filesystem.portageRepoDir)

    if os.path.isdir(sisyphus.filesystem.redcoreRepoDir):
        for files in os.listdir(sisyphus.filesystem.redcoreRepoDir):
            if os.path.isfile(os.path.join(sisyphus.filesystem.redcoreRepoDir, files)):
                os.remove(os.path.join(sisyphus.filesystem.redcoreRepoDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.filesystem.redcoreRepoDir, files))
    else:
        os.makedirs(sisyphus.filesystem.redcoreRepoDir)

    if os.path.isdir(sisyphus.filesystem.portageConfigDir):
        for files in os.listdir(sisyphus.filesystem.portageConfigDir):
            if os.path.isfile(os.path.join(sisyphus.filesystem.portageConfigDir, files)):
                os.remove(os.path.join(sisyphus.filesystem.portageConfigDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.filesystem.portageConfigDir, files))
    else:
        os.makedirs(sisyphus.filesystem.portageConfigDir)
