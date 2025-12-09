#!/usr/bin/python3

import animation
import os
import sisyphus.getfs
import sisyphus.syncdb


@animation.wait('recovering databases')
def start():
    if os.path.exists(sisyphus.getfs.rmt_pcsv):
        os.remove(sisyphus.getfs.rmt_pcsv)
    if os.path.exists(sisyphus.getfs.rmt_dcsv):
        os.remove(sisyphus.getfs.rmt_dcsv)
    if os.path.exists(sisyphus.getfs.lcl_pcsv):
        os.remove(sisyphus.getfs.lcl_pcsv)
    if os.path.exists(sisyphus.getfs.lcl_db):
        os.remove(sisyphus.getfs.lcl_db)

    sisyphus.syncdb.remote_table()
    sisyphus.syncdb.local_table()
