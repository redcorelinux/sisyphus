#!/usr/bin/python3

import animation
import os
import shutil
import sisyphus.filesystem

@animation.wait('resetting branch configuration')
def start():
    if os.path.isdir(sisyphus.filesystem.gentooEbuildDir):
        for files in os.listdir(sisyphus.filesystem.gentooEbuildDir):
            if os.path.isfile(os.path.join(sisyphus.filesystem.gentooEbuildDir, files)):
                os.remove(os.path.join(sisyphus.filesystem.gentooEbuildDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.filesystem.gentooEbuildDir, files))
    else:
        os.makedirs(sisyphus.filesystem.gentooEbuildDir)

    if os.path.isdir(sisyphus.filesystem.redcoreEbuildDir):
        for files in os.listdir(sisyphus.filesystem.redcoreEbuildDir):
            if os.path.isfile(os.path.join(sisyphus.filesystem.redcoreEbuildDir, files)):
                os.remove(os.path.join(sisyphus.filesystem.redcoreEbuildDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.filesystem.redcoreEbuildDir, files))
    else:
        os.makedirs(sisyphus.filesystem.redcoreEbuildDir)

    if os.path.isdir(sisyphus.filesystem.portageConfigDir):
        for files in os.listdir(sisyphus.filesystem.portageConfigDir):
            if os.path.isfile(os.path.join(sisyphus.filesystem.portageConfigDir, files)):
                os.remove(os.path.join(sisyphus.filesystem.portageConfigDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.filesystem.portageConfigDir, files))
    else:
        os.makedirs(sisyphus.filesystem.portageConfigDir)
