#!/usr/bin/python3

import animation
import os
import shutil
import subprocess
import sisyphus.filesystem

def regenSilent():
    if os.path.isdir(sisyphus.filesystem.portageMetadataDir):
        for files in os.listdir(sisyphus.filesystem.portageMetadataDir):
            if os.path.isfile(os.path.join(sisyphus.filesystem.portageMetadataDir, files)):
                os.remove(os.path.join(sisyphus.filesystem.portageMetadataDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.filesystem.portageMetadataDir, files))

    portageExecStage1 = subprocess.Popen(['emerge', '--quiet', '--regen'], stdout=subprocess.PIPE)
    portageExecStage1.wait()
    portageExecStage2 = subprocess.Popen(['emerge', '--quiet', '--metadata'], stdout=subprocess.PIPE)
    portageExecStage2.wait()

@animation.wait("refreshing metadata")
def regenAnimated():
    if os.path.isdir(sisyphus.filesystem.portageMetadataDir):
        for files in os.listdir(sisyphus.filesystem.portageMetadataDir):
            if os.path.isfile(os.path.join(sisyphus.filesystem.portageMetadataDir, files)):
                os.remove(os.path.join(sisyphus.filesystem.portageMetadataDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.filesystem.portageMetadataDir, files))

    portageExecStage1 = subprocess.Popen(['emerge', '--quiet', '--regen'], stdout=subprocess.PIPE)
    portageExecStage1.wait()
    portageExecStage2 = subprocess.Popen(['emerge', '--quiet', '--metadata'], stdout=subprocess.PIPE)
    portageExecStage2.wait()    
