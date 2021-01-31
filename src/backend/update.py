#!/usr/bin/python3

import animation
import sys
import sisyphus.cache
import sisyphus.check
import sisyphus.database
import sisyphus.metadata
import sisyphus.sync

@animation.wait('fetching updates')
def start():
    sisyphus.cache.clean()

    mismatch = sisyphus.check.branch()

    if mismatch == 0:
        needsPortage = sisyphus.check.portage()
        needsOverlay = sisyphus.check.overlay()

        if needsPortage == 1:
            if needsOverlay == 1:
                sisyphus.sync.portage()
                sisyphus.sync.overlay()
                sisyphus.sync.portageCfg()
                sisyphus.database.syncRemote()
                sisyphus.metadata.regenSilent()
            elif not needsOverlay == 1:
                sisyphus.sync.portage()
                sisyphus.sync.overlay()
                sisyphus.sync.portageCfg()
                sisyphus.database.syncRemote()
                sisyphus.metadata.regenSilent()
        elif not needsPortage == 1:
            if needsOverlay == 1:
                sisyphus.sync.portage()
                sisyphus.sync.overlay()
                sisyphus.sync.portageCfg()
                sisyphus.database.syncRemote()
                sisyphus.metadata.regenSilent()
            elif not needsOverlay == 1:
                sisyphus.sync.portageCfg()
    else:
        sys.exit("\n" + "")
