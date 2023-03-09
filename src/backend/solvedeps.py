#!/usr/bin/python3

import animation
import os
import pickle
import subprocess
import sisyphus.getfs


@animation.wait('resolving dependencies')
def pkg(pkgname):
    areBinaries = []
    areSources = []
    needsConfig = int()
    p_exe = subprocess.Popen(['emerge', '--quiet', '--pretend', '--getbinpkg', '--rebuilt-binaries', '--with-bdeps=y',
                              '--misspell-suggestion=n', '--fuzzy-search=n'] + list(pkgname), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p_exe.communicate()

    for p_out in stderr.decode('utf-8').splitlines():
        if "The following keyword changes are necessary to proceed:" in p_out:
            needsConfig = int(1)

        if "The following mask changes are necessary to proceed:" in p_out:
            needsConfig = int(1)

        if "The following USE changes are necessary to proceed:" in p_out:
            needsConfig = int(1)

        if "The following REQUIRED_USE flag constraints are unsatisfied:" in p_out:
            needsConfig = int(1)

        if "One of the following masked packages is required to complete your request:" in p_out:
            needsConfig = int(1)

    for p_out in stdout.decode('utf-8').splitlines():
        if "[binary" in p_out:
            isBinary = p_out.split("]")[1].split("[")[0].strip(" ")
            areBinaries.append(isBinary)

        if "[ebuild" in p_out:
            isSource = p_out.split("]")[1].split("[")[0].strip(" ")
            areSources.append(isSource)

    pickle.dump([areBinaries, areSources, needsConfig], open(os.path.join(
        sisyphus.getfs.portageMetadataDir, "sisyphus_pkgdeps.pickle"), "wb"))


@animation.wait('resolving dependencies')
def world():
    areBinaries = []
    areSources = []
    needsConfig = int()
    p_exe = subprocess.Popen(['emerge', '--quiet', '--update', '--deep', '--newuse', '--pretend', '--getbinpkg', '--rebuilt-binaries',
                              '--backtrack=100', '--with-bdeps=y', '--misspell-suggestion=n', '--fuzzy-search=n', '@world'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p_exe.communicate()

    for p_out in stderr.decode('utf-8').splitlines():
        if "The following keyword changes are necessary to proceed:" in p_out:
            needsConfig = int(1)

        if "The following mask changes are necessary to proceed:" in p_out:
            needsConfig = int(1)

        if "The following USE changes are necessary to proceed:" in p_out:
            needsConfig = int(1)

        if "The following REQUIRED_USE flag constraints are unsatisfied:" in p_out:
            needsConfig = int(1)

        if "One of the following masked packages is required to complete your request:" in p_out:
            needsConfig = int(1)

    for p_out in stdout.decode('utf-8').splitlines():
        if "[binary" in p_out:
            isBinary = p_out.split("]")[1].split("[")[0].strip(" ")
            areBinaries.append(isBinary)

        if "[ebuild" in p_out:
            isSource = p_out.split("]")[1].split("[")[0].strip(" ")
            areSources.append(isSource)

    pickle.dump([areBinaries, areSources, needsConfig], open(os.path.join(
        sisyphus.getfs.portageMetadataDir, "sisyphus_worlddeps.pickle"), "wb"))
