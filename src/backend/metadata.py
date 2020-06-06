#!/usr/bin/python3

import animation
import os
import shutil
import subprocess

portageMetadataDir = '/var/cache/edb'

def regenSilent():
    if os.path.isdir(portageMetadataDir):
        for files in os.listdir(portageMetadataDir):
            if os.path.isfile(os.path.join(portageMetadataDir, files)):
                os.remove(os.path.join(portageMetadataDir, files))
            else:
                shutil.rmtree(os.path.join(portageMetadataDir, files))

    portageExecStage1 = subprocess.Popen(['emerge', '--quiet', '--regen'], stdout=subprocess.PIPE)
    portageExecStage1.wait()
    portageExecStage2 = subprocess.Popen(['emerge', '--quiet', '--metadata'], stdout=subprocess.PIPE)
    portageExecStage2.wait()

@animation.wait("refreshing metadata")
def regenAnimated():
    if os.path.isdir(portageMetadataDir):
        for files in os.listdir(portageMetadataDir):
            if os.path.isfile(os.path.join(portageMetadataDir, files)):
                os.remove(os.path.join(portageMetadataDir, files))
            else:
                shutil.rmtree(os.path.join(portageMetadataDir, files))

    portageExecStage1 = subprocess.Popen(['emerge', '--quiet', '--regen'], stdout=subprocess.PIPE)
    portageExecStage1.wait()
    portageExecStage2 = subprocess.Popen(['emerge', '--quiet', '--metadata'], stdout=subprocess.PIPE)
    portageExecStage2.wait()    
