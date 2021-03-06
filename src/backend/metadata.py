#!/usr/bin/python3

import animation
import os
import shutil
import subprocess
import sisyphus.filesystem

def purge():
    if os.path.isdir(sisyphus.filesystem.portageMetadataDir):
        for files in os.listdir(sisyphus.filesystem.portageMetadataDir):
            if os.path.isfile(os.path.join(sisyphus.filesystem.portageMetadataDir, files)):
                os.remove(os.path.join(sisyphus.filesystem.portageMetadataDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.filesystem.portageMetadataDir, files))
