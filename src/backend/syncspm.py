#!/usr/bin/python3

import animation
import sisyphus.syncdb

@animation.wait('syncing spm changes')
def cliExec():
    sisyphus.syncdb.localTable()
