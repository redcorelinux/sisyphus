#!/usr/bin/python3

import platform

remoteGithub = 'https://github.com/redcorelinux'
remoteGitlab = 'https://gitlab.com/redcore'
remotePagure = 'https://pagure.io/redcore'

g_repo = 'portage.git'
r_repo = 'redcore-desktop.git'
p_cfg_repo = 'redcore-build.git'

g_src_dir = '/usr/ports/gentoo'
r_src_dir = '/usr/ports/redcore'
p_cfg_dir = '/opt/redcore-build'
p_cch_dir = '/var/cache/packages'
p_dst_dir = '/var/cache/distfiles'
p_mtd_dir = '/var/cache/edb'

rmt_pcsv = '/var/lib/sisyphus/csv/remotePackagesPre.csv'
rmt_dcsv = '/var/lib/sisyphus/csv/remoteDescriptionsPre.csv'
lcl_pcsv = '/var/lib/sisyphus/csv/localPackagesPre.csv'

lcl_db = '/var/lib/sisyphus/db/sisyphus.db'

if platform.uname()[4] == 'x86_64':
    mirrorCfg = '/etc/sisyphus/sisyphus-mirrors-amd64.conf'

if platform.uname()[4] == 'aarch64':
    mirrorCfg = '/etc/sisyphus/sisyphus-mirrors-arm64.conf'
