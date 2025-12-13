#!/usr/bin/python3

import platform

rmt_gh_addr = 'https://github.com/redcorelinux'
rmt_gl_addr = 'https://gitlab.com/redcore'
rmt_pg_addr = 'https://pagure.io/redcore'
rmt_cb_addr = 'https://codeberg.org/redcore'

g_repo = 'portage.git'
r_repo = 'redcore-desktop.git'
p_cfg_repo = 'redcore-build.git'

gentoo_ebuild_dir = '/usr/ports/gentoo'
redcore_ebuild_dir = '/usr/ports/redcore'
portage_cfg_dir = '/opt/redcore-build'
pkg_cache_dir = '/var/cache/packages'
src_cache_dir = '/var/cache/distfiles'
pkg_metadata_dir = '/var/cache/edb'

sisyphus_cfg_dir = '/etc/sisyphus'

remote_pkg_csv = '/var/lib/sisyphus/csv/remotePackagesPre.csv'
remote_desc_csv = '/var/lib/sisyphus/csv/remoteDescriptionsPre.csv'

local_db = '/var/lib/sisyphus/db/sisyphus.db'

if platform.uname()[4] == 'x86_64':
    mirrorCfg = '/etc/sisyphus/sisyphus-mirrors-amd64.conf'

if platform.uname()[4] == 'aarch64':
    mirrorCfg = '/etc/sisyphus/sisyphus-mirrors-arm64.conf'
