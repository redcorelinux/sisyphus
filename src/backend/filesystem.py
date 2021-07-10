#!/usr/bin/python3

import platform

remoteGitlab = 'https://gitlab.com/redcore'
remotePagure = 'https://pagure.io/redcore'

portageRepo = 'portage.git'
redcoreRepo = 'redcore-desktop.git'
portageConfigRepo = 'redcore-build.git'

portageRepoDir = '/usr/ports/gentoo'
redcoreRepoDir = '/usr/ports/redcore'
portageConfigDir = '/opt/redcore-build'
portageCacheDir = '/var/cache/packages'
portageMetadataDir = '/var/cache/edb'

remotePackagesCsv = '/var/lib/sisyphus/csv/remotePackagesPre.csv'
remoteDescriptionsCsv = '/var/lib/sisyphus/csv/remoteDescriptionsPre.csv'
localPackagesCsv = '/var/lib/sisyphus/csv/localPackagesPre.csv'

localDatabase = '/var/lib/sisyphus/db/sisyphus.db'

if platform.uname()[4] == 'x86_64':
    mirrorCfg = '/etc/sisyphus/sisyphus-mirrors-amd64.conf'

if platform.uname()[4] == 'aarch64':
    mirrorCfg = '/etc/sisyphus/sisyphus-mirrors-arm64.conf'
