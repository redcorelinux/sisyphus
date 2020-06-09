#!/usr/bin/python3

import animation
import sisyphus.database

@animation.wait('syncing spm changes')
def start():
    sisyphus.database.syncLocal()
