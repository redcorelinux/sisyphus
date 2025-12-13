#!/usr/bin/python3

import animation
import os
import sisyphus.getfs
import sisyphus.syncdb


@animation.wait('recovering databases')
def start():
    if os.path.exists(sisyphus.getfs.remote_pkg_csv):
        os.remove(sisyphus.getfs.remote_pkg_csv)
    if os.path.exists(sisyphus.getfs.remote_desc_csv):
        os.remove(sisyphus.getfs.remote_desc_csv)
    if os.path.exists(sisyphus.getfs.lcl_pcsv):
        os.remove(sisyphus.getfs.lcl_pcsv)
    if os.path.exists(sisyphus.getfs.local_db):
        os.remove(sisyphus.getfs.local_db)

    sisyphus.syncdb.remote_table()
    sisyphus.syncdb.local_table()
