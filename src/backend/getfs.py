#!/usr/bin/python3

import platform

remoteGithub = 'https://github.com/redcorelinux'
remoteGitlab = 'https://gitlab.com/redcore'
remotePagure = 'https://pagure.io/redcore'

gentooRepo = 'portage.git'
redcoreRepo = 'redcore-desktop.git'
portageConfigRepo = 'redcore-build.git'

gentooRepoDir = '/usr/ports/gentoo'
redcoreRepoDir = '/usr/ports/redcore'
portageConfigDir = '/opt/redcore-build'
portageCacheDir = '/var/cache/packages'
portageDistDir = '/var/cache/distfiles'
portageMetadataDir = '/var/cache/edb'

rmt_pcsv = '/var/lib/sisyphus/csv/remotePackagesPre.csv'
rmt_dcsv = '/var/lib/sisyphus/csv/remoteDescriptionsPre.csv'
lcl_pcsv = '/var/lib/sisyphus/csv/localPackagesPre.csv'

lcl_db = '/var/lib/sisyphus/db/sisyphus.db'

if platform.uname()[4] == 'x86_64':
    mirrorCfg = '/etc/sisyphus/sisyphus-mirrors-amd64.conf'

if platform.uname()[4] == 'aarch64':
    mirrorCfg = '/etc/sisyphus/sisyphus-mirrors-arm64.conf'
