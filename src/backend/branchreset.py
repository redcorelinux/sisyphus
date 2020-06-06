#!/usr/bin/python3

import animation
import os
import shutil

gentooEbuildDir = '/usr/ports/gentoo'
redcoreEbuildDir = '/usr/ports/redcore'
portageConfigDir = '/opt/redcore-build'

@animation.wait('resetting branch configuration')
def start():
    if os.path.isdir(gentooEbuildDir):
        for files in os.listdir(gentooEbuildDir):
            if os.path.isfile(os.path.join(gentooEbuildDir, files)):
                os.remove(os.path.join(gentooEbuildDir, files))
            else:
                shutil.rmtree(os.path.join(gentooEbuildDir, files))
    else:
        os.makedirs(gentooEbuildDir)

    if os.path.isdir(redcoreEbuildDir):
        for files in os.listdir(redcoreEbuildDir):
            if os.path.isfile(os.path.join(redcoreEbuildDir, files)):
                os.remove(os.path.join(redcoreEbuildDir, files))
            else:
                shutil.rmtree(os.path.join(redcoreEbuildDir, files))
    else:
        os.makedirs(redcoreEbuildDir)

    if os.path.isdir(portageConfigDir):
        for files in os.listdir(portageConfigDir):
            if os.path.isfile(os.path.join(portageConfigDir, files)):
                os.remove(os.path.join(portageConfigDir, files))
            else:
                shutil.rmtree(os.path.join(portageConfigDir, files))
    else:
        os.makedirs(portageConfigDir)
