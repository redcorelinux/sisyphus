#!/usr/bin/python3

import animation
import os
import shutil
import sisyphus.getfs


@animation.wait('purging branch configuration')
def branch():
    if os.path.isdir(sisyphus.getfs.gentoo_ebuild_dir):
        for files in os.listdir(sisyphus.getfs.gentoo_ebuild_dir):
            if os.path.isfile(os.path.join(sisyphus.getfs.gentoo_ebuild_dir, files)):
                os.remove(os.path.join(sisyphus.getfs.gentoo_ebuild_dir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.gentoo_ebuild_dir, files))
    else:
        os.makedirs(sisyphus.getfs.gentoo_ebuild_dir)

    if os.path.isdir(sisyphus.getfs.redcore_ebuild_dir):
        for files in os.listdir(sisyphus.getfs.redcore_ebuild_dir):
            if os.path.isfile(os.path.join(sisyphus.getfs.redcore_ebuild_dir, files)):
                os.remove(os.path.join(sisyphus.getfs.redcore_ebuild_dir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.redcore_ebuild_dir, files))
    else:
        os.makedirs(sisyphus.getfs.redcore_ebuild_dir)

    if os.path.isdir(sisyphus.getfs.portage_cfg_dir):
        for files in os.listdir(sisyphus.getfs.portage_cfg_dir):
            if os.path.isfile(os.path.join(sisyphus.getfs.portage_cfg_dir, files)):
                os.remove(os.path.join(sisyphus.getfs.portage_cfg_dir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.portage_cfg_dir, files))
    else:
        os.makedirs(sisyphus.getfs.portage_cfg_dir)


@animation.wait('purging cached files')
def cache():
    if os.path.isdir(sisyphus.getfs.pkg_cache_dir):
        for files in os.listdir(sisyphus.getfs.pkg_cache_dir):
            if os.path.isfile(os.path.join(sisyphus.getfs.pkg_cache_dir, files)):
                os.remove(os.path.join(sisyphus.getfs.pkg_cache_dir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.pkg_cache_dir, files))

    if os.path.isdir(sisyphus.getfs.src_cache_dir):
        for files in os.listdir(sisyphus.getfs.src_cache_dir):
            if os.path.isfile(os.path.join(sisyphus.getfs.src_cache_dir, files)):
                os.remove(os.path.join(sisyphus.getfs.src_cache_dir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.src_cache_dir, files))


@animation.wait('purging metadata files')
def metadata():
    if os.path.isdir(sisyphus.getfs.pkg_metadata_dir):
        for files in os.listdir(sisyphus.getfs.pkg_metadata_dir):
            if os.path.isfile(os.path.join(sisyphus.getfs.pkg_metadata_dir, files)):
                os.remove(os.path.join(
                    sisyphus.getfs.pkg_metadata_dir, files))
            else:
                shutil.rmtree(os.path.join(
                    sisyphus.getfs.pkg_metadata_dir, files))
