#!/usr/bin/python3

import animation
import sisyphus.syncdb


@animation.wait('syncing spm changes')
def start():
    sisyphus.syncdb.localTable()
