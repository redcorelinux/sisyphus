#!/usr/bin/python3

import animation
import os
import shutil
import sisyphus.getFilesystem

@animation.wait('purging branch configuration')
def branch():
    if os.path.isdir(sisyphus.getFilesystem.gentooRepoDir):
        for files in os.listdir(sisyphus.getFilesystem.gentooRepoDir):
            if os.path.isfile(os.path.join(sisyphus.getFilesystem.gentooRepoDir, files)):
                os.remove(os.path.join(sisyphus.getFilesystem.gentooRepoDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.getFilesystem.gentooRepoDir, files))
    else:
        os.makedirs(sisyphus.getFilesystem.gentooRepoDir)

    if os.path.isdir(sisyphus.getFilesystem.redcoreRepoDir):
        for files in os.listdir(sisyphus.getFilesystem.redcoreRepoDir):
            if os.path.isfile(os.path.join(sisyphus.getFilesystem.redcoreRepoDir, files)):
                os.remove(os.path.join(sisyphus.getFilesystem.redcoreRepoDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.getFilesystem.redcoreRepoDir, files))
    else:
        os.makedirs(sisyphus.getFilesystem.redcoreRepoDir)

    if os.path.isdir(sisyphus.getFilesystem.portageConfigDir):
        for files in os.listdir(sisyphus.getFilesystem.portageConfigDir):
            if os.path.isfile(os.path.join(sisyphus.getFilesystem.portageConfigDir, files)):
                os.remove(os.path.join(sisyphus.getFilesystem.portageConfigDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.getFilesystem.portageConfigDir, files))
    else:
        os.makedirs(sisyphus.getFilesystem.portageConfigDir)

def cache():
    if os.path.isdir(sisyphus.getFilesystem.portageCacheDir):
        for files in os.listdir(sisyphus.getFilesystem.portageCacheDir):
            if os.path.isfile(os.path.join(sisyphus.getFilesystem.portageCacheDir, files)):
                os.remove(os.path.join(sisyphus.getFilesystem.portageCacheDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.getFilesystem.portageCacheDir, files))

def metadata():
    if os.path.isdir(sisyphus.getFilesystem.portageMetadataDir):
        for files in os.listdir(sisyphus.getFilesystem.portageMetadataDir):
            if os.path.isfile(os.path.join(sisyphus.getFilesystem.portageMetadataDir, files)):
                os.remove(os.path.join(sisyphus.getFilesystem.portageMetadataDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.getFilesystem.portageMetadataDir, files))
