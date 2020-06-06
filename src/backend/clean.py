#!/usr/bin/python3

import os

portageCacheDir = '/var/cache/packages'

def cache():
    if os.path.isdir(portageCacheDir):
        for files in os.listdir(portageCacheDir):
            if os.path.isfile(os.path.join(portageCacheDir, files)):
                os.remove(os.path.join(portageCacheDir, files))
            else:
                shutil.rmtree(os.path.join(portageCacheDir, files))
