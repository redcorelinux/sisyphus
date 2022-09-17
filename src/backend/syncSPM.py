#!/usr/bin/python3

import animation
import sisyphus.syncDatabase

@animation.wait('syncing spm changes')
def start():
    sisyphus.syncDatabase.syncLocal()
