#!/usr/bin/python3

import animation
import os
import shutil
import sisyphus.getfs


@animation.wait('purging branch configuration')
def branch():
    if os.path.isdir(sisyphus.getfs.gentooRepoDir):
        for files in os.listdir(sisyphus.getfs.gentooRepoDir):
            if os.path.isfile(os.path.join(sisyphus.getfs.gentooRepoDir, files)):
                os.remove(os.path.join(sisyphus.getfs.gentooRepoDir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.gentooRepoDir, files))
    else:
        os.makedirs(sisyphus.getfs.gentooRepoDir)

    if os.path.isdir(sisyphus.getfs.redcoreRepoDir):
        for files in os.listdir(sisyphus.getfs.redcoreRepoDir):
            if os.path.isfile(os.path.join(sisyphus.getfs.redcoreRepoDir, files)):
                os.remove(os.path.join(sisyphus.getfs.redcoreRepoDir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.redcoreRepoDir, files))
    else:
        os.makedirs(sisyphus.getfs.redcoreRepoDir)

    if os.path.isdir(sisyphus.getfs.portageConfigDir):
        for files in os.listdir(sisyphus.getfs.portageConfigDir):
            if os.path.isfile(os.path.join(sisyphus.getfs.portageConfigDir, files)):
                os.remove(os.path.join(sisyphus.getfs.portageConfigDir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.portageConfigDir, files))
    else:
        os.makedirs(sisyphus.getfs.portageConfigDir)


@animation.wait('purging cached files')
def cache():
    if os.path.isdir(sisyphus.getfs.portageCacheDir):
        for files in os.listdir(sisyphus.getfs.portageCacheDir):
            if os.path.isfile(os.path.join(sisyphus.getfs.portageCacheDir, files)):
                os.remove(os.path.join(sisyphus.getfs.portageCacheDir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.portageCacheDir, files))

    if os.path.isdir(sisyphus.getfs.portageDistDir):
        for files in os.listdir(sisyphus.getfs.portageDistDir):
            if os.path.isfile(os.path.join(sisyphus.getfs.portageDistDir, files)):
                os.remove(os.path.join(sisyphus.getfs.portageDistDir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.portageDistDir, files))


@animation.wait('purging metadata files')
def metadata():
    if os.path.isdir(sisyphus.getfs.portageMetadataDir):
        for files in os.listdir(sisyphus.getfs.portageMetadataDir):
            if os.path.isfile(os.path.join(sisyphus.getfs.portageMetadataDir, files)):
                os.remove(os.path.join(
                    sisyphus.getfs.portageMetadataDir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.portageMetadataDir, files))
