#!/usr/bin/python3

import animation
import os
import shutil
import sisyphus.filesystem

@animation.wait('purging branch configuration')
def branch():
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

def cache():
    if os.path.isdir(sisyphus.filesystem.portageCacheDir):
        for files in os.listdir(sisyphus.filesystem.portageCacheDir):
            if os.path.isfile(os.path.join(sisyphus.filesystem.portageCacheDir, files)):
                os.remove(os.path.join(sisyphus.filesystem.portageCacheDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.filesystem.portageCacheDir, files))

def metadata():
    if os.path.isdir(sisyphus.filesystem.portageMetadataDir):
        for files in os.listdir(sisyphus.filesystem.portageMetadataDir):
            if os.path.isfile(os.path.join(sisyphus.filesystem.portageMetadataDir, files)):
                os.remove(os.path.join(sisyphus.filesystem.portageMetadataDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.filesystem.portageMetadataDir, files))
