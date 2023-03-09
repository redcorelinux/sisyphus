#!/usr/bin/python3

import animation
import os
import shutil
import sisyphus.getfs


@animation.wait('purging branch configuration')
def branch():
    if os.path.isdir(sisyphus.getfs.g_src_dir):
        for files in os.listdir(sisyphus.getfs.g_src_dir):
            if os.path.isfile(os.path.join(sisyphus.getfs.g_src_dir, files)):
                os.remove(os.path.join(sisyphus.getfs.g_src_dir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.g_src_dir, files))
    else:
        os.makedirs(sisyphus.getfs.g_src_dir)

    if os.path.isdir(sisyphus.getfs.r_src_dir):
        for files in os.listdir(sisyphus.getfs.r_src_dir):
            if os.path.isfile(os.path.join(sisyphus.getfs.r_src_dir, files)):
                os.remove(os.path.join(sisyphus.getfs.r_src_dir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.r_src_dir, files))
    else:
        os.makedirs(sisyphus.getfs.r_src_dir)

    if os.path.isdir(sisyphus.getfs.p_cfg_dir):
        for files in os.listdir(sisyphus.getfs.p_cfg_dir):
            if os.path.isfile(os.path.join(sisyphus.getfs.p_cfg_dir, files)):
                os.remove(os.path.join(sisyphus.getfs.p_cfg_dir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.p_cfg_dir, files))
    else:
        os.makedirs(sisyphus.getfs.p_cfg_dir)


@animation.wait('purging cached files')
def cache():
    if os.path.isdir(sisyphus.getfs.p_cch_dir):
        for files in os.listdir(sisyphus.getfs.p_cch_dir):
            if os.path.isfile(os.path.join(sisyphus.getfs.p_cch_dir, files)):
                os.remove(os.path.join(sisyphus.getfs.p_cch_dir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.p_cch_dir, files))

    if os.path.isdir(sisyphus.getfs.p_dst_dir):
        for files in os.listdir(sisyphus.getfs.p_dst_dir):
            if os.path.isfile(os.path.join(sisyphus.getfs.p_dst_dir, files)):
                os.remove(os.path.join(sisyphus.getfs.p_dst_dir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.p_dst_dir, files))


@animation.wait('purging metadata files')
def metadata():
    if os.path.isdir(sisyphus.getfs.p_mtd_dir):
        for files in os.listdir(sisyphus.getfs.p_mtd_dir):
            if os.path.isfile(os.path.join(sisyphus.getfs.p_mtd_dir, files)):
                os.remove(os.path.join(
                    sisyphus.getfs.p_mtd_dir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.p_mtd_dir, files))
