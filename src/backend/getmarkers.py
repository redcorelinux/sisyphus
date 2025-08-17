#!/usr/bin/python3

import os
import sisyphus.getfs

marker_paths = [
    os.path.join(sisyphus.getfs.g_src_dir, ".git"),
    os.path.join(sisyphus.getfs.r_src_dir, ".git"),
    os.path.join(sisyphus.getfs.p_cfg_dir, ".git"),
]


def markers_exist():
    return all(os.path.exists(path) for path in marker_paths)
