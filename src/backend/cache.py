#!/usr/bin/python3

import os
import shutil
import sisyphus.filesystem

def clean():
    if os.path.isdir(sisyphus.filesystem.portageCacheDir):
        for files in os.listdir(sisyphus.filesystem.portageCacheDir):
            if os.path.isfile(os.path.join(sisyphus.filesystem.portageCacheDir, files)):
                os.remove(os.path.join(sisyphus.filesystem.portageCacheDir, files))
            else:
                shutil.rmtree(os.path.join(sisyphus.filesystem.portageCacheDir, files))
